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
        self.assertEqual([s['module'] for s in plan['steps']], ['materials', 'uv', 'validation'])

    def test_invalid_task_is_rejected(self):
        for task in ({'category': 'unknown'}, {'category': 'hard_surface', 'needs': ['unknown']}, None):
            with self.assertRaises(ValueError):
                build_plan(task)
