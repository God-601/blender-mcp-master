"""Guard the root Agent Skill's progressive-disclosure and safety contract."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CompactSkillEntrypointTests(unittest.TestCase):
    def test_root_skill_remains_bounded_without_dropping_core_guards(self):
        source = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(source.encode("utf-8")), 16000, "Root instructions should route; don't inline specialist manuals")
        for text in (
            "name: blender-mcp-master",
            "GENERAL KICKOFF",
            "multi-question design interview",
            "Do not repeat answered requirements",
            "CLARIFY ->",
            "Clarify before you build",
            "Avoid global orphan purges",
            "PASS", "ISSUE", "N/A", "NOT VERIFIED",
            "references/p0-integrity.md",
            "references/quality-checklist.md",
            "references/modeling-quality-loop.md",
            "references/token-efficient-agent-execution.md",
            "references/clarification-gate.md",
            "scripts/inspect_geometry.py",
            "scripts/asset_performance_audit.py",
        ):
            with self.subTest(text=text):
                self.assertIn(text, source)
        self.assertNotIn("bpy.data.orphans_purge", source)

    def test_all_reference_and_script_names_remain_discoverable(self):
        source = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for folder, ext in (("references", "*.md"), ("scripts", "*.py")):
            paths = sorted((ROOT / folder).glob(ext))
            for path in paths:
                with self.subTest(path=path.name):
                    self.assertIn(path.name, source)
        self.assertGreater(len(re.findall(r"references/[a-z0-9-]+\.md", source)), 45)
