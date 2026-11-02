"""Static protection for the required first-contact modeling interview."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GeneralKickoffContractTests(unittest.TestCase):
    def test_skill_requires_a_new_project_general_open_question(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("GENERAL KICKOFF", skill)
        self.assertIn("even when the technical brief is complete", skill)
        self.assertIn("do not repeat answered requirements", skill)

    def test_clarification_gate_has_a_symmetric_minimal_interview(self):
        gate = (ROOT / "references" / "clarification-gate.md").read_text(encoding="utf-8")
        self.assertIn("GENERAL KICKOFF", gate)
        self.assertIn("one open-ended question", gate)
        self.assertIn("Before any scene mutation", gate)
        self.assertIn("continue the existing project", gate)
        self.assertIn("do not repeat answered requirements", gate)
        self.assertIn("BLOCKER", gate)
        self.assertIn("QUALITY-RISK", gate)
        self.assertIn("OPTIONAL", gate)

    def test_evaluation_protocol_differentiates_questions_from_redundancy(self):
        evaluation = (ROOT / "references" / "skill-evaluation-protocol.md").read_text(encoding="utf-8")
        self.assertIn("one nonredundant general kickoff question", evaluation)
        self.assertIn("repeated requirements", evaluation)
