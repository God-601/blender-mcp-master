import importlib.util
from pathlib import Path
import tempfile
import unittest

try:
    import bpy
except ImportError:
    bpy = None


@unittest.skipUnless(bpy, 'Requires actual Blender bpy')
class GodotAnimationFixtureTests(unittest.TestCase):
    def test_export_contains_actual_weighted_animation_and_refuses_overwrite(self):
        path = Path(__file__).resolve().parents[1] / 'integrations/godot/blender_animation_fixture.py'
        self.assertTrue(path.is_file(), 'Animated export fixture is missing')
        spec = importlib.util.spec_from_file_location('animation_fixture', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'animated.glb'
            report = module.generate(target)
            self.assertEqual(report['bones'], 2)
            self.assertGreater(report['maximum_vertex_displacement'], .1)
            self.assertTrue(report['all_weight_sums_one'])
            self.assertGreater(target.stat().st_size, 100)
            with self.assertRaises(FileExistsError):
                module.generate(target)
