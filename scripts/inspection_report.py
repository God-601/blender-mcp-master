"""Read-only technical report on evaluated geometry for explicit mesh targets."""
import bpy
import bmesh
import json

# ---- CONFIG ----------------------------------------------------------------
TARGET_NAMES = ["MCP_HS_Panel"]
# ----------------------------------------------------------------------------


def inspect_object(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        return {"name": obj.name, "status": "NOT VERIFIED",
                "reason": "No evaluated mesh"}
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold
                           and not edge.is_boundary and not edge.is_wire)
        boundary = sum(1 for edge in bm.edges if edge.is_boundary)
        wire = sum(1 for edge in bm.edges if edge.is_wire)
        loose_vertices = sum(1 for vert in bm.verts if not vert.link_edges)
        inconsistent_winding = sum(1 for edge in bm.edges if edge.is_manifold and not edge.is_contiguous)
        count_tris = sum(max(0, len(face.verts) - 2) for face in bm.faces)
        return {
            "name": obj.name,
            "type": obj.type,
            "evaluated": True,
            "dimensions": [round(float(v), 6) for v in obj.dimensions],
            "location": [round(float(v), 6) for v in obj.location],
            "base_faces": len(obj.data.polygons),
            "base_triangles": sum(max(0, len(poly.vertices) - 2) for poly in obj.data.polygons),
            "vertices": len(bm.verts),
            "edges": len(bm.edges),
            "faces": len(bm.faces),
            "triangles": count_tris,
            "non_manifold_edges": non_manifold,
            "boundary_edges": boundary,
            "wire_edges": wire,
            "loose_vertices": loose_vertices,
            "inconsistent_winding_edges": inconsistent_winding,
            "modifiers": [{"name": mod.name, "type": mod.type} for mod in obj.modifiers],
            "materials": [mat.name if mat else None for mat in obj.data.materials],
            "status": "ISSUE" if wire or loose_vertices or inconsistent_winding else (
                "REVIEW" if non_manifold or boundary else "PASS"),
        }
    finally:
        bm.free()
        evaluated.to_mesh_clear()


missing = [name for name in TARGET_NAMES if bpy.data.objects.get(name) is None]
non_mesh = [name for name in TARGET_NAMES
            if bpy.data.objects.get(name) is not None and bpy.data.objects[name].type != "MESH"]
depsgraph = bpy.context.evaluated_depsgraph_get()
reports = [
    inspect_object(bpy.data.objects[name], depsgraph)
    for name in TARGET_NAMES
    if bpy.data.objects.get(name) is not None and bpy.data.objects[name].type == "MESH"
]
payload = {
    "blender_version": bpy.app.version_string,
    "targets": reports,
    "missing_targets": missing,
    "non_mesh_targets": non_mesh,
    "overall": "NOT VERIFIED" if missing or non_mesh or not reports
               or any(item["status"] == "NOT VERIFIED" for item in reports) else (
        "ISSUE" if any(item["status"] == "ISSUE" for item in reports) else
        "REVIEW" if any(item["status"] == "REVIEW" for item in reports) else "PASS"
    ),
}
print("MCP_INSPECTION_REPORT_BEGIN")
print(json.dumps(payload, indent=2, sort_keys=True))
print("MCP_INSPECTION_REPORT_END")
