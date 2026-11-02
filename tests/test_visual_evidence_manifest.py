"""Actual file-backed review receipts: SHA, missing captures, and safe path checks."""
import ast
import base64
import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "visual_evidence_manifest.py"
PNG1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/iZkAAAAASUVORK5CYII="
)


def run_report(root, captures):
    script = SCRIPT.read_text(encoding="utf-8")
    for key, value in (("EVIDENCE_ROOT", str(root)), ("CAPTURES", captures)):
        script, n = re.subn(r"^" + key + r" = .*",
                            lambda _: key + " = " + repr(value),
                            script, count=1, flags=re.M)
        assert n == 1
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        exec(compile(script, str(SCRIPT), "exec"), {"__name__": "__main__"})
    return json.loads(output.getvalue().split("MCP_VISUAL_EVIDENCE_BEGIN\n", 1)[1]
                      .split("\nMCP_VISUAL_EVIDENCE_END", 1)[0])


class FileBackedVisualEvidenceTests(unittest.TestCase):
    def test_readonly_and_no_default_folder_scan(self):
        source = SCRIPT.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertIn('EVIDENCE_ROOT = ""', source)
        self.assertIn("CAPTURES = []", source)
        self.assertNotIn("bpy.ops", source)
        self.assertNotIn("unlink(", source)
        self.assertNotIn("write_bytes(", source)
        self.assertEqual(run_report("", [])["status"], "NOT VERIFIED")

    def test_hashes_three_real_named_files_but_never_certifies_art_quality(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            captures = []
            for view in ("front", "side", "three_quarter"):
                (root / (view + ".png")).write_bytes(PNG1X1)
                captures.append({"view": view, "file": view + ".png", "reviewer": "TestReviewer"})
            report = run_report(root, captures)
            self.assertEqual(report["status"], "FILES_HASHED_REVIEW_REQUIRED")
            self.assertEqual(report["missing_views"], [])
            self.assertEqual(len(report["captures"]), 3)
            self.assertEqual(report["actual_visual_quality"], "NOT VERIFIED")
            self.assertTrue(all(len(x["sha256"]) == 64 for x in report["captures"]))
            self.assertEqual((root / "front.png").read_bytes(), PNG1X1)

    def test_missing_image_invalid_header_and_traversal_are_never_verified(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "front.png").write_bytes(b"not a real image file"*4)
            for filename in ("front.png", "missing.png", "../outside.png"):
                capture = [{"view": "front", "file": filename, "reviewer": "Reviewer"}]
                result = run_report(root, capture)
                self.assertEqual(result["status"], "NOT VERIFIED")
                self.assertTrue(result["errors"])

    def test_short_and_unreviewed_capture_does_not_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "front.png").write_bytes(PNG1X1)
            result = run_report(root, [{"view": "front", "file": "front.png", "reviewer": ""}])
            self.assertEqual(result["status"], "NOT VERIFIED")
            self.assertTrue(result["errors"])
            result = run_report(root, [{"view": "front", "file": "front.png", "reviewer": "human"}])
            self.assertEqual(result["missing_views"], ["side", "three_quarter"])
            self.assertEqual(result["status"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
