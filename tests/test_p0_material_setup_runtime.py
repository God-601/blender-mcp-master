"""P0 transactional material/setup regression checks."""
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
class P0MaterialSetupTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_pbr_injected_node_failure_preserves_original_and_slots(self):
        obj = self.cube("Target")
        out, err = run_script("pbr_material.py", NAME="SafeMat", ASSIGN_TO=["Target"])
        self.assertIsNone(err, out)
        original = bpy.data.materials["SafeMat"]
        before_slots = [m.name for m in obj.data.materials]
        baseline_nodes = [(n.name, n.type) for n in original.node_tree.nodes]
        out, err = run_script("pbr_material.py", NAME="SafeMat", ROUGHNESS=0.1,
                              _source_replacements={
             '    set_input(bsdf, ["Roughness"], ROUGHNESS)':
             '    raise RuntimeError("injected node construction failure")'
        })
        self.assertIsInstance(err, RuntimeError, out)
        self.assertIs(bpy.data.materials["SafeMat"], original)
        self.assertEqual([m.name for m in obj.data.materials], before_slots)
        self.assertEqual([(n.name, n.type) for n in original.node_tree.nodes], baseline_nodes)

    def test_pbr_injected_assignment_failure_restores_existing_slots(self):
        obj = self.cube("Target")
        old = bpy.data.materials.new("Preserved")
        obj.data.materials.append(old)
        out, err = run_script("pbr_material.py", NAME="NewOwned", ASSIGN_TO=["Target"],
                              _source_replacements={
             "            _mesh.materials.append(mat)":
             '            raise RuntimeError("injected slot write failure")'
        })
        self.assertIsInstance(err, RuntimeError, out)
        self.assertEqual([m.name for m in obj.data.materials], ["Preserved"])
        self.assertNotIn("NewOwned", bpy.data.materials)

    def test_pbr_shared_legacy_material_update_requires_opt_in(self):
        a, b = self.cube("A"), self.cube("B")
        out, err = run_script("pbr_material.py", NAME="Owned", ASSIGN_TO=["A", "B"])
        self.assertIsNone(err, out)
        before = bpy.data.materials["Owned"]
        out, err = run_script("pbr_material.py", NAME="Owned", ROUGHNESS=0.2)
        self.assertIsInstance(err, ValueError, out)
        self.assertIs(before, bpy.data.materials["Owned"])

    def test_setup_failure_rolls_back_created_studio_and_units(self):
        original = self.cube("UserCube")
        scene = bpy.context.scene
        scene.unit_settings.system = "IMPERIAL"
        original_units = scene.unit_settings.system
        chosen = [o.name for o in bpy.context.selected_objects]
        out, err = run_script("setup_scene.py", ASSET_NAME="Failed",
                              ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True,
                              SET_UNITS=True, _source_replacements={
             '            studio_light(studio, "Fill", (-3.5, -2.0, 2.0), 350, 3.0)':
             '            raise RuntimeError("injected setup failure")'
        })
        self.assertIsInstance(err, RuntimeError, out)
        self.assertEqual(scene.unit_settings.system, original_units)
        self.assertEqual({o.name for o in bpy.data.objects}, {"UserCube"})
        self.assertNotIn("Failed", bpy.data.collections)
        self.assertNotIn("Studio", bpy.data.collections)
        self.assertEqual([o.name for o in bpy.context.selected_objects], chosen)
        self.assertIs(bpy.data.objects["UserCube"], original)

    def test_setup_does_not_reuse_unowned_light_camera(self):
        light_data = bpy.data.lights.new("UserLight", "AREA")
        light_data.energy = 178.0
        light = bpy.data.objects.new("Key", light_data)
        bpy.context.scene.collection.objects.link(light)
        camera_data = bpy.data.cameras.new("UserCam")
        camera = bpy.data.objects.new("Cam", camera_data)
        bpy.context.scene.collection.objects.link(camera)
        bpy.context.scene.camera = camera
        out, err = run_script("setup_scene.py", ASSET_NAME="SafeStudio",
                              ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True)
        self.assertIsNone(err, out)
        self.assertIs(bpy.data.objects["Key"], light)
        self.assertAlmostEqual(light.data.energy, 178.0)
        self.assertIs(bpy.context.scene.camera, camera)
        owned = [o for o in bpy.data.objects
                 if o.get("_blender_mcp_setup_scene") == "setup_scene_v2"]
        self.assertEqual(len(owned), 4)
        out, err = run_script("setup_scene.py", ASSET_NAME="SafeStudio",
                              ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True)
        self.assertIsNone(err, out)
        owned = [o for o in bpy.data.objects
                 if o.get("_blender_mcp_setup_scene") == "setup_scene_v2"]
        self.assertEqual(len(owned), 4)

    def test_setup_preserves_active_layer_by_default(self):
        self.cube("Cube")
        before = bpy.context.view_layer.active_layer_collection
        out, err = run_script("setup_scene.py", ASSET_NAME="NewAsset")
        self.assertIsNone(err, out)
        self.assertIs(bpy.context.view_layer.active_layer_collection, before)


if __name__ == "__main__":
    unittest.main()
