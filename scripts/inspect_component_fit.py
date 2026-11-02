"""Read-only, explicit-pair component join/penetration *candidate* inspector.

Use this to focus visual review of accidental beam-through-wall and leg-through-seat
defects. Does not prove a correct physical fit, actual volume overlap, joint
watertightness, or absence of penetration in nested shells or face islands.
Blender bpy runtime only; does not alter source objects, selection or scene.
"""
import bpy
import bmesh
import json
import math
from mathutils.bvhtree import BVHTree

# ---- CONFIG: edit before running --------------------------------------------
CHECKS = []  # [{"a":"Leg", "b":"Seat", "expectation":"surface_joint"}]
# expectation: "surface_joint", "no_penetration", or "intentional_embed".
DEFAULT_MAX_GAP = 0.002  # In scene units; not universally 2 mm.
EPSILON = 1e-6           # AABB numerical tolerance in scene units.
MAX_CHECKS = 25
MAX_TRIANGLES_PER_MESH = 20000
MAX_REPORTED_TRIANGLE_PAIRS = 15
# -----------------------------------------------------------------------------


def _snapshot(name, depsgraph):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        raise ValueError("missing or non-mesh target: " + str(name))
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    if mesh is None:
        raise ValueError("evaluated mesh unavailable: " + str(name))
    bm = bmesh.new()
    try:
        ntris = sum(max(0, len(face.vertices) - 2) for face in mesh.polygons)
        if not 0 < ntris <= MAX_TRIANGLES_PER_MESH:
            raise ValueError("evaluated mesh has no faces or exceeds triangle cap")
        bm.from_mesh(mesh)
        if not bm.verts or not bm.faces:
            raise ValueError("no measurable world-space mesh")
        # Transform only the temporary BMesh, NEVER the original object/mesh.
        bmesh.ops.transform(bm, matrix=eval_obj.matrix_world.copy(), verts=list(bm.verts))
        mins = [min(v.co[i] for v in bm.verts) for i in range(3)]
        maxs = [max(v.co[i] for v in bm.verts) for i in range(3)]
        if not all(math.isfinite(x) for x in mins + maxs):
            raise ValueError("non-finite world-space coordinates")
        tree = BVHTree.FromBMesh(bm, epsilon=0.0)
        return {"name": name, "min": mins, "max": maxs, "triangles": ntris, "tree": tree}
    finally:
        bm.free()
        eval_obj.to_mesh_clear()


