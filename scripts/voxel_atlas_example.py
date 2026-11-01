"""Safe voxel example: 0.28 m grid, exposed faces, one 64x8 palette atlas.

The 0.28 m grid and the 64x8 atlas are *historical examples*, not platform
requirements. Set GRID_UNIT and texture layout to match the actual project.
No bpy.ops, no external resources, no scene-wide object or material changes.
"""
import math
import bpy

# ---- PROJECT CONFIG --------------------------------------------------------
ASSET_PREFIX = "MCP_VoxelStudy"
COLLECTION_NAME = "MCP_VoxelStudy_Kit"
GRID_UNIT = 0.28
ATLAS_WIDTH = 64
ATLAS_HEIGHT = 8
TILE_SIZE = 8
# A small step-shaped connected solid: one block is one grid unit.
CELLS = [(0,0,0),(1,0,0),(2,0,0),(0,1,0),(1,1,0),(2,1,0),(1,0,1),(1,1,1)]
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_voxel_example"
OWNER_VALUE = "voxel_atlas_v1"
OBJ_NAME = ASSET_PREFIX + "_Mesh"
MAT_NAME = ASSET_PREFIX + "_Material"
IMAGE_NAME = ASSET_PREFIX + "_Atlas"
COLORS = [(0.24, 0.38, 0.51, 1), (0.46, 0.60, 0.69, 1),
          (0.73, 0.56, 0.34, 1), (0.35, 0.53, 0.38, 1),
          (0.71, 0.36, 0.27, 1), (0.37, 0.31, 0.55, 1),
          (0.78, 0.72, 0.54, 1), (0.22, 0.23, 0.28, 1)]
# Each neighbor direction maps to an outward-oriented quad and an atlas tile.
SIDES = (
    ((1, 0, 0), ((1,0,0),(1,1,0),(1,1,1),(1,0,1)), 0),
    ((-1,0,0), ((0,0,0),(0,0,1),(0,1,1),(0,1,0)), 1),
    ((0,1,0), ((0,1,0),(0,1,1),(1,1,1),(1,1,0)), 2),
    ((0,-1,0), ((0,0,0),(1,0,0),(1,0,1),(0,0,1)), 3),
    ((0,0,1), ((0,0,1),(1,0,1),(1,1,1),(0,1,1)), 4),
    ((0,0,-1),((0,0,0),(0,1,0),(1,1,0),(1,0,0)), 5),
)

if not math.isfinite(float(GRID_UNIT)) or GRID_UNIT <= 0:
    raise ValueError("GRID_UNIT must be positive and finite")
if not all(isinstance(n, int) and n > 0 for n in
           (ATLAS_WIDTH, ATLAS_HEIGHT, TILE_SIZE)):
    raise ValueError("Atlas dimensions/tile size must be positive integers")
if ATLAS_WIDTH % TILE_SIZE or ATLAS_HEIGHT != TILE_SIZE:
    raise ValueError("This one-row atlas example requires tile-aligned width and height")
if ATLAS_WIDTH // TILE_SIZE != len(COLORS):
    raise ValueError("Provide one palette color for every atlas tile")
if not CELLS or any(len(c) != 3 or any(not isinstance(v, int) for v in c) for c in CELLS):
    raise ValueError("CELLS must contain integer xyz grid positions")
occupied = set(CELLS)
if len(occupied) != len(CELLS):
    raise ValueError("Duplicate grid cells are not supported")
if any(name in bpy.data.objects for name in (OBJ_NAME,)):
    raise ValueError("Output object collision: " + OBJ_NAME)
if MAT_NAME in bpy.data.materials or IMAGE_NAME in bpy.data.images:
    raise ValueError("Material/image name collision; refusing to overwrite user data")
existing_col = bpy.data.collections.get(COLLECTION_NAME)
if existing_col and existing_col.get(OWNER_KEY) != OWNER_VALUE:
    raise ValueError("Refusing user-owned collection collision: " + COLLECTION_NAME)

mesh = None
image = None
material = None
obj = None
created_col = False
collection = existing_col
try:
    # Shared corner vertices keep connected voxels topologically welded.
    vertices, faces, tiles, corners = [], [], [], {}
    for cell in sorted(occupied):
        for direction, quad, tile in SIDES:
            neighbor = tuple(cell[i] + direction[i] for i in range(3))
            if neighbor in occupied:
                continue  # never build internal faces between occupied cells
            face_indices = []
            for local in quad:
                key = tuple(cell[i] + local[i] for i in range(3))
                if key not in corners:
                    corners[key] = len(vertices)
                    vertices.append(tuple(v * GRID_UNIT for v in key))
                face_indices.append(corners[key])
            faces.append(tuple(face_indices))
            tiles.append(tile)

    mesh = bpy.data.meshes.new(OBJ_NAME + "_Data")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    uv = mesh.uv_layers.new(name="PaletteAtlas")
    for polygon, tile in zip(mesh.polygons, tiles):
        u0 = (tile * TILE_SIZE + .5) / ATLAS_WIDTH
        u1 = ((tile + 1) * TILE_SIZE - .5) / ATLAS_WIDTH
        v0, v1 = .5 / ATLAS_HEIGHT, (ATLAS_HEIGHT - .5) / ATLAS_HEIGHT
        quad_uvs = ((u0,v0),(u1,v0),(u1,v1),(u0,v1))
        for loop_index, value in zip(polygon.loop_indices, quad_uvs):
            uv.data[loop_index].uv = value

    image = bpy.data.images.new(IMAGE_NAME, width=ATLAS_WIDTH,
                                height=ATLAS_HEIGHT, alpha=True)
    rgba = []
    for row in range(ATLAS_HEIGHT):
        for x in range(ATLAS_WIDTH):
            rgba.extend(COLORS[x // TILE_SIZE])
    image.pixels.foreach_set(rgba)
    image.update()

    material = bpy.data.materials.new(MAT_NAME)
    if material.node_tree is None or bpy.app.version < (5,0,0):
        material.use_nodes = True
    material.diffuse_color = COLORS[0]
    material[OWNER_KEY] = OWNER_VALUE
    nodes = material.node_tree.nodes
    bsdf = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    texture = nodes.new("ShaderNodeTexImage")
    texture.name = "PaletteAtlas_64x8_Example"
    texture.image = image
    texture.interpolation = "Closest"
    material.node_tree.links.new(texture.outputs["Color"], bsdf.inputs["Base Color"])
    mesh.materials.append(material)

    if collection is None:
        collection = bpy.data.collections.new(COLLECTION_NAME)
        collection[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(collection)
        created_col = True
    obj = bpy.data.objects.new(OBJ_NAME, mesh)
    obj[OWNER_KEY] = OWNER_VALUE
    obj["grid_unit_m"] = GRID_UNIT
    obj["cell_count"] = len(occupied)
    obj["exposed_quads"] = len(faces)
    collection.objects.link(obj)
    print("VOXEL EXAMPLE: SUCCESS cells=", len(occupied),
          "exposed_quads=", len(faces), "tris=", len(faces) * 2,
          "grid_m=", GRID_UNIT,
          "atlas=", (ATLAS_WIDTH, ATLAS_HEIGHT))
    print("Palette texture is generated inside the .blend; validate export and mip filtering separately.")
except Exception:
    if obj is not None:
        bpy.data.objects.remove(obj, do_unlink=True)
    if created_col and collection is not None and not collection.objects:
        bpy.data.collections.remove(collection)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)
    if material is not None and material.users == 0:
        bpy.data.materials.remove(material)
    if image is not None and image.users == 0:
        bpy.data.images.remove(image)
    raise
