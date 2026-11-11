"""Pure contract checks; actual provider/Blender campaigns are opt-in."""
import importlib.util
from pathlib import Path
import unittest
import tempfile
import contextlib
import io
import subprocess
from types import SimpleNamespace
from unittest.mock import patch
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

    def test_benchmark_cache_rejects_changed_generation_or_log(self):
        module = load(ROOT / 'integrations/agents/production_benchmark.py')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generation, events = root / 'generation.json', root / 'provider.jsonl'
            generation.write_bytes(b'{"parameters":{}}')
            events.write_bytes(b'original events')
            previous = {'actual_prompt_sha256': 'match', 'model_requested': 'pinned',
                'effort_requested': 'medium', 'thread_id': 'actual', 'provider_usage': {'input_tokens': 3},
                'generation_sha256': module.digest(generation.read_bytes()),
                'provider_log_sha256': module.digest(events.read_bytes())}
            self.assertTrue(module.cached_generation_matches(root, previous, previous))
            generation.write_bytes(b'{"parameters":{"altered":1}}')
            self.assertFalse(module.cached_generation_matches(root, previous, previous))
            generation.write_bytes(b'{"parameters":{}}')
            events.write_bytes(b'altered events')
            self.assertFalse(module.cached_generation_matches(root, previous, previous))

    def test_retries_keep_old_results_in_archive_only(self):
        module = load(ROOT / 'integrations/agents/production_benchmark.py')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            blender = root / 'blender'
            blender.touch()
            args = SimpleNamespace(output=str(root / 'campaign'), blender=str(blender), workers=1,
                model='first-model', effort='medium', timeout=1)
            generation = {'parameters': {name: (limits[0] + limits[1]) / 2
                          for name, limits in module.CASES['chair']['params'].items()}, 'rationale': 'test'}

            def subprocess_run(command, **kwargs):
                if command[0] == 'codex':
                    generation_path = Path(command[command.index('--output-last-message') + 1])
                    if args.model == 'first-model':
                        module.write_json(generation_path, generation)
                    for event in [{'type': 'thread.started', 'thread_id': args.model + generation_path.parent.name},
                                  {'type': 'turn.completed', 'usage': {'input_tokens': 4, 'output_tokens': 1}}]:
                        kwargs['stdout'].write(json.dumps(event) + '\n')
                elif args.model == 'first-model':
                    module.write_json(Path(command[-1]) / 'geometry.json', {'technical_status': 'PASS'})
                return subprocess.CompletedProcess(command, 0)

            with patch.dict(module.CASES, {'chair': module.CASES['chair']}, clear=True), \
                 patch.object(module.shutil, 'which', return_value='codex'), \
                 patch.object(module.subprocess, 'run', side_effect=subprocess_run), \
                 contextlib.redirect_stdout(io.StringIO()):
                module.run_campaign(args)
                args.model = 'second-model'
                module.run_campaign(args)
            summary = json.loads((Path(args.output) / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual(summary['archived_attempts'], 6)
            for arm in ('baseline', 'with_skill'):
                self.assertEqual(summary['arms'][arm]['failures'], 3)
                self.assertEqual(summary['arms'][arm]['completed'], 0)
                self.assertIsNone(summary['arms'][arm]['median_provider_plus_blender_seconds'])
