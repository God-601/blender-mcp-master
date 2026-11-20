"""P1 regression checks for final evaluated metrics and GLB export round trips."""
import json
import os
import tempfile
import unittest
from pathlib import Path

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None

from test_blender_runtime import run_script
from test_extended_architecture_runtime import execute_script


def parse_report(output, name):
    return json.loads(
        output.split(name + "_BEGIN\n", 1)[1].split("\n" + name + "_END", 1)[0]
    )


@unittest.skipIf(bpy is None, "bpy unavailable")
class P1DeliveryRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def cube(self, name):
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        obj = bpy.context.object
        obj.name = name
        return obj

    def test_object_material_overrides_survive_glb_reimport(self):
        for apply in (True, False):
            with self.subTest(apply=apply), tempfile.TemporaryDirectory() as folder:
                bpy.ops.wm.read_factory_settings(use_empty=True)
                white = self.cube("WhitePart")
                white.data.materials.append(bpy.data.materials.new("White"))
                red = white.copy()
                red.name = "RedPart"
                bpy.context.collection.objects.link(red)
                red.material_slots[0].link = "OBJECT"
                paint = bpy.data.materials.new("Red")
                paint.diffuse_color = (1, 0, 0, 1)
                red.material_slots[0].material = paint
                path = str(Path(folder) / "parts.glb")
                out, err = run_script("export_asset.py", OBJECTS=[white.name, red.name],
                                      PATH=path, FORMAT="GLB", APPLY_MODIFIERS=apply)
                self.assertIsNone(err, (out, err))
                self.assertEqual(red.data, white.data)
                self.assertEqual(red.data.materials[0].name, "White")
                self.assertEqual(red.material_slots[0].material.name, "Red")
                bpy.ops.wm.read_factory_settings(use_empty=True)
                bpy.ops.import_scene.gltf(filepath=path)
                for name, material in (("WhitePart", "White"), ("RedPart", "Red")):
                    self.assertEqual(bpy.data.objects[name].material_slots[0].material.name, material)

    def test_duplicate_audit_targets_are_refused(self):
        self.cube("Part")
        out, err = run_script("validate_asset.py", TARGETS=["Part", "Part"])
        self.assertIsInstance(err, ValueError)
        self.assertNotIn("TOTAL:", out)

    def test_nonfinite_uv_cannot_pass_validation(self):
        part = self.cube("Part")
        layer = part.data.uv_layers.active
        for value in (float("nan"), float("inf"), -float("inf")):
            # Bulk mesh import can carry non-finite floats that the ordinary
            # RNA property setter clamps. Exercise the actual stored data.
            coords = [0.0] * (2 * len(layer.data))
            layer.data.foreach_get("uv", coords)
            coords[5] = value
            layer.data.foreach_set("uv", coords)
            out, err = run_script("validate_uvs.py", TARGETS=["Part"])
            self.assertIsNone(err)
            self.assertIn(f"'Part' layer {layer.name!r} loop 2: non-finite UV", out)
            self.assertIn("RESULT: INCOMPLETE", out)
            out, err = run_script("validate_asset.py", TARGETS=["Part"])
            self.assertIsNone(err)
            self.assertIn("non-finite UV", out)
            self.assertIn("RESULT: REVIEW WARNINGS", out)

    def test_benchmark_counts_evaluated_subdivision_mesh_not_base(self):
        cube = self.cube("BenchmarkCube")
        mod = cube.modifiers.new("Subdivision", "SUBSURF")
        mod.levels = 2
        out, err = execute_script("scripts/benchmark_report.py", {
            "TARGET_NAMES": ["BenchmarkCube"]})
        self.assertIsNone(err, out)
        report = parse_report(out, "MCP_BENCHMARK_REPORT")
        item = report["targets"][0]
        self.assertEqual(item["base_faces"], 6)
        self.assertEqual(item["base_triangles"], 12)
        self.assertGreater(item["faces"], 6)
        self.assertGreater(item["triangles"], 12)
        self.assertEqual(item["status"], "MEASURED")
        self.assertEqual(report["visual_status"], "NOT VERIFIED")
        self.assertEqual(len(cube.data.polygons), 6)
        self.assertEqual(len(cube.modifiers), 1)

    def test_legacy_inspection_counts_final_modifier_output(self):
        cube = self.cube("InspectCube")
        mod = cube.modifiers.new("Triangulate", "TRIANGULATE")
        out, err = execute_script("scripts/inspection_report.py", {
            "TARGET_NAMES": ["InspectCube"]})
        self.assertIsNone(err, out)
        report = parse_report(out, "MCP_INSPECTION_REPORT")["targets"][0]
        self.assertEqual(report["base_faces"], 6)
        self.assertEqual(report["faces"], 12)
        self.assertEqual(report["triangles"], 12)
        self.assertTrue(report["evaluated"])
        self.assertEqual(mod.type, "TRIANGULATE")
        self.assertEqual(len(cube.data.polygons), 6)

    def test_GLTF_binary_roundtrip_import_reads_geometry(self):
        obj = self.cube("RoundTripAsset")
        obj.location = (1.0, 2.0, 3.0)
        bpy.context.view_layer.update()
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "roundtrip.glb")
            out, err = run_script("export_asset.py", OBJECTS=["RoundTripAsset"],
                                  PATH=path, FORMAT="GLB", TRIANGULATE=True)
            self.assertIsNone(err, out)
            self.assertTrue(Path(path).is_file())
            self.assertEqual([o.name for o in bpy.data.objects if o.type == "MESH"],
                             ["RoundTripAsset"])
            bpy.ops.wm.read_factory_settings(use_empty=True)
            result = bpy.ops.import_scene.gltf(filepath=path)
            self.assertIn("FINISHED", result)
            meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
            self.assertTrue(meshes, "Round trip should import at least one mesh")
            total_polygons = sum(len(o.data.polygons) for o in meshes)
            self.assertGreaterEqual(total_polygons, 12)
            self.assertTrue(all(len(o.data.vertices) > 0 for o in meshes))

    def test_GLTF_roundtrip_preserves_static_asset_bounds_uv_and_material_presence(self):
        """Blender-to-Blender GLB contract, NOT a Roblox/Godot/Unity import test."""
        from mathutils import Vector
        obj = self.cube("GameReadyCrate")
        obj.location = (1.25, -0.75, 2.5)
        if not obj.data.uv_layers:
            obj.data.uv_layers.new(name="UVMap")
        material = bpy.data.materials.new("CratePaint")
        material.use_nodes = True
        obj.data.materials.append(material)
        bpy.context.view_layer.update()

        def world_bounds(mesh_object):
            points = [mesh_object.matrix_world @ Vector(corner) for corner in mesh_object.bound_box]
            return [(min(float(v[i]) for v in points), max(float(v[i]) for v in points))
                    for i in range(3)]

        expected_bounds = world_bounds(obj)
        expected_origin = tuple(float(x) for x in obj.matrix_world.translation)
        before_coords = tuple(tuple(v.co) for v in obj.data.vertices)
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder) / "crate_roundtrip.glb")
            out, err = run_script("export_asset.py", OBJECTS=["GameReadyCrate"],
                                  PATH=path, FORMAT="GLB", TRIANGULATE=True,
                                  ENGINE="GODOT")
            self.assertIsNone(err, out)
            self.assertTrue(Path(path).is_file())
            self.assertEqual(before_coords, tuple(tuple(v.co) for v in obj.data.vertices))
            bpy.ops.wm.read_factory_settings(use_empty=True)
            result = bpy.ops.import_scene.gltf(filepath=path)
            self.assertIn("FINISHED", result)
            meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
            self.assertEqual(len(meshes), 1)
            imported = meshes[0]
            imported_bounds = world_bounds(imported)
            for original_pair, imported_pair in zip(expected_bounds, imported_bounds):
                for expected, actual in zip(original_pair, imported_pair):
                    self.assertAlmostEqual(expected, actual, delta=0.001)
            for expected, actual in zip(expected_origin, imported.matrix_world.translation):
                self.assertAlmostEqual(expected, float(actual), delta=0.001)
            self.assertGreater(len(imported.data.uv_layers), 0)
            self.assertGreater(sum(s.material is not None for s in imported.material_slots), 0)
            imported.data.calc_loop_triangles()
            self.assertEqual(len(imported.data.loop_triangles), 12)

    def test_benchmark_missing_target_does_not_claim_measured(self):
        out, err = execute_script("scripts/benchmark_report.py", {
            "TARGET_NAMES": ["MissingCube"]})
        self.assertIsNone(err, out)
        report = parse_report(out, "MCP_BENCHMARK_REPORT")
        self.assertEqual(report["technical_status"], "NOT VERIFIED")
        self.assertEqual(report["visual_status"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
