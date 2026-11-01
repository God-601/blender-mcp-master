"""Behavioral checks for professional evaluated-geometry quality gate."""
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

try:
    import bpy
    import bmesh
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_geometry.py"


def run_inspection(names, policies=None, relationships=None):
    source = SCRIPT.read_text(encoding="utf-8")
    for key, value in (("TARGET_NAMES", names),
                       ("POLICIES", policies or {}),
                       ("RELATIONSHIPS", relationships or [])):
        source, count = re.subn(r"^" + key + r"\s*=.*$",
                                lambda _m, k=key, v=value: f"{k} = {v!r}",
                                source, count=1, flags=re.M)
        if count != 1:
            raise AssertionError("Missing configuration " + key)
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
    text = stdout.getvalue()
    payload = text.split("MCP_PROFESSIONAL_INSPECTION_BEGIN\n", 1)[1]
    payload = payload.split("\nMCP_PROFESSIONAL_INSPECTION_END", 1)[0]
    return json.loads(payload)


@unittest.skipIf(bpy is None, "Blender bpy module unavailable")
class ProfessionalGeometryRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name, location=(0, 0, 1), size=2.0):
        bpy.ops.mesh.primitive_cube_add(size=size, location=location)
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_closed_cube_positive_volume_dimensions_ground_and_budget(self):
        obj = self.cube("Solid")
        before = tuple(tuple(v.co) for v in obj.data.vertices)
        data = run_inspection(["Solid"], {"Solid": {
            "solid": True, "single_shell": True, "positive_volume": True,
            "dimensions": (2.0, 2.0, 2.0), "dimension_tolerance": 0.01,
            "ground_z": 0.0, "ground_tolerance": 1e-4, "max_triangles": 12}})
        self.assertEqual(data["overall_technical"], "PASS")
        report = data["targets"][0]
        self.assertEqual(report["triangles"], 12)
        self.assertEqual(report["boundary_edges"], 0)
        self.assertEqual(report["non_manifold_excluding_boundary"], 0)
        self.assertGreater(report["signed_shell_volumes_if_closed"][0], 0.0)
        self.assertEqual(report["visual_quality"], "NOT VERIFIED")
        self.assertEqual(before, tuple(tuple(v.co) for v in obj.data.vertices))

    def test_reversed_normals_are_not_mistaken_for_valid_closed_solid(self):
        obj = self.cube("Inverted")
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
            bm.to_mesh(obj.data)
        finally:
            bm.free()
        obj.data.update()
        report = run_inspection(["Inverted"], {"Inverted": {
            "solid": True, "positive_volume": True}})["targets"][0]
        self.assertEqual(report["checks"]["closed_solid"]["status"], "PASS")
        self.assertEqual(report["checks"]["outward_volume"]["status"], "ISSUE")
        self.assertLess(report["signed_shell_volumes_if_closed"][0], 0)

    def test_open_sheet_is_not_automatically_a_defect(self):
        mesh = bpy.data.meshes.new("SheetMesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                         [], [(0, 1, 2, 3)])
        obj = bpy.data.objects.new("Sheet", mesh)
        bpy.context.scene.collection.objects.link(obj)
        result = run_inspection(["Sheet"])["targets"][0]
        self.assertEqual(result["boundary_edges"], 4)
        self.assertEqual(result["non_manifold_excluding_boundary"], 0)
        self.assertEqual(result["status"], "REVIEW")
        closed = run_inspection(["Sheet"], {"Sheet": {"solid": True}})["targets"][0]
        self.assertEqual(closed["checks"]["closed_solid"]["status"], "ISSUE")

    def test_single_shell_rejects_two_unjoined_closed_cubes(self):
        obj = self.cube("Shells")
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            other = bmesh.ops.create_cube(bm, size=1.0)["verts"]
            bmesh.ops.translate(bm, verts=other, vec=(5, 0, 0))
            bm.to_mesh(obj.data)
        finally:
            bm.free()
        obj.data.update()
        report = run_inspection(["Shells"], {"Shells": {
            "solid": True, "single_shell": True}})["targets"][0]
        self.assertEqual(report["face_islands"], 2)
        self.assertEqual(report["checks"]["single_shell"]["status"], "ISSUE")
        self.assertEqual(report["checks"]["closed_solid"]["status"], "PASS")

    def test_relationship_gap_detects_definite_separation_not_assumed_contact(self):
        self.cube("Seat", (0, 0, 4))
        self.cube("Leg", (0, 0, 1))
        result = run_inspection(
            ["Seat", "Leg"], relationships=[
                {"type": "max_aabb_gap", "a": "Seat", "b": "Leg", "max_gap": 0.05}
            ])
        self.assertEqual(result["relationships"][0]["status"], "ISSUE")
        self.assertAlmostEqual(result["relationships"][0]["actual"], 1.0)
        self.cube("Other", (0, 0, 2))
        result = run_inspection(
            ["Seat", "Other"], relationships=[
                {"type": "max_aabb_gap", "a": "Seat", "b": "Other", "max_gap": 0.05}
            ])
        self.assertEqual(result["relationships"][0]["status"], "REVIEW")

    def test_missing_target_never_reports_pass(self):
        result = run_inspection(["Uncreated"], {"Uncreated": {"solid": True}})
        self.assertEqual(result["overall_technical"], "NOT VERIFIED")
        self.assertEqual(result["missing_targets"], ["Uncreated"])

    def test_modifier_output_is_evaluated_and_source_is_untouched(self):
        source = self.cube("Processed")
        before = len(source.data.polygons)
        mod = source.modifiers.new("TriangulateForExport", "TRIANGULATE")
        report = run_inspection(["Processed"], {"Processed": {"max_triangles": 11}})["targets"][0]
        self.assertEqual(report["checks"]["triangle_budget"]["status"], "ISSUE")
        self.assertEqual(report["triangles"], 12)
        self.assertEqual(len(source.data.polygons), before)
        self.assertIs(source.modifiers[0], mod)


if __name__ == "__main__":
    unittest.main()
