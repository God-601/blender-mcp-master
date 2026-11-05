"""Input guard regression tests for Blender export; static tests run without bpy."""
import ast
import os
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_asset.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


class ExportGuardStaticTests(unittest.TestCase):
    def test_guards_parse_and_precede_filesystem_or_scene_mutation(self):
        source = SCRIPT.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('len(set(OBJECTS)) != len(OBJECTS)', source)
        self.assertIn('expected_extension = {"FBX": ".fbx"', source)
        self.assertLess(source.index('len(set(OBJECTS)) != len(OBJECTS)'),
                        source.index('os.makedirs('))
        self.assertLess(source.index('Export PATH must end in'),
                        source.index('os.makedirs('))


@unittest.skipIf(bpy is None, "bpy unavailable")
class ExportGuardRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "Crate"

    def test_duplicate_names_refused_without_mutating_scene(self):
        from test_blender_runtime import run_script
        before = set(bpy.data.objects.keys())
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "crate.glb")
            _, error = run_script("export_asset.py", OBJECTS=["Crate", "Crate"],
                                  PATH=path, FORMAT="GLB")
            self.assertIsInstance(error, ValueError)
            self.assertEqual(set(bpy.data.objects.keys()), before)
            self.assertFalse(Path(path).exists())
            self.assertNotIn("_EXPORT_TMP", bpy.data.collections)

    def test_wrong_extension_refused_before_creating_directory(self):
        from test_blender_runtime import run_script
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "new-folder" / "crate.fbx"
            _, error = run_script("export_asset.py", OBJECTS=["Crate"],
                                  PATH=str(path), FORMAT="GLB")
            self.assertIsInstance(error, ValueError)
            self.assertFalse(path.parent.exists())
            self.assertEqual(bpy.data.objects["Crate"].name, "Crate")


if __name__ == "__main__":
    unittest.main()
