"""Pure Python tests for paired skill-on vs skill-off efficiency evidence."""
import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "agent_efficiency_compare.py"


def load_module():
    spec = importlib.util.spec_from_file_location("agent_efficiency_compare", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(tokens=100, shell=8):
    return {
        "case_id": "E01",
        "prompt_sha256": "a" * 64,
        "scene_fixture_sha256": "b" * 64,
        "agent": "Codex",
        "model": "test-model",
        "blender_version": "4.5.15",
        "mcp_version": "2.0",
        "usage": {"input_tokens": tokens, "output_tokens": 25},
        "metrics": {"bash_calls": shell, "mcp_calls": 12, "reference_bytes": 12500},
        "checks": {"technical": "PASS", "scene_preserved": "PASS", "visual": "NOT VERIFIED"},
    }


class PairedEfficiencyTests(unittest.TestCase):
    def test_measures_token_delta_only_for_matching_input(self):
        m = load_module()
        base = record(200)
        candidate = record(100, 2)
        result = m.compare(base, candidate)
        self.assertTrue(result["comparable"])
        self.assertEqual(result["token_usage"]["status"], "MEASURED")
        self.assertEqual(result["token_usage"]["baseline"], 225)
        self.assertEqual(result["token_usage"]["candidate"], 125)
        self.assertEqual(result["token_usage"]["delta"], -100)
        self.assertAlmostEqual(result["token_usage"]["percent_change"], -100 / 225 * 100)
        self.assertEqual(result["quality_claim"], "NOT VERIFIED")

    def test_missing_or_negative_tokens_never_produce_savings_claim(self):
        m = load_module()
        for usage in ({}, {"input_tokens": -1, "output_tokens": 4},
                      {"input_tokens": True, "output_tokens": 5}):
            candidate = record()
            candidate["usage"] = usage
            result = m.compare(record(), candidate)
            self.assertEqual(result["token_usage"]["status"], "NOT VERIFIED")

    def test_different_prompt_scene_or_model_is_not_comparable(self):
        m = load_module()
        for field, value in (("prompt_sha256", "c"*64),
                             ("scene_fixture_sha256", "d"*64),
                             ("model", "another-model")):
            candidate = record()
            candidate[field] = value
            r = m.compare(record(), candidate)
            self.assertFalse(r["comparable"])
            self.assertEqual(r["token_usage"]["status"], "NOT VERIFIED")

    def test_bash_reduction_without_token_metrics_is_not_token_savings(self):
        m = load_module()
        base = record()
        target = record(shell=0)
        base.pop("usage")
        target.pop("usage")
        result = m.compare(base, target)
        self.assertEqual(result["metrics"]["bash_calls_delta"], -8)
        self.assertEqual(result["token_usage"]["status"], "NOT VERIFIED")

    def test_report_does_not_modify_inputs(self):
        m = load_module()
        a, b = record(), record(30)
        before = (repr(a), repr(b))
        m.compare(a, b)
        self.assertEqual(before, (repr(a), repr(b)))
