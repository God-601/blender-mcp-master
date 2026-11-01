"""Bevel and shade explicit mesh targets without editing their sources by default.

Set TARGETS explicitly, inspect the copy, then opt into EDIT_IN_PLACE only
when the original should be changed. No scene-wide/selected-object fallback.
"""
import bpy
import bmesh
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                  # explicit object names; empty means no operation
EDIT_IN_PLACE = False         # default: create independent owned copies
ALLOW_UNOWNED_INPLACE = False # second opt-in needed for user-owned objects
OUTPUT_SUFFIX = "_Shaded"
COLLECTION_NAME = "MCP_Bevel_Shading"
BEVEL_FRACTION = 0.01
BEVEL_SEGMENTS = 2
SHARP_ANGLE_DEG = 30.0
ADD_BEVEL = True
ADD_WEIGHTED_NORMAL = True
APPLY_MODIFIERS = False       # destructive to output; only edit source if explicitly opted in
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_bevel_shading"
OWNER_VALUE = "bevel_shading_v1"
ver = bpy.app.version


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to reuse unowned collection: " + COLLECTION_NAME)
    return col


def smooth_by_angle(ob):
    me = ob.data
    for polygon in me.polygons:
        polygon.use_smooth = True
    bm = bmesh.new()
    try:
        bm.from_mesh(me)
        angle = math.radians(SHARP_ANGLE_DEG)
        for edge in bm.edges:
            edge.smooth = edge.calc_face_angle(0.0) < angle if len(edge.link_faces) == 2 else True
        bm.to_mesh(me)
    finally:
        bm.free()
    if ver < (4, 1, 0):
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.radians(SHARP_ANGLE_DEG)
    me.update()


def check_target(ob):
    if ob is None or ob.type != "MESH":
        return "missing or non-mesh object"
    if ob.library or ob.data.library:
        return "linked/library data"
    if ob.mode != "OBJECT":
        return "object must be in Object Mode"
    if ob.data.shape_keys:
        return "shape keys (review deformation/mesh before shading)"
    if EDIT_IN_PLACE and ob.data.users > 1:
        return "shared mesh datablock (edit would affect other objects)"
    if EDIT_IN_PLACE and APPLY_MODIFIERS:
        return "in-place modifier application is unsafe; use a copy"
    if EDIT_IN_PLACE and ob.get(OWNER_KEY) != OWNER_VALUE and not ALLOW_UNOWNED_INPLACE:
        return "in-place modification requires ALLOW_UNOWNED_INPLACE"
    return None


def create_output(source, collection):
    if EDIT_IN_PLACE:
        return source
    name = source.name + OUTPUT_SUFFIX
    if name in bpy.data.objects:
        raise ValueError("Output already exists; refusing overwrite: " + name)
    output = source.copy()
    output.data = source.data.copy()
    output.name = name
    output[OWNER_KEY] = OWNER_VALUE
    output["source_object"] = source.name
    collection.objects.link(output)
    return output


def add_shading(ob):
    dims = ob.dimensions
    size = max(dims.x, dims.y, dims.z) or 1.0
    width = size * BEVEL_FRACTION
    positive_dims = [float(d) for d in dims if d > 1e-8]
    if positive_dims and width > min(positive_dims) * 0.20:
        cap = min(positive_dims) * 0.20
        print("WARNING: bevel width clamped for", ob.name, width, "to", cap)
        width = cap

    if ADD_BEVEL and "AutoBevel" not in ob.modifiers:
        mod = ob.modifiers.new("AutoBevel", "BEVEL")
        mod.width = width
        mod.use_clamp_overlap = True
        mod.segments = BEVEL_SEGMENTS
        mod.limit_method = "ANGLE"
        mod.angle_limit = math.radians(SHARP_ANGLE_DEG)
        if hasattr(mod, "harden_normals"):
            mod.harden_normals = True

    smooth_by_angle(ob)

    if ADD_WEIGHTED_NORMAL and "AutoWeightedNormal" not in ob.modifiers:
        mod = ob.modifiers.new("AutoWeightedNormal", "WEIGHTED_NORMAL")
        mod.keep_sharp = True
        mod.mode = "FACE_AREA"
        if ver < (4, 1, 0):
            ob.data.use_auto_smooth = True

    if APPLY_MODIFIERS:
        previous_active = bpy.context.view_layer.objects.active
        previous_selection = list(bpy.context.selected_objects)
        try:
            for selected in previous_selection:
                selected.select_set(False)
            ob.select_set(True)
            bpy.context.view_layer.objects.active = ob
            for name in ("AutoBevel", "AutoWeightedNormal"):
                if name in ob.modifiers:
                    if hasattr(bpy.context, "temp_override"):
                        with bpy.context.temp_override(object=ob, active_object=ob):
                            bpy.ops.object.modifier_apply(modifier=name)
                    else:
                        bpy.ops.object.modifier_apply({"object": ob, "active_object": ob}, modifier=name)
        finally:
            ob.select_set(False)
            for selected in previous_selection:
                if selected.name in bpy.data.objects:
                    selected.select_set(True)
            bpy.context.view_layer.objects.active = previous_active

    print("SHADED:", ob.name, "bevel_width=", round(width, 6),
          "modifiers=", [m.type for m in ob.modifiers])


if not TARGETS:
    print("RESULT: NO TARGETS — set explicit TARGETS; no selected-object fallback.")
else:
    working_collection = None if EDIT_IN_PLACE else get_collection()
    created = []
    errors = []
    for name in dict.fromkeys(TARGETS):
        source = bpy.data.objects.get(name)
        reason = check_target(source)
        if reason:
            errors.append((name, reason))
            print("SKIP:", name, reason)
            continue
        obj = None
        backup = None
        original_modifiers = None
        try:
            obj = create_output(source, working_collection)
            if obj is source:
                backup = source.data.copy()
                original_modifiers = {mod.name for mod in source.modifiers}
            add_shading(obj)
            if obj is not source:
                created.append(obj)
            if backup is not None and backup.users == 0:
                bpy.data.meshes.remove(backup)
        except Exception as exc:
            errors.append((name, str(exc)))
            print("ERROR:", name, repr(exc))
            if obj is source and backup is not None:
                source.data = backup
                for mod in list(source.modifiers):
                    if mod.name not in original_modifiers:
                        source.modifiers.remove(mod)
            if obj is not None and obj is not source:
                mesh = obj.data
                bpy.data.objects.remove(obj, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
    print("BEVEL/SHADING RESULT:",
          "SUCCESS" if not errors else "PARTIAL",
          "copies=", [obj.name for obj in created], "errors=", errors)
