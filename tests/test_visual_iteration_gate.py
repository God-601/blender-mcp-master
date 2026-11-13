"""Regression tests for visual correction acceptance without Blender or cameras."""
import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "visual_iteration_gate.py"


def load():
    spec = importlib.util.spec_from_file_location("visual_iteration_gate", SOURCE)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def row(view, iou, render_digest, reference_digest="a" * 64):
    return {"view": view, "status": "MEASURED_REVIEW_REQUIRED",
            "silhouette_iou": iou, "reference_sha256": reference_digest,
            "render_sha256": render_digest, "resolution": [512, 512]}


def packets(before=0.5, after=0.8):
    return ({"results": [row(view, before, "b" * 64) for view in
                         ("front", "side", "three_quarter")]},
            {"results": [row(view, after, "c" * 64) for view in
                         ("front", "side", "three_quarter")]})


SCENE = {"status": "PASS"}
REVIEW = {"visual_status": "REVIEW_RECORDED", "open_defects": []}


class VisualIterationGateTests(unittest.TestCase):
    def setUp(self):
        self.mod = load()

    def test_measured_improvement_only_qualifies_for_external_review(self):
        a, b = packets()
        result = self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertAlmostEqual(result["mean_iou_delta"], 0.3)
        self.assertEqual(result["visual_quality"], "NOT VERIFIED")
        self.assertNotIn("PASS", result["status"])

    def test_partial_scene_receipt_supports_review_without_certifying_global_scene(self):
        a, b = packets()
        scene = {"status": "PASS (escopo parcial)", "scene_global_integrity": "NOT VERIFIED"}
        result = self.mod.evaluate(a, b, scene, REVIEW)
        self.assertEqual(result["status"], "REVIEW_REQUIRED")
        self.assertEqual(result["protected_scene_check"], scene["status"])
        self.assertEqual(result["scene_global_integrity"], "NOT VERIFIED")

    def test_missing_independent_visual_review_blocks(self):
        a, b = packets()
        result = self.mod.evaluate(a, b, SCENE)
        self.assertEqual(result["status"], "NOT VERIFIED")
        self.assertIn("independent_visual_review_missing", result["reasons"])

    def test_changed_reference_cannot_be_compared(self):
        a, b = packets()
        b["results"][0]["reference_sha256"] = "d" * 64
        result = self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(result["status"], "NOT VERIFIED")
        self.assertIn("front: reference_or_resolution_changed", result["reasons"])

    def test_render_without_changed_bytes_cannot_claim_correction(self):
        a, b = packets()
        b["results"][0]["render_sha256"] = "b" * 64
        result = self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(result["status"], "NOT VERIFIED")
        self.assertIn("front: identical_before_after_render", result["reasons"])

    def test_one_regressed_view_blocks_even_if_mean_improves(self):
        a, b = packets()
        b["results"][1]["silhouette_iou"] = 0.4
        result = self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(result["status"], "ISSUE")
        self.assertIn("regressed_views: side", result["reasons"])
        self.assertEqual(result["recommendation"], "REVERT_OR_INSPECT_OWNED_COPY")

    def test_protected_scene_damage_blocks(self):
        a, b = packets()
        result = self.mod.evaluate(a, b, {"status": "ISSUE"}, REVIEW)
        self.assertEqual(result["status"], "ISSUE")
        self.assertIn("protected_scene_integrity_issue", result["reasons"])

    def test_no_scene_receipt_blocks(self):
        a, b = packets()
        self.assertEqual(self.mod.evaluate(a, b, None, REVIEW)["status"], "NOT VERIFIED")

    def test_open_visual_defect_blocks(self):
        a, b = packets()
        review = {"visual_status": "ISSUE", "open_defects": [{"severity": "major"}]}
        self.assertEqual(self.mod.evaluate(a, b, SCENE, review)["status"], "ISSUE")

    def test_no_metric_gain_does_not_qualify(self):
        a, b = packets(0.6, 0.6)
        result = self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(result["status"], "NOT VERIFIED")
        self.assertIn("no_demonstrated_mean_iou_improvement", result["reasons"])

    def test_missing_view_and_measurement_not_fabricated(self):
        a, b = packets()
        b["results"] = b["results"][:2]
        self.assertEqual(self.mod.evaluate(a, b, SCENE, REVIEW)["status"], "NOT VERIFIED")

    def test_duplicate_and_invalid_scores_rejected(self):
        a, b = packets()
        a["results"].append(dict(a["results"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.mod.evaluate(a, b, SCENE, REVIEW)
        a, b = packets()
        b["results"][0]["silhouette_iou"] = float("nan")
        result = self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(result["status"], "NOT VERIFIED")

    def test_inputs_not_mutated(self):
        a, b = packets()
        before = repr((a, b, SCENE, REVIEW))
        self.mod.evaluate(a, b, SCENE, REVIEW)
        self.assertEqual(before, repr((a, b, SCENE, REVIEW)))


if __name__ == "__main__":
    unittest.main()
