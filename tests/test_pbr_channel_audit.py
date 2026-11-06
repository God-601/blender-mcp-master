"""Read-only PBR channel audit: bpy fixtures, no mutation."""
import contextlib
import io
import os
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "pbr_channel_audit.py"
try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY") == "1":
        raise
    bpy = None


def module():
    scope = {"__name__": "__pbr_fixture__"}
    exec(compile(SCRIPT.read_text(encoding="utf-8"), str(SCRIPT), "exec"), scope)
    return scope


class StaticAuditTests(unittest.TestCase):
    def test_readonly_and_no_default_targets(self):
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("TARGETS = []", src)
        self.assertNotIn("bpy.ops.object.delete", src)
        self.assertNotIn("bpy.data.objects.remove", src)


@unittest.skipIf(bpy is None, "bpy not available")
class RuntimeAuditTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def _cube(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        obj.name = "AuditCube"
        obj.data.uv_layers.new(name="UVMap")
        return obj

    def test_missing_and_invalid_targets_fail_without_scene_mutation(self):
        inspect = module()["inspect_targets"]
        self.assertEqual(inspect([])["status"], "NOT VERIFIED")
        self.assertEqual(inspect(["Unknown"])["targets"][0]["status"], "NOT VERIFIED")
        self.assertEqual(len(bpy.data.objects), 0)

    def test_pbr_colorspace_issue_is_diagnostic_not_engine_pass(self):
        obj = self._cube()
        material = bpy.data.materials.new(name="Material")
        material.use_nodes = True
        shader = next(n for n in material.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        tex = material.node_tree.nodes.new("ShaderNodeTexImage")
        image = bpy.data.images.new("Fake_Normal", width=4, height=4, alpha=True)
        tex.image = image
        normal = material.node_tree.nodes.new("ShaderNodeNormalMap")
        material.node_tree.links.new(tex.outputs["Color"], normal.inputs["Color"])
        material.node_tree.links.new(normal.outputs["Normal"], shader.inputs["Normal"])
        obj.data.materials.append(material)
        vertex_count = len(obj.data.vertices)
        snapshot = [tuple(v.co) for v in obj.data.vertices]
        report = module()["inspect_targets"]([obj.name])
        self.assertEqual(report["status"], "ISSUE")
        self.assertEqual(report["targets"][0]["materials"][0]["channels"]["normal"]["status"], "ISSUE")
        self.assertEqual(report["in_engine_material_fidelity"], "NOT VERIFIED")
        self.assertEqual(len(obj.data.vertices), vertex_count)
        self.assertEqual(snapshot, [tuple(v.co) for v in obj.data.vertices])

    def test_missing_uv_is_issue_not_bake_failure_claim(self):
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.object
        obj.name = "NoUV"
        while obj.data.uv_layers:
            obj.data.uv_layers.remove(obj.data.uv_layers[0])
        result = module()["inspect_targets"](["NoUV"])
        self.assertEqual(result["targets"][0]["status"], "ISSUE")
        self.assertEqual(result["actual_bake"], "NOT VERIFIED")


if __name__ == "__main__":
    unittest.main()
