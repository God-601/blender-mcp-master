"""Runtime tests for the deterministic organic rock builder."""
import contextlib
import io
import os
import re
import unittest
from pathlib import Path

try:
    import bpy
except ImportError:  # pragma: no cover
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "organic_rock_builder.py"


def run_rock(**config):
    source = SCRIPT.read_text(encoding="utf-8")
    for key, value in config.items():
        source, count = re.subn(
            rf"^{key}\s*=.*$", lambda _m, k=key, v=value: f"{k} = {v!r}",
            source, count=1, flags=re.M
        )
        if count != 1:
            raise AssertionError(f"config {key} not found")
    output = io.StringIO()
    error = None
    with contextlib.redirect_stdout(output):
        try:
            exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
        except Exception as exc:
            error = exc
    return output.getvalue(), error


@unittest.skipIf(bpy is None, "bpy (Blender as a Python module) is not installed")
class OrganicRockBuilderTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_creates_irregular_mesh_and_flattens_bottom(self):
        out, err = run_rock()
        self.assertIsNone(err, out)
        obj = bpy.data.objects["MCP_Organic_Rock"]
        radii = [v.co.length for v in obj.data.vertices]
        self.assertGreater(max(radii) - min(radii), 0.05)
        self.assertGreaterEqual(min(v.co.z for v in obj.data.vertices), -0.62001)
        self.assertIn("CREATED:", out)

    def test_seed_is_deterministic(self):
        out, err = run_rock(OBJECT_NAME="RockA", COLLECTION_NAME="OrganicA", SEED=12)
        self.assertIsNone(err, out)
        first = [tuple(round(axis, 6) for axis in v.co) for v in bpy.data.objects["RockA"].data.vertices]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        out, err = run_rock(OBJECT_NAME="RockB", COLLECTION_NAME="OrganicB", SEED=12)
        self.assertIsNone(err, out)
        second = [tuple(round(axis, 6) for axis in v.co) for v in bpy.data.objects["RockB"].data.vertices]
        self.assertEqual(first, second)

    def test_existing_object_is_not_overwritten(self):
        mesh = bpy.data.meshes.new("ProtectedMesh")
        existing = bpy.data.objects.new("MCP_Organic_Rock", mesh)
        bpy.context.scene.collection.objects.link(existing)
        out, err = run_rock()
        self.assertIsInstance(err, ValueError)
        self.assertIs(bpy.data.objects["MCP_Organic_Rock"], existing)
        self.assertEqual(existing.data, mesh)

    def test_rejects_invalid_roughness(self):
        out, err = run_rock(ROUGHNESS=0.9)
        self.assertIsInstance(err, ValueError)
        self.assertNotIn("MCP_Organic_Rock", bpy.data.objects)
