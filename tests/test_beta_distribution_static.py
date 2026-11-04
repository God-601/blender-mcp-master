import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class BetaDistributionTests(unittest.TestCase):
    def test_version_and_documentation(self):
        manifest=json.loads((ROOT/"package.json").read_text())
        lock=json.loads((ROOT/"package-lock.json").read_text())
        self.assertEqual(manifest["version"],"1.2.0")
        self.assertEqual(lock["version"],manifest["version"])
        self.assertEqual(lock["packages"][""]["version"],manifest["version"])
        for name in ("docs/QUICKSTART.md","CHANGELOG.md",
                     "docs/ECOSYSTEM-COMPARISON.md",
                     "references/workflow-director.md",
                     "references/skill-evaluation-protocol.md"):
            self.assertTrue((ROOT/name).exists(),name)
        skill=(ROOT/"SKILL.md").read_text()
        self.assertIn("references/workflow-director.md",skill)
        self.assertIn("references/skill-evaluation-protocol.md",skill)

    def test_legacy_beta_flow_and_stable_release_guards(self):
        workflow=(ROOT/".github/workflows/release.yml").read_text()
        for phrase in ("gh release create","SHA256SUMS.txt",
                       "npm pack","zip -q -r","npm publish",
                       "NPM_TOKEN_SET","--prerelease"):
            self.assertIn(phrase,workflow)
        stable=(ROOT/".github/workflows/release-stable-1.0.yml").read_text()
        for phrase in ("workflow_run:", "head_sha", "RELEASE_SHA",
                       "Static checks", "1.0 readiness preflight (NO RELEASE)",
                       "npm package checks", "docs/release-notes-1.0.md",
                       "scripts/clean_install_smoke.py", "gh release create",
                       "--latest", "npm publish", "NPM_TOKEN_SET"):
            self.assertIn(phrase,stable)

if __name__=="__main__":
    unittest.main()
