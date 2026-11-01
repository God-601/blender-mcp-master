"""mesh_operations.py — non-destructive operations on explicit source meshes.

Each operation duplicates an explicitly named source object and its mesh data. The source
is never modified. Output objects and boolean cutters live in an owned collection.
Supported operations: bevel, weighted_normal, solidify, triangulate, decimate,
mirror, subdivision, boolean_difference.
"""
import bpy
import bmesh
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
COLLECTION_NAME = "MCP_Mesh_Operations"
TARGETS = [
    {"source": "Asset_Body", "output": "Asset_Body_Refined", "operations": [
        {"type": "bevel", "width": 0.025, "segments": 3},
        {"type": "weighted_normal"},
    ]},
]
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_mesh_operations"
OWNER_VALUE = "mesh_operations_v1"


def owned_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to reuse an unowned collection: " + COLLECTION_NAME)
    return col


def make_box_cutter(name, dimensions, location, collection):
    dims = Vector(dimensions)
    if min(dims) <= 0:
        raise ValueError("boolean cutter dimensions must be positive")
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, verts=bm.verts, vec=dims)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    cutter = bpy.data.objects.new(name, mesh)
    collection.objects.link(cutter)
    cutter.location = Vector(location)
    cutter.display_type = "WIRE"
    cutter.hide_render = True
    cutter.hide_set(True)
    cutter[OWNER_KEY] = OWNER_VALUE
    return cutter


def add_operation(obj, operation, collection, index):
    kind = operation.get("type")
    if kind == "bevel":
        width = float(operation.get("width", 0.02))
        if width <= 0:
            raise ValueError("bevel width must be positive")
        positive_dims = [float(d) for d in obj.dimensions if d > 1e-8]
        if positive_dims:
            cap = min(positive_dims) * 0.20
            if width > cap:
                print("WARNING: mesh operation bevel clamped for", obj.name, "from", width, "to", cap)
                width = cap
        mod = obj.modifiers.new("MCP_Bevel_%02d" % index, "BEVEL")
        mod.use_clamp_overlap = True
        mod.width = width
        mod.segments = max(1, min(12, int(operation.get("segments", 2))))
        mod.limit_method = "ANGLE"
    elif kind == "weighted_normal":
        mod = obj.modifiers.new("MCP_WeightedNormal_%02d" % index, "WEIGHTED_NORMAL")
        mod.keep_sharp = True
    elif kind == "solidify":
        thickness = float(operation.get("thickness", 0.05))
        if abs(thickness) <= 1e-8:
            raise ValueError("solidify thickness cannot be zero")
        mod = obj.modifiers.new("MCP_Solidify_%02d" % index, "SOLIDIFY")
        mod.thickness = thickness
    elif kind == "triangulate":
        obj.modifiers.new("MCP_Triangulate_%02d" % index, "TRIANGULATE")
    elif kind == "decimate":
        ratio = float(operation.get("ratio", 0.5))
        if not 0.0 < ratio <= 1.0:
            raise ValueError("decimate ratio must be in (0, 1]")
        mod = obj.modifiers.new("MCP_Decimate_%02d" % index, "DECIMATE")
        mod.ratio = ratio
    elif kind == "mirror":
        mod = obj.modifiers.new("MCP_Mirror_%02d" % index, "MIRROR")
        axes = operation.get("axes", (True, False, False))
        mod.use_axis = tuple(bool(v) for v in axes)
        mod.use_clip = bool(operation.get("use_clip", True))
    elif kind == "subdivision":
        mod = obj.modifiers.new("MCP_Subdivision_%02d" % index, "SUBSURF")
        mod.levels = max(0, min(4, int(operation.get("levels", 1))))
        mod.render_levels = max(mod.levels, min(4, int(operation.get("render_levels", mod.levels))))
    elif kind == "boolean_difference":
        cutter_name = str(operation.get("cutter_name", obj.name + "_Cutter_%02d" % index))
        if cutter_name in bpy.data.objects:
            raise ValueError("boolean cutter name already exists: " + cutter_name)
        cutter = make_box_cutter(
            cutter_name, operation.get("dimensions", (0.5, 0.5, 0.5)),
            operation.get("location", tuple(obj.location)), collection
        )
        mod = obj.modifiers.new("MCP_Boolean_%02d" % index, "BOOLEAN")
        mod.operation = "DIFFERENCE"
        mod.object = cutter
        if hasattr(mod, "solver"):
            mod.solver = "EXACT"
    else:
        raise ValueError("unsupported mesh operation: " + str(kind))
    return mod



