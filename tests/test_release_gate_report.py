"""Release metadata never automatically authorizes publication."""
import importlib.util
import unittest
import hashlib
import tempfile
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
    def test_v2_requires_actual_exact_commit_hashed_artifacts(self):
        mod = load()
        data = sample()
        data['version'] = '2.0.0'
        self.assertEqual(mod.evaluate(data)['reported_gate_status'], 'HOLD')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for gate in mod.V2_GATES:
                path = root / (gate + '.json')
                path.write_text('{"test_fixture":true}', encoding='utf-8')
                data['checks'][gate] = {'status': 'PASS', 'commit_sha': data['commit_sha'],
                    'evidence': [path.name], 'sha256': {path.name: hashlib.sha256(path.read_bytes()).hexdigest()}}
            result = mod.evaluate(data, evidence_root=root)
            self.assertEqual(result['reported_gate_status'], 'REVIEW')
            self.assertFalse(result['publication_authorized'])
            (root / 'visual_review.json').write_text('tampered', encoding='utf-8')
            self.assertIn('visual_review', mod.evaluate(data, evidence_root=root)['blockers'])

    def test_v2_cannot_bypass_live_gates_with_na_or_other_commit(self):
        data = sample()
        data['version'] = '2.0.0'
        for gate in data['checks']:
            data['checks'][gate] = {'status': 'N/A', 'reason': 'not available'}
        self.assertEqual(load().evaluate(data)['reported_gate_status'], 'HOLD')

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
