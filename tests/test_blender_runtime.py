"""Runtime regression tests: run the scripts in a real Blender via the `bpy` module.

Requires `pip install bpy` (the matching wheel for your Python). Skipped when bpy is missing.
These tests cover the Blender version bpy provides; they do not replace checking your own version.
"""
import contextlib
import io
import os
import re
import tempfile
import unittest
from pathlib import Path

try:
    import bpy
    import bmesh
except ImportError:  # pragma: no cover - depends on environment
    if os.environ.get("REQUIRE_BPY") == "1":
        raise   # CI sets this so a broken bpy install fails instead of silently skipping every test
    bpy = None

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def run_script(name, **config):
    """Exec a script with single-line CONFIG overrides; return (stdout, exception or None)."""
    source = (SCRIPTS / name).read_text(encoding="utf-8")
    source_replacements = config.pop("_source_replacements", {})
    for old_text, new_text in source_replacements.items():
        if old_text not in source:
            raise AssertionError(f"source snippet not found in {name}: {old_text!r}")
        source = source.replace(old_text, new_text, 1)
    for key, value in config.items():
        source, count = re.subn(rf"^{key}\s*=.*$", lambda _m, k=key, v=value: f"{k} = {v!r}",
                                source, count=1, flags=re.M)
        if count != 1:
            raise AssertionError(f"config {key} not found in {name}")
    out = io.StringIO()
    error = None
    with contextlib.redirect_stdout(out):
        try:
            exec(compile(source, name, "exec"), {"__name__": "__main__"})
        except BaseException as exc:  # SystemExit is caught on purpose
            error = exc
    return out.getvalue(), error


def add_mesh(name, build):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    build(bm)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def cube(bm):
    bmesh.ops.create_cube(bm, size=1.0)


def ico(bm):
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)


def grid(bm):
    bmesh.ops.create_grid(bm, x_segments=2, y_segments=2, size=1.0)


def three_face_edge(bm):
    v = [bm.verts.new(p) for p in [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)]]
    bm.faces.new([v[0], v[1], v[2]])
    bm.faces.new([v[0], v[1], v[3]])
    bm.faces.new([v[0], v[1], v[4]])


