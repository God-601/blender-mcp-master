"""Read-only, context-aware evaluated mesh inspection for Blender MCP agents.

Change TARGET_NAMES, POLICIES and RELATIONSHIPS explicitly before executing in Blender.
Measurements are not a substitute for viewport, anatomical, or downstream reviews.
"""
import bpy
import bmesh
import json
import math
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
TARGET_NAMES = ["MCP_HS_Panel"]
POLICIES = {}
RELATIONSHIPS = []
# ----------------------------------------------------------------------------

def result(status, actual, expected=None, note=None):
    entry = {"status": status, "actual": actual}
    if expected is not None:
        entry["expected"] = expected
    if note:
        entry["note"] = note
    return entry


def face_signed_volume(face):
    points = [vert.co for vert in face.verts]
    if len(points) < 3:
        return 0.0
    origin = points[0]
    return sum(origin.dot(points[i].cross(points[i + 1])) / 6.0
               for i in range(1, len(points) - 1))


def face_components(bm):
    """Return edge-connected face islands; loose vertices are reported separately."""
    remaining = set(bm.faces)
    components = []
    while remaining:
        start = remaining.pop()
        stack = [start]
        group = [start]
        while stack:
            face = stack.pop()
            for edge in face.edges:
                for neighbour in edge.link_faces:
                    if neighbour in remaining:
                        remaining.remove(neighbour)
                        stack.append(neighbour)
                        group.append(neighbour)
        components.append(group)
    return components


def world_bounds(obj, bm):
    points = [obj.matrix_world @ vert.co for vert in bm.verts]
    if not points:
        return None
    low = [min(p[axis] for p in points) for axis in range(3)]
    high = [max(p[axis] for p in points) for axis in range(3)]
    return {"min": low, "max": high,
            "dimensions": [high[i] - low[i] for i in range(3)]}


