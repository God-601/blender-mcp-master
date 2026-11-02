"""Advanced guided retopology: explicit bridge, planar fill and vertex relax.

Runs inside Blender with bpy/bmesh, on duplicate mesh objects only. This is
NOT an automatic quad-retopology or animation-ready topology solver.

Inputs are object names and vertex-index cycles defined against the BASE mesh,
which must have no modifiers or shape keys. Original objects remain untouched.
"""
import bpy
import bmesh
import json
import math
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []
COLLECTION_NAME = "MCP_Advanced_Retopology"
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_advanced_retopology"
OWNER_VALUE = "retopology_advanced_v1"


def _integer_index(value, size):
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value < size:
        raise ValueError("invalid or out-of-range vertex index: " + repr(value))
    return value


def _vertices(bm, indices):
    if not isinstance(indices, (list, tuple)):
        raise ValueError("vertex indices must be an ordered list")
    bm.verts.ensure_lookup_table()
    size = len(bm.verts)
    ids = [_integer_index(i, size) for i in indices]
    if len(ids) != len(set(ids)):
        raise ValueError("vertex indices contain duplicates")
    return [bm.verts[i] for i in ids]


def _boundary_loop(bm, indices):
    verts = _vertices(bm, indices)
    if len(verts) < 3:
        raise ValueError("loop must contain at least 3 distinct vertices")
    for i, vertex in enumerate(verts):
        adjacent = verts[(i + 1) % len(verts)]
        edge = next((e for e in vertex.link_edges if e.other_vert(vertex) is adjacent), None)
        if edge is None:
            raise ValueError("ordered loop does not follow existing mesh edges")
        if len(edge.link_faces) > 1:
            raise ValueError("loop edge is not on an open mesh boundary")
    return verts


def _bridge(bm, operation):
    loops = operation.get("loops")
    if not isinstance(loops, (list, tuple)) or len(loops) != 2:
        raise ValueError("bridge_loops requires exactly two ordered loops")
    left = _boundary_loop(bm, loops[0])
    right = _boundary_loop(bm, loops[1])
    if len(left) != len(right):
        raise ValueError("bridge_loops currently requires matching loop lengths")
    if set(left) & set(right):
        raise ValueError("bridge_loops must connect disjoint vertex loops")
    new_faces = []
    for i in range(len(left)):
        j = (i + 1) % len(left)
        face = bm.faces.new((left[i], left[j], right[j], right[i]))
        if face.calc_area() <= 1e-10:
            raise ValueError("bridge generated a zero-area face")
        new_faces.append(face)
    bmesh.ops.recalc_face_normals(bm, faces=new_faces)
    return {"bridge_faces": len(new_faces)}


def _fill(bm, operation):
    verts = _boundary_loop(bm, operation.get("loop"))
    if len(verts) > 64:
        raise ValueError("fill_hole only supports loops of up to 64 vertices")
    tolerance = float(operation.get("planarity_tolerance", 0.0001))
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("planarity_tolerance must be finite and nonnegative")
    normal = None
    origin = verts[0].co
    for i in range(1, len(verts) - 1):
        vec = (verts[i].co - origin).cross(verts[i + 1].co - origin)
        if vec.length > 1e-10:
            normal = vec.normalized()
            break
    if normal is None:
        raise ValueError("cannot fill a collinear or degenerate loop")
    if any(abs((v.co - origin).dot(normal)) > tolerance for v in verts):
        raise ValueError("fill_hole loop is not planar within tolerance")
    face = bm.faces.new(tuple(verts))
    if face.calc_area() <= 1e-10:
        raise ValueError("fill_hole produced a zero-area face")
    bmesh.ops.recalc_face_normals(bm, faces=[face])
    return {"filled_faces": 1}


