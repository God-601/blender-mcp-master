"""Pure Python routing and command-line tests without Blender."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "workflow_router.py"


def router():
    spec = importlib.util.spec_from_file_location("workflow_router", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class RouterTests(unittest.TestCase):
    def test_simple_task_routes_to_one_guide(self):
        item = router().route({"category": "hard_surface", "destination": "render", "needs": [],
                               "known": ["purpose", "materials"], "delegated": ["reference"]})
        self.assertEqual(item["primary"], "references/hard-surface.md")
        self.assertEqual(item["optional"], [])
        self.assertEqual(item["questions_to_consider"], ["silhouette", "technical"])
        self.assertEqual(item["loaded_reference_count"], 0)

    def test_continuation_never_restarts_interview(self):
        item = router().route({"category": "organic", "destination": "roblox",
                               "needs": ["visual", "optimization"], "continuation": True})
        self.assertEqual(item["questions_to_consider"], [])
        self.assertEqual(len(item["optional"]), 2)

    def test_deduplicates_primary_in_optional_guides(self):
        item = router().route({"category": "game_asset", "destination": "unity", "needs": ["export", "uv"]})
        self.assertEqual(item["optional"], ["references/uv-baking.md"])

    def test_invalid_inputs_fail_closed(self):
        m = router()
        for task in ({}, {"category": "fake"}, {"category": "organic", "needs": "visual"},
                     {"category": "organic", "needs": ["visual", "visual"]},
                     {"category": "organic", "known": ["nonsense"]},
                     {"category": "organic", "continuation": "yes"},
                     {"category": []}, {"category": "organic", "destination": {}},
                     {"category": "organic", "continuation": 1}):
            with self.subTest(task=task), self.assertRaises(ValueError):
                m.route(task)

    def test_cli_routes_the_supplied_json_brief(self):
        with tempfile.TemporaryDirectory() as directory:
            brief = Path(directory) / "brief.json"
            brief.write_text(json.dumps({
                "category": "organic", "destination": "animation", "needs": ["visual"],
                "continuation": True,
            }), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(brief)],
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        routed = json.loads(result.stdout)
        self.assertEqual(routed["destination"], "animation")
        self.assertEqual(routed["primary"], "references/organic.md")
        self.assertEqual(routed["optional"], ["references/visual-inspection.md"])
        self.assertEqual(routed["questions_to_consider"], [])

    def test_cli_reports_invalid_briefs_without_routing(self):
        with tempfile.TemporaryDirectory() as directory:
            brief = Path(directory) / "brief.json"
            for contents in ('{"category":', '{"category": []}'):
                with self.subTest(contents=contents):
                    brief.write_text(contents, encoding="utf-8")
                    result = subprocess.run([sys.executable, str(SCRIPT), str(brief)],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertIn("error:", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
