"""Regression tests for read-only post-crash scene identity and baseline gate."""
import ast
import contextlib
import io
import json
import os
import re
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scene_recovery_probe.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def check(path="", name="", protected=None):
    text = SCRIPT.read_text(encoding="utf-8")
    for key, val in (("EXPECTED_BLEND_FILE", path), ("EXPECTED_SCENE_NAME", name),
                     ("PROTECTED_OBJECTS", protected if protected is not None else [])):
        text, n = re.subn(r"^" + key + r" = .*", lambda _m, k=key, v=val:
                            k + " = " + repr(v), text, count=1, flags=re.M)
        assert n == 1, key
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(text, str(SCRIPT), "exec"), {"__name__": "__main__"})
    return json.loads(buf.getvalue().split("MCP_SCENE_RECOVERY_PROBE_BEGIN\n", 1)[1]
                      .split("\nMCP_SCENE_RECOVERY_PROBE_END", 1)[0])


class RecoveryStaticTests(unittest.TestCase):
    def test_explicit_readonly_contract(self):
        src = SCRIPT.read_text(encoding="utf-8")
        ast.parse(src)
        self.assertIn('EXPECTED_BLEND_FILE = ""', src)
        self.assertIn('PROTECTED_OBJECTS = []', src)
        self.assertNotIn("bpy.ops.", src)
        self.assertNotIn("bpy.data.objects.remove(", src)


@unittest.skipIf(bpy is None, "bpy not installed")
class RecoveryRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.object.name = "ProtectedCube"

    def test_unsaved_default_scene_never_claims_recovered(self):
        self.assertEqual(check()["status"], "NOT VERIFIED")
        report = check("/tmp/expected.blend", "Scene",
                       [{"name": "ProtectedCube", "type": "MESH"}])
        self.assertEqual(report["status"], "NOT VERIFIED")
        self.assertFalse(report["checkpoint_loaded"])
        self.assertEqual(report["original_scene_integrity"], "NOT VERIFIED")

    def test_saved_checkpoint_needs_followup_baseline_compare(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "trusted.blend")
            saved = bpy.ops.wm.save_as_mainfile(filepath=path)
            self.assertIn("FINISHED", saved)
            objects_before = set(bpy.data.objects.keys())
            report = check(path, "Scene",
                           [{"name": "ProtectedCube", "type": "MESH"}])
            self.assertEqual(report["status"], "READY_FOR_BASELINE_COMPARISON")
            self.assertTrue(report["checkpoint_loaded"])
            self.assertEqual(report["original_scene_integrity"], "NOT VERIFIED")
            self.assertEqual(set(bpy.data.objects.keys()), objects_before)
            bad = check(path, "Scene",
                        [{"name": "MissingSource", "type": "MESH"}])
            self.assertEqual(bad["status"], "NOT VERIFIED")
            bad = check(path, "Scene",
                        [{"name": "ProtectedCube", "type": "CAMERA"}])
            self.assertEqual(bad["status"], "NOT VERIFIED")
            bad = check(str(Path(directory) / "wrong.blend"), "Scene",
                        [{"name": "ProtectedCube", "type": "MESH"}])
            self.assertEqual(bad["status"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
