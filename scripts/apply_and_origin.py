"""Stage transform/origin operations on independent meshes; commit only after success.

Default behavior creates an owned copy; original source, selection and hierarchy
are never touched. In-place edits require TWO explicit opt-ins and a recoverable
mesh backup. Every target is processed independently and failures are reported.
"""
import bpy
from mathutils import Matrix, Vector

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                  # explicit names, never selected fallback
EDIT_IN_PLACE = False         # off by default
ALLOW_UNOWNED_EDIT = False    # second opt-in, only after user authorizes
OUTPUT_SUFFIX = "_Prepared"
COLLECTION_NAME = "MCP_Transform_Prepared"
APPLY_SCALE = True
APPLY_ROTATION = True
APPLY_LOCATION = False
ORIGIN = "BOTTOM_CENTER"       # BOTTOM_CENTER, CENTER, BOTTOM_CORNER, WORLD_ORIGIN, CUSTOM
CUSTOM_ORIGIN_WORLD = (0.0, 0.0, 0.0)
GROUND_TO_Z0 = False
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_transform"
OWNER_VALUE = "origin_v2"


def owned_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to reuse unowned collection " + COLLECTION_NAME)
    return col


def transform_staging_object(ob):
    loc, rot, scale = ob.matrix_basis.decompose()
    if min(abs(float(v)) for v in scale) < 1e-8:
        raise ValueError("Cannot apply transforms to a zero-scale object")
    bake = Matrix.Identity(4)
    if APPLY_SCALE:
        bake = Matrix.Diagonal(scale).to_4x4() @ bake
    if APPLY_ROTATION:
        bake = rot.to_matrix().to_4x4() @ bake
    if APPLY_LOCATION:
        bake = Matrix.Translation(loc) @ bake
    ob.data.transform(bake)
    ob.data.update()
    ob.location = Vector((0, 0, 0)) if APPLY_LOCATION else loc.copy()
    if APPLY_ROTATION:
        ob.rotation_mode = "QUATERNION"
        ob.rotation_quaternion = (1.0, 0.0, 0.0, 0.0)
        ob.rotation_mode = "XYZ"
    ob.scale = Vector((1, 1, 1)) if APPLY_SCALE else scale.copy()
    bpy.context.view_layer.update()
    world = ob.matrix_world
    verts = [world @ vert.co for vert in ob.data.vertices]
    if not verts:
        raise ValueError("Cannot set origin on empty mesh")
    minimum = Vector([min(v[i] for v in verts) for i in range(3)])
    maximum = Vector([max(v[i] for v in verts) for i in range(3)])
    center = (minimum + maximum) / 2.0
    if ORIGIN == "BOTTOM_CENTER":
        desired = Vector((center.x, center.y, minimum.z))
    elif ORIGIN == "CENTER":
        desired = center
    elif ORIGIN == "BOTTOM_CORNER":
        desired = minimum
    elif ORIGIN == "WORLD_ORIGIN":
        desired = Vector((0, 0, 0))
    else:
        desired = Vector(CUSTOM_ORIGIN_WORLD)
    offset_local = world.inverted() @ desired
    ob.data.transform(Matrix.Translation(-offset_local))
    ob.matrix_world.translation = desired
    ob.data.update()
    bpy.context.view_layer.update()
    if GROUND_TO_Z0:
        bottom = min((ob.matrix_world @ v.co).z for v in ob.data.vertices)
        ob.location.z -= bottom
        bpy.context.view_layer.update()


if ORIGIN not in {"BOTTOM_CENTER", "CENTER", "BOTTOM_CORNER", "WORLD_ORIGIN", "CUSTOM"}:
    raise ValueError("Unsupported ORIGIN: " + str(ORIGIN))
if not TARGETS:
    print("RESULT: NO TARGETS; set explicit TARGETS, no selected fallback.")
else:
    col = owned_collection()
    outputs, errors = [], []
    for name in dict.fromkeys(TARGETS):
        source = bpy.data.objects.get(name)
        reason = None
        if source is None or source.type != "MESH":
            reason = "missing or non-mesh object"
        elif source.library or source.data.library:
            reason = "linked/library data"
        elif source.mode != "OBJECT":
            reason = "object is in %s mode" % source.mode
        elif source.parent:
            reason = "parented object; preserving hierarchy"
        elif source.data.shape_keys and source.data.shape_keys.key_blocks:
            reason = "mesh has Shape Keys"
        elif EDIT_IN_PLACE and source.data.users > 1:
            reason = "shared mesh; cannot edit in place"
        elif EDIT_IN_PLACE and not ALLOW_UNOWNED_EDIT and source.get(OWNER_KEY) != OWNER_VALUE:
            reason = "unowned source; requires explicit ALLOW_UNOWNED_EDIT"
        if reason:
            print(f"[{name}] SKIP:", reason)
            errors.append((name, reason))
            continue
        output_name = source.name + OUTPUT_SUFFIX
        if not EDIT_IN_PLACE and output_name in bpy.data.objects:
            print("SKIP: output already exists:", output_name)
            errors.append((name, "output exists"))
            continue

        stage = None
        old_mesh = source.data
        old_matrix = source.matrix_world.copy()
        children = [(child, child.matrix_world.copy()) for child in source.children]
        try:
            stage = source.copy()
            stage.data = source.data.copy()
            stage.name = output_name if not EDIT_IN_PLACE else source.name + "_Origin_Staging"
            stage[OWNER_KEY] = OWNER_VALUE
            stage["mcp_source"] = source.name
            col.objects.link(stage)
            transform_staging_object(stage)
            if EDIT_IN_PLACE:
                source.data = stage.data
                source.matrix_world = stage.matrix_world.copy()
                for child, matrix in children:
                    child.matrix_world = matrix
                bpy.context.view_layer.update()
                old_mesh.name = old_mesh.name + "_BeforeOrigin"
                old_mesh.use_fake_user = True  # recovery, no deletion
                bpy.data.objects.remove(stage, do_unlink=True)
                stage = None
                outputs.append(source.name)
            else:
                outputs.append(stage.name)
            print("PREPARED:", outputs[-1], "source=", source.name)
        except Exception as exc:
            errors.append((name, str(exc)))
            print("ERROR:", name, repr(exc))
            if EDIT_IN_PLACE and source.data != old_mesh:
                source.data = old_mesh
                source.matrix_world = old_matrix
                for child, matrix in children:
                    child.matrix_world = matrix
                bpy.context.view_layer.update()
            if stage is not None:
                mesh = stage.data
                bpy.data.objects.remove(stage, do_unlink=True)
                if mesh.users == 0:
                    bpy.data.meshes.remove(mesh)
    print("TRANSFORM RESULT:", "SUCCESS" if not errors else "PARTIAL",
          "outputs=", outputs, "errors=", errors)
