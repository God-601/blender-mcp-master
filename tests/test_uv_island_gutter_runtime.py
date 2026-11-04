"""Blender bpy regression cases for conservative per-island UV gutter audit."""
import ast
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "uv_island_gutter_audit.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def run(targets, **options):
    script = SCRIPT.read_text(encoding="utf-8")
    for key, value in {"TARGETS": targets, **options}.items():
        script, n = re.subn(r"^" + key + r" = .*",
                            lambda _, k=key, v=value: k + " = " + repr(v),
                            script, count=1, flags=re.M)
        assert n == 1, key
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(script, str(SCRIPT), "exec"), {"__name__": "__main__"})
    return json.loads(buffer.getvalue().split("MCP_UV_GUTTER_BEGIN\n", 1)[1]
                      .split("\nMCP_UV_GUTTER_END", 1)[0])


class StaticGutterTests(unittest.TestCase):
    def test_script_is_read_only_and_requires_named_targets(self):
        content = SCRIPT.read_text(encoding="utf-8")
        ast.parse(content)
        self.assertIn("TARGETS = []", content)
        self.assertIn("NOT VERIFIED", content)
        self.assertNotIn("bpy.ops.", content)
        self.assertNotIn("bmesh.ops", content)


@unittest.skipIf(bpy is None, "bpy unavailable")
class RuntimeGutterTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        mesh = bpy.data.meshes.new("DoubleQuadMesh")
        # Two separate physical quads; each makes one distinct UV island.
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                          (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)],
                         [], [(0, 1, 2, 3), (4, 5, 6, 7)])
        mesh.update()
        obj = bpy.data.objects.new("IslandAsset", mesh)
        bpy.context.collection.objects.link(obj)
        self.obj = obj
        self.uv = mesh.uv_layers.new(name="UVMap")
        self.set_rectangles(0.3)

    def set_rectangles(self, left):
        for polygon in self.obj.data.polygons:
            x0 = 0.0 if polygon.index == 0 else left
            x1 = x0 + 0.25
            for offset, loop_id in enumerate(polygon.loop_indices):
                self.uv.data[loop_id].uv = [(x0, 0.0), (x1, 0.0),
                                            (x1, 0.25), (x0, 0.25)][offset]

    def test_well_separated_uv_islands_have_measured_conservative_lower_bound(self):
        original = [tuple(v.co) for v in self.obj.data.vertices]
        report = run(["IslandAsset"], TEXTURE_WIDTH=1024,
                     TEXTURE_HEIGHT=1024, DESIRED_PADDING_PX=8)
        self.assertEqual(report["overall"], "MEASURED")
        item = report["reports"][0]
        self.assertEqual(item["uv_islands"], 2)
        self.assertEqual(item["suspicious_island_pairs"], 0)
        self.assertGreater(item["lowest_aabb_gutter_bound_px"], 8)
        self.assertEqual(item["baking_quality"], "NOT VERIFIED")
        self.assertEqual(original, [tuple(v.co) for v in self.obj.data.vertices])

    def test_close_islands_require_review_not_auto_bake_success(self):
        self.set_rectangles(0.254)
        item = run(["IslandAsset"], DESIRED_PADDING_PX=8)["reports"][0]
        self.assertEqual(item["status"], "REVIEW")
        self.assertEqual(item["suspicious_island_pairs"], 1)
        self.assertLess(item["lowest_aabb_gutter_bound_px"], 8)
        self.assertEqual(item["engine_import"], "NOT VERIFIED")

    def test_touching_bounds_are_review(self):
        self.set_rectangles(0.25)
        item = run(["IslandAsset"])["reports"][0]
        self.assertEqual(item["status"], "REVIEW")
        self.assertEqual(item["lowest_aabb_gutter_bound_px"], 0)

    def test_missing_uv_or_missing_target_is_not_verified(self):
        self.assertEqual(run([])["overall"], "NOT VERIFIED")
        self.assertEqual(run(["Missing"])["overall"], "NOT VERIFIED")
        self.obj.data.uv_layers.clear()
        self.assertEqual(run(["IslandAsset"])["overall"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
