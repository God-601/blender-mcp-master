"""Write exact-checkout test evidence; never represents a live asset campaign."""
import argparse
import json
import platform
from pathlib import Path
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'scripts'))


def source_dirty(root):
    return bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=root, text=True).strip())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    suite = unittest.TestSuite()
    for name in ('test_specialist_plan', 'test_specialist_orchestrator', 'test_codex_reviewer', 'test_release_gate_report', 'test_v2_evidence_source'):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromName(name))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = source_dirty(ROOT)
    report = {
        'schema_version': 1, 'commit_sha': sha,
        'working_tree_dirty': dirty,
        'python': platform.python_version(), 'platform': platform.platform(),
        'scope': 'planner, trusted-host transport, simulated scene/agent faults, Codex worker contract and release gates',
        'status': 'PASS' if result.wasSuccessful() and not result.skipped and not dirty else 'ISSUE',
        'tests_run': result.testsRun, 'skipped': len(result.skipped),
        'failures': [str(test) for test, _ in result.failures],
        'errors': [str(test) for test, _ in result.errors],
        'live_blender_agent_campaign': 'NOT VERIFIED', 'artistic_quality': 'NOT VERIFIED',
        'engine_fidelity': 'NOT VERIFIED', 'provider_token_savings': 'NOT VERIFIED',
        'publication_authorized': False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
