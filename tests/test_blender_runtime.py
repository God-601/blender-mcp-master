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
        self.assertIn("non-manifold edges (3+ faces): 0", out)
        self.assertIn("boundary/open edges: 8", out)

    def test_validate_detects_edge_shared_by_three_faces(self):
        add_mesh("Fin", three_face_edge)
        out, err = run_script("validate_asset.py", TARGETS=["Fin"])
        self.assertIsNone(err)
        self.assertIn("non-manifold edges (3+ faces): 1", out)

    def test_validate_reports_missing_target_as_incomplete(self):
        add_mesh("Box", cube)
        out, err = run_script("validate_asset.py", TARGETS=["Box", "Ghost"])
        self.assertIsNone(err)
        self.assertIn("Ghost", out)
        self.assertIn("INCOMPLETE - CHECK TARGETS", out)

    def test_validate_reads_rotation_from_quaternion_objects(self):
        import math
        obj = add_mesh("Quat", cube)
        obj.rotation_mode = 'QUATERNION'
        obj.rotation_quaternion = (math.cos(math.pi / 4), 0.0, 0.0, math.sin(math.pi / 4))  # 90 deg about Z
        out, err = run_script("validate_asset.py", TARGETS=["Quat"])
        self.assertIsNone(err)
        self.assertIn("90.0", out)

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

    def test_lods_existing_output_creates_nothing_and_deletes_nothing(self):
        add_mesh("Rock", ico)
        existing = add_mesh("Rock_LOD2", cube)
        before = {o.name for o in bpy.data.objects}
        out, err = run_script("make_lods.py", SOURCE="Rock", RATIOS={"LOD1": 0.5, "LOD2": 0.25})
        self.assertIsInstance(err, RuntimeError)
        self.assertEqual({o.name for o in bpy.data.objects}, before)
        self.assertIn(existing.name, bpy.data.objects)

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

    def test_pbr_rerun_with_opaque_alpha_resets_transparency(self):
        run_script("pbr_material.py", NAME="M", ALPHA=0.5)
        mat = bpy.data.materials["M"]
        self.assertAlmostEqual(mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value, 0.5)
        out, err = run_script("pbr_material.py", NAME="M", ALPHA=1.0)
        self.assertIsNone(err, out)
        self.assertAlmostEqual(mat.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value, 1.0)

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
        long_name = "x" * 300 + ".fbx"          # the OS rejects the file name inside the exporter
        out, err = run_script("export_asset.py", OBJECTS=["Crate"],
                              PATH=os.path.join(self.tmp.name, long_name), FORMAT="FBX")
        self.assertIsNotNone(err)
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

    def test_export_obj_format(self):
        add_mesh("Crate", cube)
        path, (out, err) = self._export("out.obj", OBJECTS=["Crate"], FORMAT="OBJ")
        self.assertIsNone(err, out)
        self.assertTrue(os.path.getsize(path) > 0)


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
