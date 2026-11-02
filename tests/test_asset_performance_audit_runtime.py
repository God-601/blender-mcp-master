"""Read-only Blender asset performance audit tests (not an FPS benchmark)."""
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "asset_performance_audit.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def run_audit(targets, budgets=None):
    source = SCRIPT.read_text(encoding="utf-8")
    settings = {"TARGETS": targets}
    if budgets:
        settings.update(budgets)
    for key, value in settings.items():
        source, count = re.subn(
            rf"^{key}\s*=.*$", lambda _m, k=key, v=value: f"{k} = {v!r}",
            source, flags=re.M, count=1
        )
        assert count == 1, key
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
    payload = stream.getvalue().split("MCP_PERFORMANCE_AUDIT_BEGIN\n", 1)[1]
    return json.loads(payload.split("\nMCP_PERFORMANCE_AUDIT_END", 1)[0])


class PerformanceAuditStaticTests(unittest.TestCase):
    def test_read_only_contract(self):
        code = SCRIPT.read_text(encoding="utf-8")
        import ast
        ast.parse(code)
        self.assertIn("TARGETS = []", code)
        self.assertIn("NOT VERIFIED", code)
        self.assertNotIn("bpy.ops.object.delete", code)
        self.assertNotIn("bpy.data.objects.remove", code)


@unittest.skipIf(bpy is None, "bpy not installed")
class PerformanceAuditRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name="Cube"):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_requires_explicit_targets_and_never_falls_back_to_selection(self):
        self.cube()
        report = run_audit([])
        self.assertEqual(report["status"], "NOT VERIFIED")
        self.assertEqual(report["assets"], [])
        self.assertEqual(report["total_evaluated_triangles"], 0)

    def test_evaluated_count_includes_subdivision_and_is_read_only(self):
        obj = self.cube("Source")
        mod = obj.modifiers.new("Subdivision", "SUBSURF")
        mod.levels = 2
        before = [(v.co.x, v.co.y, v.co.z) for v in obj.data.vertices]
        report = run_audit(["Source"], {"MAX_EVALUATED_TRIS": 500})
        self.assertEqual(report["status"], "MEASURED")
        item = report["assets"][0]
        self.assertEqual(item["base_triangles"], 12)
        self.assertGreater(item["evaluated_triangles"], 12)
        self.assertEqual(item["visual_quality"], "NOT VERIFIED")
        self.assertEqual(report["total_evaluated_triangles"], item["evaluated_triangles"])
        self.assertEqual(before, [(v.co.x, v.co.y, v.co.z) for v in obj.data.vertices])
        self.assertEqual(len(obj.modifiers), 1)

    def test_missing_target_and_nonmesh_are_incomplete(self):
        bpy.ops.object.empty_add()
        bpy.context.object.name = "NotMesh"
        report = run_audit(["Missing", "NotMesh"])
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(len(report["errors"]), 2)
        self.assertEqual(report["assets"], [])

    def test_shared_mesh_data_not_counted_twice_for_unique_datablocks(self):
        first = self.cube("One")
        second = first.copy()
        second.name = "Two"
        bpy.context.scene.collection.objects.link(second)
        self.assertIs(first.data, second.data)
        report = run_audit(["One", "Two"])
        self.assertEqual(report["unique_base_mesh_datablocks"], 1)
        self.assertEqual(report["total_evaluated_triangles"], 24)
        self.assertTrue(any(x["shared_mesh_data"] for x in report["assets"]))

    def test_budget_overrun_warns_without_claiming_actual_fps(self):
        obj = self.cube("Heavy")
        obj.data.materials.append(bpy.data.materials.new("MatOne"))
        obj.data.materials.append(bpy.data.materials.new("MatTwo"))
        report = run_audit(["Heavy"], {"MAX_EVALUATED_TRIS": 6, "MAX_MATERIAL_SLOTS": 1})
        item = report["assets"][0]
        self.assertEqual(item["budget_status"], "ISSUE")
        self.assertGreaterEqual(len(item["recommendations"]), 1)
        self.assertEqual(report["fps_measurement"], "NOT VERIFIED")

    def test_invalid_targets_cannot_claim_measured(self):
        report = run_audit(["Cube", "Cube"])
        self.assertEqual(report["status"], "INCOMPLETE")
        self.assertEqual(report["assets"], [])
