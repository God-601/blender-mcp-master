"""Pure contract checks; actual provider/Blender campaigns are opt-in."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
import json

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AcceptanceHelperTests(unittest.TestCase):
    def test_requested_model_is_pinned_and_generation_reuse_checks_it(self):
        module = load(ROOT / 'integrations/agents/production_benchmark.py')
        command = module.provider_command('codex', Path('trial'), 'gpt-6.1-sol', 'medium')
        self.assertEqual(command[command.index('--model') + 1], 'gpt-6.1-sol')
        self.assertIn('model_reasoning_effort="medium"', command)
        previous = {'actual_prompt_sha256': 'same', 'model_requested': 'gpt-6.1-sol', 'effort_requested': 'medium', 'thread_id': 'actual', 'provider_usage': {'input_tokens': 3}}
        self.assertTrue(module.generation_matches(previous, dict(previous)))
        for key, value in [('model_requested', 'other'), ('effort_requested', 'high'), ('actual_prompt_sha256', 'changed')]:
            changed = dict(previous, **{key: value})
            self.assertFalse(module.generation_matches(previous, changed))

    def test_bounded_generation_contract_rejects_invalid_inputs(self):
        module = load(ROOT / 'integrations/agents/production_benchmark.py')
        module.self_check()

    def test_color_encoding_preserves_endpoints_and_known_midpoint(self):
        convert = load(ROOT / 'integrations/roblox/constant_pbr_fixture.py').linear_to_srgb
        self.assertEqual(convert(0), 0)
        self.assertAlmostEqual(convert(1), 1)
        self.assertAlmostEqual(convert(.5), .7353569830524495)
        for invalid in (-1, 2, float('nan')):
            with self.assertRaises(ValueError):
                convert(invalid)

    def test_changed_fixture_or_scene_bytes_cannot_reuse_canonical_source(self):
        module = load(ROOT / 'integrations/agents/production_benchmark.py')
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'fixture.blend'
            path.write_bytes(b'controlled fixture')
            spec = {'source': None}
            path.with_suffix('.input.json').write_text(json.dumps({'fixture_sha256': module.digest(spec), 'blend_sha256': module.digest(path.read_bytes())}), encoding='utf-8')
            module.check_shared_fixture(path, spec)
            with self.assertRaises(ValueError):
                module.check_shared_fixture(path, {'source': 'changed'})
            path.write_bytes(b'changed file')
            with self.assertRaises(ValueError):
                module.check_shared_fixture(path, spec)
