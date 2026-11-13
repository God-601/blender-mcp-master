"""Native bpy host for inspected callbacks, checkpoints and one scene writer.

Import inside Blender, then use as a context manager around orchestrator.run.
Callbacks are trusted, previously inspected code supplied by the agent client;
this is accidental-damage detection, not a Python security sandbox.
"""
import copy
import errno
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import uuid

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from scene_baseline_snapshot import PROTECTION_LIMITS, capture_object, node_tree_signature
from specialist_orchestrator import artifact, validate_context, write_receipt

SESSION_ID = str(uuid.uuid4())


def acquire_writer(path):
    lease = os.fdopen(os.open(str(path), os.O_RDWR | os.O_CREAT, 0o600), 'r+b')
    try:
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(lease.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as error:
        lease.close()
        if error.errno in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
            raise FileExistsError(errno.EEXIST, 'Scene already has a writer', str(path)) from error
        raise
    return lease


def material_dependencies(material):
    found = set()
    def visit(tree):
        if tree is None or tree.as_pointer() in found:
            return
        found.add(tree.as_pointer())
        for node in tree.nodes:
            if getattr(node, 'image', None):
                found.add(node.image.as_pointer())
            visit(getattr(node, 'node_tree', None))
    if material:
        found.add(material.as_pointer())
        visit(material.node_tree)
    return found


def save_recovery_checkpoint(path):
    dependencies = sorted(set(bpy.utils.blend_paths(absolute=True, packed=False)))
    missing = [name for name in dependencies if not Path(name).is_file()]
    if missing:
        raise ValueError('Checkpoint has missing or unsupported external dependencies: ' + ', '.join(missing))
    if not dependencies:
        if bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True) != {'FINISHED'}:
            raise ValueError('Could not save recovery checkpoint')
        return 'NO_EXTERNAL_PATHS_REPORTED'

    # Work in a child process so packing cannot change live images, preferences or paths.
    worker = Path(__file__).with_name('checkpoint_pack.py').resolve()
    with tempfile.TemporaryDirectory(prefix='.checkpoint-', dir=path.parent) as folder:
        staged = Path(folder) / 'source.blend'
        packed = Path(folder) / 'packed.blend'
        if bpy.ops.wm.save_as_mainfile(filepath=str(staged), copy=True, relative_remap=True) != {'FINISHED'}:
            raise ValueError('Could not save checkpoint copy for packing')
        if bpy.app.binary_path:
            command = [bpy.app.binary_path, '--background', '--factory-startup', '--disable-autoexec',
                       '--threads', '1', '--python-exit-code', '1', '--python', str(worker)]
        else:
            command = [sys.executable, str(worker)]
        try:
            process = subprocess.run([*command, '--', str(staged), str(packed)],
                                     capture_output=True, text=True, timeout=60, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValueError('Checkpoint dependency packing could not run: ' + str(error)) from error
        if (process.returncode or not packed.is_file()
                or 'PACKED_CHECKPOINT_VERIFIED' not in process.stdout.splitlines()):
            detail = (process.stderr or process.stdout).strip()[-2000:]
            raise ValueError('Checkpoint dependencies could not be packed and verified: ' + detail)
        # Validate the same limits as the orchestrator before promoting the staged file.
        artifact(Path(folder), packed.name)
        os.replace(packed, path)
    return 'PACKED_AND_REOPENED'


class BlenderNativeHost:
    def __init__(self, root, *, asset_id, owned_objects, protected_objects,
                 commit_sha, actor_id, callbacks, reviewer=None):
        self.root = Path(root).resolve()
        self.scene = bpy.context.scene
        self.scene_pointer = self.scene.as_pointer()
        self.actor_id = actor_id
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError('Actual calling agent identity required')
        if not isinstance(callbacks, dict) or any(not callable(v) for v in callbacks.values()):
            raise ValueError('Inspected callable specialist callbacks required')
        self.callbacks, self.reviewer = callbacks, reviewer
        self.context = {'asset_id': asset_id, 'scene_id': str(self.scene_pointer),
                        'owned_objects': list(owned_objects), 'protected_objects': list(protected_objects),
                        'commit_sha': commit_sha, 'checkpoint_ref': 'checkpoint-' + str(uuid.uuid4()) + '.blend'}
        validate_context(self.context)
        source = os.path.normcase(str(Path(bpy.data.filepath).resolve())) if bpy.data.filepath else None
        self.source_path = source
        scope = 'source:' + source if source else 'unsaved:%s:%s:%s' % (self.root, SESSION_ID, self.scene_pointer)
        key = hashlib.sha256(scope.encode('utf-8')).hexdigest()
        self.lease_path = Path(tempfile.gettempdir()) / ('blender-mcp-writer-' + key + '.lock')
        self.lease = None
        self.baseline = None
        self.checkpoint = None
        self.checkpoint_dependencies = None
        self.global_state = None

    def _scope(self):
        actual = set(bpy.data.objects.keys())
        owned = set(self.context['owned_objects'])
        protected = set(self.context['protected_objects'])
        if actual - owned != protected:
            raise ValueError('Every existing unowned object must be protected; scope changed')
        if any(name not in actual for name in protected):
            raise ValueError('Protected object missing')
        for name in actual & owned:
            obj = bpy.data.objects[name]
            if obj.data and obj.data.users > 1:
                raise ValueError('Owned object has shared data: ' + name)
            for slot in obj.material_slots:
                if slot.material and any(other.name not in owned and any(s.material == slot.material for s in other.material_slots) for other in bpy.data.objects):
                    raise ValueError('Owned material is shared outside ownership: ' + name)
            deps = set().union(*(material_dependencies(slot.material) for slot in obj.material_slots))
            for other in bpy.data.objects:
                if other.name not in owned:
                    for slot in other.material_slots:
                        if deps & material_dependencies(slot.material):
                            raise ValueError('Owned shader dependencies are shared outside ownership: ' + name)

    def _globals(self):
        scene = bpy.context.scene
        return {'scene': scene.as_pointer(), 'source': bpy.data.filepath,
                'engine': scene.render.engine, 'units': scene.unit_settings.scale_length,
                'camera': scene.camera.name if scene.camera else None,
                'world': ({'name': scene.world.name, 'color': list(scene.world.color),
                           'use_nodes': scene.world.use_nodes,
                           'nodes': node_tree_signature(scene.world.node_tree)} if scene.world else None)}

    def _fingerprints(self, names):
        return {name: capture_object(bpy.data.objects[name])['fingerprint_sha256'] for name in names}

    def __enter__(self):
        if self.lease is not None:
            raise ValueError('Host already owns a writer lease')
        source = os.path.normcase(str(Path(bpy.data.filepath).resolve())) if bpy.data.filepath else None
        if bpy.context.scene.as_pointer() != self.scene_pointer or source != self.source_path:
            raise ValueError('Scene or source changed before acquiring writer lease')
        self.root.mkdir(parents=True, exist_ok=True)
        self._scope()
        self.lease = acquire_writer(self.lease_path)
        try:
            self.lease.truncate(0)
            self.lease.write(json.dumps({'pid': os.getpid(), 'scene': self.scene_pointer, 'session_id': SESSION_ID}).encode('utf-8'))
            self.lease.flush()
            self.baseline = self._fingerprints(self.context['protected_objects'])
            self.global_state = self._globals()
            path = self.root / self.context['checkpoint_ref']
            if path.exists():
                raise ValueError('Checkpoint already exists')
            self.checkpoint_dependencies = save_recovery_checkpoint(path)
            self.checkpoint = artifact(self.root, path.name)
            self.probe(self.context)
            return self
        except Exception:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *unused):
        if self.lease is not None:
            self.lease.close()
            self.lease = None
            # Keep the inode: unlinking would let another opener bypass a current lock.

    def probe(self, context):
        if self.lease is None or context != self.context:
            raise ValueError('Active writer lease and exact host context required')
        if self._globals() != self.global_state:
            raise ValueError('Scene identity/source/global settings changed')
        self._scope()
        fingerprints = self._fingerprints(self.context['protected_objects'])
        if fingerprints != self.baseline:
            raise ValueError('Protected object properties changed')
        if artifact(self.root, self.context['checkpoint_ref']) != self.checkpoint:
            raise ValueError('Checkpoint bytes changed')
        modules = list(self.callbacks)
        if self.reviewer is not None and 'validation' not in modules:
            modules.append('validation')
        return {'scene_id': self.context['scene_id'], 'session_id': SESSION_ID,
                'protection_scope': 'selected_object_rna_geometry_and_world_properties',
                'limits': [*PROTECTION_LIMITS, 'The host checks selected globals, including the world, in addition to object fingerprints.',
                           'Trusted synchronous callbacks must bound work and terminate any descendants they launch.'],
                'checkpoint_dependencies': self.checkpoint_dependencies,
                'checkpoint_ref': self.context['checkpoint_ref'], 'protected': fingerprints,
                'modules': modules, 'write': True, 'delegation': self.reviewer is not None}

    def dispatch(self, request):
        self.probe(request['context'])
        step = request['step']
        request = copy.deepcopy(request)
        read_before = self._fingerprints(list(bpy.data.objects.keys())) if step['access'] == 'read' else None
        delegated_review = step['access'] == 'read' and request['mode'] == 'delegated'
        if delegated_review:
            if self.reviewer is None:
                raise ValueError('No actual independent reviewer configured')
            result = self.reviewer(request)
        else:
            callback = self.callbacks.get(step['module'])
            if callback is None:
                raise ValueError('No inspected callback for ' + step['module'])
            result = callback(request)
        self.probe(self.context)
        if read_before is not None and read_before != self._fingerprints(list(bpy.data.objects.keys())):
            raise ValueError('Read-only specialist changed scene objects')
        if not delegated_review:
            if not isinstance(result, dict) or result.get('status') not in ('PASS', 'ISSUE', 'NOT VERIFIED'):
                raise ValueError('Callback must return explicit measured status and evidence')
            result = copy.deepcopy(result)
            result.update({'request_id': request['request_id'], 'agent_id': self.actor_id,
                           'run_id': request['request_id']})
            if step['access'] == 'write' and result['status'] == 'PASS':
                name = 'stage-' + request['request_id'] + '.blend'
                path = self.root / name
                if path.exists():
                    raise ValueError('Stage file already exists')
                try:
                    if bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True) != {'FINISHED'}:
                        raise ValueError('Could not save production stage')
                    self.probe(self.context)
                except Exception:
                    path.unlink(missing_ok=True)
                    raise
                result['evidence'] = list(result.get('evidence', [])) + [name]
            result['receipt'] = write_receipt(self.root, request, result)
        return result
