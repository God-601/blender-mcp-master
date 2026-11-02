"""Editable face topology audit: no scene mutation, no automatic edge dissolve."""
import ast
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "topology_face_diagnostics.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def run_audit(targets):
    source = SCRIPT.read_text(encoding="utf-8")
    source, replaced = re.subn(
        r"^TARGETS = \[\]",
        lambda _: "TARGETS = " + repr(targets),
        source, flags=re.M, count=1,
    )
    assert replaced == 1
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
    return json.loads(stdout.getvalue().split("MCP_TOPOLOGY_FACE_AUDIT_BEGIN\n", 1)[1]
                      .split("\nMCP_TOPOLOGY_FACE_AUDIT_END", 1)[0])


class StaticFaceAuditTests(unittest.TestCase):
    def test_static_script_is_read_only_opt_in(self):
        s = SCRIPT.read_text(encoding="utf-8")
        ast.parse(s)
        self.assertIn("TARGETS = []", s)
        self.assertIn("NOT VERIFIED", s)
        self.assertNotIn("bmesh.ops.dissolve", s)
        self.assertNotIn("bpy.ops.object.delete", s)
        self.assertNotIn("bpy.data.objects.remove", s)


@unittest.skipIf(bpy is None, "bpy unavailable")
class RuntimeFaceAuditTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def make(self, name, center_z=0, kind="fan"):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        corners = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
        if kind == "fan":
            verts = corners + [(0, 0, center_z)]
            faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        elif kind == "quad":
            verts = corners
            faces = [(0, 1, 2, 3)]
        else:
            verts = corners
            faces = [(0, 1, 2), (0, 2, 3)]
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    def test_x_four_fan_flagged_for_review_and_not_removed(self):
        obj = self.make("XFace")
        original_vertices = [tuple(v.co) for v in obj.data.vertices]
        original_faces = [tuple(p.vertices) for p in obj.data.polygons]
        report = run_audit(["XFace"])
        self.assertEqual(report["overall"], "REVIEW")
        data = report["targets"][0]
        self.assertEqual(data["coplanar_four_triangle_fan_candidates"], 1)
        self.assertEqual(data["base_render_triangles_before_modifiers"], 4)
        self.assertEqual(data["base_triangle_faces"], 4)
        self.assertEqual(len(data["candidate_examples"]), 1)
        self.assertEqual([tuple(v.co) for v in obj.data.vertices], original_vertices)
        self.assertEqual([tuple(p.vertices) for p in obj.data.polygons], original_faces)

    def test_material_boundary_flags_preserve_until_review(self):
        obj = self.make("MaterialFan")
        m1 = bpy.data.materials.new("One")
        m2 = bpy.data.materials.new("Two")
        obj.data.materials.append(m1)
        obj.data.materials.append(m2)
        obj.data.polygons[0].material_index = 1
        report = run_audit(["MaterialFan"])["targets"][0]
        self.assertEqual(report["coplanar_four_triangle_fan_candidates"], 1)
        example = report["candidate_examples"][0]
        self.assertTrue(example["material_boundary"])
        self.assertEqual(example["recommendation"], "PRESERVE_UNTIL_REVIEW")

    def test_uv_split_flags_seam_and_no_auto_dissolve(self):
        obj = self.make("UVFan")
        uv = obj.data.uv_layers.new(name="UVMap")
        for index, loop in enumerate(obj.data.loops):
            uv.data[index].uv = (0.25, 0.25)
        # The same center vertex occupies multiple loops; alter exactly one.
        for poly in obj.data.polygons:
            for loop_index in poly.loop_indices:
                if obj.data.loops[loop_index].vertex_index == 4:
                    uv.data[loop_index].uv = (0.0, 1.0)
                    break
            break
        original = [tuple(v.co) for v in obj.data.vertices]
        report = run_audit(["UVFan"])["targets"][0]
        example = report["candidate_examples"][0]
        self.assertTrue(example["uv_seam_candidate"])
        self.assertEqual(example["recommendation"], "PRESERVE_UNTIL_REVIEW")
        self.assertEqual(original, [tuple(v.co) for v in obj.data.vertices])

    def test_single_quad_not_flagged(self):
        self.make("Quad", kind="quad")
        report = run_audit(["Quad"])["targets"][0]
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["base_quad_faces"], 1)
        self.assertEqual(report["base_render_triangles_before_modifiers"], 2)
        self.assertEqual(report["coplanar_four_triangle_fan_candidates"], 0)

    def test_two_triangle_split_quad_is_not_an_x_fan(self):
        self.make("TwoTri", kind="two")
        report = run_audit(["TwoTri"])["targets"][0]
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["base_render_triangles_before_modifiers"], 2)
        self.assertEqual(report["coplanar_four_triangle_fan_candidates"], 0)

    def test_nonplanar_fan_not_marked_redundant(self):
        self.make("Bent", center_z=0.15)
        report = run_audit(["Bent"])["targets"][0]
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["coplanar_four_triangle_fan_candidates"], 0)

    def test_empty_target_names_never_scan_scene(self):
        self.make("XFace")
        result = run_audit([])
        self.assertEqual(result["overall"], "NOT VERIFIED")
        self.assertEqual(result["targets"], [])

    def test_missing_object_is_not_verified(self):
        self.make("XFace")
        result = run_audit(["Missing"])
        self.assertEqual(result["overall"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
