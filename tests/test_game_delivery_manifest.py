"""Pure Python tests for authored game budgets and actual-engine receipt boundaries."""
import importlib.util
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "game_delivery_manifest.py"


def load():
    spec = importlib.util.spec_from_file_location("game_delivery_manifest", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record():
    return {"asset": "Tree", "destination": "GODOT",
            "technical": {"triangles": 1800, "material_slots": 2, "texture_bytes": 1024},
            "limits": {"max_triangles": 2000, "max_material_slots": 3,
                       "max_texture_bytes": 2048},
            "import_receipt": {"engine": "GODOT", "engine_version": "4.4.1",
                               "asset_sha256": "a" * 64,
                               "evidence_path": "logs/godot-import.txt",
                               "import_status": "IMPORTED_GEOMETRY"}}


class DeliveryTests(unittest.TestCase):
    def test_matching_receipt_never_certifies_engine_without_log(self):
        r = load().evaluate(record())
        self.assertEqual(r["import_receipt_status"], "REVIEW_RECEIPT")
        self.assertEqual(r["real_engine_import_certified"], "NOT VERIFIED")
        self.assertEqual(r["overall_technical_budget_status"], "REVIEW")
        self.assertEqual(r["rendered_material_fidelity"], "NOT VERIFIED")

    def test_excess_triangles_are_issue_even_with_receipt(self):
        data = record()
        data["technical"]["triangles"] = 2200
        r = load().evaluate(data)
        self.assertEqual(r["budget_checks"]["triangles"]["status"], "ISSUE")
        self.assertEqual(r["overall_technical_budget_status"], "ISSUE")

    def test_wrong_engine_and_missing_evidence_never_certifies(self):
        data = record()
        data["import_receipt"]["engine"] = "ROBLOX"
        self.assertEqual(load().evaluate(data)["import_receipt_status"], "NOT VERIFIED")
        data["import_receipt"]["engine"] = "GODOT"
        data["import_receipt"].pop("evidence_path")
        self.assertEqual(load().evaluate(data)["import_receipt_status"], "NOT VERIFIED")

    def test_invalid_receipts_and_bool_budgets_fail_closed(self):
        data = record()
        data["technical"]["triangles"] = True
        with self.assertRaises(ValueError):
            load().evaluate(data)
        data = record()
        data["import_receipt"]["import_status"] = "PASS"
        with self.assertRaises(ValueError):
            load().evaluate(data)
        data = record()
        data["limits"]["max_triangles"] = 0
        with self.assertRaises(ValueError):
            load().evaluate(data)

    def test_missing_budgets_not_verified(self):
        data = record()
        data["limits"].pop("max_texture_bytes")
        self.assertEqual(load().evaluate(data)["budget_checks"]["texture_bytes"]["status"],
                         "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
