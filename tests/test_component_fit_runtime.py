"""Regression tests for explicit, read-only component joint and penetration review."""
import ast
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "inspect_component_fit.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def run_checks(checks):
    source = SCRIPT.read_text(encoding="utf-8")
    source, changed = re.subn(
        r"^CHECKS = \[\]",
        lambda _: "CHECKS = " + repr(checks),
        source, flags=re.M, count=1,
    )
    assert changed == 1, "Missing explicit CHECKS configuration"
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
    payload = log.getvalue().split("MCP_COMPONENT_FIT_BEGIN\n", 1)[1]
    return json.loads(payload.split("\nMCP_COMPONENT_FIT_END", 1)[0])


class ComponentFitStaticTests(unittest.TestCase):
    def test_script_parses_and_is_opt_in_read_only(self):
        s = SCRIPT.read_text(encoding="utf-8")
        ast.parse(s)
        self.assertIn("CHECKS = []", s)
        self.assertIn("NOT VERIFIED", s)
        self.assertIn("BVHTree", s)
        self.assertNotIn("bpy.ops.object.delete", s)
        self.assertNotIn("bpy.data.objects.remove", s)


@unittest.skipIf(bpy is None, "bpy unavailable")
class ComponentFitRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name, x=0.0):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0))
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_empty_checks_do_not_fallback_to_scene(self):
        self.cube("A")
        result = run_checks([])
        self.assertEqual(result["overall"], "NOT VERIFIED")
        self.assertEqual(result["pairs"], [])
        self.assertEqual(len(bpy.data.objects), 1)

    def test_separated_objects_have_proven_no_aabb_overlap(self):
        self.cube("A", 0)
        self.cube("B", 3)
        result = run_checks([{"a": "A", "b": "B", "expectation": "no_penetration"}])
        pair = result["pairs"][0]
        self.assertEqual(pair["status"], "PASS")
        self.assertEqual(pair["aabb_positive_volume_overlap"], False)
        self.assertEqual(result["visual_quality"], "NOT VERIFIED")

    def test_overlapping_objects_require_review_and_never_auto_pass(self):
        a = self.cube("A", 0)
        b = self.cube("B", 0.5)
        before = tuple(tuple(v.co) for v in a.data.vertices)
        objects_before = set(bpy.data.objects.keys())
        result = run_checks([{"a": "A", "b": "B", "expectation": "no_penetration"}])
        pair = result["pairs"][0]
        self.assertEqual(pair["status"], "REVIEW")
        self.assertEqual(pair["aabb_positive_volume_overlap"], True)
        self.assertGreater(pair["triangle_contact_candidates"], 0)
        self.assertEqual(objects_before, set(bpy.data.objects.keys()))
        self.assertEqual(before, tuple(tuple(v.co) for v in a.data.vertices))
        self.assertEqual(b.name, "B")

    def test_touching_joint_not_misclassified_as_penetration_issue(self):
        self.cube("A", 0)
        self.cube("B", 1)
        result = run_checks([{"a": "A", "b": "B", "expectation": "surface_joint"}])
        pair = result["pairs"][0]
        self.assertEqual(pair["status"], "REVIEW")
        self.assertFalse(pair["aabb_positive_volume_overlap"])

    def test_edge_only_contact_is_not_a_valid_surface_joint(self):
        self.cube("A", 0)
        b = self.cube("B", 1)
        b.location.y = 1.0
        result = run_checks([{"a": "A", "b": "B", "expectation": "surface_joint"}])
        pair = result["pairs"][0]
        self.assertEqual(pair["status"], "ISSUE")
        self.assertEqual(pair["aabb_contact_case"], "edge_corner_or_diagonal_candidate")
        self.assertEqual(pair["aabb_face_support_axes"], [2])
        self.assertEqual(pair["actual_joint_quality"], "NOT VERIFIED")

    def test_true_face_aabb_support_still_requires_review(self):
        self.cube("A", 0)
        self.cube("B", 1)
        pair = run_checks([{"a": "A", "b": "B",
                           "expectation": "surface_joint"}])["pairs"][0]
        self.assertEqual(pair["status"], "REVIEW")
        self.assertEqual(pair["aabb_contact_case"], "face_plane_candidate")
        self.assertEqual(pair["aabb_face_support_axes"], [1, 2])
        self.assertEqual(pair["actual_joint_quality"], "NOT VERIFIED")

    def test_diagonal_near_gap_does_not_pass_as_face_joint(self):
        self.cube("A", 0)
        b = self.cube("B", 1.001)
        b.location.y = 1.001
        pair = run_checks([{"a": "A", "b": "B",
                           "expectation": "surface_joint", "max_gap": 0.01}])["pairs"][0]
        self.assertEqual(pair["status"], "ISSUE")
        self.assertEqual(pair["aabb_contact_case"], "edge_corner_or_diagonal_candidate")

    def test_gapped_joint_is_definitive_issue(self):
        self.cube("A", 0)
        self.cube("B", 2)
        result = run_checks([{"a": "A", "b": "B", "expectation": "surface_joint", "max_gap": 0.01}])
        pair = result["pairs"][0]
        self.assertEqual(pair["status"], "ISSUE")
        self.assertGreater(pair["aabb_gap"], 0.01)

    def test_intentional_embedding_is_never_auto_rejected(self):
        self.cube("A", 0)
        self.cube("B", 0.5)
        result = run_checks([{"a": "A", "b": "B", "expectation": "intentional_embed", "reason": "joinery tenon"}])
        self.assertEqual(result["pairs"][0]["status"], "REVIEW")
        self.assertIn("joinery tenon", result["pairs"][0]["reason"])

    def test_missing_and_same_object_targets_are_not_verified(self):
        self.cube("A")
        for case in [
            {"a": "A", "b": "Missing", "expectation": "surface_joint"},
            {"a": "A", "b": "A", "expectation": "surface_joint"},
            {"a": "A", "b": "Camera", "expectation": "surface_joint"},
        ]:
            self.assertEqual(run_checks([case])["overall"], "NOT VERIFIED")

    def test_no_visual_quality_claim_even_when_measured(self):
        self.cube("A", 0)
        self.cube("B", 2)
        output = run_checks([{"a": "A", "b": "B", "expectation": "no_penetration"}])
        self.assertEqual(output["visual_quality"], "NOT VERIFIED")
        self.assertEqual(output["engine_collision"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
