"""Release metadata never automatically authorizes publication."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "release_gate_report.py"


def load():
    spec = importlib.util.spec_from_file_location("release_gate_report", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sample():
    mod = load()
    return {
        "version": "1.8.0", "commit_sha": "a" * 40,
        "checks": {x: {"status": "PASS", "evidence": ["logs/" + x + ".json"]}
                   for x in mod.GATES},
    }


class ReleaseGateTests(unittest.TestCase):
    def test_even_all_claimed_pass_is_review_without_publish(self):
        r = load().evaluate(sample())
        self.assertEqual(r["reported_gate_status"], "REVIEW")
        self.assertEqual(r["publication_authorized"], False)
        self.assertEqual(r["actual_live_evidence_verified"], "NOT VERIFIED")

    def test_missing_real_visual_review_holds_release(self):
        data = sample()
        data["checks"].pop("visual_review")
        r = load().evaluate(data)
        self.assertEqual(r["reported_gate_status"], "HOLD")
        self.assertIn("visual_review", r["blockers"])

    def test_pass_without_evidence_not_verified(self):
        data = sample()
        data["checks"]["agent_live_modeling"]["evidence"] = []
        r = load().evaluate(data)
        self.assertEqual(r["checks"]["agent_live_modeling"]["status"], "NOT VERIFIED")
        self.assertFalse(r["publication_authorized"])

    def test_wrong_version_sha_or_unknown_gate_fails(self):
        m = load()
        for key, value in (("version", "2.1.0"), ("commit_sha", "head")):
            data = sample()
            data[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.evaluate(data)
        data = sample()
        data["checks"]["fake"] = {"status": "PASS"}
        with self.assertRaises(ValueError):
            m.evaluate(data)

    def test_na_without_reason_not_accepted(self):
        data = sample()
        data["checks"]["destination_validation"] = {"status": "N/A", "evidence": []}
        self.assertEqual(load().evaluate(data)["reported_gate_status"], "HOLD")


if __name__ == "__main__":
    unittest.main()
