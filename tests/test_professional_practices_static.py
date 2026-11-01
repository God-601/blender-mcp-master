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


    def test_clarification_is_p0_and_avoids_reasking_known_details(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        gate = (ROOT / "references" / "clarification-gate.md").read_text(encoding="utf-8")
        playbook = (ROOT / "references" / "professional-agent-playbook.md").read_text(encoding="utf-8")
        standards = (ROOT / "references" / "professional-modeling-standards.md").read_text(encoding="utf-8")
        self.assertIn("references/clarification-gate.md", skill)
        self.assertIn("CLARIFY ->", skill)
        self.assertIn("Clarify before you build", skill)
        self.assertIn("Priority: P0", gate)
        for term in ("BLOCKER", "QUALITY-RISK", "OPTIONAL", "before modeling",
                     "already supplied", "one focused question", "choose for me"):
            self.assertIn(term.lower(), gate.lower())
        self.assertIn("Clarify (P0)", playbook)
        self.assertIn("P0 clarification gate", standards)

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
