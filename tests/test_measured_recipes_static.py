"""Static checks keep recovered measurements as examples, not mandates."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MeasuredRecipeStaticTests(unittest.TestCase):
    def test_example_code_and_document_routes(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        docs = ("references/measured-proportion-recipes.md",
                "references/voxel-atlas-recipe.md")
        files = ("vehicle_proportion_example.py", "voxel_atlas_example.py",
                 "prop_proportion_example.py")
        for item in docs:
            self.assertIn(item, skill)
            self.assertTrue((ROOT / item).is_file())
        for name in files:
            with self.subTest(file=name):
                src = (ROOT / "scripts" / name).read_text(encoding="utf-8")
                compile(src, name, "exec")
                self.assertIn("scripts/" + name, skill)
                self.assertIn("OWNER_KEY", src)
                self.assertNotIn("bpy.ops.", src)

    def test_historical_source_and_configurability(self):
        old = "2bc6ab6841d28ea71aced74487481c5c5cce6ba5"
        hard = (ROOT / "references/measured-proportion-recipes.md").read_text(encoding="utf-8")
        vox = (ROOT / "references/voxel-atlas-recipe.md").read_text(encoding="utf-8")
        self.assertIn(old, hard)
        self.assertIn(old, vox)
        self.assertIn("not universal", vox.lower())
        self.assertIn("NOT VERIFIED", hard + vox)
        src = (ROOT / "scripts/voxel_atlas_example.py").read_text(encoding="utf-8")
        self.assertIn("GRID_UNIT = 0.28", src)
        self.assertIn("ATLAS_WIDTH = 64", src)
        self.assertIn("ATLAS_HEIGHT = 8", src)
        self.assertIn("if neighbor in occupied:", src)


if __name__ == "__main__":
    unittest.main()
