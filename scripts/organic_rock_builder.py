"""organic_rock_builder.py — deterministic stylized rock base mesh for Blender MCP.

Creates one new icosphere-derived rock in an owned collection. Existing scene objects
are never edited or deleted. The deformation uses deterministic smooth trigonometric
fields so it has no dependency on external textures or random state.
"""
import bpy
import bmesh
import math
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
OBJECT_NAME = "MCP_Organic_Rock"
COLLECTION_NAME = "MCP_Organic"
RADIUS = 1.0
SUBDIVISIONS = 2
ROUGHNESS = 0.22          # radial variation fraction; recommended 0.05–0.35
SEED = 7                  # deterministic variation selector
FLATTEN_BOTTOM = True
BOTTOM_LIMIT = -0.62      # local Z floor as a fraction of RADIUS
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_organic_rock"
OWNER_VALUE = "organic_rock_v1"


def get_owned_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Collection exists but is not owned by this generator: " + name)
    elif col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    return col


if RADIUS <= 0 or not 0.0 <= ROUGHNESS <= 0.6:
    raise ValueError("RADIUS must be positive and ROUGHNESS must be between 0 and 0.6")
if OBJECT_NAME in bpy.data.objects:
    raise ValueError("Object name already exists; refusing to overwrite: " + OBJECT_NAME)

collection = get_owned_collection(COLLECTION_NAME)
bm = bmesh.new()
try:
    bmesh.ops.create_icosphere(
        bm, subdivisions=max(1, min(6, int(SUBDIVISIONS))), radius=RADIUS
    )
    phase = float(SEED) * 0.731
    for vert in bm.verts:
        direction = vert.co.normalized()
        x, y, z = direction.x, direction.y, direction.z
        low = math.sin((x * 2.7 + phase) * 1.3) * math.sin((y * 3.1 - phase) * 1.1)
        mid = math.sin((y * 6.2 + z * 2.4 + phase) * 1.7)
        high = math.sin((x * 11.0 - y * 8.0 + z * 7.0 + phase) * 0.7)
        field = 0.55 * low + 0.30 * mid + 0.15 * high
        radius = RADIUS * (1.0 + ROUGHNESS * field)
        vert.co = direction * radius
        if FLATTEN_BOTTOM:
            vert.co.z = max(vert.co.z, RADIUS * BOTTOM_LIMIT)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(OBJECT_NAME + "_Mesh")
    bm.to_mesh(mesh)
finally:
    bm.free()

mesh.update()
obj = bpy.data.objects.new(OBJECT_NAME, mesh)
collection.objects.link(obj)
obj[OWNER_KEY] = OWNER_VALUE
obj["organic_seed"] = int(SEED)
obj["organic_roughness"] = float(ROUGHNESS)
print("CREATED:", obj.name)
print("vertices:", len(mesh.vertices), "faces:", len(mesh.polygons))
print("dimensions:", tuple(round(v, 4) for v in obj.dimensions))
print("seed:", SEED, "roughness:", ROUGHNESS, "flatten_bottom:", FLATTEN_BOTTOM)
