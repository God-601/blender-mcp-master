"""No fabricated efficiency result; aggregate only genuinely matched receipts."""
import importlib.util
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "scripts" / "benchmark_suite_summary.py"


def load():
    spec = importlib.util.spec_from_file_location("benchmark_suite_summary", SRC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(tokens=100):
    return {
        "prompt_sha256": "a" * 64, "scene_fixture_sha256": "b" * 64,
        "agent": "Codex", "model": "test-model", "blender_version": "4.5",
        "mcp_version": "1.8", "run_status": "completed",
        "checks": {"scene_preserved": "PASS", "visual": "NOT VERIFIED"},
        "incidents": [],
        "usage": {"input_tokens": tokens, "output_tokens": 20},
    }


class SuiteTests(unittest.TestCase):
    def test_measures_matched_and_retains_crashed(self):
        failed = run(100)
        failed["incidents"] = ["crash"]
        report = load().summarize({"trials": [
            {"case_id": "chair", "baseline": run(100), "with_skill": run(50)},
            {"case_id": "sword", "baseline": run(100), "with_skill": failed},
        ]})
        self.assertEqual(report["trial_count"], 2)
        self.assertEqual(report["comparable_trials"], 1)
        self.assertEqual(report["inconclusive_trials"], 1)
        self.assertEqual(report["token_usage"]["delta"], -50)
        self.assertEqual(report["quality"], "NOT VERIFIED")
        self.assertEqual(report["generalizable_savings"], "NOT VERIFIED")

    def test_missing_usage_does_not_become_zero(self):
        candidate = run()
        candidate.pop("usage")
        r = load().summarize({"trials": [
            {"case_id": "chair", "baseline": run(), "with_skill": candidate},
        ]})
        self.assertIsNone(r["token_usage"]["delta"])
        self.assertEqual(r["token_usage"]["status"], "NOT VERIFIED")
        self.assertIn("missing_actual_usage", r["trials"][0]["reasons"])

    def test_unmatched_model_blocks_comparison(self):
        candidate = run(50)
        candidate["model"] = "different"
        r = load().summarize({"trials": [
            {"case_id": "chair", "baseline": run(), "with_skill": candidate},
        ]})
        self.assertEqual(r["comparable_trials"], 0)

    def test_invalid_inputs_rejected(self):
        m = load()
        with self.assertRaises(ValueError):
            m.summarize({})
        with self.assertRaises(ValueError):
            m.summarize({"trials": [None]})
        with self.assertRaises(ValueError):
            m.summarize({"trials": [{"case_id": ""}]})


if __name__ == "__main__":
    unittest.main()
