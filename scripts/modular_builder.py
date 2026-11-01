"""modular_builder.py — reusable parametric architecture components for Blender MCP.

Creates staircase and masonry-arch components in a dedicated, owned collection.
Every generated object is new; existing scene objects and collections are protected.
"""
import bpy
import bmesh
import math
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
COLLECTION_NAME = "MCP_Modular_Architecture"
COMPONENTS = [
    {"name": "Stair", "type": "staircase", "steps": 6,
     "width": 2.0, "depth": 2.4, "rise": 1.2, "location": (0, 0, 0)},
    {"name": "GateArch", "type": "arch", "outer_radius": 1.5,
     "wall_thickness": 0.25, "leg_height": 2.0, "depth": 0.5,
     "segments": 16, "location": (4, 0, 0)},
]
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_modular_builder"
OWNER_VALUE = "modular_builder_v1"


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Collection exists but is not owned by this builder: " + COLLECTION_NAME)
    elif col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


def ensure_name_available(name):
    if name in bpy.data.objects:
        raise ValueError("Object name already exists; refusing overwrite: " + name)


def create_box(name, dimensions, location, collection):
    ensure_name_available(name)
    dims = Vector(dimensions)
    if min(dims) <= 0:
        raise ValueError("box dimensions must be positive")
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, verts=bm.verts, vec=dims)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = Vector(location)
    obj[OWNER_KEY] = OWNER_VALUE
    return obj


def build_staircase(spec, collection):
    count = int(spec.get("steps", 5))
    width = float(spec.get("width", 2.0))
    total_depth = float(spec.get("depth", 2.0))
    total_rise = float(spec.get("rise", 1.0))
    if count < 1 or width <= 0 or total_depth <= 0 or total_rise <= 0:
        raise ValueError("staircase steps and dimensions must be positive")
    origin = Vector(spec.get("location", (0, 0, 0)))
    step_depth = total_depth / count
    step_rise = total_rise / count
    created = []
    try:
        for index in range(count):
            height = (index + 1) * step_rise
            location = origin + Vector((0, (index + 0.5) * step_depth, height * 0.5))
            obj = create_box(
                "%s_Step_%02d" % (spec["name"], index + 1),
                (width, step_depth, height), location, collection
            )
            obj["stair_index"] = index + 1
            created.append(obj)
    except Exception:
        # Roll back only objects created by this operation.
        for obj in reversed(created):
            mesh = obj.data
            bpy.data.objects.remove(obj, do_unlink=True)
            if mesh.users == 0:
                bpy.data.meshes.remove(mesh)
        raise
    return created


def build_arch(spec, collection):
    name = str(spec["name"])
    ensure_name_available(name)
    outer = float(spec.get("outer_radius", 1.5))
    thickness = float(spec.get("wall_thickness", 0.25))
    leg_height = float(spec.get("leg_height", 2.0))
    depth = float(spec.get("depth", 0.5))
    segments = max(4, int(spec.get("segments", 16)))
    inner = outer - thickness
    if outer <= 0 or thickness <= 0 or inner <= 0 or leg_height <= 0 or depth <= 0:
        raise ValueError("arch dimensions are invalid")
    profile = [(-outer, 0.0), (-outer, leg_height)]
    for i in range(1, segments + 1):
        angle = 3.141592653589793 - 3.141592653589793 * i / segments
        profile.append((outer * math.cos(angle),
                        leg_height + outer * math.sin(angle)))
    profile.append((outer, 0.0))
    profile.append((inner, 0.0))
    profile.append((inner, leg_height))
    for i in range(1, segments + 1):
        angle = 3.141592653589793 * i / segments
        profile.append((inner * math.cos(angle),
                        leg_height + inner * math.sin(angle)))
    profile.append((-inner, 0.0))

    # Normalize the 2D profile winding before extruding along Y.
    area2 = sum(profile[i][0] * profile[(i + 1) % len(profile)][1] -
                profile[(i + 1) % len(profile)][0] * profile[i][1]
                for i in range(len(profile)))
    if area2 < 0:
        profile.reverse()
    n = len(profile)
    verts = [(x, -depth * 0.5, z) for x, z in profile]
    verts += [(x, depth * 0.5, z) for x, z in profile]
    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]
    for i in range(n):
        j = (i + 1) % n
        # With a CCW XZ profile, outward wall winding must go toward -Y first.
        faces.append((i, i + n, j + n, j))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(verbose=False, clean_customdata=False)
    mesh.update()
    if not mesh.polygons:
        bpy.data.meshes.remove(mesh)
        raise ValueError("arch profile generated an invalid mesh")
    # Winding can reverse when projecting the concave arch profile onto XZ.
    # A closed architectural solid must have positive signed volume.
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        if bm.calc_volume(signed=True) < 0:
            bmesh.ops.reverse_faces(bm, faces=list(bm.faces))
            bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = Vector(spec.get("location", (0, 0, 0)))
    obj[OWNER_KEY] = OWNER_VALUE
    return [obj]


def build_component(spec, collection):
    kind = spec["type"]
    if kind == "staircase":
        return build_staircase(spec, collection)
    if kind == "arch":
        return build_arch(spec, collection)
    raise ValueError("unsupported modular component type: " + str(kind))


collection = get_collection()
created = []
errors = []
for component in COMPONENTS:
    try:
        objects = build_component(component, collection)
        created.extend(objects)
        print("CREATED:", component["name"], "objects=", [obj.name for obj in objects])
    except Exception as exc:
        errors.append((component.get("name", "<unnamed>"), str(exc)))
        print("ERROR:", component.get("name", "<unnamed>"), repr(exc))

print("MODULAR BUILD REPORT")
print("created_objects:", len(created), "errors:", len(errors))
print("result:", "SUCCESS" if not errors else "PARTIAL")
