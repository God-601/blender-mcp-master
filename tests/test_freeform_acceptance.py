import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

SOURCE = Path(__file__).resolve().parents[1] / 'integrations/agents/freeform_acceptance.py'


class FreeformAcceptanceTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SOURCE.is_file(), 'Freeform acceptance runner is missing')
        spec = importlib.util.spec_from_file_location('freeform_acceptance', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_inside_rejects_live_blender_before_loading_inputs(self):
        module = self.module()
        with patch.dict('sys.modules', {'bpy': SimpleNamespace(app=SimpleNamespace(background=False))}):
            with self.assertRaisesRegex(RuntimeError, 'background Blender'):
                module.inside(None)

    def test_changed_code_cannot_reuse_approval(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'script.py'
            path.write_bytes(b'value = 1\n')
            approved = module.sha(path)
            self.assertEqual(module.approved_code(path, approved), 'value = 1\n')
            path.write_text('value = 2\n', encoding='utf-8')
            with self.assertRaises(ValueError):
                module.approved_code(path, approved)
            with self.assertRaises(ValueError):
                module.approved_code(path, '')

    def test_approval_executes_the_same_bytes_that_were_hashed(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'script.py'
            path.write_bytes(b'reviewed = True\n')
            approved = module.sha(path)
            with patch.object(Path, 'read_text', return_value='unapproved = True\n'):
                self.assertEqual(module.approved_code(path, approved), 'reviewed = True\n')

    def test_source_binding_requires_same_presence_and_bytes(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'stage.blend'
            path.write_bytes(b'reviewed source')
            expected = module.sha(path)
            module.check_source_binding(path, expected)
            module.check_source_binding(None, None)
            for source, digest in [(None, expected), (path, None), (path, '0' * 64)]:
                with self.assertRaises(ValueError):
                    module.check_source_binding(source, digest)

    def test_retry_preserves_existing_failure_log_before_launch(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            generation = root / 'generation'
            generation.mkdir()
            (generation / 'script.py').write_text('value = 1\n', encoding='utf-8')
            (generation / 'provider-receipt.json').write_text('{}', encoding='utf-8')
            output = root / 'stage'
            output.mkdir()
            output.with_suffix('.log').write_text('prior failure evidence', encoding='utf-8')
            args = SimpleNamespace(generation=generation, approved_sha=module.sha(generation / 'script.py'),
                inside=False, source=None, output=output, blender=Path('unused'), timeout=1,
                asset_id='test', module='modeling')
            with patch.object(module.subprocess, 'run', side_effect=RuntimeError('must not launch')) as launch:
                with self.assertRaises(FileExistsError):
                    module.execute(args)
                launch.assert_not_called()
            self.assertEqual(output.with_suffix('.log').read_text(encoding='utf-8'), 'prior failure evidence')

    def test_invalid_ownership_and_script_rejected_before_blender(self):
        module = self.module()
        good = {'owned_objects': ['V2_Chair_Seat'], 'code': 'import bpy\n', 'notes': []}
        module.validate_generation(good)
        for bad in ({**good, 'owned_objects': []}, {**good, 'owned_objects': ['ProtectedSentinel']},
                    {**good, 'owned_objects': ['V2_A', 'V2_A']}, {**good, 'code': 'not python syntax !!!'}):
            with self.assertRaises((ValueError, SyntaxError)):
                module.validate_generation(bad)
