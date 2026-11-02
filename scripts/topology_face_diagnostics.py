"""Read-only Blender topology audit for redundant 4-triangle planar face fans.

Detects a specific 'X across a flat face' pattern: an interior vertex with
four triangular faces forming one planar patch. It reports REVIEW candidates;
it does not dissolve edges or assert that topology is artistically incorrect.

GPU/glTF triangulation is separate from native editable Blender mesh faces.
"""
import bpy
import bmesh
import json
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []  # Explicit object names, never selection/whole-scene fallback.
MAX_TARGETS = 25
MAX_BASE_FACES = 100000
NORMAL_DOT_MIN = 0.9999
PLANAR_RELATIVE_TOL = 1e-5
MAX_EXAMPLES = 25
# ----------------------------------------------------------------------------


def inspect(obj):
    report = {
        "name": obj.name,
        "status": "NOT VERIFIED",
        "scope": "BASE_MESH_EDITABLE_TOPOLOGY_ONLY",
        "visual_quality": "NOT VERIFIED",
        "removal_safety": "NOT VERIFIED",
        "export_round_trip": "NOT VERIFIED",
    }
    if obj.type != "MESH":
        report["reason"] = "not a mesh"
        return report
    if obj.mode != "OBJECT":
        report["reason"] = "mesh must be in Object Mode for this audit"
        return report
    mesh = obj.data
    if len(mesh.polygons) > MAX_BASE_FACES:
        report["reason"] = "base face count exceeds configured cap"
        return report
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.verts.index_update()
        bm.faces.index_update()
        bm.normal_update()
        vertices = list(bm.verts)
        tris = sum(max(0, len(f.verts) - 2) for f in bm.faces)
        triangle_faces = sum(len(f.verts) == 3 for f in bm.faces)
        quad_faces = sum(len(f.verts) == 4 for f in bm.faces)
        ngon_faces = sum(len(f.verts) > 4 for f in bm.faces)
        if not vertices:
            report["reason"] = "mesh has no vertices"
            return report
        low = [min(v.co[k] for v in vertices) for k in range(3)]
        high = [max(v.co[k] for v in vertices) for k in range(3)]
        scale = max(high[k] - low[k] for k in range(3))
        epsilon = max(1e-9, scale * PLANAR_RELATIVE_TOL)
        samples = []
        candidate_count = 0
        for center in vertices:
            # An interior point on a four-triangle planar patch creates a
            # common X-like fan. Other triangulations and nonplanar fans are
            # intentionally NOT classified as these candidates.
            if len(center.link_faces) != 4 or len(center.link_edges) != 4:
                continue
            faces = list(center.link_faces)
            if any(len(f.verts) != 3 for f in faces):
                continue
            outer = {v for f in faces for v in f.verts if v is not center}
            if len(outer) != 4:
                continue
            if any(len(e.link_faces) != 2 for e in center.link_edges):
                continue
            reference = faces[0].normal
            if reference.length < 1e-8:
                continue
            if any(reference.dot(f.normal) < NORMAL_DOT_MIN for f in faces):
                continue
            if any(abs((v.co - center.co).dot(reference)) > epsilon for v in outer):
                continue
            # Four outer edges must form a connected simple ring.
            links = {v: set() for v in outer}
            for face in faces:
                edge_verts = [v for v in face.verts if v is not center]
                if len(edge_verts) != 2:
                    break
                links[edge_verts[0]].add(edge_verts[1])
                links[edge_verts[1]].add(edge_verts[0])
            if any(len(neighbors) != 2 for neighbors in links.values()):
                continue
            # This identifies only a review candidate, not an automatic fix.
            candidate_count += 1
            if len(samples) < MAX_EXAMPLES:
                uv_layer = bm.loops.layers.uv.active
                uv_discontinuity = False
                if uv_layer is not None:
                    # Check the same topological vertex mapped to differing UVs
                    # across the four faces. This is evidence of a seam, not
                    # permission to weld or dissolve any triangle.
                    uv_by_vertex = {}
                    for face in faces:
                        for loop in face.loops:
                            key = loop.vert
                            uv = loop[uv_layer].uv
                            pair = (float(uv.x), float(uv.y))
                            previous = uv_by_vertex.get(key)
                            if previous is not None and (
                                    abs(pair[0] - previous[0]) > 1e-6 or
                                    abs(pair[1] - previous[1]) > 1e-6):
                                uv_discontinuity = True
                            uv_by_vertex[key] = pair
                material_boundary = len({f.material_index for f in faces}) > 1
                shape_key_sensitive = bool(mesh.shape_keys and
                                           len(mesh.shape_keys.key_blocks) > 1)
                samples.append({
                    "center_vertex_index": int(center.index),
                    "center_local": [round(float(x), 6) for x in center.co],
                    "four_triangle_face_indices": sorted(int(f.index) for f in faces),
                    "material_boundary": material_boundary,
                    "uv_seam_candidate": uv_discontinuity,
                    "shape_keys_present": shape_key_sensitive,
                    "recommendation": ("PRESERVE_UNTIL_REVIEW"
                                       if material_boundary or uv_discontinuity or shape_key_sensitive
                                       else "REVIEW_FOR_CLEAN_QUAD_ON_COPY"),
                })
        report.update({
            "status": "REVIEW" if candidate_count else "PASS",
            "base_vertices": len(bm.verts),
            "base_faces": len(bm.faces),
            "base_triangle_faces": triangle_faces,
            "base_quad_faces": quad_faces,
            "base_ngon_faces": ngon_faces,
            "base_render_triangles_before_modifiers": tris,
            "coplanar_four_triangle_fan_candidates": candidate_count,
            "candidate_examples": samples,
            "mesh_has_modifiers": bool(obj.modifiers),
            "note": (
                "Each 4-triangle planar fan may be a needless X-like split, "
                "but intentional vertex, UV, normal, material or deformation "
                "constraints can require it. Human visual/technical review is mandatory."
            ),
        })
        return report
    except Exception as exc:
        report["status"] = "NOT VERIFIED"
        report["reason"] = str(exc)
        return report
    finally:
        bm.free()


