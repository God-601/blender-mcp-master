"""Static checks for repository scripts; these do not replace Blender runtime tests."""
from pathlib import Path
import ast
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RepositoryStaticChecks(unittest.TestCase):
    def test_scripts_parse_as_python(self):
        scripts = sorted((ROOT / "scripts").glob("*.py"))
        self.assertTrue(scripts, "No Python scripts found")
        for path in scripts:
            with self.subTest(script=path.name):
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    def test_readme_documents_manual_skill_setup_and_both_languages(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("SKILL.md", readme)
        self.assertIn("separate Blender-control MCP", readme)
        self.assertIn("# Português", readme)
        self.assertIn("# Blender MCP Master", readme)
        self.assertIn("references/quality-checklist.md", readme)
        # Install paths that users rely on must stay documented in both languages.
        self.assertGreaterEqual(readme.count("npx skills add God-601/blender-mcp-master"), 2)
        self.assertGreaterEqual(readme.count("github:God-601/blender-mcp-master"), 2)
        # The npm package is not on the registry, so the bare-name MCP config must not be advertised.
        self.assertNotIn('["-y", "blender-mcp-master"]', readme)

    def test_quality_checklist_is_referenced_and_statuses_match_core_skill(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        checklist = (ROOT / "references" / "quality-checklist.md").read_text(encoding="utf-8")
        self.assertIn("references/quality-checklist.md", readme)
        self.assertIn("references/quality-checklist.md", skill)
        for status in ("PASS", "ISSUE", "N/A", "NOT VERIFIED"):
            with self.subTest(status=status):
                self.assertIn(status, skill)
                self.assertIn(status, checklist)

    def test_skill_frontmatter_follows_agent_skills_limits(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        match = re.match(r"---\n(.*?)\n---\n", text, re.S)
        self.assertIsNotNone(match, "SKILL.md must start with YAML frontmatter")
        name = re.search(r"^name:\s*(.+)$", match.group(1), re.M).group(1).strip()
        description = re.search(r"^description:\s*(.+)$", match.group(1), re.M).group(1).strip()
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")
        self.assertLessEqual(len(name), 64)
        self.assertEqual(name, "blender-mcp-master")
        self.assertTrue(0 < len(description) <= 1024, f"description is {len(description)} chars")
        self.assertNotIn("<", description)
        self.assertNotIn(">", description)

    def test_documented_references_and_scripts_exist(self):
        documents = [ROOT / "SKILL.md", ROOT / "README.md", *sorted((ROOT / "references").glob("*.md"))]
        pattern = re.compile(r"(?<![\w/.-])((?:references|scripts)/[A-Za-z0-9_.-]+\.(?:md|py))")
        for document in documents:
            for target in sorted(set(pattern.findall(document.read_text(encoding="utf-8")))):
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((ROOT / target).is_file(), f"{document.name} mentions missing file {target}")

    def test_validator_reports_incomplete_target_selection(self):
        source = (ROOT / "scripts" / "validate_asset.py").read_text(encoding="utf-8")
        self.assertIn("INCOMPLETE - CHECK TARGETS", source)
        self.assertIn("MISSING_TARGETS", source)
        self.assertIn("INVALID_TARGETS", source)
        self.assertIn("target object is not a mesh", source)
        self.assertIn("falling back to all visible", source)

    def test_lod_script_does_not_delete_existing_lods_automatically(self):
        source = (ROOT / "scripts" / "make_lods.py").read_text(encoding="utf-8")
        self.assertIn("existing scene objects are never deleted automatically", source)
        self.assertIn("for modifier in list(lod.modifiers)", source)
        self.assertIn("def bounds_overlap", source)
        self.assertIn("place_lod_without_overlap", source)

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
        self.assertIn("temp_prefix", source)
        self.assertIn("shutil.rmtree", source)
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

    def test_optimizer_is_dry_run_and_backup_first(self):
        source = (ROOT / "scripts" / "optimize_mesh.py").read_text(encoding="utf-8")
        self.assertIn("APPLY = False", source)
        self.assertIn("BACKUP_COLLECTION", source)
        self.assertIn("backup_object(obj, backup_collection)", source)
        self.assertIn("shared mesh datablock", source)
        self.assertIn("shape keys present", source)
        self.assertIn("Faces classified as internal were NOT automatically deleted.", source)
        self.assertNotIn("orphans_purge", source)

    def test_optimization_guide_covers_visual_and_engine_tradeoffs(self):
        guide = (ROOT / "references" / "game-asset-optimization.md").read_text(encoding="utf-8")
        for phrase in ("Hidden and internal faces", "draw calls", "LOD", "Roblox-specific",
                       "silhouette", "shape keys", "dry-run"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase.lower(), guide.lower())


if __name__ == "__main__":
    unittest.main()
