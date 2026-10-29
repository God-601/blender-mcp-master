"""Run the whole test suite and exit with the real result, skipping interpreter teardown.

Why: with the `bpy` module of Blender 4.2.x, a process that has used the glTF exporter crashes
(SIGSEGV, exit code 139) while the interpreter shuts down, even though every test passed and the
export succeeded (reproducible with a 5-line script that exports a cube, no code from this repo).
Blender 4.5, 5.0, 5.1 and 5.2 are not affected. Exiting right after the results avoids a
false CI failure without hiding real failures: the exit code is 0 only if all tests passed.

Usage: python tests/run_all.py [-v]
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    verbosity = 2 if "-v" in sys.argv[1:] else 1
    suite = unittest.defaultTestLoader.discover(HERE, top_level_dir=HERE)
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
