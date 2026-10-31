"""benchmark_report.py — technical metrics for explicit benchmark targets.

This script does not assign artistic scores. It reports measurable scene evidence that can
be paired with fixed-angle MCP captures and a human/agent visual rubric.
"""
import bpy
import bmesh
import json

# ---- CONFIG ----------------------------------------------------------------
BENCHMARK_ID = "B01"
PROMPT_VERSION = "1"
TARGET_NAMES = ["Chair_Seat", "Chair_Back", "Chair_Leg_FL", "Chair_Leg_FR"]
# ----------------------------------------------------------------------------


def metrics(obj):
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold)
        boundary = sum(1 for edge in bm.edges if edge.is_boundary)
    finally:
        bm.free()
    return {
        "name": obj.name,
        "dimensions": [round(float(v), 5) for v in obj.dimensions],
        "vertices": len(obj.data.vertices),
        "edges": len(obj.data.edges),
        "faces": len(obj.data.polygons),
        "triangles": sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons),
        "non_manifold_edges": non_manifold,
        "boundary_edges": boundary,
        "modifier_types": [mod.type for mod in obj.modifiers],
        "material_count": len(obj.data.materials),
    }


missing = [name for name in TARGET_NAMES if bpy.data.objects.get(name) is None]
objects = [bpy.data.objects[name] for name in TARGET_NAMES if bpy.data.objects[name] is not None]
result = {
    "benchmark_id": BENCHMARK_ID,
    "prompt_version": PROMPT_VERSION,
    "blender_version": bpy.app.version_string,
    "targets": [metrics(obj) for obj in objects if obj.type == "MESH"],
    "missing_targets": missing,
    "technical_status": "NOT VERIFIED" if missing or not objects else "MEASURED",
    "visual_scores": None,
    "visual_status": "NOT VERIFIED",
}
print("MCP_BENCHMARK_REPORT_BEGIN")
print(json.dumps(result, indent=2, sort_keys=True))
print("MCP_BENCHMARK_REPORT_END")
