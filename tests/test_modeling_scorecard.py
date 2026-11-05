"""Pure-Python regression tests for the evidence-only modeling scorecard."""
import importlib.util
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "scripts" / "modeling_scorecard.py"


def scorecard():
    spec = importlib.util.spec_from_file_location("modeling_scorecard", PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ModelingScorecardTests(unittest.TestCase):
    def test_no_evidence_cannot_claim_pass(self):
        result = scorecard().build_scorecard({
            "asset": "Chair", "criteria": {"topology": {"status": "PASS"}}})
        self.assertEqual(result["criteria"]["topology"]["status"], "NOT VERIFIED")
        self.assertEqual(result["overall"], "NOT VERIFIED")
        self.assertEqual(result["artistic_quality"], "NOT VERIFIED")

    def test_unprovided_criteria_never_get_pass(self):
        result = scorecard().build_scorecard({
            "asset": "Crate", "criteria": {
                "scene_preservation": {"status": "PASS", "evidence": ["saved baseline hash"]}}})
        self.assertEqual(result["criteria"]["scene_preservation"]["status"], "PASS")
        self.assertEqual(result["criteria"]["silhouette"]["status"], "NOT VERIFIED")
        self.assertEqual(result["engine_certification"], "NOT VERIFIED")

    def test_issue_overrides_missing_evidence(self):
        result = scorecard().build_scorecard({
            "asset": "Sword", "criteria": {
                "component_fit": {"status": "ISSUE", "evidence": ["screenshot side"]}}})
        self.assertEqual(result["overall"], "ISSUE")

    def test_invalid_evidence_and_unknown_checks_fail_closed(self):
        m = scorecard()
        for item in (
            {"asset": "", "criteria": {}},
            {"asset": "A", "criteria": {"topology": {"status": "GOOD"}}},
            {"asset": "A", "criteria": {"topology": {"status": "PASS", "evidence": "fake"}}},
            {"asset": "A", "criteria": {"undocumented_check": {"status": "PASS"}}},
        ):
            with self.subTest(item=item), self.assertRaises(ValueError):
                m.build_scorecard(item)

    def test_evidence_is_not_mutated(self):
        m = scorecard()
        item = {"asset": "A", "criteria": {"topology": {
            "status": "PASS", "evidence": ["asset mesh audit"]}}}
        before = repr(item)
        self.assertEqual(m.build_scorecard(item)["criteria"]["topology"]["status"], "PASS")
        self.assertEqual(before, repr(item))


if __name__ == "__main__":
    unittest.main()
