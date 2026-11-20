"""Runtime Blender fixtures for 3D containment diagnostic."""
import contextlib
import io
import os
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "solid_overlap_probe.py"
try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def run(pairs):
    namespace = {"__name__": "runtime_import"}
    exec(compile(SOURCE.read_text(encoding="utf-8"), str(SOURCE), "exec"), namespace)
    return namespace["report"](pairs)


class StaticProbeTests(unittest.TestCase):
    def test_readonly_and_no_implicit_scene_targets(self):
        source = SOURCE.read_text(encoding="utf-8")
        compile(source, str(SOURCE), "exec")
        self.assertIn("PAIRS = []", source)
        self.assertNotIn("bpy.ops.object.delete", source)
        self.assertNotIn("bpy.data.objects.remove", source)


@unittest.skipIf(bpy is None, "bpy unavailable")
class RuntimeProbeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name, size=1, center=(0, 0, 0)):
        bpy.ops.mesh.primitive_cube_add(size=size, location=center)
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_nested_closed_mesh_flagged_as_containment_candidate(self):
        outer = self.cube("Outer", 4)
        self.cube("Inner", 1)
        before = [(v.co.x, v.co.y, v.co.z) for v in outer.data.vertices]
        item = run([{"a": "Outer", "b": "Inner"}])["results"][0]
        self.assertEqual(item["triangle_candidates"], 0)
        self.assertEqual(item["contact_case"], "containment_candidate")
        self.assertTrue(item["possible_containment"])
        self.assertEqual(item["actual_volume_intersection"], "NOT VERIFIED")
        self.assertEqual(before, [(v.co.x, v.co.y, v.co.z) for v in outer.data.vertices])

    def test_disjoint_boxes_measured(self):
        self.cube("A")
        self.cube("B", center=(10, 0, 0))
        item = run([{"a": "A", "b": "B"}])["results"][0]
        self.assertEqual(item["contact_case"], "disjoint_aabb")
        self.assertEqual(item["status"], "MEASURED")

    def test_wider_door_hits_obstruction_only_during_swing(self):
        from math import radians
        door = self.cube("Door")
        for vertex in door.data.vertices:
            vertex.co.x += 0.5  # hinge at x=0
        door.scale = (1, 0.08, 2)
        obstacle = self.cube("FrameStop", size=0.12, center=(1, 1, 0))
        fixed_transform = obstacle.matrix_world.copy()

        def swing():
            results = []
            for angle in (0, 45, 90):
                door.rotation_euler.z = radians(angle)
                bpy.context.view_layer.update()
                results.append(run([{"a": "Door", "b": "FrameStop"}])["results"][0])
            door.rotation_euler.z = 0
            bpy.context.view_layer.update()
            return results

        self.assertTrue(all(r["contact_case"] == "disjoint_aabb" for r in swing()))
        door.scale.x = 2
        closed, midway, opened = swing()
        self.assertEqual(closed["contact_case"], "disjoint_aabb")
        self.assertGreater(midway["triangle_candidates"], 0)
        self.assertEqual(opened["contact_case"], "disjoint_aabb")
        self.assertEqual(obstacle.matrix_world, fixed_transform)

    def test_surface_intersection_remains_review(self):
        self.cube("A")
        self.cube("B", center=(0.5, 0, 0))
        item = run([{"a": "A", "b": "B"}])["results"][0]
        self.assertEqual(item["status"], "REVIEW")
        self.assertGreater(item["triangle_candidates"], 0)

    def test_missing_target_and_empty_pairs_do_not_scan_scene(self):
        self.cube("A")
        self.assertEqual(run([{"a": "A", "b": "Missing"}])["results"][0]["status"],
                         "NOT VERIFIED")
        with self.assertRaises(ValueError):
            run([])

    def test_open_plane_does_not_claim_volumetric_result(self):
        bpy.ops.mesh.primitive_plane_add()
        bpy.context.object.name = "Open"
        self.cube("Cube")
        item = run([{"a": "Open", "b": "Cube"}])["results"][0]
        self.assertFalse(item["closed_manifold_candidates"][0])
        self.assertEqual(item["actual_volume_intersection"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
