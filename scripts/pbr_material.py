"""pbr_material.py - create (or update) a clean Principled BSDF material and optionally assign it.
Supports Blender 3.x-5.x socket names. Paste into execute_blender_code.
"""
import os
import bpy

# ---- CONFIG ----------------------------------------------------------------
NAME = "MAT_Example"
BASE_COLOR = (0.8, 0.8, 0.8, 1.0)   # linear RGBA
METALLIC = 0.0
ROUGHNESS = 0.5
EMISSION_COLOR = None               # e.g. (1, 0.4, 0.1, 1) or None
EMISSION_STRENGTH = 0.0
ALPHA = 1.0                         # <1 uses blend/clip, see ALPHA_MODE
ALPHA_MODE = "CLIP"                 # "CLIP" (binary cutout), "DITHERED", or "BLEND"
ALPHA_THRESHOLD = 0.5               # alpha values must be strictly greater than this for CLIP
IOR = 1.45
TEXTURES = {}                       # e.g. {"color": "C:/tex/wood_diff.png", "rough": "...", "normal": "...", "metal": "..."}
ASSIGN_TO = []                      # explicit objects; empty changes no objects
USE_COLOR_ALPHA = True             # use color texture's alpha channel when present
REPLACE_MATERIAL_SLOTS = False     # opt-in destructive removal of existing slots
ALLOW_SHARED_MATERIAL_UPDATE = False  # opt-in updates when material is shared
OWNER_KEY = "_blender_mcp_pbr_owned"
OWNER_VALUE = "pbr_material_v2"
# ----------------------------------------------------------------------------


def set_input(node, names, value):
    """Set the first existing socket from a list of possible names."""
    for n in names:
        s = node.inputs.get(n)
        if s is not None:
            try:
                s.default_value = value
            except TypeError:
                s.default_value = (value, value, value, 1.0) if isinstance(value, (int, float)) else value
            return True
    return False


# Validate everything that can fail BEFORE touching the material, so a bad path
# cannot leave a half-updated material or delete textures from a previous run.
if ALPHA_MODE not in {"CLIP", "DITHERED", "BLEND"}:
    raise ValueError("ALPHA_MODE must be CLIP, DITHERED or BLEND")
if not 0.0 <= ALPHA_THRESHOLD <= 1.0:
    raise ValueError("ALPHA_THRESHOLD must be in [0, 1]")
if not 0.0 <= ALPHA <= 1.0:
    raise ValueError("ALPHA must be in [0, 1]")
existing_mat = bpy.data.materials.get(NAME)
if existing_mat is not None:
    if existing_mat.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to modify existing unowned material: " + NAME)
    if existing_mat.users > 1 and not ALLOW_SHARED_MATERIAL_UPDATE:
        raise ValueError("Refusing to update a shared material: " + NAME)
for name in ASSIGN_TO:
    target = bpy.data.objects.get(name)
    if target is None or target.type != "MESH":
        print("SKIP: missing or non-mesh material target:", name)
    elif target.library or target.data.library or target.data.users > 1:
        raise ValueError("Refusing to change a linked/shared mesh's material slots: " + name)
for key, path in TEXTURES.items():
    if key not in ("color", "rough", "metal", "normal"):
        raise ValueError(f"Unknown texture slot {key!r}; use color, rough, metal or normal")
    if not os.path.isfile(bpy.path.abspath(path)):
        raise FileNotFoundError(f"Texture file for {key!r} not found: {path}")

# Load every replacement image before modifying any material nodes. A file may
# exist but still be unreadable by Blender; that must not destroy the old setup.
_loaded_images = {}
_existing_image_names = {image.name for image in bpy.data.images}
try:
    for key, path in TEXTURES.items():
        _loaded_images[key] = bpy.data.images.load(bpy.path.abspath(path), check_existing=True)
except Exception:
    for image in _loaded_images.values():
        if image.name not in _existing_image_names and image.users == 0:
            bpy.data.images.remove(image)
    raise

if existing_mat is not None:
    print(f"Updating owned material {NAME!r}.")
mat = existing_mat or bpy.data.materials.new(NAME)
mat[OWNER_KEY] = OWNER_VALUE
# use_nodes is required before Blender 5.0 and deprecated afterwards (node trees always exist there).
if mat.node_tree is None or bpy.app.version < (5, 0, 0):
    mat.use_nodes = True
nt = mat.node_tree
nodes, links = nt.nodes, nt.links
# Remove nodes created by this script on previous runs; preserve user-authored nodes.
for node in list(nodes):
    if node.get("_blender_mcp_generated", False):
        nodes.remove(node)
bsdf = next((n for n in nodes if n.type == 'BSDF_PRINCIPLED'), None)
if bsdf is None:
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
out = next((n for n in nodes if n.type == 'OUTPUT_MATERIAL'), None) or nodes.new('ShaderNodeOutputMaterial')
if not any(l.to_node == out and l.from_node == bsdf for l in links):
    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

set_input(bsdf, ["Base Color"], BASE_COLOR)
set_input(bsdf, ["Metallic"], METALLIC)
set_input(bsdf, ["Roughness"], ROUGHNESS)
set_input(bsdf, ["IOR"], IOR)
if EMISSION_COLOR is not None:
    set_input(bsdf, ["Emission Color", "Emission"], EMISSION_COLOR)
    set_input(bsdf, ["Emission Strength"], EMISSION_STRENGTH)
