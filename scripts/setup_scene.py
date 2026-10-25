"""setup_scene.py - create a clean working collection, metric units, sane clip range,
optional studio lighting + camera. Does NOT delete user objects. Paste into execute_blender_code.
"""
import bpy
import math
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
ASSET_NAME = "Asset"        # collection name for the asset being built
SET_UNITS = True            # metric, 1 unit = 1 m
ADD_STUDIO_LIGHTS = False   # 3-point lights in a separate collection "Studio"
ADD_CAMERA = False          # camera in collection "Studio" framing the origin
RENDER_ENGINE = None        # None keeps current; or 'BLENDER_EEVEE_NEXT' / 'BLENDER_EEVEE' / 'CYCLES' / 'BLENDER_WORKBENCH'
# ----------------------------------------------------------------------------


def get_or_make_collection(name, parent=None):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(col)
    elif col.name not in (parent or bpy.context.scene.collection).children:
        try:
            (parent or bpy.context.scene.collection).children.link(col)
        except RuntimeError:
            pass
    return col


scene = bpy.context.scene
print("Blender", bpy.app.version_string)

if SET_UNITS:
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'

asset_col = get_or_make_collection(ASSET_NAME)
# make new objects go into the asset collection
lc = bpy.context.view_layer.layer_collection

def find_lc(layer_col, name):
    if layer_col.name == name:
        return layer_col
    for c in layer_col.children:
        r = find_lc(c, name)
        if r:
            return r
    return None

target = find_lc(lc, asset_col.name)
if target:
    bpy.context.view_layer.active_layer_collection = target

# viewport clip range for model-sized work
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            for space in area.spaces:
                if space.type == 'VIEW_3D':
                    space.clip_start = 0.01
                    space.clip_end = 1000.0

if RENDER_ENGINE:
    try:
        scene.render.engine = RENDER_ENGINE
    except TypeError:
        print("Engine not available in this version:", RENDER_ENGINE)

if ADD_STUDIO_LIGHTS:
    studio = get_or_make_collection("Studio")
    def add_area(name, loc, power, size):
        if name in bpy.data.objects:
            return bpy.data.objects[name]
        data = bpy.data.lights.new(name, 'AREA')
        data.energy = power
        data.size = size
        ob = bpy.data.objects.new(name, data)
        ob.location = loc
        direction = Vector((0, 0, 0.5)) - Vector(loc)
        ob.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        studio.objects.link(ob)
        return ob
    add_area("Key", (3.0, -3.0, 3.5), 1000, 2.0)
    add_area("Fill", (-3.5, -2.0, 2.0), 350, 3.0)
    add_area("Rim", (0.0, 3.5, 3.0), 600, 1.5)

if ADD_CAMERA and "Cam" not in bpy.data.objects:
    studio = get_or_make_collection("Studio")
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("Cam", cam_data)
    cam.location = (3.5, -3.5, 2.2)
    cam.rotation_euler = (Vector((0, 0, 0.5)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    studio.objects.link(cam)
    scene.camera = cam

print("Units:", scene.unit_settings.system, "scale", scene.unit_settings.scale_length)
print("Active collection:", bpy.context.view_layer.active_layer_collection.name)
print("Scene objects:", len(scene.objects))
print("OK: scene ready. Build into collection:", asset_col.name)
