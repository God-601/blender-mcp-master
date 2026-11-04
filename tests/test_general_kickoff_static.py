"""Static protection for the required first-contact modeling interview."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GeneralKickoffContractTests(unittest.TestCase):
    def test_skill_requires_adaptive_multi_question_design_interview(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("GENERAL KICKOFF", skill)
        self.assertIn("multi-question design interview", skill)
        self.assertIn("several meaningful, nonredundant questions", skill)
        self.assertIn("Do not repeat answered requirements", skill)
        self.assertIn("posso seguir?", skill)
        self.assertIn("do not repeat answered requirements", skill)

    def test_clarification_gate_has_real_questions_not_permission_prompt(self):
        gate = (ROOT / "references" / "clarification-gate.md").read_text(encoding="utf-8")
        self.assertIn("GENERAL KICKOFF", gate)
        self.assertIn("4–6", gate)
        self.assertIn("2–3", gate)
        self.assertIn("Never ask", gate)
        self.assertIn("silhouette", gate.lower())
        self.assertIn("materials", gate.lower())
        self.assertIn("Before any scene mutation", gate)
        self.assertIn("continue the existing project", gate)
        self.assertIn("do not repeat answered requirements", gate)
        self.assertIn("BLOCKER", gate)
        self.assertIn("QUALITY-RISK", gate)
        self.assertIn("OPTIONAL", gate)

    def test_evaluation_protocol_differentiates_questions_from_redundancy(self):
        evaluation = (ROOT / "references" / "skill-evaluation-protocol.md").read_text(encoding="utf-8")
        self.assertIn("multiple specific unanswered artistic/functional questions", evaluation)
        self.assertIn("repeated requirements", evaluation)
