"""Blender runtime assertions for measured, copy-safe example assets."""
import os
import unittest
try:
    import bpy
    import bmesh
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

from test_extended_architecture_runtime import execute_script


@unittest.skipIf(bpy is None, "bpy not installed")
class MeasuredRecipeRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_vehicle_wheelbase_diameter_grounding_and_source_safety(self):
        bpy.ops.mesh.primitive_cube_add()
        untouched = bpy.context.object
        untouched.name = "UserAsset"
        original = untouched.data
        out, err = execute_script("scripts/vehicle_proportion_example.py")
        self.assertIsNone(err, out)
        self.assertIn("VEHICLE EXAMPLE: SUCCESS", out)
        wheels = [bpy.data.objects["MCP_ExampleCar_Wheel_"+name]
                  for name in ("FL","FR","RL","RR")]
        self.assertAlmostEqual(wheels[0].location.x - wheels[2].location.x, 2.7, places=5)
        self.assertAlmostEqual(wheels[0].location.y, -wheels[1].location.y, places=5)
        for obj in wheels:
            self.assertAlmostEqual(obj.dimensions.z, 0.7, places=5)
            self.assertAlmostEqual(min((obj.matrix_world @ v.co).z for v in obj.data.vertices),
                                   0, places=4)
        body = bpy.data.objects["MCP_ExampleCar_Body"]
        self.assertAlmostEqual(body.dimensions.x, 4.25, places=4)
        self.assertAlmostEqual(body.dimensions.y, 1.78, places=4)
        self.assertIs(untouched.data, original)

    def test_vehicle_meshes_are_closed_and_wound_outward(self):
        out, err = execute_script("scripts/vehicle_proportion_example.py")
        self.assertIsNone(err, out)
        for obj in bpy.data.objects:
            bm = bmesh.new()
            try:
                bm.from_mesh(obj.data)
                self.assertTrue(all(edge.is_manifold for edge in bm.edges), obj.name)
                self.assertTrue(all(edge.is_contiguous for edge in bm.edges), obj.name)
                self.assertGreater(bm.calc_volume(signed=True), 0, obj.name)
            finally:
                bm.free()

    def test_vehicle_dimensions_are_configurable_and_collision_safe(self):
        out, err = execute_script("scripts/vehicle_proportion_example.py", {
            "WHEELBASE": 2.45, "WHEEL_DIAMETER": 0.65, "LENGTH": 4.0})
        self.assertIsNone(err, out)
        front = bpy.data.objects["MCP_ExampleCar_Wheel_FL"]
        rear = bpy.data.objects["MCP_ExampleCar_Wheel_RL"]
        self.assertAlmostEqual(front.location.x - rear.location.x, 2.45, places=5)
        self.assertAlmostEqual(front.dimensions.z, .65, places=5)
        saved = front.data
        out, err = execute_script("scripts/vehicle_proportion_example.py")
        self.assertIsInstance(err, ValueError)
        self.assertIs(front.data, saved)

    def test_voxel_surface_faces_and_signed_volume(self):
        out, err = execute_script("scripts/voxel_atlas_example.py")
        self.assertIsNone(err, out)
        self.assertIn("VOXEL EXAMPLE: SUCCESS", out)
        obj = bpy.data.objects["MCP_VoxelStudy_Mesh"]
        mesh = obj.data
        self.assertEqual(int(obj["cell_count"]), 8)
        self.assertEqual(len(mesh.polygons), int(obj["exposed_quads"]))
        # Independently compute the six-neighbor exposed surface, not from
        # metadata written by the same script under test.
        cells = {(0,0,0),(1,0,0),(2,0,0),(0,1,0),
                 (1,1,0),(2,1,0),(1,0,1),(1,1,1)}
        dirs = ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))
        exposed = sum(
            tuple(cell[i]+step[i] for i in range(3)) not in cells
            for cell in cells for step in dirs)
        self.assertEqual(exposed, 28)
        self.assertEqual(len(mesh.polygons), exposed)
        self.assertAlmostEqual(obj.dimensions.x, .84, places=5)
        self.assertAlmostEqual(obj.dimensions.y, .56, places=5)
        self.assertAlmostEqual(obj.dimensions.z, .56, places=5)
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            self.assertTrue(all(e.is_manifold for e in bm.edges))
            self.assertTrue(all(e.is_contiguous for e in bm.edges))
            self.assertGreater(bm.calc_volume(signed=True), 0)
        finally:
            bm.free()

    def test_voxel_atlas_tile_uvs_and_palette_material(self):
        out, err = execute_script("scripts/voxel_atlas_example.py")
        self.assertIsNone(err, out)
        img = bpy.data.images["MCP_VoxelStudy_Atlas"]
        self.assertEqual(tuple(img.size), (64, 8))
        mesh = bpy.data.objects["MCP_VoxelStudy_Mesh"].data
        uv = mesh.uv_layers.active
        self.assertIsNotNone(uv)
        seen = set()
        for face in mesh.polygons:
            coords = [uv.data[i].uv for i in face.loop_indices]
            u = sum(value[0] for value in coords) / 4
            tile = int(u * 8)
            seen.add(tile)
            self.assertIn(tile, range(6))
            self.assertGreater(min(value[0] for value in coords), tile / 8)
            self.assertLess(max(value[0] for value in coords), (tile + 1)/8)
            self.assertGreater(min(value[1] for value in coords), 0)
            self.assertLess(max(value[1] for value in coords), 1)
        self.assertEqual(seen, set(range(6)))
        nodes = [node for node in bpy.data.materials["MCP_VoxelStudy_Material"].node_tree.nodes
                 if node.type == "TEX_IMAGE"]
        self.assertEqual(len(nodes), 1)
        self.assertIs(nodes[0].image, img)
        self.assertEqual(nodes[0].interpolation, "Closest")

    def test_voxel_grid_override_and_collision_preflight(self):
        out, err = execute_script("scripts/voxel_atlas_example.py", {"GRID_UNIT":0.25})
        self.assertIsNone(err, out)
        obj = bpy.data.objects["MCP_VoxelStudy_Mesh"]
        self.assertAlmostEqual(obj.dimensions.x, .75, places=5)
        self.assertAlmostEqual(obj.dimensions.z, .5, places=5)
        saved = obj.data
        out, err = execute_script("scripts/voxel_atlas_example.py")
        self.assertIsInstance(err, ValueError)
        self.assertIs(obj.data, saved)

    def test_sword_measured_blade_handle_ratio_and_guard(self):
        out, err = execute_script("scripts/prop_proportion_example.py")
        self.assertIsNone(err, out)
        blade = bpy.data.objects["MCP_PropStudy_Blade"]
        grip = bpy.data.objects["MCP_PropStudy_Grip"]
        guard = bpy.data.objects["MCP_PropStudy_Guard"]
        self.assertAlmostEqual(blade.dimensions.z / grip.dimensions.z, 3.5, places=5)
        self.assertAlmostEqual(guard.dimensions.x, .2, places=5)
        self.assertAlmostEqual(blade.location.z-blade.dimensions.z/2,
                               grip.location.z+grip.dimensions.z/2, places=5)

    def test_table_four_legs_touch_ground_and_underside(self):
        out, err = execute_script("scripts/prop_proportion_example.py", {"EXAMPLE":"TABLE"})
        self.assertIsNone(err, out)
        top = bpy.data.objects["MCP_PropStudy_Top"]
        self.assertAlmostEqual(top.dimensions.z, .04, places=5)
        self.assertAlmostEqual(top.location.z+top.dimensions.z/2, .75, places=5)
        for name in ("FL","FR","RL","RR"):
            leg = bpy.data.objects["MCP_PropStudy_Leg_"+name]
            self.assertAlmostEqual(leg.dimensions.x, .06, places=5)
            self.assertAlmostEqual(leg.location.z-leg.dimensions.z/2, 0, places=5)
            self.assertAlmostEqual(leg.location.z+leg.dimensions.z/2,
                                   top.location.z-top.dimensions.z/2, places=5)

    def test_invalid_proportion_preflight_preserves_user_objects(self):
        bpy.ops.mesh.primitive_cube_add()
        original = bpy.context.object
        original.name = "Existing"
        out, err = execute_script("scripts/prop_proportion_example.py", {
            "SWORD_BLADE_LENGTH": .24})
        self.assertIsInstance(err, ValueError)
        self.assertEqual([o.name for o in bpy.data.objects], ["Existing"])
        self.assertIs(bpy.data.objects["Existing"], original)


if __name__ == "__main__":
    unittest.main()
