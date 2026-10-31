"""hard_surface_builder.py — procedural hard-surface panel with a recessed pocket.

Creates a new owned panel, non-destructive boolean cutter, and optional fasteners.
Existing scene objects are never edited or deleted.
"""
import bpy
import bmesh
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
COLLECTION_NAME = "MCP_HardSurface"
PANEL_NAME = "MCP_HS_Panel"
DIMENSIONS = (3.0, 0.35, 2.0)       # X, Y, Z
BEVEL_WIDTH = 0.035
POCKET = {"enabled": True, "width": 1.25, "height": 0.85, "depth": 0.12,
          "center_x": 0.0, "center_z": 0.0}
FASTENERS = {"enabled": True, "radius": 0.075, "depth": 0.045,
             "offset_x": 1.25, "offset_z": 0.75, "segments": 12}
LOCATION = (0.0, 0.0, 0.0)
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_hard_surface"
OWNER_VALUE = "hard_surface_panel_v1"


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("collection collision: " + COLLECTION_NAME)
    return col


def create_box(name, dims, location, collection):
    if name in bpy.data.objects:
        raise ValueError("object collision: " + name)
    dims = Vector(dims)
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


def create_fastener(name, radius, depth, location, segments, collection):
    if name in bpy.data.objects:
        raise ValueError("object collision: " + name)
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=max(6, int(segments)),
            radius1=radius, radius2=radius, depth=depth
        )
        bm.to_mesh(mesh)
    finally:
        bm.free()
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = Vector(location)
    obj[OWNER_KEY] = OWNER_VALUE
    bevel = obj.modifiers.new("Fastener_Bevel", "BEVEL")
    bevel.width = min(radius * 0.18, depth * 0.2)
    bevel.segments = 2
    return obj


if min(DIMENSIONS) <= 0 or BEVEL_WIDTH < 0:
    raise ValueError("panel dimensions must be positive and bevel non-negative")
if PANEL_NAME in bpy.data.objects:
    raise ValueError("panel already exists; refusing overwrite: " + PANEL_NAME)

collection = get_collection()
created = []
try:
    panel = create_box(PANEL_NAME, DIMENSIONS, LOCATION, collection)
    created.append(panel)
    bevel = panel.modifiers.new("Panel_Bevel", "BEVEL")
    bevel.width = min(BEVEL_WIDTH, min(DIMENSIONS) * 0.2)
    bevel.segments = 3
    bevel.harden_normals = True

    if POCKET.get("enabled"):
        width = float(POCKET["width"])
        height = float(POCKET["height"])
        depth = float(POCKET["depth"])
        if width <= 0 or height <= 0 or depth <= 0 or depth >= DIMENSIONS[1]:
            raise ValueError("pocket dimensions are invalid")
        if width >= DIMENSIONS[0] or height >= DIMENSIONS[2]:
            raise ValueError("pocket must fit inside the panel")
        cutter_name = PANEL_NAME + "_Pocket_Cutter"
        cutter = create_box(
            cutter_name, (width, depth + 0.02, height),
            (LOCATION[0] + float(POCKET["center_x"]),
             LOCATION[1] - DIMENSIONS[1] * 0.5 + depth * 0.5,
             LOCATION[2] + float(POCKET["center_z"])), collection
        )
        created.append(cutter)
        cutter.display_type = "WIRE"
        cutter.hide_render = True
        cutter.hide_set(True)
        boolean = panel.modifiers.new("Pocket_Difference", "BOOLEAN")
        boolean.operation = "DIFFERENCE"
        boolean.object = cutter
        if hasattr(boolean, "solver"):
            boolean.solver = "EXACT"

    if FASTENERS.get("enabled"):
        radius = float(FASTENERS["radius"])
        depth = float(FASTENERS["depth"])
        if radius <= 0 or depth <= 0:
            raise ValueError("fastener dimensions must be positive")
        ox = float(FASTENERS["offset_x"])
        oz = float(FASTENERS["offset_z"])
        y = LOCATION[1] - DIMENSIONS[1] * 0.5 - depth * 0.5
        for index, (sx, sz) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1)), 1):
            fastener = create_fastener(
                PANEL_NAME + "_Fastener_%02d" % index, radius, depth,
                (LOCATION[0] + sx * ox, y, LOCATION[2] + sz * oz),
                FASTENERS["segments"], collection
            )
            created.append(fastener)
    print("HARD SURFACE CREATED:", panel.name)
    print("parts:", [obj.name for obj in created])
    print("panel modifiers:", [mod.type for mod in panel.modifiers])
except Exception:
    for obj in reversed(created):
        mesh = obj.data if obj.type == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh and mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    raise
