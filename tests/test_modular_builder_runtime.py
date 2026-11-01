"""Runtime tests for modular architecture construction."""
import contextlib
import io
import os
import re
import unittest
from pathlib import Path

try:
    import bpy
    import bmesh
except ImportError:  # pragma: no cover
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "modular_builder.py"


def run_modular(components, collection="Test_Modular"):
    source = SCRIPT.read_text(encoding="utf-8")
    source = re.sub(r"^COLLECTION_NAME\s*=.*$", f"COLLECTION_NAME = {collection!r}", source, count=1, flags=re.M)
    source, count = re.subn(
        r"^COMPONENTS\s*=\s*\[.*?^\]",
        lambda _m: f"COMPONENTS = {components!r}",
        source, count=1, flags=re.M | re.S
    )
    if count != 1:
        raise AssertionError("COMPONENTS configuration block not found")
    output = io.StringIO()
    error = None
    with contextlib.redirect_stdout(output):
        try:
            exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
        except Exception as exc:
            error = exc
    return output.getvalue(), error


@unittest.skipIf(bpy is None, "bpy (Blender as a Python module) is not installed")
class ModularBuilderTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_staircase_creates_expected_number_of_steps(self):
        out, err = run_modular([{
            "name": "Steps", "type": "staircase", "steps": 5,
            "width": 2.0, "depth": 2.5, "rise": 1.0
        }])
        self.assertIsNone(err, out)
        steps = [obj for obj in bpy.data.objects if obj.name.startswith("Steps_Step_")]
        self.assertEqual(len(steps), 5)
        self.assertAlmostEqual(max(obj.dimensions.z for obj in steps), 1.0, places=4)

    def test_arch_is_created_as_closed_extruded_mesh(self):
        out, err = run_modular([{
            "name": "Arch", "type": "arch", "outer_radius": 1.5,
            "wall_thickness": 0.25, "leg_height": 2.0, "depth": 0.5,
            "segments": 12
        }])
        self.assertIsNone(err, out)
        obj = bpy.data.objects["Arch"]
        self.assertGreater(len(obj.data.vertices), 20)
        self.assertGreater(len(obj.data.polygons), 20)
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            boundary = sum(1 for edge in bm.edges if not edge.is_manifold)
            self.assertEqual(boundary, 0)
        finally:
            bm.free()

    def test_staircase_rolls_back_its_own_partial_objects_on_collision(self):
        mesh = bpy.data.meshes.new("Existing")
        protected = bpy.data.objects.new("Steps_Step_02", mesh)
        bpy.context.scene.collection.objects.link(protected)
        out, err = run_modular([{
            "name": "Steps", "type": "staircase", "steps": 4,
            "width": 1.0, "depth": 2.0, "rise": 1.0
        }])
        self.assertIsNone(err, out)
        self.assertIs(bpy.data.objects["Steps_Step_02"], protected)
        self.assertNotIn("Steps_Step_01", bpy.data.objects)

    def test_unowned_collection_is_not_reused(self):
        col = bpy.data.collections.new("Test_Modular")
        bpy.context.scene.collection.children.link(col)
        out, err = run_modular([{"name": "Arch", "type": "arch"}])
        self.assertIsInstance(err, ValueError)
        self.assertNotIn("Arch", bpy.data.objects)

    def test_arch_default_has_outward_winding_positive_volume(self):
        out, err = run_modular([{
            "name": "GateArch", "type": "arch", "outer_radius": 1.5,
            "wall_thickness": 0.25, "leg_height": 2.0,
            "depth": 0.5, "segments": 16
        }])
        self.assertIsNone(err, out)
        bm = bmesh.new()
        try:
            bm.from_mesh(bpy.data.objects["GateArch"].data)
            self.assertTrue(all(edge.is_manifold for edge in bm.edges))
            self.assertTrue(all(edge.is_contiguous for edge in bm.edges))
            self.assertGreater(bm.calc_volume(signed=True), 0.0)
        finally:
            bm.free()
