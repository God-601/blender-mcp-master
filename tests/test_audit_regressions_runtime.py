"""Regression tests for audit findings that escaped earlier mutation checks."""
import os
import tempfile
import unittest
from pathlib import Path

try:
    import bpy
    import bmesh
    from mathutils import Vector
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

from test_blender_runtime import run_script
from test_extended_architecture_runtime import execute_script
from test_geometry_builder_runtime import run_builder


@unittest.skipIf(bpy is None, "bpy (Blender as Python module) unavailable")
class ProfessionalMutationRegressionTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def make_cube(self, name, size=1.0):
        bpy.ops.mesh.primitive_cube_add(size=size)
        obj = bpy.context.object
        obj.name = name
        return obj

    def signed_volume(self, obj, evaluated=False):
        source = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()) if evaluated else obj
        mesh = source.to_mesh() if evaluated else obj.data
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            return bm.calc_volume(signed=True)
        finally:
            bm.free()
            if evaluated:
                source.to_mesh_clear()

    def test_reference_extrusion_winding_normalized_in_both_orders(self):
        for label, profile in (
            ("CCW", [(0, 0), (1, 0), (1, 1), (0, 1)]),
            ("CW", [(0, 1), (1, 1), (1, 0), (0, 0)])):
            with self.subTest(label=label):
                bpy.ops.wm.read_factory_settings(use_empty=True)
                out, err = run_builder([{"name": "Extrusion", "type": "extruded_profile",
                                          "profile": profile, "height": 1.0}])
                self.assertIsNone(err, out)
                self.assertGreater(self.signed_volume(bpy.data.objects["Extrusion"]), 0.95)

    def test_legacy_reports_separate_boundaries_from_nonmanifold(self):
        mesh = bpy.data.meshes.new("CardData")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                         [], [(0, 1, 2, 3)])
        obj = bpy.data.objects.new("Card", mesh)
        bpy.context.scene.collection.objects.link(obj)
        import json
        out, err = execute_script("scripts/inspection_report.py", {"TARGET_NAMES": ["Card"]})
        self.assertIsNone(err, out)
        payload = json.loads(out.split("MCP_INSPECTION_REPORT_BEGIN\n")[1]
                             .split("\nMCP_INSPECTION_REPORT_END")[0])
        self.assertEqual(payload["targets"][0]["boundary_edges"], 4)
        self.assertEqual(payload["targets"][0]["non_manifold_edges"], 0)
        out, err = execute_script("scripts/benchmark_report.py", {"TARGET_NAMES": ["Card"]})
        self.assertIsNone(err, out)
        payload = json.loads(out.split("MCP_BENCHMARK_REPORT_BEGIN\n")[1]
                             .split("\nMCP_BENCHMARK_REPORT_END")[0])
        self.assertEqual(payload["targets"][0]["non_manifold_edges"], 0)
        self.assertEqual(payload["targets"][0]["boundary_edges"], 4)

    def test_inspection_report_does_not_ignore_wire_edges(self):
        mesh = bpy.data.meshes.new("WireData")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0)], [(0, 1)], [])
        obj = bpy.data.objects.new("WireOnly", mesh)
        bpy.context.scene.collection.objects.link(obj)
        import json
        out, err = execute_script("scripts/inspection_report.py", {"TARGET_NAMES": ["WireOnly"]})
        self.assertIsNone(err, out)
        payload = json.loads(out.split("MCP_INSPECTION_REPORT_BEGIN\n")[1]
                             .split("\nMCP_INSPECTION_REPORT_END")[0])
        self.assertEqual(payload["targets"][0]["wire_edges"], 1)
        self.assertEqual(payload["targets"][0]["status"], "ISSUE")

    def test_local_recalculate_normals_changes_duplicate_not_inverted_source(self):
        source = self.make_cube("Reversed")
        bm = bmesh.new()
        try:
            bm.from_mesh(source.data)
            bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
            bm.to_mesh(source.data)
        finally:
            bm.free()
        source.data.update()
        self.assertLess(self.signed_volume(source), 0.0)
        corrections = [{"source": "Reversed", "output": "Corrected",
                        "operations": [{"type": "recalculate_normals"}]}]
        out, err = execute_script("scripts/localized_correction.py", {"CORRECTIONS": corrections})
        self.assertIsNone(err, out)
        self.assertLess(self.signed_volume(source), 0.0)
        self.assertGreater(self.signed_volume(bpy.data.objects["Corrected"]), 0.0)

    def test_optimizer_skips_shared_mesh_in_apply_mode(self):
        original = self.make_cube("A")
        linked = bpy.data.objects.new("B", original.data)
        bpy.context.scene.collection.objects.link(linked)
        before = original.data
        out, err = run_script("optimize_mesh.py", TARGETS=["A"], APPLY=True)
        self.assertIsNone(err, out)
        self.assertIn("shared mesh datablock", out)
        self.assertIs(original.data, before)
        self.assertIs(linked.data, before)

    def test_boolean_difference_actually_removes_mesh_volume(self):
        source = self.make_cube("Source", size=2.0)
        specs = [{"source": "Source", "output": "Cut", "operations": [
            {"type": "boolean_difference", "dimensions": (0.5, 0.5, 0.5),
             "location": (0.5, 0.0, 0.0)}]}]
        out, err = execute_script("scripts/mesh_operations.py", {"TARGETS": specs})
        self.assertIsNone(err, out)
        obj = bpy.data.objects["Cut"]
        self.assertEqual(obj.modifiers[0].operation, "DIFFERENCE")
        self.assertGreater(self.signed_volume(source), self.signed_volume(obj, evaluated=True) + 0.05)

    def test_tree_branches_attach_near_trunk_centerline(self):
        out, err = execute_script("scripts/organic_tree_builder.py")
        self.assertIsNone(err, out)
        for i in range(1, 8):
            branch = bpy.data.objects["MCP_Tree_Branch_%02d" % i]
            zmin = min(float(v.co.z) for v in branch.data.vertices)
            base_center = branch.matrix_world @ Vector((0.0, 0.0, zmin))
            radial_distance = (Vector((base_center.x, base_center.y))).length
            self.assertLess(radial_distance, 0.23, branch.name)
            self.assertGreater(base_center.z, 0.0)

    def test_normal_map_is_noncolor_and_connected_to_principled(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "normal.png")
            image = bpy.data.images.new("NormalSource", width=4, height=4)
            image.filepath_raw = path
            image.file_format = "PNG"
            image.save()
            out, err = run_script("pbr_material.py", NAME="NormalCheck",
                                  TEXTURES={"normal": path})
            self.assertIsNone(err, out)
            mat = bpy.data.materials["NormalCheck"]
            texnodes = [node for node in mat.node_tree.nodes
                        if node.type == "TEX_IMAGE" and node.image]
            self.assertEqual(len(texnodes), 1)
            self.assertEqual(texnodes[0].image.colorspace_settings.name, "Non-Color")
            normals = [node for node in mat.node_tree.nodes if node.type == "NORMAL_MAP"]
            self.assertEqual(len(normals), 1)
            principled = next(node for node in mat.node_tree.nodes if node.type == "BSDF_PRINCIPLED")
            self.assertTrue(any(link.from_node == normals[0] and link.to_node == principled
                                for link in mat.node_tree.links))

    def test_localized_and_mesh_ops_bevels_clamp_extreme_thin_mesh(self):
        self.make_cube("Thin", size=0.004)
        corrections = [{"source": "Thin", "output": "ThinFixed",
                        "operations": [{"type": "bevel_modifier", "width": 0.012}]}]
        out, err = execute_script("scripts/localized_correction.py", {"CORRECTIONS": corrections})
        self.assertIsNone(err, out)
        self.assertLessEqual(bpy.data.objects["ThinFixed"].modifiers[0].width, 0.00080001)
        ops = [{"source": "Thin", "output": "ThinOps", "operations": [
            {"type": "bevel", "width": 0.012}]}]
        out, err = execute_script("scripts/mesh_operations.py", {"TARGETS": ops})
        self.assertIsNone(err, out)
        self.assertLessEqual(bpy.data.objects["ThinOps"].modifiers[0].width, 0.00080001)


if __name__ == "__main__":
    unittest.main()
