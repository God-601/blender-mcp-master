"""apply_and_origin.py - apply transforms, set origin, ground the object.
Uses the data API (no operators) so it works regardless of UI context.
Paste into execute_blender_code.
"""
import bpy
from mathutils import Vector, Matrix

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                  # object names; empty = selected mesh objects
APPLY_SCALE = True
APPLY_ROTATION = True
APPLY_LOCATION = False        # usually keep location; set True to bake world position into mesh
ORIGIN = "BOTTOM_CENTER"      # "BOTTOM_CENTER", "CENTER", "BOTTOM_CORNER", "WORLD_ORIGIN", or "CUSTOM"
CUSTOM_ORIGIN_WORLD = (0.0, 0.0, 0.0)   # used if ORIGIN == "CUSTOM" (world coordinates)
GROUND_TO_Z0 = False          # move object so its lowest point sits on Z=0
# ----------------------------------------------------------------------------

objs = [bpy.data.objects[n] for n in TARGETS if n in bpy.data.objects] if TARGETS else \
       [o for o in bpy.context.selected_objects if o.type == 'MESH']


def bake_matrix(ob, mat):
    """Bake a matrix into mesh data and compensate on the object matrix."""
    ob.data.transform(mat)
    ob.data.update()


for ob in objs:
    if ob.type != 'MESH':
        continue
    if ob.data.users > 1:
        print(f"[{ob.name}] SKIP: shared mesh data ({ob.data.users} users). Make single-user first (ob.data = ob.data.copy()).")
        continue
    if ob.parent or ob.children:
        print(f"[{ob.name}] note: has parent/children; children keep their world positions only if you re-parent carefully.")

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

    d = ob.dimensions
    print(f"[{ob.name}] scale={tuple(round(x,4) for x in ob.scale)} origin={tuple(round(x,4) for x in ob.location)} "
          f"dims=({d.x:.3f}, {d.y:.3f}, {d.z:.3f}) m")

print("Done.")
