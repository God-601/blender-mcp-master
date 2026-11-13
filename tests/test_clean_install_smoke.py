"""Regression coverage for installing the ZIP in a truly isolated temporary home."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "clean_install_smoke.py"


def load():
    spec = importlib.util.spec_from_file_location("blender_master_smoke", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CleanInstallSmokeTests(unittest.TestCase):
    def test_rejects_incorrect_checksum(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            archive = folder / "archive.zip"
            archive.write_bytes(b"ZIP test fixture")
            sums = folder / "SHA256SUMS.txt"
            sums.write_text("0" * 64 + "  archive.zip\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "mismatch"):
                mod.checked_hash(archive, sums)

    def test_rejects_duplicate_archive_entries_and_traversal(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "bad.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("blender-mcp-master/../escape.txt", "wrong")
            with zipfile.ZipFile(archive) as zf:
                with self.assertRaisesRegex(ValueError, "Unsafe ZIP"):
                    mod.validate_members(zf)
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("blender-mcp-master/a", "a")
                zf.writestr("blender-mcp-master/a", "b")
            with zipfile.ZipFile(archive) as zf:
                with self.assertRaisesRegex(ValueError, "Duplicate ZIP"):
                    mod.validate_members(zf)

    def test_rejects_python_caches_before_extraction(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory) / "cached.zip"
            for name in ("scripts/__pycache__/", "scripts/__pycache__/metadata.txt",
                         "integrations/agents/legacy.pyc", "scripts/optimized.pyo"):
                with self.subTest(name=name):
                    with zipfile.ZipFile(archive, "w") as zf:
                        for required in mod.REQUIRED:
                            zf.writestr("blender-mcp-master/" + required, "")
                        zf.writestr("blender-mcp-master/" + name, "")
                    with zipfile.ZipFile(archive) as zf:
                        with self.assertRaisesRegex(ValueError, "Python cache ZIP member"):
                            mod.validate_members(zf)

    def test_clean_home_install_from_newly_built_zip(self):
        mod = load()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            archive = folder / "clean-install-sample.zip"
            checksums = folder / "SHA256SUMS.txt"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zf:
                for name in ("SKILL.md", "README.md", "LICENSE",
                             "CHANGELOG.md", "CONTRIBUTING.md"):
                    zf.write(ROOT / name, "blender-mcp-master/" + name)
                for dirname in ("docs", "references", "scripts", "integrations", "assets"):
                    for source in sorted((ROOT / dirname).rglob("*")):
                        if (source.is_file() and "__pycache__" not in source.parts
                                and source.suffix not in (".pyc", ".pyo")):
                            zf.write(source, "blender-mcp-master/" +
                                     source.relative_to(ROOT).as_posix())
            checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
            checksums.write_text(checksum + "  " + archive.name + "\n",
                                 encoding="utf-8")
            report = mod.smoke(archive, checksums)
            self.assertEqual(report["result"], "PASS")
            self.assertEqual(report["sha256"], checksum)
            self.assertEqual(report["protected_object_helper"], "PASS")
            self.assertEqual(report["specialist_planning"], "PASS")
            self.assertGreater(report["python_scripts_parsed"], 20)
            self.assertEqual(report["actual_agent_discovery"], "NOT VERIFIED")
            self.assertEqual(report["live_blender_mcp_connection"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