else:
    # Prevent stale emission from a previous run when this config disables it.
    set_input(bsdf, ["Emission Color", "Emission"], (0.0, 0.0, 0.0, 1.0))
    set_input(bsdf, ["Emission Strength"], 0.0)
# Alpha render mode is chosen once, but nodes are wired after image textures.
# Color texture alpha is meaningful even when the global ALPHA is 1.
use_alpha = ALPHA < 1.0 or (USE_COLOR_ALPHA and "color" in TEXTURES)
set_input(bsdf, ["Alpha"], ALPHA)
if hasattr(mat, "surface_render_method"):                      # Blender 4.2+
    mat.surface_render_method = "BLENDED" if use_alpha and ALPHA_MODE == "BLEND" else "DITHERED"
elif hasattr(mat, "blend_method"):                             # Blender 4.1 and older
    mat.alpha_threshold = ALPHA_THRESHOLD
    mat.blend_method = ("BLEND" if ALPHA_MODE == "BLEND" else
                        ("HASHED" if ALPHA_MODE == "DITHERED" else "CLIP")) if use_alpha else "OPAQUE"

def add_tex(img, label, noncolor, x, y):
    required = 'Non-Color' if noncolor else 'sRGB'
    if img.colorspace_settings.name != required:
        if img.name in _existing_image_names:
            # Color-space metadata belongs to the image datablock globally.
            # Copy a pre-existing image rather than changing another material.
            img = img.copy()
            img.name = "MCP_" + label.replace(" ", "_") + "_" + img.name
        img.colorspace_settings.name = required
    n = nodes.new('ShaderNodeTexImage')
    n["_blender_mcp_generated"] = True
    n.image = img
    n.label = label
    n.location = (x, y)
    return n

def replace_input_link(output_socket, input_socket):
    """Replace an existing connection to this input rather than stacking links."""
    for link in list(input_socket.links):
        links.remove(link)
    links.new(output_socket, input_socket)


alpha_source = None
if TEXTURES:
    if "color" in TEXTURES:
        n = add_tex(_loaded_images["color"], "Base Color", False, -600, 300)
        replace_input_link(n.outputs['Color'], bsdf.inputs['Base Color'])
        if USE_COLOR_ALPHA:
            alpha_source = n.outputs['Alpha']
    if "rough" in TEXTURES:
        n = add_tex(_loaded_images["rough"], "Roughness", True, -600, 0)
        replace_input_link(n.outputs['Color'], bsdf.inputs['Roughness'])
    if "metal" in TEXTURES:
        n = add_tex(_loaded_images["metal"], "Metallic", True, -600, -300)
        replace_input_link(n.outputs['Color'], bsdf.inputs['Metallic'])
    if "normal" in TEXTURES:
        n = add_tex(_loaded_images["normal"], "Normal", True, -900, -600)
        nm = nodes.new('ShaderNodeNormalMap')
        nm["_blender_mcp_generated"] = True
        nm.location = (-300, -600)
        replace_input_link(n.outputs['Color'], nm.inputs['Color'])
        replace_input_link(nm.outputs['Normal'], bsdf.inputs['Normal'])

# Build alpha routing after texture nodes. This supports transparent color maps,
# including CLIP on Blender 4.2+ where the old alpha clip mode was removed.
if alpha_source is not None:
    multiply = nodes.new("ShaderNodeMath")
    multiply.operation = "MULTIPLY"
    multiply.inputs[1].default_value = ALPHA
    multiply["_blender_mcp_generated"] = True
    replace_input_link(alpha_source, multiply.inputs[0])
    alpha_source = multiply.outputs[0]

if use_alpha and ALPHA_MODE == "CLIP" and hasattr(mat, "surface_render_method"):
    clip = nodes.new("ShaderNodeMath")
    clip.operation = "GREATER_THAN"
    clip.inputs[1].default_value = ALPHA_THRESHOLD
    clip["_blender_mcp_generated"] = True
    if alpha_source is not None:
        replace_input_link(alpha_source, clip.inputs[0])
    else:
        clip.inputs[0].default_value = ALPHA
    replace_input_link(clip.outputs[0], bsdf.inputs["Alpha"])
elif alpha_source is not None:
    replace_input_link(alpha_source, bsdf.inputs["Alpha"])
else:
    for old_link in list(bsdf.inputs["Alpha"].links):
        links.remove(old_link)
    set_input(bsdf, ["Alpha"], ALPHA)

for name in ASSIGN_TO:
    ob = bpy.data.objects.get(name)
    if ob is None or ob.type != 'MESH':
        print("SKIP: missing or non-mesh material target:", name)
        continue
    if REPLACE_MATERIAL_SLOTS:
        ob.data.materials.clear()
    if not any(slot == mat for slot in ob.data.materials):
        ob.data.materials.append(mat)
    print(f"assigned {NAME} -> {name} (replace_slots={REPLACE_MATERIAL_SLOTS})")

print(f"Material '{NAME}' ready: color={tuple(round(c,3) for c in BASE_COLOR)} metallic={METALLIC} roughness={ROUGHNESS} users={mat.users}")
if mat.users == 0:
    mat.use_fake_user = True
    print("note: no users yet, fake user set so it is kept when saving. Assign it to an object.")
