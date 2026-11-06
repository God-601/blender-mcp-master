"""File-backed PNG silhouette comparator contract tests (stdlib only)."""
import importlib.util
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "reference_silhouette_compare.py"


def module():
    spec = importlib.util.spec_from_file_location("reference_silhouette_compare", SOURCE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def png(path, alphas):
    # 2x2 transparent / opaque, RGBA 8-bit, non-interlaced, filter=none
    def chunk(kind, raw):
        return struct.pack(">I", len(raw)) + kind + raw + struct.pack(">I", zlib.crc32(kind + raw) & 0xffffffff)
    raw = bytearray()
    for row in (alphas[:2], alphas[2:]):
        raw.append(0)
        for alpha in row:
            raw.extend((255, 255, 255, alpha))
    content = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    path.write_bytes(content)


class SilhouetteTests(unittest.TestCase):
    def test_identical_masks_have_one_iou_but_no_artistic_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            png(root / "ref.png", [0, 255, 255, 0])
            png(root / "model.png", [0, 255, 255, 0])
            r = module().compare_masks(root, [{"reference": "ref.png", "render": "model.png", "view": "front"}])
            self.assertEqual(r["results"][0]["silhouette_iou"], 1.0)
            self.assertEqual(r["artistic_quality"], "NOT VERIFIED")
            self.assertEqual(r["results"][0]["status"], "MEASURED_REVIEW_REQUIRED")

    def test_difference_is_measured_from_pixels(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            png(root / "a.png", [0, 255, 0, 0])
            png(root / "b.png", [0, 255, 255, 0])
            r = module().compare_masks(root, [{"reference": "a.png", "render": "b.png", "view": "side"}])
            self.assertEqual(r["results"][0]["silhouette_iou"], 0.5)

    def test_shape_proxy_finds_shifted_pixel_bounds(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            png(root / "a.png", [255, 0, 0, 0])
            png(root / "b.png", [0, 255, 0, 0])
            item = module().compare_masks(root, [
                {"reference": "a.png", "render": "b.png", "view": "front"}
            ])["results"][0]
            self.assertEqual(item["silhouette_iou"], 0)
            details = item["shape_difference"]
            self.assertEqual(details["centroid_shift_px"], [1.0, 0.0])
            self.assertEqual(details["bbox_differences_px"], [1, 0, 1, 0])
            self.assertEqual(details["disagreement_fraction"], 0.5)
            self.assertEqual(item["artistic_quality"], "NOT VERIFIED")

    def test_empty_foreground_masks_remain_unverified(self):
        detail = module()._shape_difference(bytearray([0]*4), bytearray([0]*4), (2,2))
        self.assertEqual(detail["status"], "NOT VERIFIED")

    def test_opaque_input_or_bad_chunk_refused(self):
        m = module()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            png(root / "a.png", [255, 255, 255, 255])
            with self.assertRaisesRegex(ValueError, "transparent"):
                m._png_alpha_mask(root / "a.png")
            png(root / "b.png", [0, 0, 255, 0])
            content = bytearray((root / "b.png").read_bytes())
            content[20] ^= 1
            (root / "b.png").write_bytes(content)
            with self.assertRaisesRegex(ValueError, "checksum"):
                m._png_alpha_mask(root / "b.png")

    def test_compressed_scanline_bomb_rejected_with_bounded_decode(self):
        m = module()
        with tempfile.TemporaryDirectory() as folder:
            # 2x2 claims 18 bytes of decoded RGBA scanlines; stream expands to
            # far more. Recomputing IDAT CRC ensures decompression is tested.
            root = Path(folder)
            signature = b"\\x89PNG\\r\\n\\x1a\\n"
            def chunk(kind, data):
                return (struct.pack(">I", len(data)) + kind + data
                        + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
            content = (signature
                       + chunk(b"IHDR", struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0))
                       + chunk(b"IDAT", zlib.compress(b"\\x00" * 200000))
                       + chunk(b"IEND", b""))
            image = root / "bomb.png"
            image.write_bytes(content)
            with self.assertRaisesRegex(ValueError, "exceeds cap"):
                m._png_alpha_mask(image)

    def test_path_traversal_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            png(root / "good.png", [0, 0, 255, 0])
            with self.assertRaises(ValueError):
                module().compare_masks(root, [{"reference": "../good.png", "render": "good.png", "view": "front"}])


if __name__ == "__main__":
    unittest.main()
