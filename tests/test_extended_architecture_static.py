"""Static guards for the new architecture scripts and documentation routes."""
import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPTS = [
    "mesh_operations.py",
    "hard_surface_builder.py",
    "geometry_nodes_builder.py",
    "organic_tree_builder.py",
    "inspection_report.py",
    "localized_correction.py",
    "technique_history.py",
    "technique_history_query.py",
    "technique_feedback.py",
    "capability_probe.py",
    "benchmark_report.py",
]


class ExtendedArchitectureStaticTests(unittest.TestCase):
    def test_new_scripts_parse_without_importing_blender(self):
        for filename in SCRIPTS:
            path = ROOT / "scripts" / filename
            with self.subTest(script=filename):
                source = path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(path))

    def test_every_new_script_is_routed_from_skill(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for filename in SCRIPTS:
            with self.subTest(script=filename):
                self.assertIn(filename, skill)

    def test_new_reference_modules_exist_and_are_routed(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for filename in ("agent-compatibility.md", "benchmark-prompts.md"):
            with self.subTest(reference=filename):
                self.assertTrue((ROOT / "references" / filename).is_file())
                self.assertIn(filename, skill)

    def test_agent_matrix_does_not_claim_unverified_clients_as_supported(self):
        matrix = (ROOT / "references" / "agent-compatibility.md").read_text(encoding="utf-8")
        for client in ("Codex", "Claude Desktop", "Cursor", "OpenCode", "Kilo Code"):
            with self.subTest(client=client):
                self.assertIn(client + " | NOT VERIFIED", matrix)


if __name__ == "__main__":
    unittest.main()
