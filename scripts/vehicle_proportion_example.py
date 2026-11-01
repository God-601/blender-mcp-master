"""Measured, non-destructive *example* sedan blockout for Blender MCP.

Coordinates: +X is front; +Y is left; +Z is up. Wheel origins are at axles
to support future rotation. This is not a finished production car or vehicle rig.
Historic wheelbase/diameter figures are illustrative, NOT universal dimensions.
No bpy.ops, global scene settings, user-object edits or implicit overwrites.
"""
import math
import bpy
import bmesh

# ---- PROJECT CONFIG --------------------------------------------------------
ASSET_PREFIX = "MCP_ExampleCar"
COLLECTION_NAME = "MCP_ExampleCar_Kit"
LENGTH = 4.25
WIDTH = 1.78
WHEELBASE = 2.70
WHEEL_DIAMETER = 0.70
WHEEL_WIDTH = 0.20
WHEEL_SEGMENTS = 16
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_vehicle_example"
OWNER_VALUE = "sedan_blockout_v1"
WHEELS = (("FL", 1, 1), ("FR", 1, -1), ("RL", -1, 1), ("RR", -1, -1))
NAMES = [ASSET_PREFIX + "_Body", ASSET_PREFIX + "_Cabin"] + [
    ASSET_PREFIX + "_Wheel_" + side for side, _, _ in WHEELS
]

if not all(math.isfinite(float(v)) and v > 0 for v in
           (LENGTH, WIDTH, WHEELBASE, WHEEL_DIAMETER, WHEEL_WIDTH)):
    raise ValueError("All lengths and widths must be positive finite meters")
if not isinstance(WHEEL_SEGMENTS, int) or not 8 <= WHEEL_SEGMENTS <= 64:
    raise ValueError("WHEEL_SEGMENTS must be an integer in [8, 64]")
if WHEELBASE + WHEEL_DIAMETER >= LENGTH:
    raise ValueError("Vehicle length must leave room around both axle centers")
if WHEEL_WIDTH * 2 >= WIDTH:
    raise ValueError("Tire widths cannot fill the full vehicle width")
if any(name in bpy.data.objects for name in NAMES):
    raise ValueError("Output name exists; preserving prior user/agent objects")
existing_collection = bpy.data.collections.get(COLLECTION_NAME)
if existing_collection and existing_collection.get(OWNER_KEY) != OWNER_VALUE:
    raise ValueError("Collection name belongs to user: " + COLLECTION_NAME)


def make_box_vertices(x_len, y_len, z_len):
    x, y, z = x_len / 2, y_len / 2, z_len / 2
    return [(-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
            (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z)]


CLOSED_FACES = [(0, 3, 2, 1), (4, 5, 6, 7),
                (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def create_mesh(collection, name, vertices, faces, location, tint):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = None
    try:
        mesh.from_pydata(vertices, [], faces)
        mesh.update()
        # Recalculate normals on the new, sealed mesh; never edit another datablock.
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
            bm.to_mesh(mesh)
        finally:
            bm.free()
        obj = bpy.data.objects.new(name, mesh)
        obj[OWNER_KEY] = OWNER_VALUE
        obj["recipe_role"] = name.split("_")[-1]
        obj.location = location
        obj.color = tint
        collection.objects.link(obj)
        return obj
    except Exception:
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        raise


def make_cabin():
    # Lower windshield edge is inset from the hood; roof narrows in both axes.
    lower_x, upper_x = 0.96, 0.69
    lower_y, upper_y = WIDTH * .445, WIDTH * .37
    h = .57
    v = [(-lower_x, -lower_y, 0), (lower_x, -lower_y, 0),
         (lower_x, lower_y, 0), (-lower_x, lower_y, 0),
         (-upper_x, -upper_y, h), (upper_x, -upper_y, h),
         (upper_x, upper_y, h), (-upper_x, upper_y, h)]
    return v


def make_wheel():
    # Cylinder local axis Y; +Z is up. Object origin = center of the axle.
    radius = WHEEL_DIAMETER / 2
    half_width = WHEEL_WIDTH / 2
    vertices = []
    for y in (-half_width, half_width):
        for segment in range(WHEEL_SEGMENTS):
            angle = 2 * math.pi * segment / WHEEL_SEGMENTS
            vertices.append((radius * math.cos(angle), y, radius * math.sin(angle)))
    faces = [tuple(reversed(range(WHEEL_SEGMENTS))),
             tuple(range(WHEEL_SEGMENTS, 2 * WHEEL_SEGMENTS))]
    for i in range(WHEEL_SEGMENTS):
        j = (i + 1) % WHEEL_SEGMENTS
        faces.append((i, j, j + WHEEL_SEGMENTS, i + WHEEL_SEGMENTS))
    return vertices, faces


created, new_collection = [], False
if existing_collection is None:
    collection = bpy.data.collections.new(COLLECTION_NAME)
    collection[OWNER_KEY] = OWNER_VALUE
    bpy.context.scene.collection.children.link(collection)
    new_collection = True
else:
    collection = existing_collection

try:
    lower = WHEEL_DIAMETER - .04
    body_height = .46
    body = create_mesh(collection, NAMES[0],
                       make_box_vertices(LENGTH, WIDTH, body_height),
                       CLOSED_FACES, (0, 0, lower + body_height / 2),
                       (.18, .31, .43, 1))
    created.append(body)

    cabin = create_mesh(collection, NAMES[1], make_cabin(),
                        CLOSED_FACES, (0, 0, lower + body_height - .015),
                        (.25, .40, .54, 1))
    created.append(cabin)

    wheel_verts, wheel_faces = make_wheel()
    for suffix, ax_sign, side_sign in WHEELS:
        wheel = create_mesh(
            collection, ASSET_PREFIX + "_Wheel_" + suffix,
            wheel_verts, wheel_faces,
            (ax_sign * WHEELBASE / 2,
             side_sign * (WIDTH - WHEEL_WIDTH) / 2,
             WHEEL_DIAMETER / 2),
            (.09, .11, .14, 1))
        wheel["axle_role"] = suffix
        created.append(wheel)

    bpy.context.view_layer.update()  # make measured world-space bounds current
    print("VEHICLE EXAMPLE: SUCCESS",
          "length=", LENGTH, "width=", WIDTH, "wheelbase=", WHEELBASE,
          "wheel_diameter=", WHEEL_DIAMETER, "objects=", [o.name for o in created])
    print("TECHNICAL BLOCKOUT ONLY: inspect silhouettes, wheel wells, materials, and reference match.")
except Exception:
    for obj in reversed(created):
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    if new_collection and not collection.objects:
        bpy.data.collections.remove(collection)
    raise
