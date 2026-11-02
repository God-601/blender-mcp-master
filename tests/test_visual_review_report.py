"""Proof-of-review contract tests. This module is not an image classifier."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "visual_review_report.py"


def module():
    spec = importlib.util.spec_from_file_location("visual_review_report", SCRIPT)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def sample():
    return {
        "asset": "Chair",
        "captures": [
            {"view": "front", "artifact": "capture://front", "reviewer": "human"},
            {"view": "side", "artifact": "capture://side", "reviewer": "human"},
            {"view": "three_quarter", "artifact": "capture://three_quarter", "reviewer": "human"},
        ],
        "defects": [],
    }


class VisualReviewContractTests(unittest.TestCase):
    def test_missing_views_cannot_claim_visual_review(self):
        m = module()
        r = m.assess_review({"asset": "Chair", "captures": [], "defects": []})
        self.assertEqual(r["visual_status"], "NOT VERIFIED")
        self.assertEqual(set(r["missing_views"]), {"front", "side", "three_quarter"})

    def test_complete_metadata_is_only_review_recorded_not_artistic_pass(self):
        m = module()
        r = m.assess_review(sample())
        self.assertEqual(r["visual_status"], "REVIEW_RECORDED")
        self.assertNotEqual(r["visual_status"], "PASS")
        self.assertEqual(r["open_defects"], [])

    def test_major_defects_force_issue_even_with_three_views(self):
        m = module()
        report = sample()
        report["defects"].append({"type": "shading", "severity": "major",
                                  "object": "Chair_Leg", "description": "pinching", "resolved": False})
        r = m.assess_review(report)
        self.assertEqual(r["visual_status"], "ISSUE")
        self.assertEqual(r["open_defects"][0]["object"], "Chair_Leg")
        self.assertIn("inspect", r["next_steps"][0].lower())

    def test_invalid_or_unreviewed_capture_does_not_count(self):
        m = module()
        report = sample()
        report["captures"][0]["reviewer"] = ""
        self.assertEqual(m.assess_review(report)["visual_status"], "NOT VERIFIED")
        with self.assertRaises(ValueError):
            m.assess_review({"asset": "X", "captures": [], "defects": [{"type": "none"}]})

    def test_never_changes_original_report(self):
        m = module()
        p = sample()
        orig = repr(p)
        m.assess_review(p)
        self.assertEqual(repr(p), orig)
