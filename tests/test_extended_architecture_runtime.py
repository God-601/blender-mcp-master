"""Runtime coverage for the extended Blender MCP Master architecture scripts."""
import contextlib
import io
import json
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

ROOT = Path(__file__).resolve().parents[1]


def execute_script(relative_path, replacements=None):
    path = ROOT / relative_path
    source = path.read_text(encoding="utf-8")
    for name, value in (replacements or {}).items():
        pattern = rf"^{name}\s*=\s*\[.*?^\]" if isinstance(value, list) else rf"^{name}\s*=.*$"
        source, count = re.subn(
            pattern, lambda _m, n=name, v=value: f"{n} = {v!r}",
            source, count=1, flags=re.M | (re.S if isinstance(value, list) else 0)
        )
        if count != 1:
            raise AssertionError(f"configuration {name} not found in {relative_path}")
    output = io.StringIO()
    error = None
    with contextlib.redirect_stdout(output):
        try:
            exec(compile(source, str(path), "exec"), {"__name__": "__main__"})
        except Exception as exc:
            error = exc
    return output.getvalue(), error


def add_source_cube(name="Source"):
    bpy.ops.mesh.primitive_cube_add(size=2.0)
    obj = bpy.context.object
    obj.name = name
    return obj


@unittest.skipIf(bpy is None, "bpy (Blender as a Python module) is not installed")
class ExtendedArchitectureRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_mesh_operations_duplicate_source_and_add_non_destructive_modifiers(self):
        source = add_source_cube()
        original_mesh = source.data
        original_vertices = len(source.data.vertices)
        specs = [{
            "source": "Source", "output": "Source_Processed",
            "operations": [
                {"type": "bevel", "width": 0.04, "segments": 2},
                {"type": "weighted_normal"},
                {"type": "boolean_difference", "dimensions": (0.5, 0.5, 0.5),
                 "location": (0.5, 0.0, 0.0)}
            ]
        }]
        out, err = execute_script("scripts/mesh_operations.py", {"TARGETS": specs})
        self.assertIsNone(err, out)
        result = bpy.data.objects["Source_Processed"]
        self.assertIs(source.data, original_mesh)
        self.assertEqual(len(source.data.vertices), original_vertices)
        self.assertEqual([m.type for m in result.modifiers], ["BEVEL", "WEIGHTED_NORMAL", "BOOLEAN"])
        self.assertTrue(any(obj.name.endswith("_Cutter_03") for obj in bpy.data.objects))

    def test_mesh_operations_reject_existing_output(self):
        add_source_cube()
        existing = add_source_cube("Output")
        out, err = execute_script("scripts/mesh_operations.py", {
            "TARGETS": [{"source": "Source", "output": "Output", "operations": []}]
        })
        self.assertIsNone(err, out)
        self.assertIs(bpy.data.objects["Output"], existing)
        self.assertIn("output already exists", out)

    def test_hard_surface_builder_creates_recess_boolean_and_fasteners(self):
        out, err = execute_script("scripts/hard_surface_builder.py")
        self.assertIsNone(err, out)
        panel = bpy.data.objects["MCP_HS_Panel"]
        self.assertEqual(panel.modifiers[-1].type, "BOOLEAN")
        self.assertEqual(len([o for o in bpy.data.objects if "_Fastener_" in o.name]), 4)
        for obj in [o for o in bpy.data.objects if "_Fastener_" in o.name]:
            self.assertAlmostEqual(obj.rotation_euler.x, 1.57079632679, places=5)
        cutter = bpy.data.objects["MCP_HS_Panel_Pocket_Cutter"]
        self.assertTrue(cutter.hide_render)

    def test_geometry_nodes_builder_exposes_editable_dimensions(self):
        out, err = execute_script("scripts/geometry_nodes_builder.py")
        self.assertIsNone(err, out)
        obj = bpy.data.objects["MCP_Parametric_Panel"]
        self.assertEqual(obj.modifiers[0].type, "NODES")
        group = obj.modifiers[0].node_group
        self.assertIsNotNone(group)
        if hasattr(group, "interface"):
            self.assertIsNotNone(group.interface.items_tree.get("Dimensions"))
        self.assertTrue(any(node.bl_idname == "GeometryNodeMeshCube" for node in group.nodes))

    def test_organic_tree_is_seeded_and_creates_branches_and_canopy(self):
        out, err = execute_script("scripts/organic_tree_builder.py")
        self.assertIsNone(err, out)
        names = [obj.name for obj in bpy.data.objects]
        self.assertIn("MCP_Tree_Trunk", names)
        self.assertEqual(len([n for n in names if "_Branch_" in n]), 7)
        self.assertEqual(len([n for n in names if "_Canopy_" in n]), 9)
        first_positions = [tuple(round(v, 5) for v in bpy.data.objects[n].location)
                           for n in sorted(names) if "_Canopy_" in n]
        bpy.ops.wm.read_factory_settings(use_empty=True)
        out, err = execute_script("scripts/organic_tree_builder.py")
        self.assertIsNone(err, out)
        second_positions = [tuple(round(v, 5) for v in bpy.data.objects[n].location)
                            for n in sorted(bpy.data.objects.keys()) if "_Canopy_" in n]
        self.assertEqual(first_positions, second_positions)

    def test_localized_correction_changes_only_duplicate(self):
        source = add_source_cube()
        source.scale = (2.0, 1.0, 0.5)
        original_scale = source.scale.copy()
        out, err = execute_script("scripts/localized_correction.py", {
            "CORRECTIONS": [{
                "source": "Source", "output": "Source_Fixed",
                "operations": [{"type": "apply_scale_to_mesh"}, {"type": "recalculate_normals"}]
            }]
        })
        self.assertIsNone(err, out)
        corrected = bpy.data.objects["Source_Fixed"]
        self.assertEqual(tuple(round(v, 5) for v in source.scale), tuple(round(v, 5) for v in original_scale))
        self.assertEqual(tuple(round(v, 5) for v in corrected.scale), (1.0, 1.0, 1.0))
        self.assertEqual(tuple(round(v, 5) for v in corrected.dimensions), tuple(round(v, 5) for v in source.dimensions))

    def test_inspection_report_is_read_only_and_measures_explicit_targets(self):
        source = add_source_cube()
        before = (len(source.data.vertices), len(source.data.polygons), tuple(source.location))
        out, err = execute_script("scripts/inspection_report.py", {"TARGET_NAMES": ["Source"]})
        self.assertIsNone(err, out)
        payload = out.split("MCP_INSPECTION_REPORT_BEGIN\n", 1)[1].split("\nMCP_INSPECTION_REPORT_END", 1)[0]
        report = json.loads(payload)
        self.assertEqual(report["targets"][0]["vertices"], 8)
        after = (len(source.data.vertices), len(source.data.polygons), tuple(source.location))
        self.assertEqual(before, after)

    def test_technique_history_persists_in_tagged_blend_text(self):
        out, err = execute_script("scripts/technique_history.py")
        self.assertIsNone(err, out)
        text = bpy.data.texts["MCP_Technique_History.json"]
        self.assertEqual(text.get("_blender_mcp_technique_history"), "technique_history_v1")
        records = json.loads(text.as_string())
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["status"], "USER_REVIEW_REQUIRED")

    def test_capability_probe_and_benchmark_report_are_machine_readable(self):
        out, err = execute_script("scripts/capability_probe.py")
        self.assertIsNone(err, out)
        payload = out.split("MCP_CAPABILITY_PROBE_BEGIN\n", 1)[1].split("\nMCP_CAPABILITY_PROBE_END", 1)[0]
        self.assertTrue(json.loads(payload)["mesh"])
        add_source_cube("Chair_Seat")
        out, err = execute_script("scripts/benchmark_report.py", {
            "TARGET_NAMES": ["Chair_Seat"], "BENCHMARK_ID": "B01", "PROMPT_VERSION": "1"
        })
        self.assertIsNone(err, out)
        payload = out.split("MCP_BENCHMARK_REPORT_BEGIN\n", 1)[1].split("\nMCP_BENCHMARK_REPORT_END", 1)[0]
        report = json.loads(payload)
        self.assertEqual(report["benchmark_id"], "B01")
        self.assertEqual(report["targets"][0]["name"], "Chair_Seat")
        self.assertIsNone(report["visual_scores"])
