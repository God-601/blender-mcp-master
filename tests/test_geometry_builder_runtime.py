"""Runtime tests for scripts/geometry_builder.py.

Runs when imported by the existing bpy runtime test environment. These tests verify
construction and safety contracts, not visual quality.
"""
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

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "geometry_builder.py"


def run_builder(components, asset="TestAsset", collection="TestAsset_Geometry"):
    source = SCRIPT.read_text(encoding="utf-8")
    source = re.sub(r"^ASSET_NAME\s*=.*$", f"ASSET_NAME = {asset!r}", source, count=1, flags=re.M)
    source = re.sub(r"^COLLECTION_NAME\s*=.*$", f"COLLECTION_NAME = {collection!r}", source, count=1, flags=re.M)
    source = re.sub(r"^COMPONENTS\s*=.*$", f"COMPONENTS = {components!r}", source, count=1, flags=re.M)
    output = io.StringIO()
    error = None
    with contextlib.redirect_stdout(output):
        try:
            exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
        except Exception as exc:
            error = exc
    return output.getvalue(), error


@unittest.skipIf(bpy is None, "bpy (Blender as a Python module) is not installed")
class GeometryBuilderRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_builds_multiple_geometry_families(self):
        specs = [
            {"name": "BoxA", "type": "box", "dimensions": (2, 1, 0.5)},
            {"name": "BeamA", "type": "beam", "start": (0, 0, 0), "end": (0, 0, 2)},
            {"name": "ProfileA", "type": "extruded_profile",
             "profile": [(0, 0), (1, 0), (1, 1), (0, 1)], "height": 0.5},
            {"name": "LatheA", "type": "lathe",
             "profile": [(0.5, 0), (0.5, 1), (0.2, 1.5)], "segments": 12},
            {"name": "IcoA", "type": "ico_sphere", "subdivisions": 1},
        ]
        out, err = run_builder(specs)
        self.assertIsNone(err, out)
        for name in ("BoxA", "BeamA", "ProfileA", "LatheA", "IcoA"):
            self.assertIn(name, bpy.data.objects)
            self.assertGreater(len(bpy.data.objects[name].data.polygons), 0)
        self.assertIn("result: SUCCESS", out)

    def test_invalid_dimensions_are_reported_without_aborting_other_components(self):
        specs = [
            {"name": "BadBox", "type": "box", "dimensions": (0, 1, 1)},
            {"name": "GoodBox", "type": "box", "dimensions": (1, 1, 1)},
        ]
        out, err = run_builder(specs)
        self.assertIsNone(err, out)
        self.assertNotIn("BadBox", bpy.data.objects)
        self.assertIn("GoodBox", bpy.data.objects)
        self.assertIn("result: PARTIAL", out)

    def test_unrelated_name_collision_is_never_overwritten(self):
        mesh = bpy.data.meshes.new("ExistingMesh")
        existing = bpy.data.objects.new("Protected", mesh)
        bpy.context.scene.collection.objects.link(existing)
        out, err = run_builder([{"name": "Protected", "type": "box"}])
        self.assertIsNone(err, out)
        self.assertIs(bpy.data.objects.get("Protected"), existing)
        self.assertEqual(existing.data, mesh)
        self.assertIn("not owned by this builder", out)

    def test_unowned_collection_name_is_not_reused(self):
        existing = bpy.data.collections.new("TestAsset_Geometry")
        bpy.context.scene.collection.children.link(existing)
        out, err = run_builder([{"name": "ShouldNotExist", "type": "box"}])
        self.assertIsInstance(err, ValueError)
        self.assertIn("not owned by this builder", str(err))
        self.assertNotIn("ShouldNotExist", bpy.data.objects)

    def test_beam_endpoints_determine_length_and_midpoint(self):
        out, err = run_builder([
            {"name": "Beam", "type": "beam", "start": (1, 2, 3), "end": (1, 2, 5), "radius": 0.1}
        ])
        self.assertIsNone(err, out)
        obj = bpy.data.objects["Beam"]
        self.assertAlmostEqual(obj.location.z, 4.0, places=4)
        self.assertAlmostEqual(obj.dimensions.z, 2.0, places=3)

    def test_supports_all_declared_primitives_and_optional_bevel(self):
        specs = [
            {"name": "UVSphere", "type": "sphere", "segments": 12, "rings": 8},
            {"name": "Cylinder", "type": "cylinder", "radius": 0.5, "depth": 1.0},
            {"name": "Cone", "type": "cone", "radius": 0.5, "depth": 1.0},
            {"name": "Torus", "type": "torus", "major_segments": 12, "minor_segments": 6},
            {"name": "BeveledBox", "type": "box", "bevel": 0.05, "bevel_segments": 3},
        ]
        out, err = run_builder(specs)
        self.assertIsNone(err, out)
        for name in ("UVSphere", "Cylinder", "Cone", "Torus", "BeveledBox"):
            self.assertIn(name, bpy.data.objects)
            self.assertGreater(len(bpy.data.objects[name].data.polygons), 0)
        self.assertEqual(bpy.data.objects["BeveledBox"].modifiers[0].type, "BEVEL")

    def test_repeated_run_does_not_duplicate_or_replace_owned_objects(self):
        spec = [{"name": "Stable", "type": "box"}]
        out, err = run_builder(spec)
        self.assertIsNone(err, out)
        original = bpy.data.objects["Stable"]
        out, err = run_builder(spec)
        self.assertIsNone(err, out)
        self.assertIs(bpy.data.objects["Stable"], original)
        self.assertIn("already exists", out)
