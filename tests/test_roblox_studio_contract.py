"""Roblox Studio verification aid is read-only and operator-driven."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StudioSmokeContractTests(unittest.TestCase):
    def test_operator_tool_never_mutates_or_claims_visual_pass(self):
        text = (ROOT / "integrations/roblox/studio_mesh_audit.lua").read_text(encoding="utf-8")
        self.assertIn('Selection', text)
        self.assertIn('GetDescendants()', text)
        self.assertIn('"MESHES_PRESENT_IN_STUDIO"', text)
        self.assertIn('"NOT VERIFIED"', text)
        for bad in ("InsertService:LoadAsset", "HttpService:PostAsync",
                    ":Destroy()", ".CanCollide =", ":PivotTo(", "AssetService:"):
            self.assertNotIn(bad, text)
        self.assertTrue((ROOT / "integrations/roblox/README.md").is_file())


if __name__ == "__main__":
    unittest.main()
