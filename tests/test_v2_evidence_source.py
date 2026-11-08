import subprocess
import tempfile
from pathlib import Path
import unittest

from run_v2_evidence import source_dirty


class EvidenceSourceTests(unittest.TestCase):
    def test_untracked_and_modified_source_are_not_exact_checkout(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def git(*args):
                subprocess.run(['git', *args], cwd=root, check=True, capture_output=True)
            git('init')
            source = root / 'source.py'
            source.write_text('original', encoding='utf-8')
            self.assertTrue(source_dirty(root))
            git('add', 'source.py')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-m', 'fixture')
            self.assertFalse(source_dirty(root))
            source.write_text('modified', encoding='utf-8')
            self.assertTrue(source_dirty(root))