def _relax(bm, operation):
    indices = operation.get("vertices")
    verts = _vertices(bm, indices)
    if not verts:
        raise ValueError("relax_vertices requires explicit vertices")
    factor = float(operation.get("factor", 0.5))
    iterations = operation.get("iterations", 1)
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not 1 <= iterations <= 20:
        raise ValueError("iterations must be an integer between 1 and 20")
    if not math.isfinite(factor) or not 0 < factor <= 1:
        raise ValueError("relax factor must be in (0, 1]")
    preserve_boundary = operation.get("preserve_boundary", True)
    if not isinstance(preserve_boundary, bool):
        raise ValueError("preserve_boundary must be true or false")
    changed = set()
    for _ in range(iterations):
        updates = {}
        for vert in verts:
            if preserve_boundary and any(not edge.is_manifold for edge in vert.link_edges):
                continue
            neighbors = [edge.other_vert(vert) for edge in vert.link_edges]
            if not neighbors:
                continue
            mean = sum((v.co for v in neighbors), Vector((0.0, 0.0, 0.0))) / len(neighbors)
            updates[vert] = vert.co.lerp(mean, factor)
        for vert, coord in updates.items():
            if (vert.co - coord).length > 1e-12:
                changed.add(vert)
            vert.co = coord
    return {"relaxed_vertices": len(changed), "iterations": iterations}


def _collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("refusing to reuse an unowned collection: " + COLLECTION_NAME)
    return col


def _run_one(target):
    if not isinstance(target, dict):
        raise ValueError("target must be an object")
    source_name = target.get("source")
    output_name = target.get("output")
    if not isinstance(source_name, str) or not source_name.strip():
        raise ValueError("source object name is required")
    if not isinstance(output_name, str) or not output_name.strip() or output_name == source_name:
        raise ValueError("unique output object name is required")
    if bpy.data.objects.get(output_name) is not None:
        raise ValueError("output object already exists")
    source = bpy.data.objects.get(source_name)
    if source is None or source.type != "MESH":
        raise ValueError("explicit source mesh not found")
    if source.mode != "OBJECT":
        raise ValueError("switch source to Object mode before retopology")
    if source.data.shape_keys is not None:
        raise ValueError("shape_keys cannot be preserved by topology-changing operations")
    if source.modifiers:
        raise ValueError("modifier stack exists; inspect and apply to a separate owned copy first")
    ops = target.get("operations")
    if not isinstance(ops, list) or not ops:
        raise ValueError("operations must contain at least one explicit operation")
    # Every output uses independent mesh data, never a shared mesh datablock.
    col = _collection()
    output = source.copy()
    output.data = source.data.copy()
    output.name = output_name
    output[OWNER_KEY] = OWNER_VALUE
    output["retopology_source"] = source.name
    col.objects.link(output)
    mesh = output.data
    bm = bmesh.new()
    metrics = []
    try:
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        for op in ops:
            if not isinstance(op, dict):
                raise ValueError("operation must be an object")
            kind = op.get("type")
            if kind == "bridge_loops":
                metrics.append(_bridge(bm, op))
            elif kind == "fill_hole":
                metrics.append(_fill(bm, op))
            elif kind == "relax_vertices":
                metrics.append(_relax(bm, op))
            else:
                raise ValueError("unsupported retopology operation: " + str(kind))
        bm.normal_update()
        bm.to_mesh(mesh)
        mesh.update()
    except Exception:
        # Safe rollback: remove only the newly created owned copy and its mesh.
        bm.free()
        bpy.data.objects.remove(output, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        raise
    else:
        bm.free()
    return {
        "source": source.name,
        "output": output.name,
        "vertices": len(mesh.vertices),
        "faces": len(mesh.polygons),
        "operations": metrics,
        "visual_quality": "NOT VERIFIED",
        "deformation_quality": "NOT VERIFIED",
    }


def main():
    result = {"status": "SUCCESS", "results": [], "errors": []}
    if not isinstance(TARGETS, list) or not TARGETS:
        result["status"] = "ERROR"
        result["errors"].append("TARGETS must name at least one source; no selection fallback")
    else:
        for target in TARGETS:
            try:
                result["results"].append(_run_one(target))
            except Exception as exc:
                result["status"] = "ERROR"
                result["errors"].append({
                    "source": target.get("source") if isinstance(target, dict) else None,
                    "error": str(exc),
                })
    print("MCP_RETOPO_RESULT_BEGIN")
    print(json.dumps(result, sort_keys=True, indent=2))
    print("MCP_RETOPO_RESULT_END")
    print("Inspect front/side/perspective views. This script does not prove animation-ready topology.")


if __name__ == "__main__":
    main()
