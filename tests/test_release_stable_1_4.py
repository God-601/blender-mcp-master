"""v1.4 GitHub release must be authorized, exact-SHA-gated and non-npm."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StableReleaseV14Tests(unittest.TestCase):
    def test_manifest_and_lock_versions_match(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package["version"], "1.4.0")
        self.assertEqual(lock["version"], "1.4.0")
        self.assertEqual(lock["packages"][""]["version"], "1.4.0")

    def test_release_is_exact_commit_after_successful_real_CI(self):
        source = (ROOT / ".github/workflows/release-stable-1.4.yml").read_text(encoding="utf-8")
        for name in (
            "workflow_run:", "github.event.workflow_run.event == 'push'",
            "github.event.workflow_run.conclusion == 'success'",
            'RELEASE_SHA:', 'VERSION: \'1.4.0\'', 'TAG: \'v1.4.0\'',
            "test \"$(git rev-parse HEAD)\" = \"$RELEASE_SHA\"",
            "Release readiness preflight (NO RELEASE)",
            "npm package checks", "Real Godot 4 GLB importer smoke",
            "gh release create", "--notes-file docs/release-notes-1.4.md",
            "SHA256SUMS.txt", "scripts/clean_install_smoke.py",
            "integrations/roblox/studio_mesh_audit.lua",
            "integrations/godot/gltf_import_probe.gd",
        ):
            with self.subTest(required=name):
                self.assertIn(name, source)
        self.assertIn("contents: write", source)
        self.assertNotRegex(source, r"(?m)^\\s*npm publish\\b")
        self.assertNotIn("NODE_AUTH_TOKEN", source)

    def test_release_claims_do_not_overstate_user_observation(self):
        notes = (ROOT / "docs/release-notes-1.4.md").read_text(encoding="utf-8")
        self.assertIn("user-reported", notes)
        self.assertIn("not independently verified", notes.lower())
        self.assertIn("3,860", notes)
        self.assertIn("Godot", notes)
        self.assertIn("No npm registry publication", notes)


if __name__ == "__main__":
    unittest.main()
