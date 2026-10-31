"""organic_tree_builder.py — deterministic stylized tree with tapered branches and foliage."""
import bpy
import bmesh
import math
import random
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
OBJECT_PREFIX = "MCP_Tree"
COLLECTION_NAME = "MCP_Organic_Tree"
SEED = 17
TRUNK_HEIGHT = 4.0
TRUNK_RADIUS = 0.22
BRANCH_COUNT = 7
FOLIAGE_COUNT = 9
FOLIAGE_RADIUS = 0.62
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_organic_tree"
OWNER_VALUE = "organic_tree_v1"


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("collection collision: " + COLLECTION_NAME)
    return col


def make_tapered(name, start, end, radius_start, radius_end, collection, vertices=8):
    delta = end - start
    if delta.length <= 1e-8:
        raise ValueError("branch endpoints must differ")
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=max(5, int(vertices)),
            radius1=radius_start, radius2=radius_end, depth=delta.length
        )
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = (start + end) * 0.5
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    obj[OWNER_KEY] = OWNER_VALUE
    return obj


def make_foliage(name, location, radius, collection, subdivisions=1):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_icosphere(bm, subdivisions=max(1, int(subdivisions)), radius=radius)
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    obj[OWNER_KEY] = OWNER_VALUE
    return obj


if TRUNK_HEIGHT <= 0 or TRUNK_RADIUS <= 0 or BRANCH_COUNT < 0 or FOLIAGE_COUNT < 1 or FOLIAGE_RADIUS <= 0:
    raise ValueError("tree parameters are invalid")
planned_names = [OBJECT_PREFIX + "_Trunk"] + [
    OBJECT_PREFIX + "_Branch_%02d" % (index + 1) for index in range(BRANCH_COUNT)
] + [
    OBJECT_PREFIX + "_Canopy_%02d" % (index + 1) for index in range(FOLIAGE_COUNT)
]
collisions = [name for name in planned_names if name in bpy.data.objects]
if collisions:
    raise ValueError("tree output names already exist; refusing overwrite: " + ", ".join(collisions))
rng = random.Random(int(SEED))
collection = get_collection()
created = []
try:
    trunk = make_tapered(
        OBJECT_PREFIX + "_Trunk", Vector((0, 0, 0)),
        Vector((0, 0, TRUNK_HEIGHT)), TRUNK_RADIUS, TRUNK_RADIUS * 0.48,
        collection, 10
    )
    created.append(trunk)
    branch_ends = []
    for index in range(BRANCH_COUNT):
        z = TRUNK_HEIGHT * (0.30 + 0.62 * (index + 1) / (BRANCH_COUNT + 1))
        angle = (2.0 * math.pi * index / max(1, BRANCH_COUNT)) + rng.uniform(-0.22, 0.22)
        length = TRUNK_HEIGHT * rng.uniform(0.22, 0.38)
        start = Vector((0, 0, z))
        end = Vector((math.cos(angle) * length, math.sin(angle) * length, z + length * rng.uniform(0.22, 0.52)))
        branch = make_tapered(
            OBJECT_PREFIX + "_Branch_%02d" % (index + 1), start, end,
            TRUNK_RADIUS * 0.46, TRUNK_RADIUS * 0.16, collection, 7
        )
        created.append(branch)
        branch_ends.append(end)
    for index in range(FOLIAGE_COUNT):
        if index < len(branch_ends):
            center = branch_ends[index] + Vector((0, 0, 0.28))
        else:
            center = Vector((rng.uniform(-0.85, 0.85), rng.uniform(-0.85, 0.85),
                             TRUNK_HEIGHT * rng.uniform(0.68, 1.12)))
        radius = FOLIAGE_RADIUS * rng.uniform(0.72, 1.12)
        foliage = make_foliage(
            OBJECT_PREFIX + "_Canopy_%02d" % (index + 1), center, radius, collection, 1
        )
        created.append(foliage)
    for obj in created:
        obj["organic_seed"] = int(SEED)
    print("ORGANIC TREE:", OBJECT_PREFIX, "objects=", len(created), "seed=", SEED)
except Exception:
    for obj in reversed(created):
        mesh = obj.data
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    raise
