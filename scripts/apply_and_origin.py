"""apply_and_origin.py - apply transforms, set origin, ground the object.
Uses the data API (no operators) so it works regardless of UI context.
Paste into execute_blender_code.
"""
import bpy
from mathutils import Vector, Matrix

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                  # explicit object names; empty means no action
EDIT_IN_PLACE = False          # default: write independent transformed copies
OUTPUT_SUFFIX = "_Prepared"
COLLECTION_NAME = "MCP_Transform_Prepared"
APPLY_SCALE = True
APPLY_ROTATION = True
APPLY_LOCATION = False        # usually keep location; set True to bake world position into mesh
ORIGIN = "BOTTOM_CENTER"      # "BOTTOM_CENTER", "CENTER", "BOTTOM_CORNER", "WORLD_ORIGIN", or "CUSTOM"
CUSTOM_ORIGIN_WORLD = (0.0, 0.0, 0.0)   # used if ORIGIN == "CUSTOM" (world coordinates)
GROUND_TO_Z0 = False          # move object so its lowest point sits on Z=0
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_transform"
OWNER_VALUE = "origin_v2"
def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing unowned collection: " + COLLECTION_NAME)
    return col

objs = [bpy.data.objects[n] for n in TARGETS if n in bpy.data.objects]


def bake_matrix(ob, mat):
    """Bake a matrix into mesh data and compensate on the object matrix."""
    ob.data.transform(mat)
    ob.data.update()


if not TARGETS:
    print("RESULT: NO TARGETS; set TARGETS explicitly. No selected-object fallback.")
if ORIGIN not in ("BOTTOM_CENTER", "CENTER", "BOTTOM_CORNER", "WORLD_ORIGIN", "CUSTOM"):
    raise ValueError("Unknown origin policy: " + str(ORIGIN))
working_collection = get_collection() if TARGETS and not EDIT_IN_PLACE else None

for source in objs:
    if source.type != 'MESH':
        continue
    ob = source
    if not EDIT_IN_PLACE:
        output_name = source.name + OUTPUT_SUFFIX
        if output_name in bpy.data.objects:
            print("SKIP: output already exists:", output_name)
            continue
        if source.library or source.data.library:
            print("SKIP: linked/library data", source.name)
            continue
        if source.mode != 'OBJECT' or source.parent or source.data.shape_keys:
            print("SKIP: unsupported source state", source.name)
            continue
        ob = source.copy()
        ob.data = source.data.copy()
        ob.name = output_name
        ob[OWNER_KEY] = OWNER_VALUE
        ob["mcp_source"] = source.name
        working_collection.objects.link(ob)
    if ob.type != 'MESH':
        continue
    if ob.data.users > 1:
        print(f"[{ob.name}] SKIP: shared mesh data ({ob.data.users} users). Make single-user first (ob.data = ob.data.copy()).")
        continue
    if ob.data.shape_keys and ob.data.shape_keys.key_blocks:
        print(f"[{ob.name}] SKIP: mesh has Shape Keys; applying transforms/origin directly can desynchronize key data.")
        continue
    if ob.mode != 'OBJECT':
        print(f"[{ob.name}] SKIP: object is in {ob.mode} mode; switch to Object Mode so the change is not lost.")
        continue
    if ob.parent:
        print(f"[{ob.name}] SKIP: parented object; preserving the parent hierarchy.")
        continue
    if EDIT_IN_PLACE and source.get(OWNER_KEY) != OWNER_VALUE:
        print(f"[{source.name}] SKIP: edit-in-place requires tool-owned object.")
        continue
    # In-place operations keep a named, fake-user mesh recovery backup.
    backup = None
    if EDIT_IN_PLACE:
        backup = ob.data.copy()
        backup.name = ob.data.name + "_BeforeOrigin"
        backup.use_fake_user = True

    # Children must keep their world position when this object's origin moves.
    bpy.context.view_layer.update()
    child_worlds = [(child, child.matrix_world.copy()) for child in ob.children]

    loc, rot, scale = ob.matrix_basis.decompose()
    m = Matrix.Identity(4)
    if APPLY_SCALE:
        m = Matrix.Diagonal(scale).to_4x4() @ m
    if APPLY_ROTATION:
        m = rot.to_matrix().to_4x4() @ m
    if APPLY_LOCATION:
        m = Matrix.Translation(loc) @ m

    # Compute the new basis after baking
    new_loc = Vector((0, 0, 0)) if APPLY_LOCATION else loc.copy()
    new_rot = rot if not APPLY_ROTATION else type(rot)((1, 0, 0, 0))
    new_scale = scale.copy() if not APPLY_SCALE else Vector((1, 1, 1))

    bake_matrix(ob, m)
    ob.location = new_loc
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = new_rot
    ob.rotation_mode = 'XYZ'
    ob.scale = new_scale
    bpy.context.view_layer.update()

    # Set origin: compute desired origin in world space, shift mesh to compensate
    mw = ob.matrix_world
    ws = [mw @ v.co for v in ob.data.vertices]
    if not ws:
        continue
    mn = Vector((min(v.x for v in ws), min(v.y for v in ws), min(v.z for v in ws)))
    mx = Vector((max(v.x for v in ws), max(v.y for v in ws), max(v.z for v in ws)))
    ctr = (mn + mx) / 2
    if ORIGIN == "BOTTOM_CENTER":
        target = Vector((ctr.x, ctr.y, mn.z))
    elif ORIGIN == "CENTER":
        target = ctr
    elif ORIGIN == "BOTTOM_CORNER":
        target = mn
    elif ORIGIN == "WORLD_ORIGIN":
        target = Vector((0, 0, 0))
    elif ORIGIN == "CUSTOM":
        target = Vector(CUSTOM_ORIGIN_WORLD)
    else:
        target = mw.translation.copy()

    offset_local = mw.inverted() @ target       # target in local space
    ob.data.transform(Matrix.Translation(-offset_local))
    ob.matrix_world.translation = target
    ob.data.update()
    bpy.context.view_layer.update()

    if GROUND_TO_Z0:
        ws = [ob.matrix_world @ v.co for v in ob.data.vertices]
        ob.location.z -= min(v.z for v in ws)
        bpy.context.view_layer.update()

    for child, world in child_worlds:
        child.matrix_world = world
    bpy.context.view_layer.update()

    d = ob.dimensions
    print(f"[{ob.name}] scale={tuple(round(x,4) for x in ob.scale)} origin={tuple(round(x,4) for x in ob.location)} "
          f"dims=({d.x:.3f}, {d.y:.3f}, {d.z:.3f}) m")

print("Done.")
