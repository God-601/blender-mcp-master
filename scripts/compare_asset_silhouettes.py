"""Read-only paired Blender silhouette *proxy* comparison for optimization.

Compare named source and optimized objects using evaluated world-space mesh
vertices. Orthographic projection and convex-hull area/extents detect large
changes in outer dimensions; holes, concavities, shading, topology and artistic
quality are NOT measured. Never declare a model visually equivalent solely
because this proxy passes. No bpy operator, file save or mesh mutation.
"""
import bpy
import json
import math

# ---- Explicit opt-in configuration -----------------------------------------
PAIRS = []  # [{"source": "Chest_A", "optimized": "Chest_C"}]
MAX_PAIRS = 20
MAX_EVALUATED_VERTICES = 200000
MAX_RELATIVE_DIFFERENCE = 0.08  # An authored project tolerance, not universal.
# ----------------------------------------------------------------------------


def _hull(points):
    pts = sorted(set((float(x), float(y)) for x, y in points))
    if len(pts) <= 1:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def _area(points):
    if len(points) < 3:
        return 0.0
    return abs(sum(points[i][0] * points[(i+1) % len(points)][1]
                   - points[(i+1) % len(points)][0] * points[i][1]
                   for i in range(len(points)))) * 0.5


def _snapshot(name, graph):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        raise ValueError("missing or non-mesh object: " + str(name))
    evaluated = obj.evaluated_get(graph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        raise ValueError("unavailable evaluated mesh: " + name)
    try:
        if not 3 <= len(mesh.vertices) <= MAX_EVALUATED_VERTICES:
            raise ValueError("evaluated mesh vertex count out of range")
        verts = [evaluated.matrix_world @ vert.co for vert in mesh.vertices]
        if any(not all(math.isfinite(float(v[k])) for k in range(3)) for v in verts):
            raise ValueError("non-finite evaluated vertices")
        mesh.calc_loop_triangles()
        triangles = len(mesh.loop_triangles)
        if triangles <= 0:
            raise ValueError("no evaluated triangles")
        sqrt2 = math.sqrt(2)
        projections = {
            "front": [(float(v.x), float(v.z)) for v in verts],
            "side": [(float(v.y), float(v.z)) for v in verts],
            "top": [(float(v.x), float(v.y)) for v in verts],
            "three_quarter": [(float((v.x-v.y)/sqrt2), float(v.z)) for v in verts],
        }
        metrics = {}
        for view, points in projections.items():
            xlo = min(p[0] for p in points)
            xhi = max(p[0] for p in points)
            ylo = min(p[1] for p in points)
            yhi = max(p[1] for p in points)
            metrics[view] = {
                "hull_area": _area(_hull(points)),
                "width": xhi-xlo, "height": yhi-ylo,
            }
        return {"name": name, "evaluated_triangles": triangles, "views": metrics}
    finally:
        evaluated.to_mesh_clear()


def _relative_change(before, after):
    if before == 0 and after == 0:
        return 0.0
    if before <= 1e-12 or after <= 1e-12:
        return 1.0
    return abs(after - before) / before


def compare_pair(pair, graph):
    result = {
        "source": pair.get("source") if isinstance(pair, dict) else None,
        "optimized": pair.get("optimized") if isinstance(pair, dict) else None,
        "status": "NOT VERIFIED",
        "visual_quality": "NOT VERIFIED",
        "actual_render_silhouette": "NOT VERIFIED",
        "negative_space_and_concavity": "NOT VERIFIED",
        "uv_and_shading": "NOT VERIFIED",
    }
    if not isinstance(pair, dict):
        result["error"] = "Each PAIRS entry must be a dictionary"
        return result
    source, dest = pair.get("source"), pair.get("optimized")
    if (not isinstance(source, str) or not source.strip()
            or not isinstance(dest, str) or not dest.strip() or source == dest):
        result["error"] = "Specify two different, nonempty mesh object names"
        return result
    try:
        limit = float(pair.get("max_relative_difference", MAX_RELATIVE_DIFFERENCE))
        if not math.isfinite(limit) or not 0 <= limit < 1:
            raise ValueError("max_relative_difference must be finite in [0,1)")
        before, after = _snapshot(source, graph), _snapshot(dest, graph)
        view_results = {}
        largest = 0.0
        for view in before["views"]:
            metrics = {}
            for key in ("hull_area", "width", "height"):
                old = before["views"][view][key]
                new = after["views"][view][key]
                difference = _relative_change(old, new)
                largest = max(largest, difference)
                metrics[key] = {
                    "source": round(old, 8), "optimized": round(new, 8),
                    "relative_change": round(difference, 6),
                }
            view_results[view] = metrics
        delta = after["evaluated_triangles"] - before["evaluated_triangles"]
        result.update({
            "status": "ISSUE" if largest > limit else "REVIEW",
            "source_evaluated_triangles": before["evaluated_triangles"],
            "optimized_evaluated_triangles": after["evaluated_triangles"],
            "evaluated_triangle_delta": delta,
            "largest_relative_projection_change": round(largest, 6),
            "max_relative_difference": limit,
            "views": view_results,
            "note": ("Projection convex hulls cannot detect lost rivets, holes, bevel "
                     "quality, concavities or changed shading. Review matched real "
                     "images and source/optimized mesh details."),
        })
    except Exception as exc:
        result["error"] = str(exc)
    return result


def main():
    output = {
        "status": "NOT VERIFIED",
        "scope": "explicit_pairs_convex_hull_projection_proxy_not_artistic_validation",
        "blender_version": bpy.app.version_string,
        "pair_results": [],
        "limitations": [
            "Convex hull projection misses concavities, holes, internal details and shading.",
            "Separate object pairs only; multipart assemblies and engine runtime are NOT VERIFIED.",
            "Relative tolerance is project-authored; measured match cannot certify visuals.",
            "Evaluated geometry is read only; no auto-decimation or corrections.",
        ],
    }
    if not isinstance(PAIRS, list) or not 1 <= len(PAIRS) <= MAX_PAIRS:
        output["reason"] = "Provide 1..20 explicit PAIRS"
    else:
        graph = bpy.context.evaluated_depsgraph_get()
        output["pair_results"] = [compare_pair(pair, graph) for pair in PAIRS]
        states = {p["status"] for p in output["pair_results"]}
        output["status"] = ("NOT VERIFIED" if "NOT VERIFIED" in states else
                            "ISSUE" if "ISSUE" in states else "REVIEW")
    print("MCP_SILHOUETTE_PROXY_BEGIN")
    print(json.dumps(output, sort_keys=True, indent=2))
    print("MCP_SILHOUETTE_PROXY_END")


if __name__ == "__main__":
    main()
