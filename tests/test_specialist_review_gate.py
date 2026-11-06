"""Specialist report contract tests (no Blender, files or agent sessions needed)."""
import importlib.util
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "specialist_review_gate.py"


def module():
    spec = importlib.util.spec_from_file_location("specialist_review_gate", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def packet():
    return {"asset": "Chair", "builder": "AgentBuilder",
            "required_roles": ["geometry", "visual", "scene_safety"],
            "reviews": [{"role": "geometry", "reviewer": "GeometryQA", "status": "PASS",
                         "evidence": ["geometry-report.json"]},
                        {"role": "visual", "reviewer": "VisualQA", "status": "PASS",
                         "evidence": ["actual-front.png"]},
                        {"role": "scene_safety", "reviewer": "SafetyQA", "status": "PASS",
                         "evidence": ["preservation.json"]}]}


class GateTests(unittest.TestCase):
    def test_visual_receipt_does_not_prove_pixels(self):
        result = module().evaluate(packet())
        self.assertEqual(result["reviews"]["visual"]["status"], "NOT VERIFIED")
        self.assertEqual(result["overall"], "NOT VERIFIED")
        self.assertEqual(result["real_engine_import"], "NOT VERIFIED")

    def test_builder_cannot_self_certify_technical_role(self):
        payload = packet()
        payload["reviews"][0]["reviewer"] = payload["builder"]
        result = module().evaluate(payload)
        self.assertEqual(result["reviews"]["geometry"]["status"], "NOT VERIFIED")

    def test_missing_role_or_missing_evidence_prevents_review(self):
        payload = packet()
        payload["reviews"] = payload["reviews"][:1]
        result = module().evaluate(payload)
        self.assertIn("visual", result["reviews"])
        self.assertEqual(result["reviews"]["visual"]["status"], "NOT VERIFIED")
        payload = packet()
        payload["reviews"][0]["evidence"] = []
        self.assertEqual(module().evaluate(payload)["reviews"]["geometry"]["status"], "NOT VERIFIED")

    def test_issues_override_unverified_results(self):
        payload = packet()
        payload["reviews"][0]["status"] = "ISSUE"
        self.assertEqual(module().evaluate(payload)["overall"], "ISSUE")

    def test_duplicate_role_and_unsupported_values_fail(self):
        payload = packet()
        payload["reviews"].append(dict(payload["reviews"][0]))
        with self.assertRaises(ValueError):
            module().evaluate(payload)
        payload = packet()
        payload["reviews"][0]["role"] = "invented"
        with self.assertRaises(ValueError):
            module().evaluate(payload)


if __name__ == "__main__":
    unittest.main()
