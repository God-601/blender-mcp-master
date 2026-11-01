"""P1 base-mesh UV overlap, density and inconclusive-state regressions."""
import json
import os
import unittest

try:
    import bpy
except ImportError:
    if os.environ.get("REQUIRE_BPY")=="1":
        raise
    bpy=None
from test_extended_architecture_runtime import execute_script

def report(output):
    return json.loads(output.split("MCP_UV_DIAGNOSTICS_BEGIN\n",1)[1].split(
        "\nMCP_UV_DIAGNOSTICS_END",1)[0])

@unittest.skipIf(bpy is None,"bpy unavailable")
class P1UVDiagnosticTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def two_quads(self, second=None, first=None):
        vertices=[(0,0,0),(1,0,0),(1,1,0),(0,1,0),
                  (2,0,0),(3,0,0),(3,1,0),(2,1,0)]
        mesh=bpy.data.meshes.new("UV_Test_Mesh")
        mesh.from_pydata(vertices,[],[(0,1,2,3),(4,5,6,7)])
        mesh.update()
        a=first or [(0.05,.05),(.45,.05),(.45,.45),(.05,.45)]
        b=second or [(.55,.05),(.95,.05),(.95,.45),(.55,.45)]
        layer=mesh.uv_layers.new(name="UV_Main")
        for i,uv in enumerate(a+b):
            layer.data[i].uv=uv
        obj=bpy.data.objects.new("UV_Test",mesh)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.update()
        return obj

    def analyze(self,**config):
        config.setdefault("TARGETS",["UV_Test"])
        out,err=execute_script("scripts/uv_diagnostics.py",config)
        self.assertIsNone(err,out)
        return report(out)

    def test_separate_islands_have_no_false_overlap_and_even_density(self):
        self.two_quads()
        d=self.analyze()["reports"][0]
        self.assertEqual(d["status"],"MEASURED")
        self.assertEqual(d["overlap_status"],"PASS")
        self.assertEqual(d["overlap_pairs"],0)
        self.assertAlmostEqual(d["density_max_to_min_ratio"],1.0,places=4)
        self.assertEqual(d["island_padding_status"],"NOT VERIFIED")

    def test_coincident_uv_quads_are_detected_as_overlap(self):
        self.two_quads(second=[(.05,.05),(.45,.05),(.45,.45),(.05,.45)])
        d=self.analyze()["reports"][0]
        self.assertEqual(d["overlap_status"],"ISSUE")
        self.assertGreater(d["overlap_pairs"],0)
        self.assertEqual(d["status"],"ISSUE")

    def test_borders_touching_only_do_not_count_as_area_overlap(self):
        self.two_quads(first=[(.05,.05),(.50,.05),(.50,.5),(.05,.5)],
                       second=[(.50,.05),(.95,.05),(.95,.5),(.50,.5)])
        self.assertEqual(self.analyze()["reports"][0]["overlap_pairs"],0)

    def test_stacking_can_be_intentional_but_must_be_reviewed(self):
        self.two_quads(second=[(.05,.05),(.45,.05),(.45,.45),(.05,.45)])
        d=self.analyze(ALLOW_STACKING=True)["reports"][0]
        self.assertEqual(d["overlap_status"],"REVIEW")
        self.assertEqual(d["status"],"REVIEW")

    def test_texel_density_variation_prompts_review_not_fabricated_issue(self):
        self.two_quads(second=[(.55,.05),(.59,.05),(.59,.09),(.55,.09)])
        d=self.analyze()["reports"][0]
        self.assertEqual(d["density_status"],"REVIEW")
        self.assertGreater(d["density_max_to_min_ratio"],5)
        self.assertEqual(d["status"],"REVIEW")

    def test_missing_uv_layer_never_claims_a_measured_result(self):
        bpy.ops.mesh.primitive_cube_add()
        obj=bpy.context.object
        obj.name="UV_Test"
        obj.data.uv_layers.clear()
        d=self.analyze()["reports"][0]
        self.assertEqual(d["status"],"NOT VERIFIED")
        self.assertIn("UV layer",d["reason"])

    def test_missing_target_does_not_pass(self):
        d=self.analyze(TARGETS=["Unknown"]) 
        self.assertEqual(d["summary"],"NOT VERIFIED")
        self.assertEqual(d["reports"][0]["status"],"NOT VERIFIED")

    def test_pairwise_cap_reports_not_verified_not_zero_overlaps(self):
        self.two_quads()
        d=self.analyze(MAX_PAIRWISE_TRIANGLES=2)["reports"][0]
        self.assertEqual(d["overlap_status"],"NOT VERIFIED")
        self.assertIsNone(d["overlap_pairs"])
        self.assertEqual(d["status"],"NOT VERIFIED")

    def test_zero_area_uv_is_an_issue(self):
        self.two_quads(second=[(.7,.2)]*4)
        d=self.analyze()["reports"][0]
        self.assertEqual(d["status"],"ISSUE")
        self.assertGreater(d["degenerate_uv_or_world_triangles"],0)

    def test_diagnostics_preserve_uvs_mesh_and_selection(self):
        obj=self.two_quads()
        before_uv=[tuple(v.uv) for v in obj.data.uv_layers.active.data]
        before_verts=[tuple(v.co) for v in obj.data.vertices]
        before_selected=list(bpy.context.selected_objects)
        d=self.analyze()
        self.assertEqual(d["summary"],"MEASURED")
        self.assertEqual([tuple(v.uv) for v in obj.data.uv_layers.active.data],before_uv)
        self.assertEqual([tuple(v.co) for v in obj.data.vertices],before_verts)
        self.assertEqual(list(bpy.context.selected_objects),before_selected)

if __name__=="__main__":
    unittest.main()
