"""Native bpy host for inspected callbacks, checkpoints and one scene writer.

Import inside Blender, then use as a context manager around orchestrator.run.
Callbacks are trusted, previously inspected code supplied by the agent client;
this is accidental-damage detection, not a Python security sandbox.
"""
import copy
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from scene_baseline_snapshot import capture_object, node_tree_signature
from specialist_orchestrator import artifact, validate_context, write_receipt

SESSION_ID = str(uuid.uuid4())


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
        self.lease_path = Path(tempfile.gettempdir()) / ('blender-mcp-writer-%s-%s.lock' % (os.getpid(), self.scene_pointer))
        self.lease = None
        self.baseline = None
        self.checkpoint = None
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
        self.root.mkdir(parents=True, exist_ok=True)
        self._scope()
        self.lease = self.lease_path.open('x', encoding='utf-8')
        try:
            self.lease.write(json.dumps({'pid': os.getpid(), 'scene': self.scene_pointer, 'session_id': SESSION_ID}))
            self.lease.flush()
            self.baseline = self._fingerprints(self.context['protected_objects'])
            self.global_state = self._globals()
            path = self.root / self.context['checkpoint_ref']
            if path.exists():
                raise ValueError('Checkpoint already exists')
            bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
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
            self.lease_path.unlink()

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
                'limits': ['Image pixels, arbitrary collection/custom properties and external files are not fully fingerprinted.',
                           'Trusted synchronous callbacks must bound work and terminate any descendants they launch.'],
                'checkpoint_ref': self.context['checkpoint_ref'], 'protected': fingerprints,
                'modules': modules, 'write': True, 'delegation': self.reviewer is not None}

    def dispatch(self, request):
        self.probe(request['context'])
        step = request['step']
        request = copy.deepcopy(request)
        read_before = self._fingerprints(list(bpy.data.objects.keys())) if step['access'] == 'read' else None
        if step['access'] == 'read' and request['mode'] == 'delegated':
            if self.reviewer is None:
                raise ValueError('No actual independent reviewer configured')
            result = self.reviewer(request)
        else:
            callback = self.callbacks.get(step['module'])
            if callback is None:
                raise ValueError('No inspected callback for ' + step['module'])
            result = callback(request)
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
                bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
                result['evidence'] = list(result.get('evidence', [])) + [name]
            result['receipt'] = write_receipt(self.root, request, result)
        self.probe(self.context)
        if read_before is not None and read_before != self._fingerprints(list(bpy.data.objects.keys())):
            raise ValueError('Read-only specialist changed scene objects')
        return result