@unittest.skipIf(bpy is None, "bpy (Blender as a Python module) is not installed")
class BlenderRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    # --- validate_asset.py -------------------------------------------------
    def test_validate_open_surface_is_not_reported_as_nonmanifold(self):
        add_mesh("Card", grid)
        out, err = run_script("validate_asset.py", TARGETS=["Card"])
        self.assertIsNone(err)
        self.assertIn("non-manifold edges with 3+ linked faces: 0", out)
        self.assertIn("boundary/open edges: 8", out)

    def test_validate_detects_edge_shared_by_three_faces(self):
        add_mesh("Fin", three_face_edge)
        out, err = run_script("validate_asset.py", TARGETS=["Fin"])
        self.assertIsNone(err)
        self.assertIn("non-manifold edges with 3+ linked faces: 1", out)

    def test_validate_reports_missing_target_as_incomplete(self):
        add_mesh("Box", cube)
        out, err = run_script("validate_asset.py", TARGETS=["Box", "Ghost"])
        self.assertIsNone(err)
        self.assertIn("Ghost", out)
        self.assertIn("INCOMPLETE - CHECK TARGETS", out)

    def test_validate_reports_non_mesh_target_as_incomplete(self):
        add_mesh("Box", cube)
        camera_data = bpy.data.cameras.new("CameraData")
        camera = bpy.data.objects.new("CameraTarget", camera_data)
        bpy.context.scene.collection.objects.link(camera)
        out, err = run_script("validate_asset.py", TARGETS=["Box", "CameraTarget"])
        self.assertIsNone(err, out)
        self.assertIn("target object is not a mesh: 'CameraTarget' (type: CAMERA)", out)
        self.assertIn("[Box]", out)
        self.assertIn("INCOMPLETE - CHECK TARGETS", out)

    def test_validate_empty_targets_do_not_fall_back_to_scene(self):
        add_mesh("UnselectedBox", cube)
        out, err = run_script("validate_asset.py", TARGETS=[])
        self.assertIsNone(err, out)
        self.assertIn("scene-wide fallback", out)
        self.assertIn("INCOMPLETE - CHECK TARGETS", out)
        self.assertNotIn("[UnselectedBox]", out)

    def test_optimizer_backup_works_with_excluded_collection(self):
        obj = add_mesh("Box", cube)
        collection = bpy.data.collections.new("_MCP_OPTIMIZATION_BACKUPS")
        bpy.context.scene.collection.children.link(collection)
        bpy.context.view_layer.layer_collection.children[collection.name].exclude = True
        original = obj.data
        out, err = run_script("optimize_mesh.py", TARGETS=["Box"], APPLY=True)
        self.assertIsNone(err, out)
        self.assertIsNot(obj.data, original)
        self.assertTrue(any(o.data == original for o in collection.objects))

    def test_uv_validator_reports_degenerate_uvs_without_changing_them(self):
        obj = add_mesh("Card", grid)
        layer = obj.data.uv_layers.new(name="UVMap")
        for loop in layer.data:
            loop.uv = (0.0, 0.0)
        before = [tuple(loop.uv) for loop in layer.data]
        out, err = run_script("validate_uvs.py", TARGETS=["Card"])
        self.assertIsNone(err, out)
        self.assertIn("WARN: polygons with zero/negligible UV area:", out)
        self.assertIn("RESULT: REVIEW WARNINGS", out)
        self.assertEqual([tuple(loop.uv) for loop in layer.data], before)

    def test_uv_validator_reports_partial_target_selection(self):
        obj = add_mesh("Card", grid)
        obj.data.uv_layers.new(name="UVMap")
        out, err = run_script("validate_uvs.py", TARGETS=["Card", "Missing"])
        self.assertIsNone(err, out)
        self.assertIn("RESULT: INCOMPLETE", out)

    def test_validate_reads_rotation_from_quaternion_objects(self):
        import math
        obj = add_mesh("Quat", cube)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = (math.cos(math.pi / 4), 0.0, 0.0, math.sin(math.pi / 4))  # 90 deg about Z
        out, err = run_script("validate_asset.py", TARGETS=["Quat"])
        self.assertIsNone(err)
        self.assertIn("90.0", out)

    def test_validate_ignores_unrelated_images(self):
        add_mesh("Box", cube)
        bpy.data.images.new("UnrelatedHugeImage", 4096, 4)
        out, err = run_script("validate_asset.py", TARGETS=["Box"])
        self.assertIsNone(err, out)
        self.assertNotIn("UnrelatedHugeImage", out)

    # --- cleanup_mesh.py ---------------------------------------------------
    def test_cleanup_merges_duplicate_vertices(self):
        def doubled(bm):
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.create_cube(bm, size=1.0)   # coincident copy
        obj = add_mesh("Dup", doubled)
        before = len(obj.data.vertices)
        out, err = run_script("cleanup_mesh.py", TARGETS=["Dup"])
        self.assertIsNone(err)
        self.assertLess(len(obj.data.vertices), before)

    def test_cleanup_skips_truly_shared_mesh(self):
        first = add_mesh("A", cube)
        second = bpy.data.objects.new("B", first.data)
        bpy.context.scene.collection.objects.link(second)
        out, err = run_script("cleanup_mesh.py", TARGETS=["A"])
        self.assertIsNone(err)
        self.assertIn("SKIP: mesh data is shared", out)

    def test_cleanup_treats_fake_user_as_not_shared(self):
        obj = add_mesh("Solo", cube)
        obj.data.use_fake_user = True
        out, err = run_script("cleanup_mesh.py", TARGETS=["Solo"])
        self.assertIsNone(err)
        self.assertNotIn("SKIP", out)
        self.assertIn("[Solo] verts", out)

    def test_cleanup_skips_objects_in_edit_mode(self):
        obj = add_mesh("Editing", cube)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            out, err = run_script("cleanup_mesh.py", TARGETS=["Editing"])
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
        self.assertIsNone(err)
        self.assertIn("SKIP: object is in EDIT mode", out)

    def test_cleanup_warns_about_missing_target(self):
        out, err = run_script("cleanup_mesh.py", TARGETS=["Nope"])
        self.assertIsNone(err)
        self.assertIn("target object not found", out)

    def test_cleanup_skips_shape_key_mesh(self):
        obj = add_mesh("Morph", cube)
        obj.shape_key_add(name="Basis")
        obj.shape_key_add(name="Smile")
        before = (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons))
        out, err = run_script("cleanup_mesh.py", TARGETS=["Morph"])
        self.assertIsNone(err, out)
        self.assertIn("SKIP: mesh has Shape Keys", out)
        self.assertEqual(before, (len(obj.data.vertices), len(obj.data.edges), len(obj.data.polygons)))
        self.assertEqual(len(obj.data.shape_keys.key_blocks), 2)

    # --- make_lods.py ------------------------------------------------------
    def test_lods_missing_source_raises_regular_exception(self):
        out, err = run_script("make_lods.py", SOURCE="Nope")
        self.assertIsInstance(err, RuntimeError)   # not SystemExit
        self.assertIsInstance(err, Exception)

    def test_lods_create_reduced_modifier_free_copies_and_keep_source(self):
        source = add_mesh("Rock", ico)
        source_tris = len(source.data.polygons)
        out, err = run_script("make_lods.py", SOURCE="Rock", RATIOS={"LOD1": 0.5, "LOD2": 0.25})
        self.assertIsNone(err, out)
        lod1, lod2 = bpy.data.objects["Rock_LOD1"], bpy.data.objects["Rock_LOD2"]
        self.assertLess(len(lod1.data.polygons), len(lod2.data.polygons) * 4)
        self.assertLess(len(lod2.data.polygons), len(lod1.data.polygons))
        self.assertEqual(len(lod1.modifiers), 0)
        self.assertEqual(len(source.data.polygons), source_tris)
        self.assertEqual(len(source.modifiers), 0)

    def test_lods_preserve_multiple_uv_layers(self):
        source = add_mesh("UVRock", ico)
        source.data.uv_layers.new(name="UVMap")
        source.data.uv_layers.new(name="ExtraUV")
        out, err = run_script("make_lods.py", SOURCE="UVRock", RATIOS={"LOD1": 0.5})
        self.assertIsNone(err, out)
        self.assertGreaterEqual(len(bpy.data.objects["UVRock_LOD1"].data.uv_layers), 2)

    def test_lods_shift_outputs_when_target_position_overlaps_mesh(self):
        source = add_mesh("Rock", cube)
        obstacle = add_mesh("Obstacle", cube)
        # Match the script's initial LOD offset, independent of the primitive's edge length.
        obstacle.location.x = source.location.x + source.dimensions.x * 1.3 + 0.1
        bpy.context.view_layer.update()
        out, err = run_script("make_lods.py", SOURCE="Rock", RATIOS={"LOD1": 0.5})
        self.assertIsNone(err, out)
        lod = bpy.data.objects["Rock_LOD1"]
        self.assertIn("target position overlapped 'Obstacle'", out)
        self.assertIn("shifted along +X", out)
        self.assertGreater(lod.location.x, obstacle.location.x)
        self.assertEqual(len(source.modifiers), 0)

    def test_lods_existing_output_creates_nothing_and_deletes_nothing(self):
        add_mesh("Rock", ico)
        existing = add_mesh("Rock_LOD2", cube)
        before = {o.name for o in bpy.data.objects}
        out, err = run_script("make_lods.py", SOURCE="Rock", RATIOS={"LOD1": 0.5, "LOD2": 0.25})
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual({o.name for o in bpy.data.objects}, before)
        self.assertIn(existing.name, bpy.data.objects)

    def test_lods_rolls_back_objects_after_mid_run_failure(self):
        source = add_mesh("RollbackRock", ico)
        before_objects = {o.name for o in bpy.data.objects}
        before_meshes = {m.name for m in bpy.data.meshes}
        out, err = run_script(
            "make_lods.py",
            SOURCE="RollbackRock",
            RATIOS={"LOD1": 0.5, "LOD2": 0.25},
            _source_replacements={
                '        name = f"{SOURCE}_{suffix}"':
                '        if index == 2:\n            raise RuntimeError("injected LOD failure")\n        name = f"{SOURCE}_{suffix}"'
            }
        )
        self.assertIsInstance(err, RuntimeError)
        self.assertIn("injected LOD failure", str(err))
        self.assertEqual({o.name for o in bpy.data.objects}, before_objects)
        self.assertEqual({m.name for m in bpy.data.meshes}, before_meshes)
        self.assertIs(source, bpy.data.objects["RollbackRock"])

    def test_lods_reject_invalid_ratio_before_creating_anything(self):
        add_mesh("Rock", ico)
        before = {o.name for o in bpy.data.objects}
        out, err = run_script("make_lods.py", SOURCE="Rock", RATIOS={"LOD1": 0.5, "LOD2": 1.5})
        self.assertIsInstance(err, ValueError)
        self.assertEqual({o.name for o in bpy.data.objects}, before)

    # --- pbr_material.py ---------------------------------------------------
    def _png(self, name):
        path = os.path.join(self.tmp.name, name)
        image = bpy.data.images.new(name, 4, 4)
        image.filepath_raw = path
        image.file_format = 'PNG'
        image.save()
        bpy.data.images.remove(image)
        return path

    def _generated_nodes(self, material):
        return [n for n in material.node_tree.nodes if n.get("_blender_mcp_generated")]

    def test_pbr_clip_uses_binary_threshold_on_blender_42_plus(self):
        if bpy.app.version < (4, 2, 0):
            self.skipTest("surface_render_method is available in Blender 4.2+")
        out, err = run_script("pbr_material.py", NAME="ClipAlpha", ALPHA=0.4, ALPHA_MODE="CLIP")
        self.assertIsNone(err, out)
        mat = bpy.data.materials["ClipAlpha"]
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        self.assertEqual(mat.surface_render_method, "DITHERED")
        clip_nodes = [n for n in mat.node_tree.nodes if n.get("_blender_mcp_generated") and n.type == "MATH" and n.operation == "GREATER_THAN"]
        self.assertEqual(len(clip_nodes), 1)
        self.assertAlmostEqual(clip_nodes[0].inputs[0].default_value, 0.4)
        self.assertAlmostEqual(clip_nodes[0].inputs[1].default_value, 0.5)
        self.assertEqual(len(bsdf.inputs["Alpha"].links), 1)
        out, err = run_script("pbr_material.py", NAME="ClipAlpha", ALPHA=0.8, ALPHA_MODE="CLIP")
        self.assertIsNone(err, out)
        clip_nodes = [n for n in mat.node_tree.nodes if n.get("_blender_mcp_generated") and n.type == "MATH" and n.operation == "GREATER_THAN"]
        self.assertEqual(len(clip_nodes), 1)
        self.assertAlmostEqual(clip_nodes[0].inputs[0].default_value, 0.8)

    def test_pbr_rerun_with_opaque_alpha_resets_transparency(self):
        run_script("pbr_material.py", NAME="M", ALPHA=0.5)
        mat = bpy.data.materials["M"]
        self.assertAlmostEqual(mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value, 0.5)
        out, err = run_script("pbr_material.py", NAME="M", ALPHA=1.0)
        self.assertIsNone(err, out)
        self.assertAlmostEqual(mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value, 1.0)

    def test_pbr_rerun_disables_previous_emission(self):
        run_script("pbr_material.py", NAME="Glow", EMISSION_COLOR=(1.0, 0.2, 0.1, 1.0), EMISSION_STRENGTH=4.0)
        mat = bpy.data.materials["Glow"]
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        strength = bsdf.inputs.get("Emission Strength")
        if strength is not None:
            self.assertAlmostEqual(strength.default_value, 4.0)
        out, err = run_script("pbr_material.py", NAME="Glow", EMISSION_COLOR=None)
        self.assertIsNone(err, out)
        strength = bsdf.inputs.get("Emission Strength")
        if strength is not None:
            self.assertAlmostEqual(strength.default_value, 0.0)

    def test_pbr_is_idempotent_with_textures(self):
        textures = {"color": self._png("c.png"), "rough": self._png("r.png"), "normal": self._png("n.png")}
        for _ in range(2):
            out, err = run_script("pbr_material.py", NAME="Tex", TEXTURES=textures)
            self.assertIsNone(err, out)
        mat = bpy.data.materials["Tex"]
        self.assertEqual(len(self._generated_nodes(mat)), 4)   # 3 images + 1 normal map
        bsdf = mat.node_tree.nodes["Principled BSDF"]
        for socket in ("Base Color", "Roughness", "Normal"):
            self.assertEqual(len(bsdf.inputs[socket].links), 1, socket)

    def test_pbr_missing_texture_fails_without_touching_existing_material(self):
        textures = {"color": self._png("c.png")}
        run_script("pbr_material.py", NAME="Keep", TEXTURES=textures)
        mat = bpy.data.materials["Keep"]
        nodes_before = sorted(n.name for n in mat.node_tree.nodes)
        out, err = run_script("pbr_material.py", NAME="Keep", TEXTURES={"color": "/no/such/file.png"})
        self.assertIsInstance(err, FileNotFoundError)
        self.assertEqual(sorted(n.name for n in mat.node_tree.nodes), nodes_before)

    def test_pbr_image_load_failure_preserves_existing_material(self):
        texture = self._png("valid.png")
        run_script("pbr_material.py", NAME="KeepOnLoadFailure", TEXTURES={"color": texture})
        mat = bpy.data.materials["KeepOnLoadFailure"]
        nodes_before = sorted((n.name, n.type) for n in mat.node_tree.nodes)
        links_before = sorted((link.from_node.name, link.from_socket.name,
                               link.to_node.name, link.to_socket.name)
                              for link in mat.node_tree.links)
        out, err = run_script(
            "pbr_material.py",
            NAME="KeepOnLoadFailure",
            TEXTURES={"color": texture},
            _source_replacements={
                "bpy.data.images.load(bpy.path.abspath(path), check_existing=True)":
                    '(_ for _ in ()).throw(RuntimeError("simulated image load failure"))'
            },
        )
        self.assertIsInstance(err, RuntimeError)
        self.assertIn("simulated image load failure", str(err))
        self.assertEqual(sorted((n.name, n.type) for n in mat.node_tree.nodes), nodes_before)
        self.assertEqual(sorted((link.from_node.name, link.from_socket.name,
                                 link.to_node.name, link.to_socket.name)
                                for link in mat.node_tree.links), links_before)

    def test_pbr_missing_texture_does_not_create_material(self):
        out, err = run_script("pbr_material.py", NAME="Ghost", TEXTURES={"color": "/no/such/file.png"})
        self.assertIsInstance(err, FileNotFoundError)
        self.assertNotIn("Ghost", bpy.data.materials)

    def test_pbr_preserves_user_nodes(self):
        run_script("pbr_material.py", NAME="User")
        mat = bpy.data.materials["User"]
        note = mat.node_tree.nodes.new("ShaderNodeValue")
        note.name = "UserValue"
        textures = {"color": self._png("c.png")}
        run_script("pbr_material.py", NAME="User", TEXTURES=textures)
        run_script("pbr_material.py", NAME="User", TEXTURES=textures)
        self.assertIn("UserValue", mat.node_tree.nodes)

    # --- export_asset.py ---------------------------------------------------
    def _export(self, filename="out.fbx", **config):
        path = os.path.join(self.tmp.name, filename)
        config.setdefault("FORMAT", "FBX")
        return path, run_script("export_asset.py", PATH=path, **config)

    def test_export_writes_file_and_restores_scene_state(self):
        asset = add_mesh("Crate", cube)
        other = add_mesh("Other", cube)
        bpy.context.view_layer.objects.active = other
        other.select_set(True)
        path, (out, err) = self._export(OBJECTS=["Crate"])
        self.assertIsNone(err, out)
        self.assertTrue(os.path.getsize(path) > 0)
        self.assertEqual(sorted(o.name for o in bpy.data.objects), ["Crate", "Other"])
        self.assertNotIn("_EXPORT_TMP", bpy.data.collections)
        self.assertEqual(bpy.context.view_layer.objects.active.name, "Other")
        self.assertEqual([o.name for o in bpy.context.selected_objects], ["Other"])
        self.assertEqual(asset.name, "Crate")
        self.assertEqual(len([m for m in bpy.data.meshes if m.users == 0]), 0)

    def test_export_textured_fbx_leaves_no_temporary_sidecars(self):
        asset = add_mesh("TexturedCrate", cube)
        texture_path = self._png("export-texture.png")
        image = bpy.data.images.load(texture_path)
        material = bpy.data.materials.new("ExportTextureMaterial")
        material.use_nodes = True
        image_node = material.node_tree.nodes.new("ShaderNodeTexImage")
        image_node.image = image
        bsdf = material.node_tree.nodes.get("Principled BSDF")
        material.node_tree.links.new(image_node.outputs["Color"], bsdf.inputs["Base Color"])
        asset.data.materials.append(material)

        output_dir = os.path.join(self.tmp.name, "textured-export")
        os.makedirs(output_dir)
        path = os.path.join(output_dir, "textured.fbx")
        out, err = run_script("export_asset.py", OBJECTS=["TexturedCrate"], PATH=path, FORMAT="FBX")
        self.assertIsNone(err, out)
        self.assertTrue(os.path.isfile(path), out)
        self.assertEqual(os.listdir(output_dir), ["textured.fbx"], out)

    def test_export_relative_path_does_not_crash(self):
        add_mesh("Crate", cube)
        previous = os.getcwd()
        os.chdir(self.tmp.name)
        try:
            out, err = run_script("export_asset.py", OBJECTS=["Crate"], PATH="relative.fbx", FORMAT="FBX")
            self.assertIsNone(err, out)
            self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "relative.fbx")))
        finally:
            os.chdir(previous)

    def test_export_restores_state_when_exporter_fails(self):
        add_mesh("Crate", cube)
        out, err = run_script(
            "export_asset.py",
            OBJECTS=["Crate"],
            PATH=os.path.join(self.tmp.name, "failed.fbx"),
            FORMAT="FBX",
            _source_replacements={
                "export_result = bpy.ops.export_scene.fbx(**kw)":
                    'raise RuntimeError("simulated exporter failure")'
            },
        )
        self.assertIsInstance(err, RuntimeError)
        self.assertIn("simulated exporter failure", str(err))
        self.assertEqual([o.name for o in bpy.data.objects], ["Crate"])
        self.assertNotIn("_EXPORT_TMP", bpy.data.collections)
        self.assertEqual(len(bpy.data.meshes), 1)

    def test_export_with_no_valid_objects_raises_and_leaves_scene_clean(self):
        add_mesh("Crate", cube)
        path, (out, err) = self._export(OBJECTS=["Missing"])
        self.assertIsInstance(err, RuntimeError)
        self.assertFalse(os.path.exists(path))
        self.assertEqual([o.name for o in bpy.data.objects], ["Crate"])
        self.assertNotIn("_EXPORT_TMP", bpy.data.collections)

    def test_export_rejects_unknown_format_before_touching_scene(self):
        add_mesh("Crate", cube)
        path, (out, err) = self._export(OBJECTS=["Crate"], FORMAT="XYZ")
        self.assertIsInstance(err, ValueError)
        self.assertEqual([o.name for o in bpy.data.objects], ["Crate"])

    def test_export_glb_format(self):
        add_mesh("Crate", cube)
        path, (out, err) = self._export("out.glb", OBJECTS=["Crate"], FORMAT="GLB")
        self.assertIsNone(err, out)
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 0)
        with open(path, "rb") as stream:
            self.assertEqual(stream.read(4), b"glTF")
        self.assertNotIn("_EXPORT_TMP", bpy.data.collections)

    def test_export_obj_format(self):
        add_mesh("Crate", cube)
        path, (out, err) = self._export("out.obj", OBJECTS=["Crate"], FORMAT="OBJ")
        self.assertIsNone(err, out)
        self.assertTrue(os.path.getsize(path) > 0)


    def test_export_refuses_to_overwrite_existing_file(self):
        add_mesh("Crate", cube)
        path = os.path.join(self.tmp.name, "existing.fbx")
        with open(path, "wb") as stream:
            stream.write(b"preserve existing export")
        out, err = run_script("export_asset.py", OBJECTS=["Crate"], PATH=path, FORMAT="FBX")
        self.assertIsInstance(err, FileExistsError)
        with open(path, "rb") as stream:
            self.assertEqual(stream.read(), b"preserve existing export")
        self.assertEqual([o.name for o in bpy.data.objects], ["Crate"])

    def test_apply_and_origin_skips_shape_key_mesh(self):
        obj = add_mesh("Morph", cube)
        obj.shape_key_add(name="Basis")
        obj.shape_key_add(name="Smile")
        obj.scale = (2, 2, 2)
        out, err = run_script("apply_and_origin.py", TARGETS=["Morph"])
        self.assertIsNone(err, out)
        self.assertIn("SKIP: mesh has Shape Keys", out)
        self.assertEqual(tuple(obj.scale), (2.0, 2.0, 2.0))
        self.assertEqual(len(obj.data.shape_keys.key_blocks), 2)

    # --- scripts covered only by smoke/behaviour tests ----------------------
    def test_apply_and_origin_bakes_transforms_and_grounds_object(self):
        obj = add_mesh("Box", cube)
        obj.location = (2, 3, 4)
        obj.scale = (0.8, 0.5, 1.2)
        obj.rotation_euler = (0, 0, 0.5)
        out, err = run_script("apply_and_origin.py", TARGETS=["Box"], GROUND_TO_Z0=True)
        self.assertIsNone(err, out)
        self.assertEqual(tuple(round(v, 4) for v in obj.scale), (1.0, 1.0, 1.0))
        self.assertAlmostEqual(obj.location.x, 2.0, places=4)
        self.assertAlmostEqual(obj.location.y, 3.0, places=4)
        lowest = min((obj.matrix_world @ v.co).z for v in obj.data.vertices)
        self.assertAlmostEqual(lowest, 0.0, places=4)

    def test_apply_and_origin_skips_shared_mesh(self):
        first = add_mesh("A", cube)
        second = bpy.data.objects.new("B", first.data)
        bpy.context.scene.collection.objects.link(second)
        first.scale = (2, 2, 2)
        out, err = run_script("apply_and_origin.py", TARGETS=["A"])
        self.assertIsNone(err)
        self.assertIn("SKIP: shared mesh data", out)
        self.assertEqual(tuple(first.scale), (2.0, 2.0, 2.0))

    def test_apply_and_origin_keeps_children_in_place(self):
        parent = add_mesh("Parent", cube)
        parent.location = (0, 0, 2)
        child = add_mesh("Child", cube)
        child.parent = parent
        child.matrix_parent_inverse = parent.matrix_world.inverted()
        child.location = (1, 0, 0)
        bpy.context.view_layer.update()
        before = child.matrix_world.translation.copy()
        out, err = run_script("apply_and_origin.py", TARGETS=["Parent"], ORIGIN="CUSTOM",
                              CUSTOM_ORIGIN_WORLD=(5.0, 5.0, 0.0))
        self.assertIsNone(err, out)
        bpy.context.view_layer.update()
        self.assertAlmostEqual((child.matrix_world.translation - before).length, 0.0, places=4)
        self.assertAlmostEqual(parent.location.x, 5.0, places=4)

    def test_apply_and_origin_skips_objects_in_edit_mode(self):
        obj = add_mesh("Box", cube)
        obj.scale = (2, 2, 2)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='EDIT')
        try:
            out, err = run_script("apply_and_origin.py", TARGETS=["Box"])
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
        self.assertIsNone(err)
        self.assertIn("SKIP: object is in EDIT mode", out)
        self.assertEqual(tuple(obj.scale), (2.0, 2.0, 2.0))
        self.assertAlmostEqual(obj.dimensions.x, 2.0, places=4)

    def test_setup_scene_does_not_silently_skip_on_name_collision(self):
        user_mesh = add_mesh("Key", cube)
        user_camera_data = bpy.data.cameras.new("Cam")
        user_camera = bpy.data.objects.new("Cam", user_camera_data)
        bpy.context.scene.collection.objects.link(user_camera)
        bpy.context.scene.camera = user_camera
        out, err = run_script("setup_scene.py", ASSET_NAME="Probe", ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True)
        self.assertIsNone(err, out)
        self.assertEqual(user_mesh.type, 'MESH')                       # the user's object is untouched
        lights = [o for o in bpy.data.objects if o.type == 'LIGHT']
        self.assertEqual(len(lights), 3)                                # Key, Fill and Rim all exist as lights
        self.assertEqual(bpy.context.scene.camera, user_camera)         # active camera is not replaced
        self.assertIn("Key", out)                                       # the conflict is reported

    def test_setup_scene_is_repeatable(self):
        run_script("setup_scene.py", ASSET_NAME="Probe", ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True)
        out, err = run_script("setup_scene.py", ASSET_NAME="Probe", ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True)
        self.assertIsNone(err, out)
        self.assertEqual(len([o for o in bpy.data.objects if o.type == 'LIGHT']), 3)
        self.assertEqual(len([o for o in bpy.data.objects if o.type == 'CAMERA']), 1)

    def test_pbr_material_does_not_use_deprecated_use_nodes_api(self):
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            out, err = run_script("pbr_material.py", NAME="NoWarn")
        self.assertIsNone(err, out)
        self.assertFalse([w for w in caught if "use_nodes" in str(w.message)], [str(w.message) for w in caught])
        self.assertIsNotNone(bpy.data.materials["NoWarn"].node_tree)

    def test_validate_does_not_use_deprecated_use_nodes_api(self):
        import warnings
        obj = add_mesh("Box", cube)
        obj.data.materials.append(bpy.data.materials.new("M"))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            out, err = run_script("validate_asset.py", TARGETS=["Box"])
        self.assertIsNone(err, out)
        self.assertFalse([w for w in caught if "use_nodes" in str(w.message)], [str(w.message) for w in caught])

    def test_bevel_and_shade_applies_modifiers_cleanly(self):
        obj = add_mesh("Box", cube)
        out, err = run_script("bevel_and_shade.py", TARGETS=["Box"], APPLY_MODIFIERS=True)
        self.assertIsNone(err, out)
        self.assertEqual(len(obj.modifiers), 0)
        self.assertGreater(len(obj.data.polygons), 6)   # bevel added geometry

    def test_setup_scene_creates_collection_lights_and_camera(self):
        out, err = run_script("setup_scene.py", ASSET_NAME="Probe", ADD_STUDIO_LIGHTS=True, ADD_CAMERA=True)
        self.assertIsNone(err, out)
        self.assertIn("Probe", bpy.data.collections)
        self.assertEqual(bpy.context.scene.unit_settings.system, 'METRIC')
        self.assertTrue({"Key", "Fill", "Rim", "Cam"} <= set(bpy.data.objects.keys()))


if __name__ == "__main__":
    unittest.main()
