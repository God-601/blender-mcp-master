"""Conservative UV-island gutter distance audit for static game meshes.

Read-only base-mesh UV audit for explicitly named objects. It groups polygons
across mesh edges only where both endpoint UVs agree, so UV seams separate
islands. Per-island axis-aligned 2D bounding boxes provide a LOWER BOUND
on spacing: overlapping bounds do not prove actual UV polygons overlap,
and adequate bbox gap does not certify baking or mipmapping.
"""
import bpy
import json
import math

TARGETS = []               # e.g. ["Crate_LOD0"] (explicit, no scene fallback)
UV_LAYER_NAME = ""         # empty = active
TEXTURE_WIDTH = 1024
TEXTURE_HEIGHT = 1024
DESIRED_PADDING_PX = 8     # authored project goal, not universal engine rule
MAX_TARGETS = 25
MAX_POLYGONS = 10000
MAX_ISLANDS = 250
MAX_PAIR_EXAMPLES = 15
UV_MATCH_EPS = 1e-6


def inspect(obj):
    report = {
        "name": obj.name,
        "status": "NOT VERIFIED",
        "baking_quality": "NOT VERIFIED",
        "post_modifier_uv": "NOT VERIFIED",
        "engine_import": "NOT VERIFIED",
        "gutter_distance_is_lower_bound": True,
    }
    if obj.type != "MESH" or obj.mode != "OBJECT":
        report["reason"] = "Require a mesh in Object Mode"
        return report
    mesh = obj.data
    uv = mesh.uv_layers.get(UV_LAYER_NAME) if UV_LAYER_NAME else mesh.uv_layers.active
    if uv is None:
        report["reason"] = "Missing requested UV layer"
        return report
    count = len(mesh.polygons)
    if not 1 <= count <= MAX_POLYGONS:
        report["reason"] = "Base polygon count outside cap"
        return report
    parents = list(range(count))

    def root(index):
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def unite(a, b):
        a, b = root(a), root(b)
        if a != b:
            parents[b] = a

    by_edge = {}
    coordinates = {}
    outside = False
    for face in mesh.polygons:
        indices = list(face.loop_indices)
        points = []
        for idx in indices:
            u, v = (float(x) for x in uv.data[idx].uv)
            if not math.isfinite(u) or not math.isfinite(v):
                report["reason"] = "Nonfinite UV coordinates"
                return report
            outside = outside or u < -UV_MATCH_EPS or v < -UV_MATCH_EPS or u > 1+UV_MATCH_EPS or v > 1+UV_MATCH_EPS
            points.append((u, v))
        coordinates[face.index] = points
        for offset, loop_id in enumerate(indices):
            edge = mesh.loops[loop_id].edge_index
            vertex_a = mesh.loops[loop_id].vertex_index
            vertex_b = mesh.loops[indices[(offset + 1) % len(indices)]].vertex_index
            a_uv, b_uv = points[offset], points[(offset + 1) % len(indices)]
            endpoint_pair = (a_uv, b_uv) if vertex_a <= vertex_b else (b_uv, a_uv)
            by_edge.setdefault(edge, []).append((face.index, endpoint_pair))
    # A mesh edge is UV-continuous when both endpoint UV coordinates match.
    for faces in by_edge.values():
        for i in range(len(faces)):
            for j in range(i + 1, len(faces)):
                first, a_uv = faces[i]
                second, b_uv = faces[j]
                if all(abs(a_uv[v][axis] - b_uv[v][axis]) <= UV_MATCH_EPS
                       for v in range(2) for axis in range(2)):
                    unite(first, second)
    points_by_island = {}
    for face_index, points in coordinates.items():
        points_by_island.setdefault(root(face_index), []).extend(points)
    if len(points_by_island) > MAX_ISLANDS:
        report["reason"] = "UV island count exceeds conservative comparison cap"
        return report
    boxes = []
    for points in points_by_island.values():
        boxes.append((min(x for x, _ in points), max(x for x, _ in points),
                      min(y for _, y in points), max(y for _, y in points)))
    smallest = None
    suspicious = 0
    samples = []
    for i in range(len(boxes)):
        a = boxes[i]
        for j in range(i + 1, len(boxes)):
            b = boxes[j]
            du = max(0.0, a[0] - b[1], b[0] - a[1])
            dv = max(0.0, a[2] - b[3], b[2] - a[3])
            distance = math.hypot(du * TEXTURE_WIDTH, dv * TEXTURE_HEIGHT)
            smallest = distance if smallest is None else min(smallest, distance)
            if distance < DESIRED_PADDING_PX:
                suspicious += 1
                if len(samples) < MAX_PAIR_EXAMPLES:
                    samples.append({"islands": [i, j], "aabb_lower_bound_px": round(distance, 4)})
    report.update({
        "status": ("REVIEW" if outside or suspicious else "MEASURED"),
        "uv_layer": uv.name,
        "base_mesh_polygons": count,
        "uv_islands": len(boxes),
        "texture_size_px": [TEXTURE_WIDTH, TEXTURE_HEIGHT],
        "desired_padding_px": DESIRED_PADDING_PX,
        "lowest_aabb_gutter_bound_px": round(smallest, 4) if smallest is not None else None,
        "suspicious_island_pairs": suspicious,
        "examples": samples,
        "uv_outside_0_1": outside,
        "padding_scope": "UV_ISLAND_AABB_LOWER_BOUND_ONLY",
        "note": "MEASURED means bbox lower bounds meet target or only one island exists, not proof that baked textures or mip levels have adequate padding.",
    })
    return report


def main():
    output = {
        "overall": "NOT VERIFIED", "blender_version": bpy.app.version_string,
        "reports": [], "baked_texture_validation": "NOT VERIFIED",
        "in_engine_visual_quality": "NOT VERIFIED",
    }
    if (not isinstance(TARGETS, list) or not 1 <= len(TARGETS) <= MAX_TARGETS or
            any(not isinstance(x, str) or not x.strip() for x in TARGETS) or
            len(TARGETS) != len(set(TARGETS))):
        output["error"] = "Provide unique explicit mesh TARGETS (1..25)"
    elif (not isinstance(TEXTURE_WIDTH, int) or TEXTURE_WIDTH < 1 or
          not isinstance(TEXTURE_HEIGHT, int) or TEXTURE_HEIGHT < 1 or
          not isinstance(DESIRED_PADDING_PX, int) or DESIRED_PADDING_PX < 0):
        output["error"] = "Set valid texture dimensions and nonnegative desired padding"
    else:
        for name in TARGETS:
            obj = bpy.data.objects.get(name)
            if obj is None:
                output["reports"].append({"name": name, "status": "NOT VERIFIED", "reason": "Missing object"})
            else:
                output["reports"].append(inspect(obj))
        statuses = {item["status"] for item in output["reports"]}
        output["overall"] = "NOT VERIFIED" if "NOT VERIFIED" in statuses else "REVIEW" if "REVIEW" in statuses else "MEASURED"
    print("MCP_UV_GUTTER_BEGIN")
    print(json.dumps(output, sort_keys=True, indent=2))
    print("MCP_UV_GUTTER_END")


if __name__ == "__main__":
    main()
