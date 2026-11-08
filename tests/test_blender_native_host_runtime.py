import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from specialist_orchestrator import run

try:
    import bpy
except ImportError:
    if os.environ.get('REQUIRE_BPY') == '1':
        raise
    bpy = None


@unittest.skipUnless(bpy, 'requires actual bpy')
class NativeHostTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        mesh = bpy.data.meshes.new('KeepMesh')
        self.keep = bpy.data.objects.new('Keep', mesh)
        bpy.context.scene.collection.objects.link(self.keep)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        spec = importlib.util.spec_from_file_location('tested_native_host', ROOT / 'integrations/agents/blender_native_host.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)

    def evidence(self, request, status='PASS'):
        name = request['request_id'] + '.json'
        (self.root / name).write_text(json.dumps({'module': request['step']['module'], 'actual_blender': bpy.app.version_string}), encoding='utf-8')
        return {'status': status, 'evidence': [name], 'errors': [], 'metrics': {}}

    def host(self, callbacks=None):
        def create(request):
            mesh = bpy.data.meshes.new('OwnedMesh')
            mesh.from_pydata([(0,0,0), (1,0,0), (0,1,0)], [], [(0,1,2)])
            obj = bpy.data.objects.new('Owned', mesh)
            bpy.context.scene.collection.objects.link(obj)
            return self.evidence(request)
        callbacks = callbacks or {'modeling': create, 'validation': self.evidence}
        return self.mod.BlenderNativeHost(self.root, asset_id='fixture', owned_objects=['Owned'],
            protected_objects=['Keep'], commit_sha='a' * 40, actor_id='actual-test-coordinator', callbacks=callbacks)

    def test_actual_checkpoint_production_stage_and_reopen(self):
        original_path = bpy.data.filepath
        with self.host() as host:
            result = run({'category': 'hard_surface'}, host.context, self.root, host, dry_run=False)
            self.assertEqual(result['status'], 'REVIEW')
            checkpoint = self.root / host.context['checkpoint_ref']
            self.assertEqual(bpy.data.filepath, original_path)
            self.assertIn('Owned', bpy.data.objects)
            self.assertEqual(self.keep.location.x, 0)
            stage = [e['path'] for e in result['steps'][0]['evidence'] if e['path'].endswith('.blend')][0]
            self.assertTrue((self.root / stage).is_file())
        # Reopening verifies the actual checkpoint across Blender file-format versions.
        bpy.ops.wm.open_mainfile(filepath=str(checkpoint))
        self.assertIn('Keep', bpy.data.objects)
        self.assertNotIn('Owned', bpy.data.objects)

    def test_second_writer_lease_is_rejected(self):
        with self.host():
            with self.assertRaises(FileExistsError):
                with self.host():
                    self.fail('a second writer acquired the same scene')
        self.assertFalse(self.host().lease_path.exists())

    def test_shared_owned_data_is_rejected_before_checkpoint(self):
        obj = bpy.data.objects.new('Owned', self.keep.data)
        bpy.context.scene.collection.objects.link(obj)
        with self.assertRaisesRegex(ValueError, 'shared data'):
            with self.host():
                self.fail('shared data accepted')
        self.assertEqual(list(self.root.glob('*.blend')), [])

    def test_all_unowned_objects_must_be_protected(self):
        extra = bpy.data.objects.new('Unlisted', None)
        bpy.context.scene.collection.objects.link(extra)
        with self.assertRaisesRegex(ValueError, 'Every existing unowned'):
            with self.host():
                self.fail('unlisted object accepted')

    def test_protected_damage_stops_with_real_checkpoint(self):
        def damage(request):
            self.keep.location.x = 9
            return self.evidence(request)
        with self.host({'modeling': damage, 'validation': self.evidence}) as host:
            result = run({'category': 'hard_surface'}, host.context, self.root, host, dry_run=False)
            self.assertEqual(result['status'], 'ISSUE')
            self.assertTrue(result['recovery_required'])
            self.assertTrue((self.root / host.context['checkpoint_ref']).is_file())

    def test_read_stage_cannot_modify_owned_geometry(self):
        host = self.host()
        def mutate(request):
            bpy.data.objects['Owned'].data.vertices[0].co.x = 4
            return self.evidence(request)
        host.callbacks['validation'] = mutate
        with host:
            result = run({'category': 'hard_surface'}, host.context, self.root, host, dry_run=False)
            self.assertEqual(result['status'], 'ISSUE')
            self.assertIn('Read-only specialist', result['errors'][0])

    def test_world_content_change_is_detected(self):
        bpy.context.scene.world = bpy.data.worlds.new('World')
        def damage(request):
            bpy.context.scene.world.color = (0.3, 0.2, 0.1)
            return self.evidence(request)
        with self.host({'modeling': damage, 'validation': self.evidence}) as host:
            result = run({'category': 'hard_surface'}, host.context, self.root, host, dry_run=False)
            self.assertEqual(result['status'], 'ISSUE')

    def test_shared_image_dependency_is_rejected(self):
        mesh = bpy.data.meshes.new('OwnedMesh')
        obj = bpy.data.objects.new('Owned', mesh)
        bpy.context.scene.collection.objects.link(obj)
        image = bpy.data.images.new('SharedImage', width=2, height=2)
        for target in (obj, self.keep):
            material = bpy.data.materials.new(target.name + 'Material')
            material.use_nodes = True
            material.node_tree.nodes.new('ShaderNodeTexImage').image = image
            target.data.materials.append(material)
        with self.assertRaisesRegex(ValueError, 'shader dependencies'):
            with self.host():
                self.fail('shared image accepted')

    def test_protected_modifier_parameter_change_is_detected(self):
        mod = self.keep.modifiers.new('Subdivision', 'SUBSURF')
        def damage(request):
            mod.levels = 3
            return self.evidence(request)
        with self.host({'modeling': damage, 'validation': self.evidence}) as host:
            result = run({'category': 'hard_surface'}, host.context, self.root, host, dry_run=False)
            self.assertEqual(result['status'], 'ISSUE')
