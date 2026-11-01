"""Validate the README SVG artwork contract without requiring a display or Blender."""
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SVG = "{http://www.w3.org/2000/svg}"


class VectorGraphicsTests(unittest.TestCase):
    def test_all_diagrams_have_valid_accessible_self_contained_svg(self):
        for file in sorted(ASSETS.glob("*.svg")):
            with self.subTest(asset=file.name):
                root = ET.parse(file).getroot()
                self.assertEqual(root.tag, SVG + "svg")
                self.assertTrue(root.attrib.get("viewBox"))
                self.assertTrue(root.find(SVG + "title") is not None)
                self.assertTrue(root.find(SVG + "desc") is not None)
                self.assertTrue(root.find(SVG + "title").text.strip())
                self.assertTrue(root.find(SVG + "desc").text.strip())
                self.assertNotIn("http://", file.read_text(encoding="utf-8").split("<defs>")[-1])
                for node in root.iter():
                    self.assertNotIn(node.tag.split("}")[-1], {"script", "foreignObject", "image"})
                    for attr, value in node.attrib.items():
                        self.assertNotIn("javascript:", value.lower())
                        self.assertNotIn("file:", value.lower())

    def test_readme_uses_current_artwork_and_discloses_illustration(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for name in ("banner.svg", "workflow.svg", "architecture.svg"):
            self.assertIn("assets/" + name, readme)
        self.assertIn("Concept illustration", readme)
        banner = (ASSETS / "banner.svg").read_text(encoding="utf-8")
        self.assertIn("without pretending it was produced by an AI agent", banner)
        self.assertIn("VECTOR STUDY", banner)
        self.assertGreater(banner.count("<polygon"), 8)

    def test_workflow_keeps_clarification_and_correction_loop(self):
        workflow = (ASSETS / "workflow.svg").read_text(encoding="utf-8")
        self.assertIn("CLARIFY", workflow)
        self.assertIn("INSPECT", workflow)
        self.assertIn("Correct and re-check", workflow)


if __name__ == "__main__":
    unittest.main()
