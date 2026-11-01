"""localized_correction.py — apply explicit mesh corrections to safe duplicates.

The named source objects are never modified. Corrections are deterministic and limited to
the requested targets. Supported actions: recalculate_normals, merge_by_distance,
apply_scale_to_mesh, bevel_modifier, weighted_normal.
"""
import bpy
import bmesh
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
CORRECTIONS = [
    {"source": "Asset_Body", "output": "Asset_Body_Corrected",
     "operations": [{"type": "recalculate_normals"}, {"type": "weighted_normal"}]},
]
COLLECTION_NAME = "MCP_Local_Corrections"
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_local_correction"
OWNER_VALUE = "localized_correction_v1"


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("collection collision: " + COLLECTION_NAME)
    return col


def apply_correction(obj, operation):
    kind = operation.get("type")
    if kind in ("recalculate_normals", "merge_by_distance", "apply_scale_to_mesh"):
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            if kind == "recalculate_normals":
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
            elif kind == "merge_by_distance":
                distance = float(operation.get("distance", 0.0001))
                if distance <= 0:
                    raise ValueError("merge distance must be positive")
                bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=distance)
            else:
                scale = obj.scale.copy()
                if min(abs(float(v)) for v in scale) <= 1e-8:
                    raise ValueError("cannot bake a zero object scale")
                bmesh.ops.scale(bm, verts=bm.verts, vec=scale)
                obj.scale = (1.0, 1.0, 1.0)
            bm.to_mesh(obj.data)
            obj.data.update()
        finally:
            bm.free()
    elif kind == "bevel_modifier":
        width = float(operation.get("width", 0.02))
        if width <= 0:
            raise ValueError("bevel width must be positive")
        dimensions = [float(d) for d in obj.dimensions if d > 1e-8]
        if dimensions:
            cap = min(dimensions) * 0.20
            if width > cap:
                print("WARNING: localized bevel clamped for", obj.name, "from", width, "to", cap)
                width = cap
        mod = obj.modifiers.new("Localized_Bevel", "BEVEL")
        mod.use_clamp_overlap = True
        mod.width = width
        mod.segments = max(1, min(8, int(operation.get("segments", 2))))
    elif kind == "weighted_normal":
        obj.modifiers.new("Localized_WeightedNormal", "WEIGHTED_NORMAL")
    else:
        raise ValueError("unsupported correction: " + str(kind))


collection = get_collection()
created = []
errors = []
for correction in CORRECTIONS:
    source_name = str(correction["source"])
    output_name = str(correction["output"])
    source = bpy.data.objects.get(source_name)
    if source is None or source.type != "MESH":
        errors.append((source_name, "source mesh not found"))
        print("ERROR:", source_name, "source mesh not found")
        continue
    if output_name in bpy.data.objects:
        errors.append((source_name, "output already exists"))
        print("ERROR:", source_name, "output already exists")
        continue
    output = source.copy()
    output.data = source.data.copy()
    output.name = output_name
    output[OWNER_KEY] = OWNER_VALUE
    output["correction_source"] = source.name
    collection.objects.link(output)
    try:
        for operation in correction.get("operations", []):
            apply_correction(output, operation)
        created.append(output)
        print("CORRECTED COPY:", output.name, "operations=", len(correction.get("operations", [])))
    except Exception as exc:
        mesh = output.data
        bpy.data.objects.remove(output, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        errors.append((source_name, str(exc)))
        print("ERROR:", source_name, repr(exc))
print("LOCAL CORRECTION REPORT")
print("created:", [obj.name for obj in created], "errors:", errors)
print("source objects modified: 0")
