"""Regression tests for read-only measured game asset preflight."""
import ast
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "game_asset_preflight.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def preflight(targets, **options):
    code = SCRIPT.read_text(encoding="utf-8")
    for key, val in {"TARGETS": targets, **options}.items():
        code, count = re.subn(r"^" + key + r" = .*",
                              lambda _, k=key, v=val: k + " = " + repr(v),
                              code, count=1, flags=re.M)
        assert count == 1, key
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, str(SCRIPT), "exec"), {"__name__": "__main__"})
    return json.loads(buf.getvalue().split("MCP_GAME_PREFLIGHT_BEGIN\n", 1)[1]
                      .split("\nMCP_GAME_PREFLIGHT_END", 1)[0])


class StaticTests(unittest.TestCase):
    def test_opt_in_and_read_only(self):
        code = SCRIPT.read_text(encoding="utf-8")
        ast.parse(code)
        self.assertIn("TARGETS = []", code)
        self.assertIn("NOT VERIFIED", code)
        self.assertNotIn("bpy.ops.", code)
        self.assertNotIn("bpy.data.objects.remove", code)


@unittest.skipIf(bpy is None, "bpy unavailable")
class RuntimeGamePreflightTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add(size=2.0)
        self.obj = bpy.context.object
        self.obj.name = "GameCrate"
        if not self.obj.data.uv_layers:
            self.obj.data.uv_layers.new(name="UVMap")

    def test_evaluated_counts_pivot_and_uv_without_engine_pass(self):
        before = [tuple(v.co) for v in self.obj.data.vertices]
        report = preflight(["GameCrate"], ENGINE="ROBLOX")
        self.assertEqual(report["overall"], "MEASURED")
        item = report["objects"][0]
        self.assertEqual(item["evaluated_triangles"], 12)
        self.assertEqual(item["world_extent_xyz"], [2.0, 2.0, 2.0])
        self.assertGreaterEqual(item["evaluated_uv_layers"], 1)
        self.assertEqual(report["engine_test"], "NOT VERIFIED")
        self.assertEqual(before, [tuple(v.co) for v in self.obj.data.vertices])

    def test_modifier_budget_and_scaled_object(self):
        self.obj.scale.x = 1.5
        modifier = self.obj.modifiers.new("Subsurf", "SUBSURF")
        modifier.levels = 1
        report = preflight(["GameCrate"], MAX_EVALUATED_TRIANGLES=12)
        item = report["objects"][0]
        self.assertEqual(item["status"], "ISSUE")
        self.assertGreater(item["evaluated_triangles"], 12)
        self.assertTrue(item["warnings"])
        self.assertEqual(len(self.obj.modifiers), 1)

    def test_missing_uv_and_texture_file_are_reported(self):
        while self.obj.data.uv_layers:
            self.obj.data.uv_layers.remove(self.obj.data.uv_layers[0])
        mat = bpy.data.materials.new("Wood")
        mat.use_nodes = True
        tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
        img = bpy.data.images.new("MissingWood", width=4, height=4)
        img.source = "FILE"
        img.filepath = "//this_file_does_not_exist_784.png"
        tex.image = img
        self.obj.data.materials.append(mat)
        result = preflight(["GameCrate"], REQUIRE_IMAGE_FILES=True)
        item = result["objects"][0]
        self.assertEqual(item["status"], "ISSUE")
        self.assertTrue(any("UV" in error for error in item["issues"]))
        self.assertTrue(any("texture" in error for error in item["issues"]))
        self.assertEqual(result["engine_test"], "NOT VERIFIED")

    def test_missing_and_invalid_targets_stay_not_verified(self):
        self.assertEqual(preflight([])["overall"], "NOT VERIFIED")
        self.assertEqual(preflight(["GameCrate", "GameCrate"])["overall"], "NOT VERIFIED")
        self.assertEqual(preflight(["DoesNotExist"])["overall"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
