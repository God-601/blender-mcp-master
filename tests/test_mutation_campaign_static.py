"""Check mutation-campaign definitions without executing Blender subprocesses."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN = ROOT / "tests" / "run_mutation_campaign.py"

class MutationCampaignStaticTests(unittest.TestCase):
    def test_mutants_have_real_unique_source_anchors_and_selected_tests(self):
        spec = importlib.util.spec_from_file_location("mutation_campaign", CAMPAIGN)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        mutants = module.MUTANTS
        self.assertEqual(len(mutants), 15)
        self.assertEqual(len(set(item["id"] for item in mutants)), 15)
        self.assertEqual(sum(item["kind"] == "claude-previous-survivor" for item in mutants), 9)
        for mutant in mutants:
            with self.subTest(mutant=mutant["id"]):
                source = (ROOT / mutant["file"]).read_text(encoding="utf-8")
                self.assertEqual(source.count(mutant["old"]), 1)
                self.assertNotEqual(mutant["new"], mutant["old"])
                compile(source.replace(mutant["old"], mutant["new"], 1),
                        mutant["file"], "exec")
                self.assertTrue(mutant["tests"])
                self.assertTrue(all("." in name for name in mutant["tests"]))

    def test_campaign_never_edits_original_source(self):
        text = CAMPAIGN.read_text(encoding="utf-8")
        self.assertIn("TemporaryDirectory", text)
        self.assertIn('shutil.copytree(source / "scripts"', text)
        self.assertIn('shutil.copytree(source / "tests"', text)
        self.assertTrue((ROOT / "tests" / "run_mutation_subset.py").is_file())