def _pair(spec, depsgraph):
    entry = {
        "a": spec.get("a") if isinstance(spec, dict) else None,
        "b": spec.get("b") if isinstance(spec, dict) else None,
        "expectation": spec.get("expectation") if isinstance(spec, dict) else None,
        "status": "NOT VERIFIED", "actual_joint_quality": "NOT VERIFIED",
        "actual_volume_intersection": "NOT VERIFIED",
    }
    if not isinstance(spec, dict):
        entry["error"] = "spec must be an object with a, b, expectation"
        return entry
    a, b, expectation = spec.get("a"), spec.get("b"), spec.get("expectation")
    if (not isinstance(a, str) or not a.strip() or not isinstance(b, str)
            or not b.strip() or a == b):
        entry["error"] = "two different explicitly named objects are required"
        return entry
    if expectation not in {"surface_joint", "no_penetration", "intentional_embed"}:
        entry["error"] = "unsupported expectation"
        return entry
    try:
        max_gap = float(spec.get("max_gap", DEFAULT_MAX_GAP))
        if not math.isfinite(max_gap) or max_gap < 0:
            raise ValueError("max_gap must be a finite nonnegative number")
        if expectation == "intentional_embed" and not str(spec.get("reason", "")).strip():
            raise ValueError("intentional_embed requires a documented reason")
        first = _snapshot(a, depsgraph)
        second = _snapshot(b, depsgraph)
        separations = [max(0.0, first["min"][i] - second["max"][i],
                           second["min"][i] - first["max"][i]) for i in range(3)]
        shared = [min(first["max"][i], second["max"][i]) -
                  max(first["min"][i], second["min"][i]) for i in range(3)]
        gap = math.sqrt(sum(x * x for x in separations))
        positive_volume_aabb = all(x > EPSILON for x in shared)
        candidates = first["tree"].overlap(second["tree"]) if gap <= EPSILON else []
        supported_axes = [i for i, length in enumerate(shared) if length > EPSILON]
        nearly_touching = [i for i, length in enumerate(shared)
                           if -max_gap <= length <= EPSILON]
        if positive_volume_aabb:
            contact_case = "volume_overlap_candidate"
        elif len(supported_axes) == 2 and len(nearly_touching) == 1:
            contact_case = "face_plane_candidate"
        elif gap > max_gap:
            contact_case = "separated_beyond_tolerance"
        elif len(supported_axes) < 2:
            contact_case = "edge_corner_or_diagonal_candidate"
        else:
            contact_case = "uncertain_aabb_contact"
        entry.update({
            "aabb_gap": round(gap, 8),
            "aabb_positive_volume_overlap": positive_volume_aabb,
            "aabb_overlap_lengths": [round(x, 8) for x in shared],
            "aabb_separation_by_axis": [round(x, 8) for x in separations],
            "aabb_face_support_axes": supported_axes,
            "aabb_contact_case": contact_case,
            "triangle_contact_candidates": len(candidates),
            "triangle_candidate_examples": [[int(x), int(y)] for x, y in
                                             candidates[:MAX_REPORTED_TRIANGLE_PAIRS]],
            "measured_evaluated_triangles": [first["triangles"], second["triangles"]],
        })
        if expectation == "surface_joint":
            if gap > max_gap:
                entry["status"] = "ISSUE"
                entry["note"] = "Definite AABB separation beyond required joint tolerance"
            elif not positive_volume_aabb and len(supported_axes) < 2:
                entry["status"] = "ISSUE"
                entry["note"] = ("AABB geometry has no two overlapping axes to support a face-area joint; "
                                 "only edge/corner/diagonal proximity is possible at this tolerance")
            else:
                entry["status"] = "REVIEW"
                entry["note"] = ("Bounds near or overlapping, but correct seam, insertion depth, "
                                 "and true face-to-face contact require visual inspection")
        elif expectation == "no_penetration":
            if not positive_volume_aabb:
                entry["status"] = "PASS"
                entry["note"] = ("No positive AABB *volume* overlap; this excludes volumetric "
                                 "penetration but does not verify surface appearance")
            else:
                entry["status"] = "REVIEW"
                entry["note"] = ("AABB volumes overlap; BVH triangles are candidates, not a "
                                 "volume proof. Interpenetration or full containment must be checked.")
        else:
            entry["status"] = "REVIEW"
            entry["reason"] = str(spec["reason"])
            entry["note"] = ("User-declared intentional embed; verify joinery depth, internal faces, "
                             "shading and silhouette; never auto-dismiss")
    except Exception as exc:
        entry["status"] = "NOT VERIFIED"
        entry["error"] = str(exc)
    return entry


def main():
    payload = {
        "blender_version": bpy.app.version_string,
        "mode": "read-only evaluated object pairs (BVH surface candidates + world AABB)",
        "overall": "NOT VERIFIED",
        "visual_quality": "NOT VERIFIED",
        "engine_collision": "NOT VERIFIED",
        "within_single_mesh_islands": "NOT VERIFIED",
        "limitations": [
            "AABB overlap is NOT proof of intersecting surfaces; boxes can overlap while geometry does not.",
            "BVH surface triangles near a shared face may touch without harmful penetration.",
            "AABB face-plane support is only a necessary bounding-box condition, not proof of face-area contact.",
            "Full containment and unrelated islands in one object are not proven by this script.",
            "No automatic realignment, booleans, object deletion or material edits are performed.",
        ],
        "pairs": [],
    }
    if not isinstance(CHECKS, list) or not CHECKS or len(CHECKS) > MAX_CHECKS:
        payload["reason"] = "Supply 1 to 25 explicitly named object-pair CHECKS"
    elif not math.isfinite(EPSILON) or EPSILON <= 0:
        payload["reason"] = "EPSILON must be finite and positive"
    else:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        payload["pairs"] = [_pair(spec, depsgraph) for spec in CHECKS]
        statuses = {x["status"] for x in payload["pairs"]}
        payload["overall"] = ("ISSUE" if "ISSUE" in statuses else
                              "NOT VERIFIED" if "NOT VERIFIED" in statuses else
                              "REVIEW" if "REVIEW" in statuses else "PASS")
    print("MCP_COMPONENT_FIT_BEGIN")
    print(json.dumps(payload, sort_keys=True, indent=2))
    print("MCP_COMPONENT_FIT_END")


if __name__ == "__main__":
    main()
