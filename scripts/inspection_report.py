"""inspection_report.py — read-only technical report for explicit mesh targets."""
import bpy
import bmesh
import json

# ---- CONFIG ----------------------------------------------------------------
TARGET_NAMES = ["MCP_HS_Panel"]
# ----------------------------------------------------------------------------


def inspect_object(obj):
    mesh = obj.data
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        non_manifold = sum(1 for edge in bm.edges if not edge.is_manifold and not edge.is_boundary and not edge.is_wire)
        boundary = sum(1 for edge in bm.edges if edge.is_boundary)
        wire = sum(1 for edge in bm.edges if edge.is_wire)
        loose_vertices = sum(1 for vert in bm.verts if not vert.link_edges)
    finally:
        bm.free()
    dimensions = [round(float(v), 6) for v in obj.dimensions]
    return {
        "name": obj.name,
        "type": obj.type,
        "dimensions": dimensions,
        "location": [round(float(v), 6) for v in obj.location],
        "vertices": len(mesh.vertices),
        "edges": len(mesh.edges),
        "faces": len(mesh.polygons),
        "triangles": sum(max(0, len(poly.vertices) - 2) for poly in mesh.polygons),
        "non_manifold_edges": non_manifold,
        "boundary_edges": boundary,
        "wire_edges": wire,
        "loose_vertices": loose_vertices,
        "modifiers": [{"name": mod.name, "type": mod.type} for mod in obj.modifiers],
        "materials": [mat.name if mat else None for mat in mesh.materials],
        "status": "ISSUE" if wire or loose_vertices else ("REVIEW" if non_manifold or boundary else "PASS"),
    }


missing = [name for name in TARGET_NAMES if bpy.data.objects.get(name) is None]
non_mesh = [name for name in TARGET_NAMES if bpy.data.objects.get(name) is not None and bpy.data.objects[name].type != "MESH"]
reports = [inspect_object(bpy.data.objects[name]) for name in TARGET_NAMES if bpy.data.objects[name] is not None and bpy.data.objects[name].type == "MESH"]
payload = {
    "blender_version": bpy.app.version_string,
    "targets": reports,
    "missing_targets": missing,
    "non_mesh_targets": non_mesh,
    "overall": "NOT VERIFIED" if missing or non_mesh or not reports else (
        "ISSUE" if any(item["status"] == "ISSUE" for item in reports) else
        "REVIEW" if any(item["status"] == "REVIEW" for item in reports) else "PASS"
    ),
}
print("MCP_INSPECTION_REPORT_BEGIN")
print(json.dumps(payload, indent=2, sort_keys=True))
print("MCP_INSPECTION_REPORT_END")
