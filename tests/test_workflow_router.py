"""Pure Python routing tests: no file access, Blender or optional dependencies."""
import importlib.util
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
                     {"category": "organic", "continuation": "yes"}):
            with self.subTest(task=task), self.assertRaises(ValueError):
                m.route(task)


if __name__ == "__main__":
    unittest.main()
