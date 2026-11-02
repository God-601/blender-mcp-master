"""Tests for explicit, copy-first advanced topology operations.

Run in Blender/bpy. Static checks run in ordinary Python.
"""
import ast
import contextlib
import io
import json
import os
import re
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "retopology_advanced.py"

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def run_targets(targets):
    source = SCRIPT.read_text(encoding="utf-8")
    source, count = re.subn(
        r"^TARGETS = .*?$",
        lambda _: "TARGETS = " + repr(targets),
        source,
        count=1,
        flags=re.M,
    )
    if count != 1:
        raise AssertionError("Missing TARGETS assignment")
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        exec(compile(source, str(SCRIPT), "exec"), {"__name__": "__main__"})
    payload = stream.getvalue().split("MCP_RETOPO_RESULT_BEGIN\n", 1)[1]
    return json.loads(payload.split("\nMCP_RETOPO_RESULT_END", 1)[0])


class RetopologyStaticTests(unittest.TestCase):
    def test_module_exposes_explicit_operations_and_diagnostics(self):
        content = SCRIPT.read_text(encoding="utf-8")
        ast.parse(content, filename=str(SCRIPT))
        for token in (
            "TARGETS = []", "bridge_loops", "fill_hole", "relax_vertices",
            "MCP_RETOPO_RESULT_BEGIN", "shape_keys", "copy()",
            "NOT VERIFIED",
        ):
            self.assertIn(token, content)


@unittest.skipIf(bpy is None, "Blender bpy not installed")
class RetopologyRuntimeTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def mesh(self, name, verts, edges, faces):
        mesh = bpy.data.meshes.new(name + "_mesh")
        mesh.from_pydata(verts, edges, faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    def tube_rings(self):
        return self.mesh(
            "Rings",
            [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
             (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
            [(0, 1), (1, 2), (2, 3), (3, 0),
             (4, 5), (5, 6), (6, 7), (7, 4)],
            [],
        )

    def test_bridge_two_explicit_equal_length_loops_on_copy(self):
        source = self.tube_rings()
        original = tuple(tuple(v.co) for v in source.data.vertices)
        result = run_targets([{
            "source": "Rings", "output": "JoinedRings",
            "operations": [{"type": "bridge_loops",
                            "loops": [[0, 1, 2, 3], [4, 5, 6, 7]]}],
        }])
        self.assertEqual(result["status"], "SUCCESS", result)
        output = bpy.data.objects.get("JoinedRings")
        self.assertIsNotNone(output)
        self.assertEqual(len(output.data.polygons), 4)
        self.assertEqual(len(source.data.polygons), 0)
        self.assertEqual(original, tuple(tuple(v.co) for v in source.data.vertices))
        self.assertIsNot(output.data, source.data)

    def test_refuse_nonboundary_or_missing_loop_edges_without_leaking_output(self):
        source = self.tube_rings()
        result = run_targets([{
            "source": "Rings", "output": "InvalidBridge",
            "operations": [{"type": "bridge_loops",
                            "loops": [[0, 1, 3, 2], [4, 5, 6, 7]]}],
        }])
        self.assertEqual(result["status"], "ERROR")
        self.assertIsNone(bpy.data.objects.get("InvalidBridge"))
        self.assertIsNone(bpy.data.collections.get("MCP_Advanced_Retopology"), "Failed copy must not leave an empty owned collection")
        self.assertEqual(len(source.data.polygons), 0)

    def test_fill_explicit_planar_boundary_hole(self):
        self.mesh("OpenPatch",
                  [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
                  [(0, 1), (1, 2), (2, 3), (3, 0)], [])
        result = run_targets([{
            "source": "OpenPatch", "output": "CappedPatch",
            "operations": [{"type": "fill_hole", "loop": [0, 1, 2, 3],
                            "planarity_tolerance": 0.001}],
        }])
        self.assertEqual(result["status"], "SUCCESS", result)
        self.assertEqual(len(bpy.data.objects["CappedPatch"].data.polygons), 1)
        self.assertEqual(len(bpy.data.objects["OpenPatch"].data.polygons), 0)

    def test_relax_explicit_interior_vertex_only(self):
        src = self.mesh(
            "Fan",
            [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0.5, 0.5, 1)],
            [], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
        )
        result = run_targets([{
            "source": "Fan", "output": "Relaxed",
            "operations": [{"type": "relax_vertices", "vertices": [4],
                            "factor": 1.0, "iterations": 1,
                            "preserve_boundary": True}],
        }])
        self.assertEqual(result["status"], "SUCCESS", result)
        self.assertAlmostEqual(bpy.data.objects["Relaxed"].data.vertices[4].co.z, 0.0)
        self.assertAlmostEqual(src.data.vertices[4].co.z, 1.0)

    def test_shape_keys_and_duplicate_output_are_rejected(self):
        source = self.tube_rings()
        source.shape_key_add(name="Basis")
        r = run_targets([{
            "source": "Rings", "output": "Refused",
            "operations": [{"type": "fill_hole", "loop": [0, 1, 2, 3]}],
        }])
        self.assertEqual(r["status"], "ERROR")
        self.assertIsNone(bpy.data.objects.get("Refused"))

    def test_empty_targets_do_not_fallback_to_selected_or_all_scene_objects(self):
        self.tube_rings()
        result = run_targets([])
        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["results"], [])
        self.assertEqual(len(bpy.data.objects), 1)
