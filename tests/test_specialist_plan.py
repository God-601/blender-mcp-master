from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from specialist_plan import build_plan, load_modules


class SpecialistPlanTests(unittest.TestCase):
    def test_registry_reuses_shipped_resources(self):
        modules = load_modules()
        self.assertEqual(set(modules), {'modeling', 'materials', 'uv', 'retopology', 'optimization', 'export', 'validation'})
        for module in modules.values():
            for path in module['guides'] + module['scripts']:
                self.assertTrue((ROOT / path).is_file(), path)

    def test_simple_task_stays_single_agent(self):
        plan = build_plan({'category': 'hard_surface'})
        self.assertEqual(plan['mode'], 'single')
        self.assertEqual([s['module'] for s in plan['steps']], ['modeling', 'validation'])
        self.assertEqual(plan['steps'][1]['depends_on'], ['modeling'])

    def test_complex_task_has_only_requested_specialists(self):
        plan = build_plan({'category': 'game_asset', 'destination': 'roblox', 'needs': ['uv', 'pbr', 'optimization', 'export']})
        self.assertEqual(plan['mode'], 'delegated')
        self.assertEqual([s['module'] for s in plan['steps']], ['modeling', 'uv', 'materials', 'optimization', 'export', 'validation'])
        self.assertEqual(plan['route']['loaded_reference_count'], 0)

    def test_material_edit_does_not_rebuild_geometry(self):
        plan = build_plan({'category': 'materials', 'needs': ['pbr', 'uv']})
        self.assertEqual([s['module'] for s in plan['steps']], ['uv', 'materials', 'validation'])

    def test_export_is_last_regardless_of_requirement_order(self):
        first = build_plan({'category': 'game_asset', 'needs': ['export', 'pbr', 'uv', 'optimization']})
        second = build_plan({'category': 'game_asset', 'needs': ['optimization', 'uv', 'pbr', 'export']})
        self.assertEqual(first['steps'], second['steps'])
        self.assertEqual(first['steps'][-2]['module'], 'export')

    def test_invalid_task_is_rejected(self):
        for task in ({'category': 'unknown'}, {'category': 'hard_surface', 'needs': ['unknown']}, None):
            with self.assertRaises(ValueError):
                build_plan(task)

    def test_task_specific_guides_reach_actual_specialist_steps(self):
        for category, expected in [('organic', 'references/organic.md'), ('architecture', 'references/modular-modeling.md'), ('character', 'references/character-rig.md')]:
            plan = build_plan({'category': category, 'needs': ['rigging', 'measure']})
            self.assertIn(expected, plan['steps'][0]['guides'])
            self.assertIn('references/topology-retopology.md', plan['steps'][0]['guides'])
            self.assertIn('references/measured-proportion-recipes.md', plan['steps'][0]['guides'])
