import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess
import uuid

PATH = Path(__file__).resolve().parents[1] / 'integrations/agents/codex_reviewer.py'
spec = importlib.util.spec_from_file_location('codex_reviewer', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CodexReviewerTests(unittest.TestCase):
    def test_writer_is_rejected_without_launching_codex(self):
        with patch.object(module.subprocess, 'run') as launch:
            with self.assertRaises(ValueError):
                module.CodexReviewer('.').dispatch({'step': {'access': 'write'}})
            launch.assert_not_called()

    def test_actual_identity_comes_from_cli_events_not_model_output(self):
        def launch(command, **kwargs):
            self.assertIn('read-only', command)
            self.assertIn('--ignore-user-config', command)
            output = Path(command[command.index('--output-last-message') + 1])
            output.write_text(json.dumps({'status': 'NOT VERIFIED', 'evidence': [], 'errors': ['No live Blender'], 'measurements': []}), encoding='utf-8')
            return subprocess.CompletedProcess(command, 0, '{"type":"thread.started","thread_id":"actual-session"}\n', '')
        request_id = str(uuid.uuid4())
        with tempfile.TemporaryDirectory() as folder, patch.object(module.subprocess, 'run', side_effect=launch):
            request = {'request_id': request_id, 'step': {'access': 'read', 'module': 'validation'},
                       'context': {'asset_id': 'panel', 'scene_id': 'scene', 'commit_sha': 'a' * 40}}
            result = module.CodexReviewer(folder).dispatch(request)
            self.assertTrue((Path(folder) / result['receipt']).is_file())
        self.assertEqual(result['agent_id'], 'actual-session')
        self.assertEqual(result['request_id'], request_id)

    def test_missing_cli_identity_cannot_pass(self):
        with patch.object(module.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, '', '')):
            with self.assertRaises(ValueError):
                module.CodexReviewer('.').dispatch({'request_id': 'r', 'step': {'access': 'read'}})
