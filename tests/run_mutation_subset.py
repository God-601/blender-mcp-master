"""Subprocess-only focused unittest runner for a mutation's scratch checkout.

os._exit avoids the known bpy 4.2 glTF importer interpreter-teardown crash.
"""
import os
import sys
import unittest

def main():
    if len(sys.argv) < 2:
        raise SystemExit("At least one test name required")
    suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:])
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()
