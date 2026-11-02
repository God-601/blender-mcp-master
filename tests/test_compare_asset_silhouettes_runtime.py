"""Runtime regression tests for paired evaluated silhouette-proxy comparisons."""
import ast
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_asset_silhouettes.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def measure(pairs):
    src = SCRIPT.read_text(encoding="utf-8")
    src, count = re.subn(r"^PAIRS = \[\]", lambda _: "PAIRS = " + repr(pairs),
                         src, flags=re.M, count=1)
    assert count == 1
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(src, str(SCRIPT), "exec"), {"__name__": "__main__"})
    return json.loads(output.getvalue().split("MCP_SILHOUETTE_PROXY_BEGIN\n", 1)[1]
                      .split("\nMCP_SILHOUETTE_PROXY_END", 1)[0])


class StaticSilhouetteTests(unittest.TestCase):
    def test_safe_readonly_explicit_optin(self):
        text = SCRIPT.read_text(encoding="utf-8")
        ast.parse(text)
        self.assertIn("PAIRS = []", text)
        self.assertNotIn("bpy.ops.object.delete", text)
        self.assertNotIn("bmesh.ops.delete", text)
        self.assertNotIn("bpy.ops.wm.save_as_mainfile", text)


@unittest.skipIf(bpy is None, "bpy not installed")
class SilhouetteRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        self.original = bpy.context.object
        self.original.name = "Original"
        self.copy = self.original.copy()
        self.copy.name = "Optimized"
        self.copy.data = self.original.data.copy()
        self.copy.location.x = 3.0
        bpy.context.scene.collection.objects.link(self.copy)
        bpy.context.view_layer.update()

    def test_unmodified_copy_requires_visual_review_not_auto_visual_pass(self):
        before = tuple(v.co[:] for v in self.original.data.vertices)
        result = measure([{"source": "Original", "optimized": "Optimized"}])
        self.assertEqual(result["status"], "REVIEW")
        self.assertEqual(result["pair_results"][0]["largest_relative_projection_change"], 0)
        self.assertEqual(result["pair_results"][0]["visual_quality"], "NOT VERIFIED")
        self.assertEqual(before, tuple(v.co[:] for v in self.original.data.vertices))

    def test_changes_in_evaluated_silhouette_are_caught(self):
        self.copy.scale.x = 0.6
        bpy.context.view_layer.update()
        output = measure([{"source": "Original", "optimized": "Optimized"}])
        self.assertEqual(output["status"], "ISSUE")
        self.assertGreater(output["pair_results"][0]["largest_relative_projection_change"], 0.08)

    def test_modifiers_count_evaluated_geometry(self):
        modifier = self.copy.modifiers.new("Subsurf", "SUBSURF")
        modifier.levels = 1
        output = measure([{"source": "Original", "optimized": "Optimized"}])
        item = output["pair_results"][0]
        self.assertEqual(item["source_evaluated_triangles"], 12)
        self.assertGreater(item["optimized_evaluated_triangles"], 12)
        self.assertEqual(item["visual_quality"], "NOT VERIFIED")

    def test_missing_invalid_or_same_object_is_not_verified(self):
        self.assertEqual(measure([])["status"], "NOT VERIFIED")
        cases = [{"source": "Original", "optimized": "Missing"},
                 {"source": "Original", "optimized": "Original"},
                 {"source": "Original", "optimized": "Optimized",
                  "max_relative_difference": -1}]
        for case in cases:
            self.assertEqual(measure([case])["status"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
