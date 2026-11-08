"""Real PNG-to-report smoke for one-command visual correction audit."""
import json
import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "visual_iteration_audit.py"


def png(path, alphas):
    def chunk(kind, body):
        return (struct.pack(">I", len(body)) + kind + body +
                struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff))
    raw = bytearray()
    for row in (alphas[:2], alphas[2:]):
        raw.append(0)
        for alpha in row:
            raw.extend([220, 220, 220, alpha])
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" +
        chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0)) +
        chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    )


def make_files(folder):
    root = Path(folder)
    views = []
    for view in ("front", "side", "three_quarter"):
        png(root / (view + "_ref.png"), [255, 0, 0, 0])
        png(root / (view + "_before.png"), [0, 255, 0, 0])
        png(root / (view + "_after.png"), [255, 0, 0, 0])
        views.append({"view": view, "reference": view + "_ref.png",
                      "before": view + "_before.png", "after": view + "_after.png"})
    manifest = {"asset": "Sofa", "views": views}
    review = {
        "asset": "Sofa",
        "captures": [{"view": view, "artifact": view + "_after.png", "reviewer": "human"}
                     for view in ("front", "side", "three_quarter")],
        "defects": [],
    }
    def scene(fingerprint="a" * 64):
        return {
            "schema_version": 1,
            "scope": "explicit_protected_objects_selected_properties",
            "status": "MEASURED", "missing_names": [], "errors": [],
            "objects": [{"name": "USER_Source", "fingerprint_sha256": fingerprint}],
        }
    for name, data in (("manifest.json", manifest), ("review.json", review),
                       ("scene_before.json", scene()), ("scene_after.json", scene())):
        (root / name).write_text(json.dumps(data), encoding="utf-8")
    return root


def execute(folder):
    args = [sys.executable, str(SCRIPT), str(folder / "manifest.json"),
            "--evidence-root", str(folder), "--scene-before", str(folder / "scene_before.json"),
            "--scene-after", str(folder / "scene_after.json"),
            "--review", str(folder / "review.json")]
    result = subprocess.run(args, text=True, capture_output=True, check=True)
    return json.loads(result.stdout)


class VisualIterationEndToEndTests(unittest.TestCase):
    def test_real_pngs_improve_and_keep_source_but_still_require_art_review(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_files(folder)
            response = execute(root)
            self.assertEqual(response["result"]["status"], "REVIEW_REQUIRED")
            self.assertEqual(response["result"]["mean_iou_delta"], 1.0)
            self.assertEqual(response["source_provenance"]["scene_check"]["status"], "PASS")
            self.assertEqual(response["material_and_artistic_quality"], "NOT VERIFIED")
            self.assertEqual(len(response["result"]["compared_views"]), 3)

    def test_scene_mutation_blocks_correction_even_when_images_improve(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_files(folder)
            path = root / "scene_after.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["objects"][0]["fingerprint_sha256"] = "b" * 64
            path.write_text(json.dumps(data), encoding="utf-8")
            response = execute(root)
            self.assertEqual(response["result"]["status"], "ISSUE")
            self.assertIn("protected_scene_integrity_issue", response["result"]["reasons"])

    def test_missing_reference_image_reports_unverified(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_files(folder)
            (root / "front_ref.png").unlink()
            response = execute(root)
            self.assertEqual(response["status"], "NOT VERIFIED")
            self.assertIn("missing", response["error"].lower())

    def test_unresolved_visual_defect_not_silenced_by_iou(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_files(folder)
            path = root / "review.json"
            review = json.loads(path.read_text(encoding="utf-8"))
            review["defects"].append({
                "type": "shading", "severity": "critical",
                "object": "Sofa", "description": "normal map visibly inverted",
                "resolved": False,
            })
            path.write_text(json.dumps(review), encoding="utf-8")
            response = execute(root)
            self.assertEqual(response["result"]["status"], "ISSUE")
            self.assertIn("unresolved_visual_defects", response["result"]["reasons"])

    def test_unsafe_png_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = make_files(folder)
            path = root / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["views"][0]["before"] = "../escaped.png"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            response = execute(root)
            self.assertEqual(response["status"], "NOT VERIFIED")
            self.assertIn("unsafe", response["error"].lower())


if __name__ == "__main__":
    unittest.main()
