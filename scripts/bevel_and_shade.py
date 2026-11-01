"""bevel_and_shade.py - add a Bevel modifier (angle-limited), set smooth shading with
sharp edges by angle, and optionally Weighted Normal. Version-aware (Blender 3.x and 4.x).
Paste into execute_blender_code.
"""
import bpy
import bmesh
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                 # object names; empty = selected mesh objects
BEVEL_FRACTION = 0.01        # bevel width as a fraction of the object's largest dimension
BEVEL_SEGMENTS = 2
SHARP_ANGLE_DEG = 30.0       # edges sharper than this stay hard
ADD_BEVEL = True
ADD_WEIGHTED_NORMAL = True   # recommended with bevels on hard-surface
APPLY_MODIFIERS = False      # True = apply the created modifiers (destructive; do this last)
# ----------------------------------------------------------------------------

objs = [bpy.data.objects[n] for n in TARGETS if n in bpy.data.objects] if TARGETS else \
       [o for o in bpy.context.selected_objects if o.type == 'MESH']

ver = bpy.app.version


def smooth_by_angle(ob):
    """Smooth shading + mark sharp edges by angle, works on 3.x and 4.x."""
    me = ob.data
    for p in me.polygons:
        p.use_smooth = True
    bm = bmesh.new()
    bm.from_mesh(me)
    ang = math.radians(SHARP_ANGLE_DEG)
    for e in bm.edges:
        if len(e.link_faces) == 2:
            e.smooth = e.calc_face_angle(0.0) < ang
        else:
            e.smooth = True
    bm.to_mesh(me)
    bm.free()
    if ver < (4, 1, 0):
        me.use_auto_smooth = True
        me.auto_smooth_angle = math.radians(SHARP_ANGLE_DEG)
    me.update()


for ob in objs:
    if ob.type != 'MESH':
        continue
    dims = ob.dimensions
    size = max(dims.x, dims.y, dims.z) or 1.0
    width = size * BEVEL_FRACTION
    positive_dims = [float(d) for d in dims if d > 1e-8]
    if positive_dims:
        cap = min(positive_dims) * 0.20
        if width > cap:
            print(f"[{ob.name}] WARNING: bevel requested {width:.6f} but clamped to {cap:.6f}")
            width = cap

    if ADD_BEVEL and "AutoBevel" not in ob.modifiers:
        m = ob.modifiers.new("AutoBevel", 'BEVEL')
        m.width = width
        m.use_clamp_overlap = True
        m.segments = BEVEL_SEGMENTS
        m.limit_method = 'ANGLE'
        m.angle_limit = math.radians(SHARP_ANGLE_DEG)
        try:
            m.harden_normals = True
        except AttributeError:
            pass

    smooth_by_angle(ob)

    if ADD_WEIGHTED_NORMAL and "AutoWeightedNormal" not in ob.modifiers:
        w = ob.modifiers.new("AutoWeightedNormal", 'WEIGHTED_NORMAL')
        w.keep_sharp = True
        w.mode = 'FACE_AREA'
        if ver < (4, 1, 0):
            ob.data.use_auto_smooth = True   # required by Weighted Normal before 4.1

    if APPLY_MODIFIERS:
        bpy.context.view_layer.objects.active = ob
        for name in ("AutoBevel", "AutoWeightedNormal"):
            if name in ob.modifiers:
                try:
                    if hasattr(bpy.context, "temp_override"):      # Blender 3.2+
                        with bpy.context.temp_override(object=ob, active_object=ob):
                            bpy.ops.object.modifier_apply(modifier=name)
                    else:                                          # Blender 2.9x to 3.1
                        bpy.ops.object.modifier_apply({"object": ob, "active_object": ob}, modifier=name)
                except Exception as ex:
                    print(f"[{ob.name}] could not apply {name}: {ex}")

    print(f"[{ob.name}] bevel width={width:.4f} m, segments={BEVEL_SEGMENTS}, sharp>{SHARP_ANGLE_DEG} deg, "
          f"modifiers={[m.name for m in ob.modifiers]}")

print("Done. Use look(shading='wireframe') and look(mode='angles') to verify shading.")