def inspect_mesh(obj, policy, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        return {"name": obj.name, "status": "NOT VERIFIED",
                "reason": "No evaluated mesh available"}
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.normal_update()
        boundary = sum(edge.is_boundary for edge in bm.edges)
        wire = sum(edge.is_wire for edge in bm.edges)
        non_manifold = sum(not edge.is_manifold and not edge.is_boundary and not edge.is_wire
                           for edge in bm.edges)
        inconsistent_winding = sum(edge.is_manifold and not edge.is_contiguous for edge in bm.edges)
        loose = sum(not vertex.link_edges for vertex in bm.verts)
        bounds = world_bounds(obj, bm)
        side = max(bounds["dimensions"]) if bounds else 0.0
        face_epsilon = max(1.0e-16, side * side * 1.0e-12)
        degenerate = sum(face.calc_area() <= face_epsilon for face in bm.faces)
        tris = sum(max(0, len(face.verts) - 2) for face in bm.faces)
        parts = face_components(bm)
        all_closed = bool(bm.faces) and boundary == 0 and wire == 0 and non_manifold == 0 and loose == 0
        matrix_sign = -1 if obj.matrix_world.determinant() < 0 else 1
        volumes = [sum(face_signed_volume(face) for face in group) *
                   obj.matrix_world.determinant() for group in parts] if all_closed else []
        volume_epsilon = max(1e-15, (side ** 3) * 1e-12)
        inverted = sum(volume < -volume_epsilon for volume in volumes)
        zero_volume = sum(abs(volume) <= volume_epsilon for volume in volumes)
        checks = {}
        if degenerate:
            checks["degenerate_faces"] = result("ISSUE", degenerate, 0,
                "Evaluated mesh contains zero-area or very small faces; inspect scale")
        else:
            checks["degenerate_faces"] = result("PASS", 0, 0)
        if loose or wire:
            checks["loose_geometry"] = result("ISSUE", {"vertices": loose, "wire_edges": wire},
                                               {"vertices": 0, "wire_edges": 0})
        else:
            checks["loose_geometry"] = result("PASS", {"vertices": 0, "wire_edges": 0})
        if non_manifold:
            checks["non_manifold_excluding_boundary"] = result("REVIEW", non_manifold, 0,
                "Investigate by target use; open boundaries are counted separately")
        if inconsistent_winding:
            checks["face_winding_continuity"] = result(
                "ISSUE", inconsistent_winding, 0,
                "Adjacent faces disagree on edge direction; signed volume alone can miss this")
        else:
            checks["face_winding_continuity"] = result("PASS", 0, 0)
        if policy.get("solid"):
            checks["closed_solid"] = result(
                "PASS" if all_closed else "ISSUE",
                {"closed": all_closed, "boundary_edges": boundary,
                 "non_manifold_excluding_boundary": non_manifold},
                {"closed": True})
        if policy.get("single_shell"):
            checks["single_shell"] = result("PASS" if len(parts) == 1 else "ISSUE",
                                            len(parts), 1)
        if policy.get("positive_volume"):
            if not all_closed or not parts:
                checks["outward_volume"] = result("NOT VERIFIED", None, "positive signed volume",
                                                  "Volume sign requires closed mesh geometry")
            else:
                good = inverted == 0 and zero_volume == 0 and inconsistent_winding == 0 and all(
                    v > volume_epsilon for v in volumes)
                checks["outward_volume"] = result(
                    "PASS" if good else "ISSUE",
                    {"signed_volumes": volumes, "inverted_shells": inverted,
                     "near_zero_shells": zero_volume}, "all evaluated shells positively oriented",
                    "Negative volume can be intentional for cavity shells; change policy only with evidence")
        if "max_triangles" in policy:
            limit = int(policy["max_triangles"])
            checks["triangle_budget"] = result("PASS" if tris <= limit else "ISSUE", tris, limit)
        if "dimensions" in policy:
            expected = list(map(float, policy["dimensions"]))
            tol = float(policy.get("dimension_tolerance", 0.01))
            if len(expected) != 3 or any(x <= 0 for x in expected) or tol < 0:
                checks["dimensions"] = result("NOT VERIFIED", None, expected, "Invalid dimension policy")
            elif bounds:
                actual = bounds["dimensions"]
                matches = all(abs(a - e) <= tol * e for a, e in zip(actual, expected))
                checks["dimensions"] = result("PASS" if matches else "ISSUE", actual, expected,
                                               "Relative tolerance: " + str(tol))
            else:
                checks["dimensions"] = result("NOT VERIFIED", None, expected, "No evaluated vertices")
        if "ground_z" in policy:
            desired = float(policy["ground_z"])
            tol = max(0.0, float(policy.get("ground_tolerance", 0.005)))
            if bounds:
                z = bounds["min"][2]
                checks["ground_min_z"] = result("PASS" if abs(z - desired) <= tol else "ISSUE",
                                                 z, desired, "Checks minimum height, not structural support")
            else:
                checks["ground_min_z"] = result("NOT VERIFIED", None, desired, "No vertices")
        statuses = [v["status"] for v in checks.values()]
        status = "ISSUE" if "ISSUE" in statuses else (
            "NOT VERIFIED" if "NOT VERIFIED" in statuses else (
            "REVIEW" if "REVIEW" in statuses or not policy else "PASS"))
        return {
            "name": obj.name, "status": status,
            "evaluated": True, "triangles": tris, "faces": len(bm.faces),
            "boundary_edges": boundary, "non_manifold_excluding_boundary": non_manifold,
            "wire_edges": wire, "loose_vertices": loose, "degenerate_faces": degenerate,
            "inconsistent_winding_edges": inconsistent_winding,
            "face_islands": len(parts), "closed": all_closed,
            "signed_shell_volumes_if_closed": volumes,
            "world_transform_mirrored": matrix_sign < 0,
            "world_bounds": bounds, "checks": checks,
            "visual_quality": "NOT VERIFIED",
        }
    finally:
        bm.free()
        evaluated.to_mesh_clear()


def bounds_gap(a, b):
    """Minimum separation of axis-aligned world-space bounding boxes."""
    gaps = [max(0.0, a["min"][i] - b["max"][i], b["min"][i] - a["max"][i])
            for i in range(3)]
    return math.sqrt(sum(g * g for g in gaps))


def inspect_relationship(spec, reports):
    one, two = str(spec.get("a", "")), str(spec.get("b", ""))
    kind = spec.get("type")
    entry = {"a": one, "b": two, "type": kind}
    if one not in reports or two not in reports:
        entry.update(result("NOT VERIFIED", None, note="Missing or invalid mesh targets"))
        return entry
    a, b = reports[one].get("world_bounds"), reports[two].get("world_bounds")
    if not a or not b:
        entry.update(result("NOT VERIFIED", None, note="No evaluated world bounds"))
        return entry
    gap = bounds_gap(a, b)
    if kind == "max_aabb_gap":
        threshold = float(spec.get("max_gap", 0.01))
        if threshold < 0:
            entry.update(result("NOT VERIFIED", gap, threshold, "Invalid gap threshold"))
        else:
            # Bounds close together do not prove actual surface contact.
            entry.update(result("ISSUE" if gap > threshold else "REVIEW", gap, threshold,
                "AABB separation only; a small gap cannot prove mesh contact"))
    elif kind == "no_aabb_overlap":
        overlapping = gap <= 1e-12
        entry.update(result("REVIEW" if overlapping else "PASS", overlapping, False,
            "Overlapping AABBs may be harmless; check actual surfaces before calling intersection"))
    else:
        entry.update(result("NOT VERIFIED", None, note="Unsupported relationship policy"))
    return entry


def main():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    reports, missing, invalid = {}, [], []
    for name in dict.fromkeys(TARGET_NAMES):
        obj = bpy.data.objects.get(name)
        if obj is None:
            missing.append(name)
        elif obj.type != "MESH":
            invalid.append({"name": name, "type": obj.type})
        else:
            try:
                reports[name] = inspect_mesh(obj, POLICIES.get(name, {}), depsgraph)
            except Exception as exc:
                reports[name] = {"name": name, "status": "NOT VERIFIED",
                                 "error": str(exc), "visual_quality": "NOT VERIFIED"}
    relations = [inspect_relationship(spec, reports) for spec in RELATIONSHIPS]
    statuses = [r["status"] for r in reports.values()] + [r["status"] for r in relations]
    overall = ("ISSUE" if "ISSUE" in statuses else
               "NOT VERIFIED" if missing or invalid or not statuses or "NOT VERIFIED" in statuses else
               "REVIEW" if "REVIEW" in statuses else "PASS")
    payload = {
        "blender_version": bpy.app.version_string,
        "mode": "read-only evaluated geometry; NOT a visual inspector",
        "targets": list(reports.values()),
        "missing_targets": missing,
        "non_mesh_targets": invalid,
        "relationships": relations,
        "overall_technical": overall,
        "overall_visual": "NOT VERIFIED",
    }
    print("MCP_PROFESSIONAL_INSPECTION_BEGIN")
    print(json.dumps(payload, sort_keys=True, indent=2))
    print("MCP_PROFESSIONAL_INSPECTION_END")


if __name__ == "__main__":
    main()
