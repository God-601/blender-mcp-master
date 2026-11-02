"""Regression coverage for protected-scene snapshot and comparison tools."""
import ast
import contextlib
import importlib.util
import io
import json
import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "scripts" / "scene_baseline_snapshot.py"
COMPARATOR = ROOT / "scripts" / "compare_scene_baselines.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def compare_module():
    spec = importlib.util.spec_from_file_location("scene_comparator", COMPARATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_snapshot(names):
    source = SNAPSHOT.read_text(encoding="utf-8")
    source, n = re.subn(r"^TARGET_NAMES = \[\]", lambda _: "TARGET_NAMES = " + repr(names),
                        source, flags=re.M, count=1)
    assert n == 1
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(source, str(SNAPSHOT), "exec"), {"__name__": "__main__"})
    return json.loads(out.getvalue().split("MCP_SCENE_BASELINE_BEGIN\n", 1)[1]
                      .split("\nMCP_SCENE_BASELINE_END", 1)[0])


def fake_baseline(name="A", digest="a"*64):
    return {
        "schema_version": 1,
        "scope": "explicit_protected_objects_selected_properties",
        "status": "MEASURED",
        "objects": [{"name": name, "fingerprint_sha256": digest}],
        "errors": [], "missing_names": [],
    }


class BaselineStaticTests(unittest.TestCase):
    def test_scripts_parse_and_are_nonmutating(self):
        for f in (SNAPSHOT, COMPARATOR):
            text = f.read_text(encoding="utf-8")
            ast.parse(text)
            self.assertNotIn("bpy.ops.object.delete", text)
            self.assertNotIn("bpy.data.objects.remove", text)
        self.assertIn("TARGET_NAMES = []", SNAPSHOT.read_text(encoding="utf-8"))

    def test_missing_before_or_after_never_passes(self):
        c = compare_module()
        complete = fake_baseline()
        for missing in ({}, None, {"status": "NOT VERIFIED"}):
            self.assertEqual(c.compare(missing, complete)["status"], "NOT VERIFIED")
            self.assertEqual(c.compare(complete, missing)["status"], "NOT VERIFIED")

    def test_changed_removed_and_added_names_are_explicit(self):
        c = compare_module()
        before = fake_baseline()
        self.assertEqual(c.compare(before, fake_baseline())["status"], "PASS")
        changed = c.compare(before, fake_baseline(digest="b"*64))
        self.assertEqual(changed["status"], "ISSUE")
        self.assertEqual(changed["changed"], ["A"])
        after = fake_baseline("B")
        missing = c.compare(before, after)
        self.assertEqual(missing["status"], "ISSUE")
        self.assertEqual(missing["removed_or_missing"], ["A"])
        self.assertEqual(missing["added_to_scope"], ["B"])

    def test_unrelated_new_objects_are_not_implicitly_verified(self):
        c = compare_module()
        before = fake_baseline()
        after = fake_baseline()
        after["objects"].append({"name": "EXTRA", "fingerprint_sha256": "b"*64})
        self.assertEqual(c.compare(before, after)["status"], "NOT VERIFIED")


@unittest.skipIf(bpy is None, "bpy unavailable")
class BaselineRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add()
        self.cube = bpy.context.object
        self.cube.name = "USER_Keep_Mesh"
        light_data = bpy.data.lights.new("TestLight", "POINT")
        self.light = bpy.data.objects.new("USER_Keep_Light", light_data)
        bpy.context.scene.collection.objects.link(self.light)
        bpy.context.view_layer.update()

    def test_read_only_and_exact_snapshot_match(self):
        names = ["USER_Keep_Mesh", "USER_Keep_Light"]
        original_count = len(bpy.data.objects)
        before = run_snapshot(names)
        self.assertEqual(before["status"], "MEASURED")
        self.assertEqual(original_count, len(bpy.data.objects))
        self.assertEqual(compare_module().compare(before, run_snapshot(names))["status"], "PASS")

    def test_mutated_mesh_and_light_are_caught(self):
        names = ["USER_Keep_Mesh", "USER_Keep_Light"]
        before = run_snapshot(names)
        self.cube.data.vertices[0].co.x += 0.25
        self.light.data.energy += 200.0
        bpy.context.view_layer.update()
        result = compare_module().compare(before, run_snapshot(names))
        self.assertEqual(result["status"], "ISSUE")
        self.assertEqual(sorted(result["changed"]), names)

    def test_existing_material_change_is_detected(self):
        mat = bpy.data.materials.new("ProtectedMaterial")
        self.cube.data.materials.append(mat)
        before = run_snapshot(["USER_Keep_Mesh"])
        mat.diffuse_color = (0.25, 0.2, 0.9, 1)
        after = run_snapshot(["USER_Keep_Mesh"])
        self.assertEqual(compare_module().compare(before, after)["status"], "ISSUE")

    def test_missing_target_or_empty_configuration_does_not_scan_scene(self):
        self.assertEqual(run_snapshot([])["status"], "NOT VERIFIED")
        payload = run_snapshot(["USER_Keep_Mesh", "MISSING"])
        self.assertEqual(payload["status"], "NOT VERIFIED")
        self.assertEqual(payload["missing_names"], ["MISSING"])


if __name__ == "__main__":
    unittest.main()
