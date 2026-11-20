"""Reject receipts from the wrong experiment before preparing review images."""
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
