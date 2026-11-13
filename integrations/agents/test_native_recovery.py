"""Opt-in real Blender kill/restart exercise; never attaches to a running UI.

python integrations/agents/test_native_recovery.py --blender /path/to/blender --output /new/evidence/dir
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2), encoding='utf-8')
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blender_phase(args):
    import bpy
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from blender_native_host import BlenderNativeHost
    from scene_baseline_snapshot import capture_object

    root = args.output

    def snapshot():
        return {name: {'fingerprint': capture_object(bpy.data.objects[name])['fingerprint_sha256'],
                       'location': list(bpy.data.objects[name].location)}
                for name in ('ProtectedSentinel', 'OwnedAsset')}

    def host(directory):
        return BlenderNativeHost(root / directory, asset_id='isolated-recovery-fixture',
            owned_objects=['OwnedAsset'], protected_objects=['ProtectedSentinel'],
            commit_sha=args.commit, actor_id='native-recovery-test', callbacks={})

    if args.phase == 'prepare':
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global=False)
        for name, x in [('ProtectedSentinel', 3), ('OwnedAsset', 0)]:
            bpy.ops.mesh.primitive_cube_add(location=(x, 2, 1))
            bpy.context.object.name = name
        bpy.ops.wm.save_as_mainfile(filepath=str(root / 'source.blend'))
        before = snapshot()
        primary = host('primary')
        primary.__enter__()
        contender = host('same-process-contender')
        try:
            contender.__enter__()
        except FileExistsError:
            rejected = True
        else:
            contender.__exit__(None, None, None)
            raise AssertionError('Same-process second writer was admitted')
        bpy.data.objects['OwnedAsset'].location.x = 17
        primary.probe(primary.context)
        after = snapshot()
        assert after['ProtectedSentinel'] == before['ProtectedSentinel']
        assert after['OwnedAsset'] != before['OwnedAsset']
        write(root / 'ready.json', {'pid': os.getpid(), 'version': bpy.app.version_string,
            'before': before, 'unsaved': after, 'checkpoint': str(root / 'primary' / primary.context['checkpoint_ref']),
            'checkpoint_sha256': primary.checkpoint['sha256'], 'source_sha256': digest(root / 'source.blend'),
            'lease': str(primary.lease_path), 'session_id': primary.probe(primary.context)['session_id'],
            'same_process_writer_rejected': rejected})
        # Parent deliberately terminates only this Popen child, bypassing __exit__.
        while True:
            time.sleep(0.1)
    elif args.phase == 'contender':
        contender = host('cross-process-contender')
        try:
            with contender:
                raise AssertionError('Separate-process writer was admitted')
        except FileExistsError:
            write(root / 'contender.json', {'pid': os.getpid(), 'admitted': False,
                'source': bpy.data.filepath, 'lease': str(contender.lease_path)})
    elif args.phase == 'reacquire':
        ready = read(root / 'ready.json')
        assert snapshot() == ready['before']
        with host('same-source-after-crash') as restarted:
            assert str(restarted.lease_path) == ready['lease']
            write(root / 'reacquired.json', {'pid': os.getpid(),
                'source': bpy.data.filepath, 'lease': str(restarted.lease_path),
                'session_id': restarted.probe(restarted.context)['session_id']})
    elif args.phase == 'recover':
        ready = read(root / 'ready.json')
        actual = snapshot()
        assert actual == ready['before'], (actual, ready['before'])
        assert actual['OwnedAsset'] != ready['unsaved']['OwnedAsset']
        with host('restarted') as restarted:
            probe = restarted.probe(restarted.context)
            assert probe['session_id'] != ready['session_id']
            write(root / 'recovered.json', {'pid': os.getpid(), 'actual': actual,
                'opened_checkpoint': bpy.data.filepath,
                'new_lease': str(restarted.lease_path), 'session_id': probe['session_id'],
                'persistent_lock_file_exists': Path(ready['lease']).exists()})


def campaign(args):
    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError('Evidence directory must be empty; preserve previous runs')
    args.commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'],
        cwd=Path(__file__).resolve().parents[2], text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'],
        cwd=Path(__file__).resolve().parents[2], text=True).strip())
    report = {'status': 'FAIL', 'commit_sha': args.commit, 'commit_sha_role': 'base revision',
        'working_tree_dirty': dirty, 'tested_source_sha256': {
            'native_host': digest(Path(__file__).with_name('blender_native_host.py')),
            'campaign': digest(Path(__file__))}, 'checks': {}, 'limits': [
        'Process restart from an explicit saved checkpoint; no addon, socket, or MCP reconnect tested.',
        'Advisory OS locks coordinate cooperating hosts on this machine; external tools can ignore the lock.',
        'Lock identity uses the normalized saved-source path or the unsaved scene within its Blender process. Different hard links are separate.',
        'Selected object fingerprints and source/checkpoint hashes do not certify every Blender property.']}
    child = None
    logs = []

    def launch(phase, scene=None):
        command = [str(args.blender), '--background', '--factory-startup']
        if scene:
            command.append(str(scene))
        command += ['--python-exit-code', '1', '--python', str(Path(__file__).resolve()), '--',
                    '--phase', phase, '--output', str(root), '--commit', args.commit]
        log = (root / (phase + '.log')).open('w', encoding='utf-8')
        logs.append(log)
        return subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    try:
        child = launch('prepare')
        deadline = time.monotonic() + args.timeout
        while not (root / 'ready.json').exists():
            if child.poll() is not None:
                raise RuntimeError('Preparation exited: see prepare.log')
            if time.monotonic() >= deadline:
                raise TimeoutError('Preparation timeout')
            time.sleep(0.1)
        ready = read(root / 'ready.json')
        assert ready['pid'] == child.pid
        report['blender_version'] = ready['version']
        report['checks']['same_process_second_writer_rejected'] = ready['same_process_writer_rejected']
        contender = launch('contender', root / 'source.blend')
        try:
            assert contender.wait(timeout=args.timeout) == 0, 'See contender.log'
        finally:
            if contender.poll() is None:
                contender.kill()
                contender.wait()
        cross = read(root / 'contender.json')
        report['checks']['cross_process_second_writer_rejected'] = not cross['admitted']
        assert cross['pid'] != ready['pid'] and cross['lease'] == ready['lease']
        assert not cross['admitted']
        assert Path(cross['source']).resolve() == root / 'source.blend'
        assert child.poll() is None, 'Primary writer must still be alive during contention'
        child.kill()
        report['terminated_child_pid'] = child.pid
        report['terminated_child_exit_code'] = child.wait(timeout=15)
        lease = Path(ready['lease'])
        assert lease.exists() and read(lease)['pid'] == child.pid
        write(root / 'lease-metadata-after-kill.json', read(lease))
        report['checks']['persistent_lock_file_survives_abrupt_kill'] = True
        assert digest(root / 'source.blend') == ready['source_sha256']
        assert digest(Path(ready['checkpoint'])) == ready['checkpoint_sha256']
        reacquire = launch('reacquire', root / 'source.blend')
        try:
            assert reacquire.wait(timeout=args.timeout) == 0, 'See reacquire.log'
        finally:
            if reacquire.poll() is None:
                reacquire.kill()
                reacquire.wait()
        reacquired = read(root / 'reacquired.json')
        assert reacquired['lease'] == ready['lease'] and reacquired['pid'] != ready['pid']
        restart = launch('recover', ready['checkpoint'])
        try:
            assert restart.wait(timeout=args.timeout) == 0, 'See recover.log'
        finally:
            if restart.poll() is None:
                restart.kill()
                restart.wait()
        recovered = read(root / 'recovered.json')
        assert recovered['actual'] == ready['before']
        assert recovered['persistent_lock_file_exists']
        assert digest(root / 'source.blend') == ready['source_sha256']
        report['checks'].update({'checkpoint_restores_owned_state': True,
            'protected_sentinel_preserved': True, 'source_file_unchanged': True,
            'same_source_lock_reacquired_after_crash': True,
            'new_process_can_acquire_lease': True})
        report['status'] = 'PASS'
        report['writer_exclusion_status'] = 'PASS_ACROSS_PROCESSES'
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        if child and child.poll() is None:
            child.kill()
            child.wait()
        for log in logs:
            log.close()
        write(root / 'report.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=90)
    parser.add_argument('--phase', choices=['prepare', 'contender', 'reacquire', 'recover'])
    parser.add_argument('--commit')
    arguments = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    arguments.output = arguments.output.resolve()
    if arguments.phase:
        blender_phase(arguments)
    else:
        if not arguments.blender or not arguments.blender.is_file() or arguments.timeout <= 0:
            parser.error('--blender must be an existing executable and --timeout must be positive')
        campaign(arguments)
