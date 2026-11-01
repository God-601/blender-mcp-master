"""P0 safety regressions against unintended edits and misleading successful outputs."""
import os
import json
import tempfile
import unittest
from pathlib import Path

try:
    import bpy
    import bmesh
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

from test_blender_runtime import run_script
from test_professional_quality_runtime import run_inspection


@unittest.skipIf(bpy is None, "Blender bpy module unavailable")
class P0SafetyRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.object
        obj.name = name
        return obj

    def png(self, root):
        image = bpy.data.images.new("SourceImage", width=4, height=4, alpha=True)
        path = str(Path(root) / "albedo.png")
        image.filepath_raw = path
        image.file_format = "PNG"
        image.save()
        return path, image

    def test_material_name_collision_refuses_unowned_existing_material(self):
        user = bpy.data.materials.new("UserOwned")
        user.diffuse_color = (0.1, 0.2, 0.3, 1.0)
        out, err = run_script("pbr_material.py", NAME="UserOwned")
        self.assertIsInstance(err, ValueError, out)
        self.assertIn("unowned material", str(err))
        self.assertEqual(tuple(user.diffuse_color), (0.1, 0.2, 0.3, 1.0))

    def test_material_will_not_change_shared_mesh_slots(self):
        first = self.cube("Original")
        second = bpy.data.objects.new("LinkedCopy", first.data)
        bpy.context.scene.collection.objects.link(second)
        kept = bpy.data.materials.new("Kept")
        first.data.materials.append(kept)
        out, err = run_script("pbr_material.py", NAME="NewMCP", ASSIGN_TO=["Original"])
        self.assertIsInstance(err, ValueError, out)
        self.assertIs(first.data, second.data)
        self.assertEqual([m.name for m in first.data.materials], ["Kept"])
        self.assertNotIn("NewMCP", bpy.data.materials)

    def test_material_default_appends_without_replacing_existing_slots(self):
        first = self.cube("Target")
        kept = bpy.data.materials.new("Kept")
        first.data.materials.append(kept)
        out, err = run_script("pbr_material.py", NAME="OwnedMCP", ASSIGN_TO=["Target"])
        self.assertIsNone(err, out)
        self.assertEqual([m.name for m in first.data.materials], ["Kept", "OwnedMCP"])

    def test_material_updates_refuse_shared_owned_material(self):
        obj_a, obj_b = self.cube("A"), self.cube("B")
        out, err = run_script("pbr_material.py", NAME="Owned", ASSIGN_TO=["A", "B"])
        self.assertIsNone(err, out)
        material = bpy.data.materials["Owned"]
        old_roughness = material.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value
        out, err = run_script("pbr_material.py", NAME="Owned", ROUGHNESS=0.15)
        self.assertIsInstance(err, ValueError, out)
        self.assertAlmostEqual(material.node_tree.nodes.get("Principled BSDF").inputs["Roughness"].default_value, old_roughness)

    def test_normal_image_colorspace_does_not_mutate_shared_color_image(self):
        with tempfile.TemporaryDirectory() as root:
            path, original = self.png(root)
            original.colorspace_settings.name = "sRGB"
            user_mat = bpy.data.materials.new("Other")
            user_mat.use_nodes = True
            node = user_mat.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = original
            out, err = run_script("pbr_material.py", NAME="NormalMCP", TEXTURES={"normal": path})
            self.assertIsNone(err, out)
            self.assertEqual(original.colorspace_settings.name, "sRGB")
            generated = next(n for n in bpy.data.materials["NormalMCP"].node_tree.nodes
                             if n.type == "TEX_IMAGE")
            self.assertEqual(generated.image.colorspace_settings.name, "Non-Color")
            self.assertNotEqual(generated.image.name, original.name)

    def test_color_texture_alpha_is_connected_to_cutout(self):
        with tempfile.TemporaryDirectory() as root:
            path, image = self.png(root)
            out, err = run_script("pbr_material.py", NAME="Cutout", TEXTURES={"color": path},
                                  USE_COLOR_ALPHA=True, ALPHA_MODE="CLIP")
            self.assertIsNone(err, out)
            mat = bpy.data.materials["Cutout"]
            nodes = mat.node_tree.nodes
            links = mat.node_tree.links
            tex = next(n for n in nodes if n.type == "TEX_IMAGE")
            multiply = next(n for n in nodes if n.type == "MATH" and n.operation == "MULTIPLY")
            self.assertTrue(any(link.from_node == tex and link.from_socket.name == "Alpha"
                                and link.to_node == multiply for link in links))
            bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
            if hasattr(mat, "surface_render_method"):
                clip = next(n for n in nodes if n.type == "MATH" and n.operation == "GREATER_THAN")
                self.assertTrue(any(link.from_node == multiply and link.to_node == clip for link in links))
                self.assertTrue(any(link.from_node == clip and link.to_node == bsdf and
                                    link.to_socket.name == "Alpha" for link in links))
            else:
                self.assertTrue(any(link.from_node == multiply and link.to_node == bsdf and
                                    link.to_socket.name == "Alpha" for link in links))

    def test_bevel_default_creates_copy_without_modifying_source(self):
        src = self.cube("Source")
        source_mesh = src.data
        old_smoothing = [poly.use_smooth for poly in src.data.polygons]
        out, err = run_script("bevel_and_shade.py", TARGETS=["Source"])
        self.assertIsNone(err, out)
        self.assertIn("Source_Shaded", bpy.data.objects)
        output = bpy.data.objects["Source_Shaded"]
        self.assertIs(src.data, source_mesh)
        self.assertIsNot(output.data, src.data)
        self.assertEqual([poly.use_smooth for poly in src.data.polygons], old_smoothing)
        self.assertEqual(len(src.modifiers), 0)
        self.assertEqual(output.modifiers[0].type, "BEVEL")

    def test_bevel_empty_targets_do_not_change_selected_meshes(self):
        obj = self.cube("Selected")
        out, err = run_script("bevel_and_shade.py", TARGETS=[])
        self.assertIsNone(err, out)
        self.assertIn("NO TARGETS", out)
        self.assertEqual([o.name for o in bpy.data.objects], ["Selected"])
        self.assertEqual(len(obj.modifiers), 0)

    def test_setup_preserves_existing_unit_settings_by_default(self):
        scene = bpy.context.scene
        scene.unit_settings.system = "IMPERIAL"
        out, err = run_script("setup_scene.py", ASSET_NAME="NewProp")
        self.assertIsNone(err, out)
        self.assertEqual(scene.unit_settings.system, "IMPERIAL")

    def test_setup_refuses_unowned_collection_without_changing_units(self):
        user = bpy.data.collections.new("DoNotTouch")
        bpy.context.scene.collection.children.link(user)
        out, err = run_script("setup_scene.py", ASSET_NAME="DoNotTouch", SET_UNITS=True)
        self.assertIsInstance(err, ValueError)
        self.assertEqual(bpy.context.scene.unit_settings.system, "NONE")

    def test_export_rejects_shape_keys_without_writing_any_file(self):
        obj = self.cube("Animated")
        obj.shape_key_add(name="Basis")
        obj.shape_key_add(name="Expression")
        with tempfile.TemporaryDirectory() as root:
            path = str(Path(root) / "static.glb")
            out, err = run_script("export_asset.py", OBJECTS=["Animated"], PATH=path, FORMAT="GLB")
            self.assertIsInstance(err, ValueError, out)
            self.assertIn("shape-key", str(err))
            self.assertFalse(Path(path).exists())

    def test_export_requires_an_explicit_path(self):
        self.cube("Mesh")
        out, err = run_script("export_asset.py", OBJECTS=["Mesh"], PATH="")
        self.assertIsInstance(err, ValueError)
        self.assertIn("PATH", str(err))

    def test_mixed_face_normals_are_detected_even_when_volume_is_positive(self):
        obj = self.cube("MixedWinding")
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            face = list(bm.faces)[0]
            bmesh.ops.reverse_faces(bm, faces=[face])
            bm.to_mesh(obj.data)
        finally:
            bm.free()
        obj.data.update()
        report = run_inspection(["MixedWinding"], {"MixedWinding": {
            "solid": True, "positive_volume": True}})["targets"][0]
        self.assertGreater(report["signed_shell_volumes_if_closed"][0], 0.0)
        self.assertGreater(report["inconsistent_winding_edges"], 0)
        self.assertEqual(report["checks"]["face_winding_continuity"]["status"], "ISSUE")
        self.assertEqual(report["checks"]["outward_volume"]["status"], "ISSUE")

    def test_parented_origin_changes_are_skipped(self):
        parent = self.cube("Parent")
        child = self.cube("Child")
        child.parent = parent
        child.scale = (2, 2, 2)
        out, err = run_script("apply_and_origin.py", TARGETS=["Child"])
        self.assertIsNone(err, out)
        self.assertIn("SKIP: parented object", out)
        self.assertEqual(tuple(child.scale), (2.0, 2.0, 2.0))


if __name__ == "__main__":
    unittest.main()
