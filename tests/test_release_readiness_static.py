"""Stable 1.0 publication must be manually authorized and evidence-grounded."""
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path
from textwrap import dedent

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

    @unittest.skipUnless(all(shutil.which(tool) for tool in ("bash", "zip", "sha256sum")),
                         "Requires the release runner's shell and ZIP utilities")
    def test_readiness_zip_excludes_python_caches_even_on_rebuild(self):
        workflow = (ROOT / ".github/workflows/release-readiness.yml").read_text(encoding="utf-8")
        build = workflow.split("- name: Build and verify standalone nonpublishing readiness ZIP\n", 1)[1]
        script = dedent(build.split("        run: |\n", 1)[1].split("\n      - ", 1)[0])
        name = "blender-mcp-master-test-PREFLIGHT-NOT-A-RELEASE.zip"
        with tempfile.TemporaryDirectory() as directory:
            checkout = Path(directory)
            for source in ("SKILL.md", "README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md"):
                shutil.copyfile(ROOT / source, checkout / source)
            for source in ("references", "scripts", "integrations", "assets", "docs"):
                shutil.copytree(ROOT / source, checkout / source)
            cache = checkout / "integrations/agents/__pycache__"
            cache.mkdir(exist_ok=True)
            (cache / "metadata.txt").touch()
            (checkout / "scripts/stale.pyc").touch()
            (checkout / "scripts/optimized.pyo").touch()
            archive = checkout / "dist" / name
            archive.parent.mkdir()
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("blender-mcp-master/scripts/previous-build.pyc", "stale bytecode")

            subprocess.run(["bash", "-ec", script], cwd=checkout,
                           env={**os.environ, "PREFLIGHT_NAME": name}, check=True, timeout=30)

            with zipfile.ZipFile(archive) as zf:
                names = zf.namelist()
            self.assertIn("blender-mcp-master/scripts/scene_baseline_snapshot.py", names)
            self.assertEqual([entry for entry in names if "__pycache__" in entry.split("/")
                              or entry.endswith((".pyc", ".pyo"))], [])

    def test_stable_v1_release_is_one_time_and_pinned_to_published_sha(self):
        source = (ROOT / ".github/workflows/release-stable-1.0.yml").read_text(encoding="utf-8")
        self.assertIn("github.event.workflow_run.head_sha == '30a7f65ea0c070a70be26f63fc5c2eaf0f987147'", source)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", source)
        self.assertIn("gh release create", source)
        self.assertIn("Tag exists at a DIFFERENT SHA", source)

    def test_stable_v11_has_exact_sha_ci_and_clean_zip_gates(self):
        source = (ROOT / ".github/workflows/release-stable-1.1.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_run:", source)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", source)
        self.assertIn("github.event.workflow_run.head_sha == '9b4a120c59a40e1db1cdb22d925dd62cb565451e'", source)
        self.assertIn('MAIN_SHA', source)
        self.assertIn('RELEASE_SHA', source)
        self.assertIn('p.version !== "1.1.0"', source)
        self.assertIn("Release readiness preflight (NO RELEASE)", source)
        self.assertIn("npm package checks", source)
        self.assertIn("for retry in $(seq 1 18)", source)
        self.assertIn("scripts/clean_install_smoke.py", source)
        self.assertIn("docs/release-notes-1.1.md", source)
        self.assertIn("Tag exists at a DIFFERENT SHA", source)

    def test_stable_v12_release_requires_exact_main_ci_and_zip_smoke(self):
        workflow = (ROOT / ".github/workflows/release-stable-1.2.yml").read_text(encoding="utf-8")
        for item in ("workflow_run:", "github.event.workflow_run.conclusion == 'success'",
                     "RELEASE_SHA", "MAIN_SHA", 'p.version !== "1.2.0"',
                     "l.version !== \"1.2.0\"", "npm package checks",
                     "Release readiness preflight (NO RELEASE)", "for retry in $(seq 1 18)",
                     "scripts/clean_install_smoke.py", "docs/release-notes-1.2.md",
                     "docs/RELEASE-1.2-EVIDENCE.md", "gh release create",
                     "Tag exists at a DIFFERENT SHA"):
            self.assertIn(item, workflow)
        self.assertIn("github.event.workflow_run.head_sha == 'dae006042b5274de8dce83268cb66870dae868bf'", workflow)

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