def main():
    output = {
        "blender_version": bpy.app.version_string,
        "overall": "NOT VERIFIED",
        "mode": "read-only explicit-target base mesh inspection",
        "targets": [],
        "limits": [
            "Blender quads and n-gons are internally tessellated for rendering; do not equate that with editable triangular faces.",
            "glTF/GLB may encode triangles and split vertices by UV, normal or material seam.",
            "Only four-triangle coplanar fans around a degree-four center vertex are detected; other unnecessary diagonals are NOT VERIFIED.",
            "A zero-candidate result is PASS for this narrow pattern only, not proof of clean topology.",
            "Material/UV discontinuity or shape keys increase the risk of replacing a four-triangle fan; flags are hints only.",
            "No dissolving, merging, modifier application or destructive changes occur.",
        ],
    }
    if not isinstance(TARGETS, list) or not TARGETS or len(TARGETS) > MAX_TARGETS:
        output["reason"] = "Specify 1..25 explicit TARGETS; no fallback"
    else:
        for name in dict.fromkeys(TARGETS):
            obj = bpy.data.objects.get(name) if isinstance(name, str) else None
            if obj is None:
                output["targets"].append({"name": name, "status": "NOT VERIFIED", "reason": "missing object"})
            else:
                output["targets"].append(inspect(obj))
        statuses = {entry["status"] for entry in output["targets"]}
        output["overall"] = ("NOT VERIFIED" if "NOT VERIFIED" in statuses else
                             "REVIEW" if "REVIEW" in statuses else "PASS")
    print("MCP_TOPOLOGY_FACE_AUDIT_BEGIN")
    print(json.dumps(output, sort_keys=True, indent=2))
    print("MCP_TOPOLOGY_FACE_AUDIT_END")


if __name__ == "__main__":
    main()
