"""Defect Memory must be opt-in, evidence-backed and backwards compatible."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "technique_registry.py"


def load():
    spec = importlib.util.spec_from_file_location("technique_registry", SOURCE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def legacy():
    return {"task": "Chair", "technique": "bridge", "blender_version": "4.5",
            "status": "REVIEWED_PASS", "review": {
                "result": "pass", "reviewer": "reviewer", "score": 4},
            "evidence": ["front.png"], "parameters": {"steps": 2}}


def defect():
    return dict(legacy(), kind="defect_resolution", defect_id="G2-001",
                symptom="leg floating", root_cause="wrong Z", correction="move leg 0.05",
                affected_objects=["Chair_Leg"], before_evidence=["before.png"],
                after_evidence=["after.png"])


class DefectMemoryTests(unittest.TestCase):
    def test_reviewed_defect_is_accepted_and_distinct(self):
        m = load()
        original, corrected = legacy(), defect()
        self.assertTrue(m._approved(corrected))
        self.assertNotEqual(m._fingerprint(original), m._fingerprint(corrected))
        merged = m.merge_reviewed([], [original, corrected])
        self.assertEqual(merged["added"], 2)

    def test_missing_review_or_before_after_evidence_rejected(self):
        m = load()
        for key in ("defect_id", "root_cause", "correction", "affected_objects",
                    "before_evidence", "after_evidence"):
            broken = defect()
            broken.pop(key)
            with self.subTest(key=key):
                self.assertFalse(m._approved(broken))
        broken = defect()
        broken["review"]["result"] = "issue"
        self.assertFalse(m._approved(broken))

    def test_no_automatic_persistence(self):
        m = load()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "records.json"
            with self.assertRaisesRegex(ValueError, "explicit approval"):
                m.persist_registry(str(path), [defect()])
            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
