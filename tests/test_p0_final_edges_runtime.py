"""P0 filesystem/LOD/in-place permission failure injection tests."""
import os
import tempfile
import unittest
from pathlib import Path
try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None
from test_blender_runtime import run_script


@unittest.skipIf(bpy is None, "bpy missing")
class P0FinalEdgesTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name):
        bpy.ops.mesh.primitive_cube_add()
        ob = bpy.context.object
        ob.name = name
        return ob

    def test_bevel_explicit_inplace_refuses_unowned_and_applied_modifiers(self):
        original = self.cube("MySceneObject")
        out, err = run_script("bevel_and_shade.py", TARGETS=["MySceneObject"],
                              EDIT_IN_PLACE=True)
        self.assertIsNone(err, out)
        self.assertIn("requires ALLOW_UNOWNED_INPLACE", out)
        self.assertEqual(len(original.modifiers), 0)
        out, err = run_script("bevel_and_shade.py", TARGETS=["MySceneObject"],
                              EDIT_IN_PLACE=True, ALLOW_UNOWNED_INPLACE=True,
                              APPLY_MODIFIERS=True)
        self.assertIsNone(err, out)
        self.assertIn("in-place modifier application is unsafe", out)
        self.assertEqual(len(original.data.polygons), 6)

    def test_bevel_inplace_fail_injection_restores_source_mesh_and_modifiers(self):
        obj = self.cube("MySceneObject")
        source = obj.data
        out, err = run_script("bevel_and_shade.py", TARGETS=["MySceneObject"],
                              EDIT_IN_PLACE=True, ALLOW_UNOWNED_INPLACE=True,
                              _source_replacements={
             '    smooth_by_angle(ob)': '    raise RuntimeError("injected shading failure")'
        })
        self.assertIsNone(err, out)
        self.assertIn("injected shading failure", out)
        self.assertEqual(len(obj.modifiers), 0)
        self.assertEqual(len(obj.data.polygons), 6)
        self.assertTrue(all(not p.use_smooth for p in obj.data.polygons))

    def test_lods_refuse_animated_mesh_without_creating_copies(self):
        obj = self.cube("Character")
        obj.shape_key_add(name="Basis")
        obj.shape_key_add(name="Blink")
        before = {o.name for o in bpy.data.objects}
        out, err = run_script("make_lods.py", SOURCE="Character")
        self.assertIsInstance(err, ValueError, out)
        self.assertEqual({o.name for o in bpy.data.objects}, before)

    def test_export_obj_material_failure_restores_both_user_files(self):
        obj = self.cube("Crate")
        mat = bpy.data.materials.new("Stone")
        obj.data.materials.append(mat)
        with tempfile.TemporaryDirectory() as folder:
            obj_file = Path(folder) / "existing.obj"
            mtl_file = Path(folder) / "existing.mtl"
            obj_file.write_bytes(b"OLD OBJ")
            mtl_file.write_bytes(b"OLD MTL")
            out, err = run_script(
                "export_asset.py", OBJECTS=["Crate"], FORMAT="OBJ",
                PATH=str(obj_file), OVERWRITE=True,
                _source_replacements={
                    '            os.replace(_src, _dest)':
                    '            if _src == temp_path:\n'
                    '                raise RuntimeError("injected final commit failure")\n'
                    '            os.replace(_src, _dest)'
                }
            )
            self.assertIsInstance(err, RuntimeError, out)
            self.assertEqual(obj_file.read_bytes(), b"OLD OBJ")
            self.assertEqual(mtl_file.read_bytes(), b"OLD MTL")
            self.assertEqual(sorted(p.name for p in Path(folder).iterdir()),
                             ["existing.mtl", "existing.obj"])
            self.assertIn("Crate", bpy.data.objects)
            self.assertNotIn("_EXPORT_TMP", bpy.data.collections)


if __name__ == "__main__":
    unittest.main()
