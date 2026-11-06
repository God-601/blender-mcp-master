"""Regression guards for pre-v2 runtime support and distribution consistency."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PreV2DistributionTests(unittest.TestCase):
    def test_node_engine_does_not_understate_transitive_requirement(self):
        package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        lock = json.loads((ROOT / "package-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(package["engines"]["node"], ">=20")
        self.assertEqual(lock["packages"][""]["engines"]["node"], ">=20")
        deps = lock["packages"]
        self.assertIn("node_modules/@hono/node-server", deps)
        self.assertIn(">=20", deps["node_modules/@hono/node-server"]["engines"]["node"])

    def test_preflight_zip_contains_engine_probe_not_only_npm_package(self):
        src = (ROOT / ".github" / "workflows" / "release-readiness.yml").read_text(encoding="utf-8")
        self.assertIn("references scripts integrations assets docs", src)
        self.assertIn('"integrations/godot/gltf_import_probe.gd"', src)
        self.assertIn('"integrations/godot/README.md"', src)
        self.assertTrue((ROOT / "integrations" / "godot" / "gltf_import_probe.gd").is_file())

    def test_readiness_artifact_uses_actual_package_version_not_old_v12_label(self):
        src = (ROOT / ".github" / "workflows" / "release-readiness.yml").read_text(encoding="utf-8")
        self.assertIn('VERSION="$(node -p', src)
        self.assertIn('PREFLIGHT_NAME=blender-mcp-master-', src)
        self.assertIn('os.environ["PREFLIGHT_NAME"]', src)
        self.assertIn('dist/*-PREFLIGHT-NOT-A-RELEASE.zip', src)
        self.assertNotIn('blender-mcp-master-1.2-PREFLIGHT-NOT-A-RELEASE.zip', src)
        for required in ("pbr_channel_audit.py", "game_delivery_manifest.py",
                         "specialist_review_gate.py", "benchmark_suite_summary.py",
                         "release_gate_report.py"):
            self.assertIn(required, src)

    def test_png_decoder_has_decompression_and_flush_limits(self):
        src = (ROOT / "scripts" / "reference_silhouette_compare.py").read_text(encoding="utf-8")
        self.assertIn("inflater.flush(max(1, required + 1 - len(raw)))", src)
        self.assertIn("inflater.unused_data", src)


if __name__ == "__main__":
    unittest.main()
