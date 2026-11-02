"""Tests for reviewed, opt-in cross-project technique registry (pure Python)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "technique_registry.py"


def load_registry_module():
    spec = importlib.util.spec_from_file_location("technique_registry", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def approved(technique="edge_bridge"):
    return {
        "task": "mechanical panel",
        "technique": technique,
        "parameters": {"count": 4},
        "status": "REVIEWED_PASS",
        "blender_version": "4.5.15",
        "evidence": ["actual-screenshot-1.png"],
        "limitations": [],
        "review": {"reviewer": "human", "result": "pass", "score": 3},
    }


class TechniqueRegistryTests(unittest.TestCase):
    def test_merge_imports_only_reviewed_success_with_evidence(self):
        m = load_registry_module()
        bad = approved("bad")
        bad["status"] = "USER_REVIEW_REQUIRED"
        without_evidence = approved("no_evidence")
        without_evidence["evidence"] = []
        result = m.merge_reviewed([], [approved(), bad, without_evidence])
        self.assertEqual(len(result["records"]), 1)
        self.assertEqual(result["records"][0]["technique"], "edge_bridge")
        self.assertEqual(result["rejected"], 2)

    def test_duplicate_records_are_idempotent(self):
        m = load_registry_module()
        one = m.merge_reviewed([], [approved()])
        two = m.merge_reviewed(one["records"], [approved()])
        self.assertEqual(one["records"], two["records"])
        self.assertEqual(two["added"], 0)

    def test_persist_requires_explicit_opt_in_absolute_path_and_backup(self):
        m = load_registry_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            with self.assertRaises(ValueError):
                m.persist_registry(path, [approved()], allow_write=False)
            self.assertFalse(path.exists())
            with self.assertRaises(ValueError):
                m.persist_registry(Path("relative.json"), [approved()], allow_write=True)
            created = m.persist_registry(path, [approved()], allow_write=True)
            self.assertEqual(created["added"], 1)
            self.assertTrue(path.exists())
            self.assertEqual(len(m.read_registry(path)), 1)
            other = m.persist_registry(path, [approved("new")], allow_write=True)
            self.assertEqual(other["added"], 1)
            self.assertEqual(len(m.read_registry(path)), 2)
            self.assertTrue(any(Path(tmp).glob("registry.json.backup-*")))

    def test_never_overwrites_invalid_existing_json(self):
        m = load_registry_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text('{"unexpected": true}', encoding="utf-8")
            with self.assertRaises(ValueError):
                m.persist_registry(path, [approved()], allow_write=True)
            self.assertEqual(json.loads(path.read_text()), {"unexpected": True})

    def test_ranked_query_excludes_unreviewed_data(self):
        m = load_registry_module()
        records = m.merge_reviewed([], [approved("a"), approved("b")])["records"]
        result = m.find_techniques(records, "mechanical panel")
        self.assertEqual(len(result), 2)
        self.assertEqual(m.find_techniques(records, "not a task"), [])
