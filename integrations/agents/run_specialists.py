"""Standalone process CLI; do not execute this entrypoint inside a Blender host."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from specialist_orchestrator import main

if __name__ == '__main__':
    raise SystemExit(main())
