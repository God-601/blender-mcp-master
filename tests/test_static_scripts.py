"""Static checks for repository scripts; these do not replace Blender runtime tests."""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryStaticChecks(unittest.TestCase):
    def test_scripts_parse_as_python(self):
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        self.assertTrue(scripts, "No Python scripts found")
        for path in scripts:
            with self.subTest(script=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_readme_documents_skills_cli_and_both_languages(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("npx skills add God-601/blender-mcp-master", readme)
        self.assertIn("# Português", readme)
        self.assertIn("# blender-mcp-master", readme)

    def test_validator_reports_incomplete_target_selection(self):
        source = (ROOT / "scripts" / "validate_asset.py").read_text(encoding="utf-8")
        self.assertIn("INCOMPLETE - CHECK TARGETS", source)
        self.assertIn("MISSING_TARGETS", source)

    def test_lod_script_does_not_delete_existing_lods_automatically(self):
        source = (ROOT / "scripts" / "make_lods.py").read_text(encoding="utf-8")
        self.assertIn("existing scene objects are never deleted automatically", source)
        self.assertIn("for modifier in list(lod.modifiers)", source)


if __name__ == "__main__":
    unittest.main()