def apply_topology_operation(obj, operation):
    """Apply a topology edit to the duplicated output mesh, never the source."""
    kind = operation.get("type")
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        if kind in ("inset_faces", "extrude_faces"):
            indices = [int(i) for i in operation.get("face_indices", [])]
            if not indices or any(i < 0 or i >= len(bm.faces) for i in indices):
                raise ValueError(kind + " requires valid explicit face_indices")
            faces = [bm.faces[i] for i in indices]
            if kind == "inset_faces":
                thickness = float(operation.get("thickness", 0.05))
                if thickness <= 0:
                    raise ValueError("inset thickness must be positive")
                bmesh.ops.inset_region(
                    bm, faces=faces, thickness=thickness,
                    depth=float(operation.get("depth", 0.0)),
                    use_even_offset=bool(operation.get("use_even_offset", True)),
                    use_interpolate=True, use_relative_offset=False
                )
            else:
                offset = Vector(operation.get("offset", (0.0, 0.0, 0.2)))
                if offset.length <= 1e-8:
                    raise ValueError("extrude offset must be non-zero")
                result = bmesh.ops.extrude_face_region(bm, geom=faces, use_keep_orig=False)
                verts = [element for element in result["geom"] if isinstance(element, bmesh.types.BMVert)]
                if not verts:
                    raise ValueError("face extrusion produced no vertices")
                bmesh.ops.translate(bm, verts=verts, vec=offset)
        else:
            raise ValueError("unsupported topology operation: " + str(kind))
        bm.normal_update()
        bm.to_mesh(obj.data)
        obj.data.update()
    finally:
        bm.free()


def process_target(spec, collection):
    source_name = str(spec["source"])
    output_name = str(spec["output"])
    source = bpy.data.objects.get(source_name)
    if source is None or source.type != "MESH":
        raise ValueError("source must be an existing mesh object: " + source_name)
    if output_name in bpy.data.objects:
        raise ValueError("output already exists; refusing overwrite: " + output_name)
    modifier_seen = bool(source.modifiers)
    for operation in spec.get("operations", []):
        if operation.get("type") in ("inset_faces", "extrude_faces"):
            if modifier_seen:
                raise ValueError("topology edits must precede modifiers, including source modifiers")
        else:
            modifier_seen = True
    output = source.copy()
    output.data = source.data.copy()
    output.name = output_name
    output[OWNER_KEY] = OWNER_VALUE
    output["mcp_source_object"] = source.name
    collection.objects.link(output)
    created_cutters = []
    try:
        for index, operation in enumerate(spec.get("operations", []), 1):
            if operation.get("type") in ("inset_faces", "extrude_faces"):
                apply_topology_operation(output, operation)
                continue
            before = set(bpy.data.objects.keys())
            add_operation(output, operation, collection, index)
            created_cutters.extend(
                bpy.data.objects[name] for name in (set(bpy.data.objects.keys()) - before)
                if bpy.data.objects[name].get(OWNER_KEY) == OWNER_VALUE
            )
    except Exception:
        for cutter in reversed(created_cutters):
            mesh = cutter.data if cutter.type == "MESH" else None
            bpy.data.objects.remove(cutter, do_unlink=True)
            if mesh and mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        mesh = output.data
        bpy.data.objects.remove(output, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        raise
    return output


collection = owned_collection()
created = []
errors = []
for target in TARGETS:
    try:
        obj = process_target(target, collection)
        created.append(obj)
        print("CREATED:", obj.name, "source=", target["source"],
              "modifiers=", [mod.type for mod in obj.modifiers])
    except Exception as exc:
        errors.append((target.get("source", "<missing>"), str(exc)))
        print("ERROR:", target.get("source", "<missing>"), repr(exc))
print("MESH OPERATION REPORT")
print("created:", len(created), "errors:", len(errors))
print("source objects preserved: True")
print("result:", "SUCCESS" if not errors else "PARTIAL")
