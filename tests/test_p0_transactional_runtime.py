"""P0 failure-injection regressions: no user data changes on failures."""
import unittest
import os
import tempfile
from pathlib import Path

try:
    import bpy
    import bmesh
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None
from test_blender_runtime import run_script


@unittest.skipIf(bpy is None, "bpy unavailable")
class P0TransactionalTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name):
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_cleanup_default_source_is_unchanged_and_no_selected_fallback(self):
        obj = self.cube("UserCube")
        before = tuple(tuple(v.co) for v in obj.data.vertices)
        out, err = run_script("cleanup_mesh.py", TARGETS=[])
        self.assertIsNone(err, out)
        self.assertIn("NO TARGETS", out)
        self.assertNotIn("UserCube_Cleaned", bpy.data.objects)
        out, err = run_script("cleanup_mesh.py", TARGETS=["UserCube"])
        self.assertIsNone(err, out)
        self.assertIn("UserCube_Cleaned", bpy.data.objects)
        self.assertEqual(tuple(tuple(v.co) for v in obj.data.vertices), before)
        self.assertIsNot(obj.data, bpy.data.objects["UserCube_Cleaned"].data)

    def test_cleanup_injected_failure_removes_staging_and_preserves_source(self):
        obj = self.cube("SafeSource")
        initial = tuple(tuple(v.co) for v in obj.data.vertices)
        old_data = obj.data
        out, err = run_script("cleanup_mesh.py", TARGETS=["SafeSource"],
                              _source_replacements={
            "        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=MERGE_DISTANCE)":
            '        raise RuntimeError("injected cleanup failure")'
        })
        self.assertIsNone(err, out)
        self.assertIn("injected cleanup failure", out)
        self.assertNotIn("SafeSource_Cleaned", bpy.data.objects)
        self.assertIs(obj.data, old_data)
        self.assertEqual(tuple(tuple(v.co) for v in obj.data.vertices), initial)

    def test_cleanup_invalid_parameter_preflight_changes_nothing(self):
        obj = self.cube("Preserve")
        before = set(bpy.data.meshes.keys())
        out, err = run_script("cleanup_mesh.py", TARGETS=["Preserve"], MERGE_DISTANCE=-1)
        self.assertIsInstance(err, ValueError)
        self.assertEqual(set(bpy.data.meshes.keys()), before)

    def test_cleanup_name_collision_never_overwrites(self):
        obj = self.cube("Box")
        other = self.cube("Box_Cleaned")
        old_data = other.data
        out, err = run_script("cleanup_mesh.py", TARGETS=["Box"])
        self.assertIsNone(err, out)
        self.assertIn("refusing output name collision", out)
        self.assertIs(other.data, old_data)

    def test_origin_default_duplicates_and_keeps_scene_selection(self):
        obj = self.cube("UserBox")
        obj.scale = (2, 3, 4)
        original = obj.data
        out, err = run_script("apply_and_origin.py", TARGETS=["UserBox"])
        self.assertIsNone(err, out)
        self.assertIs(obj.data, original)
        self.assertEqual(tuple(obj.scale), (2, 3, 4))
        self.assertIn("UserBox_Prepared", bpy.data.objects)

    def test_origin_injected_failure_removes_staging(self):
        obj = self.cube("UserBox")
        matrix = obj.matrix_world.copy()
        original = obj.data
        out, err = run_script("apply_and_origin.py", TARGETS=["UserBox"],
                              _source_replacements={
           "    ob.data.transform(bake)":
           '    raise RuntimeError("injected transform failure")'
        })
        self.assertIsNone(err, out)
        self.assertIn("injected transform failure", out)
        self.assertNotIn("UserBox_Prepared", bpy.data.objects)
        self.assertIs(obj.data, original)
        self.assertEqual(obj.matrix_world, matrix)

    def test_origin_inplace_requires_explicit_permission(self):
        obj = self.cube("UserBox")
        out, err = run_script("apply_and_origin.py", TARGETS=["UserBox"], EDIT_IN_PLACE=True)
        self.assertIsNone(err, out)
        self.assertIn("unowned source", out)
        self.assertEqual(len(bpy.data.objects), 1)
        out, err = run_script("apply_and_origin.py", TARGETS=["UserBox"],
                              EDIT_IN_PLACE=True, ALLOW_UNOWNED_EDIT=True)
        self.assertIsNone(err, out)
        self.assertEqual(len(bpy.data.objects), 1)
        self.assertTrue(any(me.use_fake_user and "BeforeOrigin" in me.name for me in bpy.data.meshes))

    def test_origin_wrong_policy_rejected_before_changes(self):
        self.cube("UserBox")
        out, err = run_script("apply_and_origin.py", TARGETS=["UserBox"], ORIGIN="INVENTED")
        self.assertIsInstance(err, ValueError)
        self.assertNotIn("UserBox_Prepared", bpy.data.objects)


if __name__ == "__main__":
    unittest.main()
