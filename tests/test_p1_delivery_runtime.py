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

    def test_benchmark_missing_target_does_not_claim_measured(self):
        out, err = execute_script("scripts/benchmark_report.py", {
            "TARGET_NAMES": ["MissingCube"]})
        self.assertIsNone(err, out)
        report = parse_report(out, "MCP_BENCHMARK_REPORT")
        self.assertEqual(report["technical_status"], "NOT VERIFIED")
        self.assertEqual(report["visual_status"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
