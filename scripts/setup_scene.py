"""Transactional scene setup: preserve existing user state and roll back on errors.

No user object, camera, light or material is reused unless it carries this
helper's ownership tag. Defaults do not change global units/engine/viewport.
"""
import bpy
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
ASSET_NAME = "Asset"
SET_UNITS = False
ADD_STUDIO_LIGHTS = False
ADD_CAMERA = False
RENDER_ENGINE = None
ACTIVATE_COLLECTION = False
SET_VIEWPORT_CLIP = False
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_setup_scene"
OWNER_VALUE = "setup_scene_v2"
ROLE_KEY = "_blender_mcp_setup_role"


def get_or_make_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to reuse unowned collection: " + name)
    return col


def find_layer_collection(layer_col, name):
    if layer_col.name == name:
        return layer_col
    for child in layer_col.children:
        item = find_layer_collection(child, name)
        if item:
            return item
    return None


def owned_object(studio, role, kind):
    return next((obj for obj in studio.objects
                 if obj.get(OWNER_KEY) == OWNER_VALUE
                 and obj.get(ROLE_KEY) == role and obj.type == kind), None)


def studio_light(studio, role, location, power, size):
    existing = owned_object(studio, role, "LIGHT")
    if existing is not None:
        print("REUSE owned light:", existing.name)
        return existing
    if role in bpy.data.objects:
        print("WARNING: user-owned object named", role, "is untouched; using a suffixed name")
    data = bpy.data.lights.new(role, "AREA")
    data.energy = power
    data.size = size
    obj = bpy.data.objects.new(role, data)
    obj[OWNER_KEY] = OWNER_VALUE
    obj[ROLE_KEY] = role
    obj.location = location
    obj.rotation_euler = (Vector((0, 0, 0.5)) - Vector(location)).to_track_quat("-Z", "Y").to_euler()
    studio.objects.link(obj)
    return obj


def studio_camera(studio):
    existing = owned_object(studio, "Cam", "CAMERA")
    if existing is not None:
        print("REUSE owned camera:", existing.name)
        return existing
    if "Cam" in bpy.data.objects:
        print("WARNING: user camera 'Cam' is untouched; using a suffixed name")
    data = bpy.data.cameras.new("Cam")
    data.lens = 50
    obj = bpy.data.objects.new("Cam", data)
    obj[OWNER_KEY] = OWNER_VALUE
    obj[ROLE_KEY] = "Cam"
    obj.location = (3.5, -3.5, 2.2)
    obj.rotation_euler = (Vector((0, 0, 0.5)) - obj.location).to_track_quat("-Z", "Y").to_euler()
    studio.objects.link(obj)
    return obj


scene = bpy.context.scene
if not isinstance(ASSET_NAME, str) or not ASSET_NAME.strip():
    raise ValueError("ASSET_NAME must be a nonempty collection name")
requested_collections = [ASSET_NAME] + (["Studio"] if ADD_STUDIO_LIGHTS or ADD_CAMERA else [])
for name in set(requested_collections):
    existing = bpy.data.collections.get(name)
    if existing and existing.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to reuse unowned collection: " + name)

unit = scene.unit_settings
old_units = (unit.system, unit.scale_length, unit.length_unit)
old_engine = scene.render.engine
old_camera = scene.camera
old_active_layer = bpy.context.view_layer.active_layer_collection
viewport_settings = []
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    viewport_settings.append((space, space.clip_start, space.clip_end))
prior_objects = set(bpy.data.objects)
prior_collections = set(bpy.data.collections)

try:
    asset_col = get_or_make_collection(ASSET_NAME)
    if SET_UNITS:
        unit.system = "METRIC"
        unit.scale_length = 1.0
        unit.length_unit = "METERS"
    if ACTIVATE_COLLECTION:
        layer = find_layer_collection(bpy.context.view_layer.layer_collection, asset_col.name)
        if layer:
            bpy.context.view_layer.active_layer_collection = layer
    if SET_VIEWPORT_CLIP:
        for space, _, _ in viewport_settings:
            space.clip_start = 0.01
            space.clip_end = 1000.0
    if RENDER_ENGINE is not None:
        scene.render.engine = RENDER_ENGINE

    if ADD_STUDIO_LIGHTS or ADD_CAMERA:
        studio = get_or_make_collection("Studio")
        if ADD_STUDIO_LIGHTS:
            studio_light(studio, "Key", (3.0, -3.0, 3.5), 1000, 2.0)
            studio_light(studio, "Fill", (-3.5, -2.0, 2.0), 350, 3.0)
            studio_light(studio, "Rim", (0.0, 3.5, 3.0), 600, 1.5)
        if ADD_CAMERA:
            cam = studio_camera(studio)
            if scene.camera is None:
                scene.camera = cam
            elif scene.camera != cam:
                print("Existing active scene camera retained:", scene.camera.name)
    print("Units:", unit.system, "scale", unit.scale_length)
    print("Active collection:", bpy.context.view_layer.active_layer_collection.name)
    print("Scene objects:", len(scene.objects))
    print("OK: scene ready. Build into collection:", asset_col.name)
except Exception:
    # Only remove objects/collections newly created during this call.
    for obj in list(bpy.data.objects):
        if obj not in prior_objects:
            data = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if data and data.users == 0:
                if isinstance(data, bpy.types.Light):
                    bpy.data.lights.remove(data)
                elif isinstance(data, bpy.types.Camera):
                    bpy.data.cameras.remove(data)
    for col in list(bpy.data.collections):
        if col not in prior_collections:
            bpy.data.collections.remove(col)
    unit.system, unit.scale_length, unit.length_unit = old_units
    scene.render.engine = old_engine
    scene.camera = old_camera
    bpy.context.view_layer.active_layer_collection = old_active_layer
    for space, start, end in viewport_settings:
        space.clip_start, space.clip_end = start, end
    print("ROLLBACK: scene setup restored previous state")
    raise
