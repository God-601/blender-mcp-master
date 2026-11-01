"""Read-only benchmark metrics for named targets, using evaluated Blender geometry.

Counts include mesh-producing modifiers. They do not automatically include
separately instanced scene objects or prove visual quality.
"""
import bpy
import bmesh
import json

# ---- CONFIG ----------------------------------------------------------------
BENCHMARK_ID = "B01"
PROMPT_VERSION = "1"
TARGET_NAMES = ["Chair_Seat", "Chair_Back", "Chair_Leg_FL", "Chair_Leg_FR"]
# ----------------------------------------------------------------------------


def metrics(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        return {"name": obj.name, "status": "NOT VERIFIED",
                "reason": "No evaluated mesh"}
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        non_manifold = sum(1 for edge in bm.edges
                           if not edge.is_manifold and not edge.is_boundary and not edge.is_wire)
        boundary = sum(1 for edge in bm.edges if edge.is_boundary)
        points = [obj.matrix_world @ vert.co for vert in bm.verts]
        world_dimensions = (
            [round(max(p[i] for p in points) - min(p[i] for p in points), 5)
             for i in range(3)] if points else None
        )
        return {
            "name": obj.name,
            "status": "MEASURED",
            "evaluated": True,
            "dimensions": [round(float(v), 5) for v in obj.dimensions],
            "evaluated_world_dimensions": world_dimensions,
            "base_faces": len(obj.data.polygons),
            "base_triangles": sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons),
            "vertices": len(bm.verts),
            "edges": len(bm.edges),
            "faces": len(bm.faces),
            "triangles": sum(max(0, len(face.verts) - 2) for face in bm.faces),
            "non_manifold_edges": non_manifold,
            "boundary_edges": boundary,
            "modifier_types": [mod.type for mod in obj.modifiers],
            "material_count": len(obj.data.materials),
        }
    finally:
        bm.free()
        evaluated.to_mesh_clear()


missing = [name for name in TARGET_NAMES if bpy.data.objects.get(name) is None]
objects = [bpy.data.objects[name] for name in TARGET_NAMES if bpy.data.objects.get(name) is not None]
mesh_objects = [obj for obj in objects if obj.type == "MESH"]
non_mesh = [obj.name for obj in objects if obj.type != "MESH"]
depsgraph = bpy.context.evaluated_depsgraph_get()
reports = [metrics(obj, depsgraph) for obj in mesh_objects]
result = {
    "benchmark_id": BENCHMARK_ID,
    "prompt_version": PROMPT_VERSION,
    "blender_version": bpy.app.version_string,
    "targets": reports,
    "non_mesh_targets": non_mesh,
    "missing_targets": missing,
    "technical_status": "NOT VERIFIED" if missing or non_mesh or not reports
                        or any(r["status"] != "MEASURED" for r in reports) else "MEASURED",
    "visual_scores": None,
    "visual_status": "NOT VERIFIED",
}
print("MCP_BENCHMARK_REPORT_BEGIN")
print(json.dumps(result, indent=2, sort_keys=True))
print("MCP_BENCHMARK_REPORT_END")
