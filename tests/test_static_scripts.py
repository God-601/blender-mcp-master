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
        self.assertIn("INVALID_TARGETS", source)
        self.assertIn("target object is not a mesh", source)

    def test_lod_script_does_not_delete_existing_lods_automatically(self):
        source = (ROOT / "scripts" / "make_lods.py").read_text(encoding="utf-8")
        self.assertIn("existing scene objects are never deleted automatically", source)
        self.assertIn("for modifier in list(lod.modifiers)", source)

    def test_cleanup_skips_shared_mesh_data_by_default(self):
        source = (ROOT / "scripts" / "cleanup_mesh.py").read_text(encoding="utf-8")
        self.assertIn("ALLOW_SHARED_MESH_DATA = False", source)
        self.assertIn("SKIP: mesh data is shared", source)

    def test_pbr_script_tags_generated_nodes_and_replaces_texture_links(self):
        source = (ROOT / "scripts" / "pbr_material.py").read_text(encoding="utf-8")
        self.assertIn('node.get("_blender_mcp_generated", False)', source)
        self.assertIn('n["_blender_mcp_generated"] = True', source)
        self.assertIn("replace_input_link", source)


    def test_scripts_never_use_systemexit(self):
        # SystemExit is a BaseException: MCP executors that catch Exception would not handle it.
        for path in sorted((ROOT / "scripts").glob("*.py")):
            with self.subTest(script=path.name):
                self.assertNotIn("SystemExit", path.read_text(encoding="utf-8"))

    def test_export_script_restores_state_in_finally(self):
        source = (ROOT / "scripts" / "export_asset.py").read_text(encoding="utf-8")
        self.assertIn("finally:", source)
        self.assertNotIn("INCLUDE_ARMATURE", source)


    def test_docs_do_not_promise_a_fail_level_the_validator_never_emits(self):
        validator = (ROOT / "scripts" / "validate_asset.py").read_text(encoding="utf-8")
        self.assertNotIn('"FAIL"', validator)
        for name in ("SKILL.md", "references/modeling-quality-loop.md", "assets/workflow.svg"):
            with self.subTest(doc=name):
                text = (ROOT / name).read_text(encoding="utf-8").replace("INCOMPLETE", "")
                self.assertNotIn("FAIL", text)

    def test_budgets_are_not_described_as_universal_hard_limits(self):
        text = (ROOT / "references" / "budgets.md").read_text(encoding="utf-8")
        self.assertNotIn("Treat them as hard limits", text)
        self.assertIn("Platform limits", text)

    def test_no_script_calls_orphans_purge(self):
        for path in sorted((ROOT / "scripts").glob("*.py")):
            with self.subTest(script=path.name):
                self.assertNotIn("orphans_purge", path.read_text(encoding="utf-8"))

    def test_skill_does_not_recommend_global_orphan_purge(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("bpy.data.orphans_purge", skill)
        self.assertIn("Avoid global orphan purges", skill)

    def test_github_actions_checkouts_do_not_persist_credentials(self):
        workflow = (ROOT / ".github" / "workflows" / "static-checks.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("persist-credentials: false"), 2)
        self.assertEqual(workflow.count("contents: read"), 2)


if __name__ == "__main__":
    unittest.main()
