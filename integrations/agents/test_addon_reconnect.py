"""Opt-in installed-addon JSON/TCP reconnect test in an owned hidden GUI Blender.

Does not attach to the user's Blender or exercise a full MCP/JSON-RPC client.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import traceback
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_native_recovery import digest, read, write


def child(args):
    import bpy
    from blender_native_host import BlenderNativeHost
    from scene_baseline_snapshot import capture_object

    assert not bpy.app.background, 'The real addon requires the normal GUI event loop'
    spec = importlib.util.spec_from_file_location('reconnect_installed_addon', args.addon)
    addon = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = addon
    spec.loader.exec_module(addon)
    os.environ[addon.ADDON_UPDATE_CHECK_ENV] = '1'
    addon.register()
    bpy.context.scene.blendermcp_auto_start_server = False
    bpy.context.scene.blendermcp_port = args.port
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.mesh.primitive_cube_add(location=(3, 2, 1))
    sentinel = bpy.context.object
    sentinel.name = 'ReconnectProtectedSentinel'
    baseline = capture_object(sentinel)['fingerprint_sha256']
    host = BlenderNativeHost(args.output / 'native-host', asset_id='addon-reconnect-test',
        owned_objects=['FutureOwnedAsset'], protected_objects=[sentinel.name],
        commit_sha=args.commit, actor_id='isolated-addon-reconnect-test', callbacks={})
    host.__enter__()
    servers = []

    def start():
        server = addon.BlenderMCPServer(host='127.0.0.1', port=args.port)
        servers.append(server)
        bpy.types.blendermcp_server = server
        server.start()
        assert server.running, 'Actual addon server failed to start'
        return server

    server = start()

    def state():
        assert capture_object(sentinel)['fingerprint_sha256'] == baseline
        return {'pid': os.getpid(), 'blender_version': bpy.app.version_string,
            'addon_version': list(addon.bl_info['version']), 'protocol_version': addon.ADDON_PROTOCOL_VERSION,
            'port': args.port, 'server_running': server.running, 'server_instance': id(server),
            'native_probe': host.probe(host.context), 'sentinel_fingerprint': baseline,
            'auto_start_disabled': not bpy.context.scene.blendermcp_auto_start_server}

    write(args.output / 'ready.json', state())
    last = None

    def control():
        nonlocal server, last
        path = args.output / 'control.json'
        if not path.exists():
            return 0.1
        command = read(path)
        if command['id'] == last:
            return 0.1
        last = command['id']
        try:
            action = command['action']
            if action == 'stop':
                server.stop()
            elif action == 'start':
                assert not server.running
                server = start()
            elif action == 'finish':
                result = state()
                server.stop()
                host.__exit__(None, None, None)
                addon.unregister()
                write(args.output / ('control-' + last + '.json'), result)
                bpy.ops.wm.quit_blender()
                return None
            elif action != 'probe':
                raise ValueError('Unknown control action')
            write(args.output / ('control-' + last + '.json'), state())
        except Exception:
            write(args.output / ('control-' + last + '.json'), {'error': traceback.format_exc()})
        return 0.1

    bpy.app.timers.register(control, first_interval=0.1)


def campaign(args):
    root = args.output
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError('Evidence directory must be empty; preserve prior runs')
    repo = Path(__file__).resolve().parents[2]
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=repo, text=True).strip())
    with socket.socket() as reservation:
        reservation.bind(('127.0.0.1', 0))
        port = reservation.getsockname()[1]
    report = {'status': 'FAIL', 'protocol': 'installed addon JSON over TCP',
        'commit_sha': commit, 'commit_sha_role': 'base revision', 'working_tree_dirty': dirty,
        'tested_source_sha256': {'addon': digest(args.addon), 'campaign': digest(Path(__file__)),
            'native_host': digest(Path(__file__).with_name('blender_native_host.py'))},
        'checks': {}, 'limits': ['No full MCP/JSON-RPC client or agent framework was exercised.',
            'Native host identity is process-scoped; addon transport restarts do not invalidate it.',
            'Selected-property sentinel fingerprints do not cover every Blender property.']}
    transcript = []
    child_process = None
    connections = []
    log = (root / 'blender.log').open('w', encoding='utf-8')

    def wait_json(path):
        deadline = time.monotonic() + args.timeout
        while not path.exists():
            if child_process.poll() is not None:
                raise RuntimeError('Owned Blender exited; see blender.log')
            if time.monotonic() >= deadline:
                raise TimeoutError('Timed out waiting for ' + path.name)
            time.sleep(0.1)
        result = read(path)
        if 'error' in result:
            raise RuntimeError(result['error'])
        return result

    def control(action):
        command = {'id': str(uuid.uuid4()), 'action': action}
        write(root / 'control.json', command)
        return wait_json(root / ('control-' + command['id'] + '.json'))

    def connect():
        connection = socket.create_connection(('127.0.0.1', port), timeout=10)
        connections.append(connection)
        return connection

    def request(connection, command_type, params=None):
        command = {'type': command_type, 'params': params or {}}
        item = {'connection': connections.index(connection) + 1, 'request': command}
        transcript.append(item)
        write(root / 'requests.json', transcript)
        connection.sendall(json.dumps(command).encode('utf-8'))
        buffer = b''
        while len(buffer) < 2_000_000:
            chunk = connection.recv(8192)
            if not chunk:
                raise ConnectionError('Addon closed connection before JSON response')
            buffer += chunk
            try:
                response = json.loads(buffer.decode('utf-8'))
                break
            except (ValueError, UnicodeDecodeError):
                continue
        else:
            raise ValueError('Oversized addon response')
        item['response'] = response
        write(root / 'requests.json', transcript)
        assert response['status'] == 'success', response
        return response['result']

    try:
        startup = None
        if os.name == 'nt':
            startup = subprocess.STARTUPINFO()
            startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startup.wShowWindow = 0
        command = [str(args.blender), '--factory-startup', '--python-exit-code', '1',
            '--python', str(Path(__file__).resolve()), '--', '--child', '--addon', str(args.addon),
            '--output', str(root), '--port', str(port), '--commit', commit]
        runtime_temp = root / 'runtime-temp'
        runtime_temp.mkdir()
        environment = dict(os.environ, TEMP=str(runtime_temp), TMP=str(runtime_temp))
        child_process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
            startupinfo=startup, env=environment)
        ready = wait_json(root / 'ready.json')
        assert ready['pid'] == child_process.pid
        report.update({'owned_child_pid': child_process.pid, 'port': port,
            'blender_version': ready['blender_version'], 'addon_version': ready['addon_version'],
            'addon_protocol_version': ready['protocol_version']})
        first = connect()
        assert request(first, 'ping')['pong']
        report['addon_handshake'] = request(first, 'get_addon_info')
        scene_before = request(first, 'get_scene_info')
        first.shutdown(socket.SHUT_RDWR)
        first.close()
        second = connect()
        assert request(second, 'ping')['pong']
        assert request(second, 'get_scene_info') == scene_before
        request(second, 'get_object_info', {'name': 'ReconnectProtectedSentinel'})
        reconnected = control('probe')
        stopped = control('stop')
        assert not stopped['server_running']
        try:
            assert second.recv(1) == b'', 'Stopped server left live connection'
        except ConnectionResetError:
            pass
        second.close()
        restarted = control('start')
        assert restarted['server_instance'] != ready['server_instance']
        third = connect()
        assert request(third, 'ping')['pong']
        assert request(third, 'get_scene_info') == scene_before
        third.close()
        final = control('finish')
        assert child_process.wait(timeout=20) == 0
        assert ready['sentinel_fingerprint'] == final['sentinel_fingerprint']
        sessions = [value['native_probe']['session_id'] for value in (ready, reconnected, restarted, final)]
        report['native_session_ids'] = sessions
        report['checks'] = {'ping_and_data_requests': True, 'client_close_reconnect': True,
            'owned_server_stop_closes_connection': True, 'owned_server_restart_reconnect': True,
            'protected_sentinel_preserved': True, 'native_probe_still_valid': True,
            'native_identity_changes_on_addon_restart': len(set(sessions)) > 1,
            'default_port_autostart_disabled': ready['auto_start_disabled']}
        report['status'] = 'PASS_WITH_PROCESS_SCOPED_IDENTITY_LIMIT'
    except Exception:
        report['error'] = traceback.format_exc()
        raise
    finally:
        for connection in connections:
            connection.close()
        if child_process and child_process.poll() is None:
            child_process.kill()
            child_process.wait()
            report['owned_child_force_terminated_after_failure'] = True
        log.close()
        write(root / 'report.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--blender', type=Path)
    parser.add_argument('--addon', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=90)
    parser.add_argument('--child', action='store_true')
    parser.add_argument('--port', type=int)
    parser.add_argument('--commit')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    args.output = args.output.resolve()
    args.addon = args.addon.resolve()
    if args.child:
        child(args)
    else:
        if not args.blender or not args.blender.is_file() or not args.addon.is_file() or args.timeout <= 0:
            parser.error('Existing --blender and --addon files and positive --timeout required')
        campaign(args)
