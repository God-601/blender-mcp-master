"""Static contract for the professional modeling agent skill."""
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ProfessionalPracticesStaticTests(unittest.TestCase):
    def test_blender_inspector_parses_and_does_not_mutate_scene(self):
        content = (ROOT / "scripts" / "inspect_geometry.py").read_text(encoding="utf-8")
        tree = ast.parse(content)
        self.assertIn("to_mesh_clear()", content)
        self.assertNotIn("bpy.ops.", content)
        self.assertNotIn("bpy.data.objects.remove", content)
        self.assertNotIn("bpy.ops.wm.save", content)
        self.assertTrue(any(isinstance(node, ast.FunctionDef) and node.name == "inspect_mesh"
                            for node in tree.body))

    def test_professional_guides_are_routed_and_truthful(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for guide in ("professional-modeling-standards.md",
                      "modeling-decision-framework.md",
                      "professional-agent-playbook.md",
                      "production-recipes.md"):
            self.assertTrue((ROOT / "references" / guide).is_file())
            self.assertIn(guide, skill)
        self.assertIn("scripts/inspect_geometry.py", skill)
        text = (ROOT / "references" / "professional-modeling-standards.md").read_text(encoding="utf-8")
        for phrase in ("NOT VERIFIED", "signed volume", "AABB", "evaluated"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
