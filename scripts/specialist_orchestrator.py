"""Execute specialist plans through an explicitly trusted host, dry-run by default.

The host owns real tool invocation, sandboxing, scene fingerprints and checkpoint
creation. This coordinator checks receipts and stops on drift; it cannot sandbox
a dishonest host or certify visual/engine quality. Never auto-replay mutations.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import uuid

from specialist_plan import build_plan


def artifact(root, name):
    if not isinstance(name, str) or not name or Path(name).is_absolute():
        raise ValueError("Evidence must be a relative file path")
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("Missing, escaped or oversized artifact: " + name)
    return {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def validate_context(context):
    if not isinstance(context, dict):
        raise ValueError("Context must be an object")
    for key in ("asset_id", "scene_id", "checkpoint_ref"):
        if not isinstance(context.get(key), str) or not context[key].strip():
            raise ValueError("Missing context: " + key)
    if not isinstance(context.get("commit_sha"), str) or not re.fullmatch("[0-9a-f]{40}", context["commit_sha"]):
        raise ValueError("Exact source commit_sha required")
    for key in ("owned_objects", "protected_objects"):
        values = context.get(key)
        if (not isinstance(values, list) or len(values) > 100 or
                any(not isinstance(v, str) or not v.strip() for v in values) or len(set(values)) != len(values)):
            raise ValueError("Invalid " + key)
    if not context['owned_objects'] or set(context['owned_objects']) & set(context['protected_objects']):
        raise ValueError("Owned targets must be explicit and disjoint from protected objects")


def write_receipt(root, request, result):
    """Trusted host helper: bind the actual run to inspected artifact bytes."""
    root = Path(root).resolve()
    request_id = str(uuid.UUID(request['request_id']))
    if request_id != request['request_id']:
        raise ValueError('Canonical request UUID required')
    receipt = {k: result[k] for k in ('agent_id', 'run_id', 'status')}
    receipt.update({k: request['context'][k] for k in ('asset_id', 'scene_id', 'commit_sha')})
    receipt.update({'request_id': request_id, 'module': request['step']['module'],
                    'evidence': [artifact(root, name) for name in result['evidence']]})
    name = 'receipt-' + request_id + '.json'
    with (root / name).open('x', encoding='utf-8') as output:
        json.dump(receipt, output, allow_nan=False)
    return name


def verify_upstream(root, steps):
    for step in steps:
        for recorded in step['evidence'] + [step['receipt']]:
            if artifact(root, recorded['path']) != recorded:
                raise ValueError('Previously accepted evidence changed: ' + recorded['path'])


def validate_probe(probe, context):
    if not isinstance(probe, dict) or probe.get('scene_id') != context['scene_id']:
        raise ValueError("Scene identity mismatch")
    if not isinstance(probe.get('session_id'), str) or not probe['session_id']:
        raise ValueError("Missing connection/session identity")
    if probe.get('checkpoint_ref') != context['checkpoint_ref']:
        raise ValueError("Checkpoint identity mismatch")
    protected = probe.get('protected')
    if not isinstance(protected, dict) or set(protected) != set(context['protected_objects']):
        raise ValueError("Protected scope mismatch")
    if any(not isinstance(v, str) or not re.fullmatch('[0-9a-f]{64}', v) for v in protected.values()):
        raise ValueError("Invalid protected-object fingerprints")
    return copy.deepcopy({key: probe[key] for key in ('scene_id', 'session_id', 'checkpoint_ref', 'protected')})


class CommandHost:
    """JSON stdin/stdout bridge to a trusted local agent/MCP host, without a shell.

    Commands come from separate operator configuration, never a task or model.
    The host must enforce read/write scope and terminate its own child agents
    on timeout. No commands are inferred from names of MCP tools or LLM roles.
    """
    def __init__(self, command, cwd, timeout=60):
        if (not isinstance(command, list) or not command or
                any(not isinstance(v, str) or not v for v in command)):
            raise ValueError("Trusted command argv required")
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 0 < timeout <= 3600:
            raise ValueError("Timeout must be in (0, 3600]")
        self.command, self.cwd, self.timeout = command, str(cwd), timeout

    def call(self, operation, payload):
        result = subprocess.run(self.command, input=json.dumps({'operation': operation, 'payload': payload}),
                                cwd=self.cwd, capture_output=True, text=True, encoding='utf-8',
                                timeout=self.timeout, check=True, shell=False)
        if len(result.stdout) > 2_000_000:
            raise ValueError("Host response too large")
        data = json.loads(result.stdout)
        if not isinstance(data, dict):
            raise ValueError("Host response must be an object")
        return data

    def probe(self, context):
        return self.call('probe', context)

    def dispatch(self, request):
        return self.call('dispatch', request)


def run(task, context, evidence_root, host=None, *, dry_run=True):
    if not isinstance(dry_run, bool):
        raise ValueError('dry_run must be boolean')
    plan = build_plan(task)
    report = {'schema_version': 1, 'status': 'DRY_RUN', 'plan': plan, 'steps': [], 'errors': [],
              'recovery_required': False, 'publication_authorized': False,
              'independent_review': 'NOT VERIFIED',
              'artistic_quality': 'NOT VERIFIED', 'engine_validation': 'NOT VERIFIED'}
    if dry_run:
        return report
    validate_context(context)
    root = Path(evidence_root).resolve()
    checkpoint = artifact(root, context['checkpoint_ref'])
    report.update({'context': context, 'checkpoint': checkpoint, 'status': 'NOT VERIFIED'})
    if host is None:
        report['errors'].append('No live host adapter supplied')
        return report
    writers, run_ids = set(), set()
    baseline = None
    required_modules = {step['module'] for step in plan['steps']}
    for step in plan['steps']:
        dispatched = False
        entry = {'id': step['id'], 'status': 'NOT VERIFIED', 'evidence': []}
        try:
            probe = host.probe(context)
            identity = validate_probe(probe, context)
            if baseline is None:
                baseline = identity
            if identity != baseline or artifact(root, context['checkpoint_ref']) != checkpoint:
                raise ValueError('Scene/session/protected objects or checkpoint changed; stop and inspect recovery')
            verify_upstream(root, report['steps'])
            if (not required_modules.issubset(probe.get('modules', [])) or
                    (any(s['access'] == 'write' for s in plan['steps']) and probe.get('write') is not True) or
                    (plan['mode'] == 'delegated' and probe.get('delegation') is not True)):
                report['errors'].append('Required plan capabilities unavailable')
                report['recovery_required'] = bool(writers)
                return report
            request = {'schema_version': 1, 'request_id': str(uuid.uuid4()), 'task': task,
                       'destination': plan['destination'],
                       'context': context, 'step': step, 'mode': plan['mode'],
                       'upstream': report['steps'], 'checkpoint': checkpoint}
            dispatched = True
            result = host.dispatch(request)
            # Always probe after a dispatch, including failed writers in the exception path.
            if validate_probe(host.probe(context), context) != baseline:
                raise ValueError('Scene/session or protected objects changed during dispatch')
            if artifact(root, context['checkpoint_ref']) != checkpoint:
                raise ValueError('Recovery checkpoint was overwritten')
            verify_upstream(root, report['steps'])
            if not isinstance(result, dict) or result.get('request_id') != request['request_id']:
                raise ValueError('Stale or mismatched specialist response')
            for key in ('agent_id', 'run_id'):
                if not isinstance(result.get(key), str) or not result[key].strip():
                    raise ValueError('Actual agent and run identities required')
            if result['run_id'] in run_ids:
                raise ValueError('Replayed specialist run')
            run_ids.add(result['run_id'])
            state = result.get('status')
            if state not in ('PASS', 'ISSUE', 'NOT VERIFIED'):
                raise ValueError('Invalid specialist status')
            refs = result.get('evidence', [])
            errors = result.get('errors', [])
            notes = result.get('notes', [])
            metrics = result.get('metrics', {})
            if not isinstance(refs, list) or len(refs) > 30 or not isinstance(errors, list) or any(not isinstance(e, str) for e in errors) or not isinstance(metrics, dict):
                raise ValueError('Invalid evidence/errors/metrics contract')
            if not isinstance(notes, list) or any(not isinstance(note, str) for note in notes):
                raise ValueError('Invalid scoped review notes')
            evidence = [artifact(root, name) for name in refs]
            receipt_file = artifact(root, result.get('receipt'))
            receipt = json.loads((root / receipt_file['path']).read_text(encoding='utf-8'))
            expected = {'request_id': request['request_id'], 'run_id': result['run_id'],
                        'agent_id': result['agent_id'], 'module': step['module'],
                        'asset_id': context['asset_id'], 'scene_id': context['scene_id'],
                        'commit_sha': context['commit_sha'], 'status': state, 'evidence': evidence}
            if not isinstance(receipt, dict) or any(receipt.get(k) != v for k, v in expected.items()):
                raise ValueError('Stale, mismatched or modified evidence receipt')
            if state == 'PASS' and (not evidence or errors):
                state = 'NOT VERIFIED'
            if step['access'] == 'write':
                if plan['mode'] == 'single' and writers and result['agent_id'] not in writers:
                    raise ValueError('Simple plan unexpectedly changed production agent')
                writers.add(result['agent_id'])
            elif plan['mode'] == 'single' and result['agent_id'] not in writers:
                raise ValueError('Simple plan unexpectedly changed coordinator for validation')
            elif plan['mode'] == 'delegated' and result['agent_id'] in writers:
                state = 'NOT VERIFIED'
                errors = errors + ['Independent review cannot be performed by a producer']
            elif step['access'] == 'read' and plan['mode'] == 'delegated' and state == 'PASS':
                report['independent_review'] = 'RECEIPT VERIFIED'
            entry.update({'status': state, 'agent_id': result['agent_id'], 'run_id': result['run_id'],
                          'request_id': request['request_id'], 'evidence': evidence, 'receipt': receipt_file,
                          'errors': errors, 'notes': notes, 'metrics': metrics})
            report['steps'].append(entry)
            if state != 'PASS':
                report['status'] = state
                report['recovery_required'] = step['access'] == 'write'
                return report
        except Exception as error:
            entry.update({'status': 'ISSUE', 'error': str(error)})
            report['steps'].append(entry)
            report['status'] = 'ISSUE'
            report['errors'].append(str(error))
            report['recovery_required'] = baseline is not None or (dispatched and step['access'] == 'write')
            if dispatched:
                try:
                    report['failure_scene_probe'] = validate_probe(host.probe(context), context)
                    if report['failure_scene_probe'] != baseline:
                        report['recovery_required'] = True
                except Exception as probe_error:
                    report['errors'].append('Post-failure probe unavailable: ' + str(probe_error))
                    report['recovery_required'] = True
            return report
    report['status'] = 'REVIEW'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task', type=Path)
    parser.add_argument('--context', type=Path)
    parser.add_argument('--evidence-root', type=Path, default=Path('.'))
    parser.add_argument('--adapter-config', type=Path, help='Trusted operator configuration, never model output')
    parser.add_argument('--execute', action='store_true', help='Invoke host; default only prints plan')
    args = parser.parse_args()
    try:
        context = json.loads(args.context.read_text(encoding='utf-8')) if args.context else {}
        host = None
        if args.execute and args.adapter_config:
            config = json.loads(args.adapter_config.read_text(encoding='utf-8'))
            host = CommandHost(config['command'], args.evidence_root, config.get('timeout_seconds', 60))
        result = run(json.loads(args.task.read_text(encoding='utf-8')), context, args.evidence_root,
                     host, dry_run=not args.execute)
    except (ValueError, OSError, KeyError) as error:
        result = {'status': 'NOT VERIFIED', 'errors': [str(error)]}
    print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    return 0 if result['status'] in ('DRY_RUN', 'REVIEW') else 1


