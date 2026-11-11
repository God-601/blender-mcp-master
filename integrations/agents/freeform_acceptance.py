"""Opt-in actual agent-authored bpy acceptance; inspected code, never a Python sandbox.

Generate preserves provider receipts. Execute requires an operator-approved code
receipt hash and runs only in a new background Blender, never the user's live scene.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
REVIEW_INPUTS = ('generation.json', 'script.py', 'prompt.txt', 'provider.jsonl')
SCHEMA = {'type': 'object', 'additionalProperties': False, 'properties': {
    'owned_objects': {'type': 'array', 'items': {'type': 'string'}},
    'code': {'type': 'string'}, 'notes': {'type': 'array', 'items': {'type': 'string'}}},
    'required': ['owned_objects', 'code', 'notes']}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def approved_code(path, approved):
    code = Path(path).read_bytes()
    if not approved or hashlib.sha256(code).hexdigest() != approved:
        raise ValueError('Inspect the generation packet and approve its current receipt SHA256')
    return code.decode('utf-8')


def check_source_binding(source, expected_hash):
    if bool(source) != bool(expected_hash):
        raise ValueError('Execution source presence differs from specialist generation')
    if source and sha(source) != expected_hash:
        raise ValueError('Specialist source bytes changed after generation')


def validate_generation(value):
    if not isinstance(value, dict) or set(value) != {'owned_objects', 'code', 'notes'}:
        raise ValueError('Unexpected generated response')
    names = value['owned_objects']
    if not isinstance(names, list) or not names or len(names) > 100:
        raise ValueError('Explicit unique owned objects required')
    if any(not isinstance(name, str) or not name.startswith('V2_') or name == 'V2_' for name in names):
        raise ValueError('Owned names must start V2_')
    if len(set(names)) != len(names):
        raise ValueError('Explicit unique owned objects required')
    if not isinstance(value['code'], str) or not value['code'].strip() or len(value['code']) > 150_000:
        raise ValueError('Missing or oversized generated script')
    if not isinstance(value['notes'], list) or any(not isinstance(v, str) for v in value['notes']):
        raise ValueError('Invalid notes')
    ast.parse(value['code'])


def provider_observations(log):
    events = [json.loads(line) for line in log.splitlines() if line.strip()]
    threads = [e['thread_id'] for e in events if e.get('type') == 'thread.started']
    usage = [e['usage'] for e in events if e.get('type') == 'turn.completed']
    if len(threads) != 1 or not isinstance(threads[0], str) or not threads[0]:
        raise ValueError('Expected one recorded provider thread')
    if (len(usage) != 1 or not isinstance(usage[0], dict) or any(
            type(usage[0].get(key)) is not int or usage[0][key] < 0
            for key in ('input_tokens', 'output_tokens'))):
        raise ValueError('Expected one completed provider usage record')
    return threads, usage


def load_reviewed_generation(directory, approved):
    receipt = json.loads(approved_code(directory / 'provider-receipt.json', approved))
    if receipt['status'] != 'GENERATED_REVIEW_REQUIRED' or receipt['runner_sha256'] != sha(__file__):
        raise ValueError('Generation did not complete on the current runner')
    expected = receipt.get('input_sha256', {})
    inputs = {}
    for name in REVIEW_INPUTS:
        path = directory / name
        if not path.is_file():
            raise ValueError('Reviewed generation input missing: ' + name)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != expected.get(name):
            raise ValueError('Reviewed generation input changed: ' + name)
        inputs[name] = data.decode('utf-8')
    value = json.loads(inputs['generation.json'])
    validate_generation(value)
    if inputs['script.py'] != value['code']:
        raise ValueError('Reviewed script differs from the generated response')
    threads, usage = provider_observations(inputs['provider.jsonl'])
    if threads != receipt['thread_ids'] or usage != receipt['provider_usage']:
        raise ValueError('Provider log differs from the reviewed receipt')
    return value, receipt, inputs['prompt.txt']


def source_revision(declared):
    if declared is not None and not re.fullmatch('[0-9a-f]{40}', declared):
        raise ValueError('--source-commit must be a 40-character Git SHA')
    if (ROOT / '.git').exists():
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        if declared is not None and revision != declared:
            raise ValueError('--source-commit differs from the checkout revision')
        dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'],
                                       cwd=ROOT, text=True).strip()
        return revision, 'checkout_dirty' if dirty else 'checkout_clean'
    if declared is None:
        raise ValueError('Supply --source-commit from the verified archive provenance')
    return declared, 'operator_declared'


def check_scene_objects(bpy, owned, protected):
    if set(bpy.data.objects.keys()) != set(owned) | set(protected):
        raise ValueError('Generated objects differ from approved declared ownership')
    if not set(owned) <= set(bpy.context.scene.objects.keys()):
        raise ValueError('Owned objects must be linked to the active scene')


def generate(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    prompt = args.prompt.read_text(encoding='utf-8')
    source_hash = sha(args.source) if args.source else None
    if args.source:
        prompt += f'\n\nPrior Blender stage: {args.source.resolve()}\nSHA256: {source_hash}\n'
        prompt += 'Use the scene facts in the brief and bpy to inspect the opened stage when the script runs. Declare existing names only when the brief authorizes editing them.'
    (out / 'prompt.txt').write_bytes(prompt.encode('utf-8'))
    write(out / 'schema.json', SCHEMA)
    command = [shutil.which('codex') or 'codex', '-a', 'never', 'exec', '--ignore-user-config',
        '--ephemeral', '--json', '--skip-git-repo-check', '--sandbox', 'read-only',
        '--model', args.model, '-c', 'model_reasoning_effort="medium"',
        '--output-schema', str(out / 'schema.json'), '--output-last-message', str(out / 'generation.json'), '-']
    record = {'status': 'FAIL', 'command': command, 'model_requested': args.model,
        'model_reported': 'NOT VERIFIED', 'prompt_sha256': sha(out / 'prompt.txt'),
        'runner_sha256': sha(__file__), 'source': str(args.source.resolve()) if args.source else None,
        'source_sha256': source_hash,
        'scope': 'Agent-authored bpy, executed separately only after code review/hash approval.'}
    started = time.monotonic()
    try:
        with (out / 'provider.jsonl').open('w', encoding='utf-8') as stdout, (out / 'provider.stderr.txt').open('w', encoding='utf-8') as stderr:
            process = subprocess.run(command, input=prompt, cwd=out, text=True, encoding='utf-8',
                stdout=stdout, stderr=stderr, timeout=args.timeout)
        record['exit_code'] = process.returncode
        if process.returncode:
            raise RuntimeError(f'Provider exited with status {process.returncode}')
        record['thread_ids'], record['provider_usage'] = provider_observations(
            (out / 'provider.jsonl').read_text(encoding='utf-8'))
        result = json.loads((out / 'generation.json').read_text(encoding='utf-8'))
        validate_generation(result)
        if args.source and sha(args.source) != record['source_sha256']:
            raise ValueError('Source bytes changed during specialist generation')
        (out / 'script.py').write_bytes(result['code'].encode('utf-8'))
        record.update(status='GENERATED_REVIEW_REQUIRED', code_sha256=sha(out / 'script.py'),
                      input_sha256={name: sha(out / name) for name in REVIEW_INPUTS})
    except Exception as error:
        record['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        record['seconds'] = round(time.monotonic() - started, 3)
        write(out / 'provider-receipt.json', record)
    print(json.dumps(dict(record, review_sha256=sha(out / 'provider-receipt.json'))))


def audit(bpy, names):
    records = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for name in names:
        obj = bpy.data.objects[name]
        record = {'name': name, 'type': obj.type, 'dimensions': list(obj.dimensions),
            'location': list(obj.location), 'modifiers': [{'type': m.type, 'name': m.name} for m in obj.modifiers]}
        if obj.type == 'MESH':
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                mesh.calc_loop_triangles()
                edges = {tuple(sorted(e.vertices)): 0 for e in mesh.edges}
                for polygon in mesh.polygons:
                    for edge in polygon.edge_keys:
                        edges[tuple(sorted(edge))] += 1
                record.update(vertices=len(mesh.vertices), faces=len(mesh.polygons), triangles=len(mesh.loop_triangles),
                    boundary_edges=sum(v == 1 for v in edges.values()), nonmanifold_edges=sum(v > 2 for v in edges.values()),
                    loose_edges=sum(v == 0 for v in edges.values()), uv_layers=len(mesh.uv_layers),
                    materials=[m.name if m else None for m in mesh.materials],
                    degenerate_triangles=sum(t.area < 1e-12 for t in mesh.loop_triangles))
            finally:
                evaluated.to_mesh_clear()
            record['unweighted_vertices'] = sum(not v.groups for v in obj.data.vertices) if any(m.type == 'ARMATURE' for m in obj.modifiers) else None
        elif obj.type == 'ARMATURE':
            record.update(bones=[b.name for b in obj.data.bones], pose_bones=[b.name for b in obj.pose.bones])
        records.append(record)
    return {'blender_version': bpy.app.version_string, 'objects': records,
        'limits': 'Measured metadata, not independent visual quality or engine certification.'}


def inside(args):
    import bpy
    if not bpy.app.background:
        raise RuntimeError('Requires a disposable background Blender; live scene execution is refused')
    import math
    import mathutils
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from blender_native_host import BlenderNativeHost
    from scene_baseline_snapshot import capture_object
    generation_dir, out = args.generation.resolve(), args.output.resolve()
    value, provider, prompt = load_reviewed_generation(generation_dir, args.approved_sha)
    code = value['code']
    check_source_binding(args.source, provider['source_sha256'])
    check_source_binding(args.input_copy, provider['source_sha256'])
    if args.source and Path(bpy.data.filepath).resolve() != args.input_copy.resolve():
        raise ValueError('Blender did not open the reviewed source copy')
    out.mkdir(parents=True, exist_ok=False)
    if not args.source:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.render.engine = 'CYCLES'
        bpy.ops.mesh.primitive_cube_add(size=1, location=(50, 50, 50))
        sentinel = bpy.context.object
        sentinel.name = 'ProtectedSentinel'
        sentinel.hide_render = True
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'source.blend'))
    source_path = Path(bpy.data.filepath)
    source_hash = sha(source_path)
    protected = [name for name in bpy.data.objects.keys() if name not in value['owned_objects']]
    before = {name: capture_object(bpy.data.objects[name]) for name in protected}
    write(out / 'protected-before.json', before)
    commit, revision_status = source_revision(args.source_commit)

    def execute(request):
        namespace = {'bpy': bpy, 'math': math, 'mathutils': mathutils, 'OUTPUT_ROOT': out}
        exec(compile(code, str(generation_dir / 'script.py'), 'exec'), namespace)
        check_scene_objects(bpy, value['owned_objects'], protected)
        measured = audit(bpy, value['owned_objects'])
        write(out / 'audit.json', measured)
        errors = [r['name'] + ': degenerate/nonmanifold/loose geometry' for r in measured['objects']
            if r['type'] == 'MESH' and any(r[k] for k in ('nonmanifold_edges', 'loose_edges', 'degenerate_triangles'))]
        if not any(r.get('triangles', 0) > 0 for r in measured['objects']):
            errors.append('No evaluated mesh faces in the owned scene output')
        return {'status': 'ISSUE' if errors else 'PASS', 'evidence': ['audit.json'], 'errors': errors, 'metrics': {}}

    with BlenderNativeHost(out, asset_id=args.asset_id, owned_objects=value['owned_objects'],
            protected_objects=protected, commit_sha=commit, actor_id=provider['thread_ids'][0],
            callbacks={args.module: execute}) as host:
        request = {'schema_version': 1, 'request_id': str(uuid.uuid4()), 'task': {'brief': prompt},
            'destination': 'controlled_acceptance', 'context': host.context, 'mode': 'single',
            'step': {'module': args.module, 'access': 'write'}, 'upstream': [], 'checkpoint': host.checkpoint}
        result = host.dispatch(request)
        write(out / 'dispatch.json', result)
        if result['status'] != 'PASS':
            raise ValueError('Generated stage failed measured geometry checks')
    after = {name: capture_object(bpy.data.objects[name]) for name in protected}
    if before != after or sha(source_path) != source_hash:
        raise ValueError('Protected scene or source file changed')
    check_source_binding(args.source, provider['source_sha256'])
    write(out / 'protected-after.json', after)
    stages = [name for name in result['evidence'] if name.endswith('.blend')]
    assert len(stages) == 1
    write(out / 'stage.json', {'status': 'EXECUTED_SCOPED_STAGE', 'stage_blend': stages[0], 'source': str(args.source.resolve() if args.source else source_path),
        'source_sha256': source_hash, 'source_preserved': True,
        'code_sha256': provider['input_sha256']['script.py'], 'review_sha256': args.approved_sha,
        'revision_status': revision_status,
        'actual_specialist_thread': provider['thread_ids'][0], 'commit_sha': commit,
        'runner_sha256': sha(__file__), 'owned_objects': value['owned_objects']})
    print('FREEFORM_STAGE_COMPLETE', str(out))


def execute(args):
    if args.inside:
        return inside(args)
    if args.output.exists() or args.output.with_suffix('.log').exists():
        raise FileExistsError('Use a new stage directory and log; preserve prior attempts')
    _, provider, _ = load_reviewed_generation(args.generation, args.approved_sha)
    check_source_binding(args.source, provider['source_sha256'])
    source_revision(args.source_commit)
    if not args.blender:
        raise ValueError('--blender is required to launch a disposable stage')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='reviewed-blender-source-') as scratch:
        command = [str(args.blender), '--background', '--factory-startup', '--disable-autoexec', '--threads', '2']
        copy = None
        if args.source:
            copy = Path(scratch) / 'source.blend'
            shutil.copyfile(args.source, copy)
            check_source_binding(copy, provider['source_sha256'])
            command.append(str(copy))
        command.extend(['--python-exit-code', '1', '--python', str(Path(__file__).resolve()), '--', 'execute',
            '--inside', '--generation', str(args.generation.resolve()), '--output', str(args.output.resolve()),
            '--approved-sha', args.approved_sha, '--asset-id', args.asset_id, '--module', args.module])
        if copy is not None:
            command.extend(['--source', str(args.source.resolve()), '--input-copy', str(copy)])
        if args.source_commit:
            command.extend(['--source-commit', args.source_commit])
        with args.output.with_suffix('.log').open('x', encoding='utf-8') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=args.timeout, check=True)
    print((args.output / 'stage.json').read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    gen = commands.add_parser('generate')
    gen.add_argument('--prompt', type=Path, required=True)
    gen.add_argument('--model', required=True)
    gen.add_argument('--source', type=Path)
    gen.add_argument('--output', type=Path, required=True)
    gen.add_argument('--timeout', type=float, default=600)
    run = commands.add_parser('execute')
    run.add_argument('--generation', type=Path, required=True)
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--approved-sha', required=True, help='SHA256 of the reviewed provider-receipt.json')
    run.add_argument('--source-commit', help='Source Git SHA for an extracted archive without Git metadata')
    run.add_argument('--input-copy', type=Path, help=argparse.SUPPRESS)
    run.add_argument('--source', type=Path)
    run.add_argument('--blender', type=Path)
    run.add_argument('--asset-id', required=True)
    run.add_argument('--module', choices=['modeling', 'uv', 'materials', 'retopology'], required=True)
    run.add_argument('--inside', action='store_true')
    run.add_argument('--timeout', type=float, default=600)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    if args.timeout <= 0:
        parser.error('Positive timeout required')
    generate(args) if args.operation == 'generate' else execute(args)


if __name__ == '__main__':
    main()
