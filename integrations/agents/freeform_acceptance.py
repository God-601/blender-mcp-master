"""Opt-in actual agent-authored bpy acceptance; inspected code, never a Python sandbox.

Generate preserves provider receipts. Execute requires an operator-approved code
hash and runs only in a new background Blender, never the user's live scene.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
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
        raise ValueError('Inspect the exact script and explicitly approve its current SHA256')
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
    if not isinstance(names, list) or not names or len(names) > 100 or len(set(names)) != len(names):
        raise ValueError('Explicit unique owned objects required')
    if any(not isinstance(name, str) or not name.startswith('V2_') for name in names):
        raise ValueError('Owned names must start V2_')
    if not isinstance(value['code'], str) or not value['code'].strip() or len(value['code']) > 150_000:
        raise ValueError('Missing or oversized generated script')
    if not isinstance(value['notes'], list) or any(not isinstance(v, str) for v in value['notes']):
        raise ValueError('Invalid notes')
    ast.parse(value['code'])


def generate(args):
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    prompt = args.prompt.read_text(encoding='utf-8')
    (out / 'prompt.txt').write_text(prompt, encoding='utf-8')
    write(out / 'schema.json', SCHEMA)
    command = [shutil.which('codex') or 'codex', '-a', 'never', 'exec', '--ignore-user-config',
        '--ephemeral', '--json', '--skip-git-repo-check', '--sandbox', 'read-only',
        '--model', args.model, '-c', 'model_reasoning_effort="medium"',
        '--output-schema', str(out / 'schema.json'), '--output-last-message', str(out / 'generation.json'), '-']
    record = {'status': 'FAIL', 'command': command, 'model_requested': args.model,
        'model_reported': 'NOT VERIFIED', 'prompt_sha256': sha(out / 'prompt.txt'),
        'runner_sha256': sha(__file__), 'source': str(args.source.resolve()) if args.source else None,
        'source_sha256': sha(args.source) if args.source else None,
        'scope': 'Agent-authored bpy, executed separately only after code review/hash approval.'}
    started = time.monotonic()
    try:
        with (out / 'provider.jsonl').open('w', encoding='utf-8') as stdout, (out / 'provider.stderr.txt').open('w', encoding='utf-8') as stderr:
            process = subprocess.run(command, input=prompt, cwd=out, text=True, encoding='utf-8',
                stdout=stdout, stderr=stderr, timeout=args.timeout)
        record['exit_code'] = process.returncode
        events = [json.loads(line) for line in (out / 'provider.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
        threads = [e['thread_id'] for e in events if e.get('type') == 'thread.started']
        usage = [e['usage'] for e in events if e.get('type') == 'turn.completed' and isinstance(e.get('usage'), dict)]
        record['thread_ids'], record['provider_usage'] = threads, usage
        if process.returncode or len(threads) != 1 or len(usage) != 1:
            raise RuntimeError('Provider did not return one completed recorded generation')
        result = json.loads((out / 'generation.json').read_text(encoding='utf-8'))
        validate_generation(result)
        if args.source and sha(args.source) != record['source_sha256']:
            raise ValueError('Source bytes changed during specialist generation')
        (out / 'script.py').write_text(result['code'], encoding='utf-8')
        record.update(status='GENERATED_REVIEW_REQUIRED', code_sha256=sha(out / 'script.py'))
    except Exception as error:
        record['error'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        record['seconds'] = round(time.monotonic() - started, 3)
        write(out / 'provider-receipt.json', record)
    print(json.dumps(record))


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
    value = json.loads((generation_dir / 'generation.json').read_text(encoding='utf-8'))
    validate_generation(value)
    code = approved_code(generation_dir / 'script.py', args.approved_sha)
    provider = json.loads((generation_dir / 'provider-receipt.json').read_text(encoding='utf-8'))
    if provider['status'] != 'GENERATED_REVIEW_REQUIRED' or provider['code_sha256'] != args.approved_sha:
        raise ValueError('Generated provider receipt does not bind this script')
    check_source_binding(args.source, provider['source_sha256'])
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
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()

    def execute(request):
        namespace = {'bpy': bpy, 'math': math, 'mathutils': mathutils, 'OUTPUT_ROOT': out}
        exec(compile(code, str(generation_dir / 'script.py'), 'exec'), namespace)
        if set(bpy.data.objects.keys()) != set(value['owned_objects']) | set(protected):
            raise ValueError('Generated objects differ from approved declared ownership')
        measured = audit(bpy, value['owned_objects'])
        write(out / 'audit.json', measured)
        errors = [r['name'] + ': degenerate/nonmanifold/loose geometry' for r in measured['objects']
            if r['type'] == 'MESH' and any(r[k] for k in ('nonmanifold_edges', 'loose_edges', 'degenerate_triangles'))]
        return {'status': 'ISSUE' if errors else 'PASS', 'evidence': ['audit.json'], 'errors': errors, 'metrics': {}}

    with BlenderNativeHost(out, asset_id=args.asset_id, owned_objects=value['owned_objects'],
            protected_objects=protected, commit_sha=commit, actor_id=provider['thread_ids'][0],
            callbacks={args.module: execute}) as host:
        request = {'schema_version': 1, 'request_id': str(uuid.uuid4()), 'task': {'brief': (generation_dir / 'prompt.txt').read_text(encoding='utf-8')},
            'destination': 'controlled_acceptance', 'context': host.context, 'mode': 'single',
            'step': {'module': args.module, 'access': 'write'}, 'upstream': [], 'checkpoint': host.checkpoint}
        result = host.dispatch(request)
        write(out / 'dispatch.json', result)
        if result['status'] != 'PASS':
            raise ValueError('Generated stage failed measured geometry checks')
    after = {name: capture_object(bpy.data.objects[name]) for name in protected}
    assert before == after and sha(source_path) == source_hash
    write(out / 'protected-after.json', after)
    stages = [name for name in result['evidence'] if name.endswith('.blend')]
    assert len(stages) == 1
    write(out / 'stage.json', {'status': 'EXECUTED_SCOPED_STAGE', 'stage_blend': stages[0], 'source': str(source_path),
        'source_sha256': source_hash, 'source_preserved': True, 'code_sha256': args.approved_sha,
        'actual_specialist_thread': provider['thread_ids'][0], 'commit_sha': commit,
        'runner_sha256': sha(__file__), 'owned_objects': value['owned_objects']})
    print('FREEFORM_STAGE_COMPLETE', str(out))


def execute(args):
    approved_code(args.generation / 'script.py', args.approved_sha)
    provider = json.loads((args.generation / 'provider-receipt.json').read_text(encoding='utf-8'))
    check_source_binding(args.source, provider.get('source_sha256'))
    if args.inside:
        return inside(args)
    if args.output.exists() or args.output.with_suffix('.log').exists():
        raise FileExistsError('Use a new stage directory and log; preserve prior attempts')
    command = [str(args.blender), '--background', '--factory-startup', '--threads', '2']
    if args.source:
        command.append(str(args.source.resolve()))
    command.extend(['--python-exit-code', '1', '--python', str(Path(__file__).resolve()), '--', 'execute',
        '--inside', '--generation', str(args.generation.resolve()), '--output', str(args.output.resolve()),
        '--approved-sha', args.approved_sha, '--asset-id', args.asset_id, '--module', args.module])
    if args.source:
        command.extend(['--source', str(args.source.resolve())])
    args.output.parent.mkdir(parents=True, exist_ok=True)
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
    run.add_argument('--approved-sha', required=True)
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
