"""Preserve authored boundaries when dissolving redundant planar edges."""
import os
import unittest

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

from test_blender_runtime import run_script


@unittest.skipIf(bpy is None, "bpy unavailable")
class BoundaryPreservationTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def panel(self):
        mesh = bpy.data.meshes.new("PanelMesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (2, 0, 0),
                          (0, 1, 0), (1, 1, 0), (2, 1, 0)], [],
                         [(0, 1, 4, 3), (1, 2, 5, 4)])
        obj = bpy.data.objects.new("Panel", mesh)
        bpy.context.collection.objects.link(obj)
        return obj

    def test_authored_boundaries_survive_limited_dissolve(self):
        for boundary in ("seam", "sharp", "uv"):
            with self.subTest(boundary=boundary):
                bpy.ops.wm.read_factory_settings(use_empty=True)
                obj = self.panel()
                edge = next(e for e in obj.data.edges if set(e.vertices) == {1, 4})
                if boundary == "seam":
                    edge.use_seam = True
                elif boundary == "sharp":
                    edge.use_edge_sharp = True
                else:
                    layer = obj.data.uv_layers.new()
                    for face in obj.data.polygons:
                        for index in face.loop_indices:
                            co = obj.data.vertices[obj.data.loops[index].vertex_index].co
                            layer.data[index].uv = (co.x + face.index * 2, co.y)
                original = obj.data
                before_uvs = [tuple(loop.uv) for loop in original.uv_layers.active.data] if boundary == "uv" else None
                output, error = run_script("optimize_mesh.py", TARGETS=["Panel"], APPLY=True,
                                          MODE="balanced", USE_LIMITED_DISSOLVE=True,
                                          MERGE_DISTANCE=0)
                self.assertIsNone(error, (error, output))
                self.assertEqual(len(obj.data.polygons), 2)
                self.assertEqual(len(original.polygons), 2)
                self.assertIsNot(obj.data, original)
                preserved = next(e for e in obj.data.edges if set(e.vertices) == {1, 4})
                if boundary == "seam":
                    self.assertTrue(preserved.use_seam)
                elif boundary == "sharp":
                    self.assertTrue(preserved.use_edge_sharp)
                else:
                    self.assertEqual([tuple(loop.uv) for loop in obj.data.uv_layers.active.data], before_uvs)

    def test_unmarked_coplanar_edge_still_dissolves(self):
        obj = self.panel()
        output, error = run_script("optimize_mesh.py", TARGETS=["Panel"], APPLY=True,
                                  MODE="balanced", USE_LIMITED_DISSOLVE=True,
                                  MERGE_DISTANCE=0)
        self.assertIsNone(error, (error, output))
        self.assertEqual(len(obj.data.polygons), 1)

    def test_deforming_mesh_is_preserved(self):
        obj = self.panel()
        obj.modifiers.new("Rig", "ARMATURE")
        original = obj.data
        output, error = run_script("optimize_mesh.py", TARGETS=["Panel"], APPLY=True,
                                  MODE="balanced", USE_LIMITED_DISSOLVE=True)
        self.assertIsNone(error, (error, output))
        self.assertIn("deformation-dependent modifier present", output)
        self.assertEqual(obj.data, original)
        self.assertEqual(len(obj.data.polygons), 2)
