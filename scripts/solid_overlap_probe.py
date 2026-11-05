"""Read-only evaluated mesh overlap/containment evidence for named Blender objects.

Works with closed, edge-manifold surface candidates; does NOT prove that two
solids are clean, outward-oriented, non-self-intersecting or physically joined.
BVH overlap catches triangle intersections; ray parity probes catch possible
full containment that surface-overlap-only tests miss. All warnings are REVIEW.
"""
import bpy
import bmesh
import json
import math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

PAIRS = []  # [{"a": "Outer", "b": "Inner"}]
MAX_PAIRS = 20
MAX_TRIANGLES = 30000
MAX_SAMPLES = 24
MAX_RAY_HITS = 128
EPS = 1e-5
DIRECTIONS = tuple(v.normalized() for v in (
    Vector((1, .231, .157)), Vector((.193, 1, .337)), Vector((.377, .119, 1))
))


def _mesh(name, depsgraph):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        raise ValueError("Target missing/non-mesh: " + str(name))
    eval_obj = obj.evaluated_get(depsgraph)
    evaluated = eval_obj.to_mesh()
    if evaluated is None:
        raise ValueError("No evaluated mesh: " + name)
    bm = bmesh.new()
    try:
        bm.from_mesh(evaluated)
        bm.normal_update()
        if not bm.faces or not bm.verts:
            raise ValueError("Empty surface: " + name)
        tri_count = sum(max(0, len(f.verts) - 2) for f in bm.faces)
        if tri_count > MAX_TRIANGLES:
            raise ValueError("Triangle budget exceeded: " + name)
        # Check edge manifoldness before creating diagnostic tree.
        closed = all(len(edge.link_faces) == 2 for edge in bm.edges)
        bmesh.ops.transform(bm, matrix=eval_obj.matrix_world.copy(), verts=list(bm.verts))
        positions = [v.co.copy() for v in bm.verts]
        if not all(math.isfinite(float(x)) for v in positions for x in v):
            raise ValueError("Nonfinite coordinates: " + name)
        step = max(1, (len(positions) + MAX_SAMPLES - 1) // MAX_SAMPLES)
        samples = positions[::step][:MAX_SAMPLES]
        return {
            "name": name, "closed_manifold_candidate": closed,
            "triangles": tri_count, "tree": BVHTree.FromBMesh(bm, epsilon=0.0),
            "samples": samples,
            "bounds": [[min(v[i] for v in positions), max(v[i] for v in positions)]
                       for i in range(3)],
        }
    finally:
        bm.free()
        eval_obj.to_mesh_clear()


def _parity_inside(point, target):
    # Multiple ray directions reduce—but do not eliminate—edge/tangent ambiguity.
    if not target["closed_manifold_candidate"]:
        return None
    opinions = []
    for direction in DIRECTIONS:
        origin = point.copy()
        hits = 0
        for _ in range(MAX_RAY_HITS):
            location, normal, face, distance = target["tree"].ray_cast(origin, direction)
            if location is None:
                break
            if distance <= 2 * EPS:
                return None  # On surface or numerically ambiguous
            hits += 1
            origin = location + direction * (4 * EPS)
        else:
            return None  # Ray exceeded bound
        opinions.append(hits % 2 == 1)
    return opinions[0] if len(set(opinions)) == 1 else None


def inspect_pair(first, second):
    separated = any(first["bounds"][i][1] < second["bounds"][i][0] - EPS or
                    second["bounds"][i][1] < first["bounds"][i][0] - EPS
                    for i in range(3))
    out = {
        "a": first["name"], "b": second["name"],
        "closed_manifold_candidates": [first["closed_manifold_candidate"],
                                       second["closed_manifold_candidate"]],
        "triangles": [first["triangles"], second["triangles"]],
        "status": "REVIEW",
        "actual_volume_intersection": "NOT VERIFIED",
        "visual_quality": "NOT VERIFIED",
    }
    if separated:
        out.update({"status": "MEASURED", "contact_case": "disjoint_aabb",
                    "triangle_candidates": 0,
                    "possible_containment": False})
        return out
    overlaps = first["tree"].overlap(second["tree"])
    out["triangle_candidates"] = len(overlaps)
    out["triangle_examples"] = [[int(a), int(b)] for a, b in overlaps[:12]]
    if overlaps:
        out["contact_case"] = "surface_triangle_overlap_candidate"
    else:
        observations = {}
        for source, target in ((first, second), (second, first)):
            observations[source["name"] + "_inside_" + target["name"]] = [
                _parity_inside(p, target) for p in source["samples"]]
        out["sample_inside_votes"] = {
            name: {"inside": sum(v is True for v in values),
                   "outside": sum(v is False for v in values),
                   "uncertain": sum(v is None for v in values)}
            for name, values in observations.items()
        }
        possible = any(any(v is True for v in values) for values in observations.values())
        out["possible_containment"] = possible
        out["contact_case"] = ("containment_candidate" if possible else
                               "overlap_unresolved_no_surface_candidates")
    out["note"] = ("BVH triangles and ray-parity samples are candidate evidence only; "
                   "self-intersection, inverted normals, near-coplanarity and topology may invalidate classification.")
    return out


def report(pairs):
    if not isinstance(pairs, list) or not 1 <= len(pairs) <= MAX_PAIRS:
        raise ValueError("Specify 1–20 explicit object pairs")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    results = []
    for spec in pairs:
        if not isinstance(spec, dict) or not isinstance(spec.get("a"), str) or not isinstance(spec.get("b"), str):
            results.append({"status": "NOT VERIFIED", "error": "Pair needs named targets"})
            continue
        if not spec["a"].strip() or not spec["b"].strip() or spec["a"] == spec["b"]:
            results.append({"status": "NOT VERIFIED", "error": "Two distinct named targets required"})
            continue
        try:
            results.append(inspect_pair(_mesh(spec["a"], depsgraph),
                                        _mesh(spec["b"], depsgraph)))
        except Exception as exc:
            results.append({"a": spec["a"], "b": spec["b"],
                            "status": "NOT VERIFIED", "error": str(exc)})
    return {
        "mode": "read-only evaluated mesh BVH + bounded ray parity",
        "results": results,
        "actual_joint_quality": "NOT VERIFIED",
        "limitations": ["Requires independent review of surface/containment candidates",
                        "Not a physical collision or watertight certification",
                        "Open, nonmanifold and self-intersecting meshes may be inconclusive"],
    }


if __name__ == "__main__":
    print("MCP_SOLID_OVERLAP_BEGIN")
    print(json.dumps(report(PAIRS), indent=2, sort_keys=True))
    print("MCP_SOLID_OVERLAP_END")
