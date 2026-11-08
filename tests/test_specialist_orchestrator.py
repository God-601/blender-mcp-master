import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from specialist_orchestrator import CommandHost, artifact, run


class Host:
    def __init__(self):
        self.calls = []
        self.drift = False
        self.fail = False
        self.same_reviewer = False
        self.delegation = True
        self.bad_evidence = False
        self.stale_receipt = False
        self.root = None

    def probe(self, context):
        return {'scene_id': context['scene_id'], 'session_id': 'session-1',
                'checkpoint_ref': context['checkpoint_ref'],
                'protected': {'Keep': ('b' if self.drift else 'a') * 64},
                'modules': ['modeling', 'materials', 'uv', 'retopology', 'optimization', 'export', 'validation'],
                'delegation': self.delegation, 'write': True}

    def dispatch(self, request):
        self.calls.append(copy.deepcopy(request))
        if self.fail:
            raise RuntimeError('worker disconnected after edit')
        role = request['step']['module']
        result = {'request_id': request['request_id'], 'agent_id': 'builder' if self.same_reviewer or role != 'validation' else 'reviewer',
                'run_id': request['request_id'], 'status': 'PASS',
                'evidence': ['missing.json' if self.bad_evidence else 'audit.json'], 'errors': [], 'metrics': {'triangles': 12}}
        receipt = {k: result[k] for k in ('request_id', 'agent_id', 'run_id', 'status')}
        receipt.update({k: request['context'][k] for k in ('asset_id', 'scene_id', 'commit_sha')})
        receipt.update({'module': role, 'evidence': [artifact(self.root, 'audit.json')]})
        if self.stale_receipt:
            receipt['request_id'] = 'old-run'
        result['receipt'] = request['request_id'] + '.json'
        (self.root / result['receipt']).write_text(json.dumps(receipt), encoding='utf-8')
        return result


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'checkpoint.blend').write_bytes(b'fixture, not a real Blender checkpoint')
        (self.root / 'audit.json').write_text('{"fixture": true}', encoding='utf-8')
        self.context = {'asset_id': 'panel', 'scene_id': 'scene-1', 'commit_sha': 'c' * 40,
                        'owned_objects': ['Panel'], 'protected_objects': ['Keep'],
                        'checkpoint_ref': 'checkpoint.blend'}
        self.task = {'category': 'hard_surface'}
        self.host = Host()
        self.host.root = self.root

    def execute(self, **kwargs):
        return run(self.task, self.context, self.root, self.host, dry_run=False, **kwargs)

    def test_default_dry_run_does_not_probe_or_dispatch(self):
        self.assertEqual(run(self.task, {}, self.root)['status'], 'DRY_RUN')
        self.assertEqual(self.host.calls, [])

    def test_real_dispatch_and_hashed_handoffs(self):
        result = self.execute()
        self.assertEqual(result['status'], 'REVIEW')
        self.assertEqual(len(self.host.calls), 2)
        self.assertEqual(self.host.calls[1]['upstream'][0]['agent_id'], 'builder')
        self.assertEqual(result['steps'][0]['evidence'][0]['sha256'], hashlib.sha256((self.root / 'audit.json').read_bytes()).hexdigest())
        self.assertFalse(result['publication_authorized'])
        self.assertEqual(result['artistic_quality'], 'NOT VERIFIED')

    def test_missing_adapter_blocks_without_fabricating_agent(self):
        result = run(self.task, self.context, self.root, dry_run=False)
        self.assertEqual(result['status'], 'NOT VERIFIED')
        self.assertEqual(result['steps'], [])

    def test_stale_receipt_cannot_pass_with_fresh_response_id(self):
        self.host.stale_receipt = True
        self.assertEqual(self.execute()['status'], 'ISSUE')

    def test_dispatch_carries_actual_task_and_destination(self):
        self.task.update({'category': 'organic', 'destination': 'unity', 'needs': ['export']})
        self.execute()
        self.assertEqual(self.host.calls[0]['task'], self.task)
        self.assertEqual(self.host.calls[0]['destination'], 'unity')

    def test_drift_before_next_dispatch_requires_recovery(self):
        probe = self.host.probe
        count = [0]
        def drift(context):
            count[0] += 1
            self.host.drift = count[0] >= 3
            return probe(context)
        self.host.probe = drift
        result = self.execute()
        self.assertEqual(result['status'], 'ISSUE')
        self.assertTrue(result['recovery_required'])
        self.assertEqual(len(self.host.calls), 1)

    def test_unavailable_delegation_stops_before_writes(self):
        self.task['needs'] = ['uv', 'pbr']
        self.host.delegation = False
        self.assertEqual(self.execute()['status'], 'NOT VERIFIED')
        self.assertEqual(self.host.calls, [])

    def test_writer_failure_is_not_retried_or_auto_reverted(self):
        self.host.fail = True
        result = self.execute()
        self.assertEqual(result['status'], 'ISSUE')
        self.assertTrue(result['recovery_required'])
        self.assertEqual(len(self.host.calls), 1)

    def test_independent_review_and_evidence_required(self):
        self.host.same_reviewer = True
        self.assertEqual(self.execute()['status'], 'NOT VERIFIED')
        self.host.same_reviewer = False
        self.host.bad_evidence = True
        self.assertEqual(self.execute()['status'], 'ISSUE')

    def test_protected_damage_stops_later_stages(self):
        original = self.host.dispatch
        def damage(request):
            result = original(request)
            self.host.drift = True
            return result
        self.host.dispatch = damage
        result = self.execute()
        self.assertEqual(result['status'], 'ISSUE')
        self.assertTrue(result['recovery_required'])
        self.assertEqual(len(self.host.calls), 1)

    def test_invalid_ownership_and_paths_fail_before_dispatch(self):
        self.context['owned_objects'] = ['Keep']
        with self.assertRaises(ValueError):
            self.execute()
        self.context['owned_objects'] = ['Panel']
        self.context['checkpoint_ref'] = '../outside.blend'
        with self.assertRaises(ValueError):
            self.execute()
        self.assertEqual(self.host.calls, [])

    def test_subprocess_adapter_actually_exchanges_json(self):
        worker = self.root / 'worker.py'
        worker.write_text('import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({"operation": r["operation"]}))', encoding='utf-8')
        host = CommandHost([sys.executable, str(worker)], self.root, timeout=2)
        self.assertEqual(host.probe({}), {'operation': 'probe'})
        self.assertEqual(host.dispatch({}), {'operation': 'dispatch'})

    def test_subprocess_timeout_and_malformed_output(self):
        worker = self.root / 'worker.py'
        worker.write_text('print("not JSON")', encoding='utf-8')
        with self.assertRaises(ValueError):
            CommandHost([sys.executable, str(worker)], self.root).probe({})
        worker.write_text('import time\ntime.sleep(5)', encoding='utf-8')
        with self.assertRaises(subprocess.TimeoutExpired):
            CommandHost([sys.executable, str(worker)], self.root, timeout=0.05).probe({})
