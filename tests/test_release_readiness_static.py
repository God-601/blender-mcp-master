"""Stable 1.0 publication must be manually authorized and evidence-grounded."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ReleaseReadinessStaticTests(unittest.TestCase):
    def test_legacy_beta_never_auto_publishes_on_main_changes(self):
        text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        triggers = text.split("permissions:", 1)[0]
        self.assertIn("workflow_dispatch:", triggers)
        self.assertNotRegex(triggers, r"(?m)^\s+push:")
        self.assertNotIn("branches: [main]", triggers)

    def test_rc_preflight_is_artifact_only(self):
        text = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch", text)
        self.assertIn("pull_request", text)
        self.assertIn("contents: read", text)
        self.assertIn("SHA256SUMS.txt", text)
        self.assertIn("archive.testzip()", text)
        self.assertIn("Packaged README contains broken local links", text)
        self.assertIn("CHANGELOG.md CONTRIBUTING.md", text)
        self.assertNotRegex(text, r"(?m)^\s*(?:gh release create|npm publish|git push)\b")

    def test_release_evidence_does_not_fabricate_agent_or_engine_pass(self):
        evidence = (ROOT / "docs/RELEASE-1.0-EVIDENCE.md").read_text(encoding="utf-8")
        self.assertIn("T08", evidence)
        self.assertIn("INCONCLUSIVE", evidence)
        self.assertIn("T10 is explicitly excluded", evidence)
        self.assertIn("engine import", evidence.lower())
        self.assertIn("NOT VERIFIED", evidence)
        self.assertIn("user release approval", evidence.lower())
        self.assertIn("scripts/compare_scene_baselines.py", evidence)

    def test_readme_source_local_links_resolve(self):
        source = (ROOT / "README.md").read_text(encoding="utf-8")
        links = re.findall(r'(?:\]\(|href="|src=")([^")]+)', source)
        relative = [x.split("#", 1)[0] for x in links
                    if not x.startswith(("http://", "https://", "#", "mailto:", "data:"))]
        missing = [x for x in relative if x and not (ROOT / x).is_file()]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
