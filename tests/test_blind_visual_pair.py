"""Reject receipts from the wrong experiment before preparing review images."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "integrations/agents/blind_visual_pair.py"
spec = importlib.util.spec_from_file_location("blind_visual_pair", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class BlindReceiptTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("PIL"), "visual packets require Pillow")
    def test_render_bytes_must_match_the_receipt(self):
        from PIL import Image

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            left, right = root / "baseline", root / "with_skill"
            for arm in (left, right):
                arm.mkdir()
                (arm / "common_task.txt").write_text("Build a chair")
                (arm / "scene_fixture.blend").write_bytes(b"shared input")
                hashes = {}
                for view in module.VIEWS:
                    path = arm / (view + ".png")
                    Image.new("RGB", (4, 4), "blue").save(path)
                    hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
                receipt = dict(arm=arm.name, case_id="chair", trial=1,
                               status="completed", artifact_hashes=hashes)
                (arm / "receipt.json").write_text(json.dumps(receipt))
            good = root / "good"
            module.prepare(left, right, good, ["Seat shape"])
            self.assertEqual(len(list((good / "review").glob("*.png"))), 6)
            path = right / "three_quarter.png"
            original = path.read_bytes()
            Image.new("RGB", (4, 4), "magenta").save(path)
            bad = root / "bad"
            with self.assertRaisesRegex(ValueError, "three_quarter.png"):
                module.prepare(left, right, bad, ["Seat shape"])
            self.assertFalse(bad.exists())
            path.write_bytes(original)
            del receipt["artifact_hashes"][path.name]
            (right / "receipt.json").write_text(json.dumps(receipt))
            with self.assertRaisesRegex(ValueError, "three_quarter.png"):
                module.prepare(left, right, bad, ["Seat shape"])
            self.assertFalse(bad.exists())

    def test_mismatched_pairs_leave_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            left, right, packet = root / "left", root / "right", root / "packet"
            left.mkdir()
            right.mkdir()
            base = dict(arm="baseline", case_id="chair", trial=1, status="completed")
            (left / "receipt.json").write_text(json.dumps(base))
            for changes in (dict(arm="baseline"), dict(case_id="table"), dict(trial=2),
                            dict(status="failed"), dict(trial=True), dict(case_id=None)):
                with self.subTest(changes=changes):
                    record = dict(base, arm="with_skill")
                    record.update(changes)
                    (right / "receipt.json").write_text(json.dumps(record))
                    with self.assertRaises(ValueError):
                        module.prepare(left, right, packet, ["Seat shape"])
                    self.assertFalse(packet.exists())
