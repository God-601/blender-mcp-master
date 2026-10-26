"""pbr_material.py - create (or update) a clean Principled BSDF material and optionally assign it.
Works on Blender 3.x and 4.x socket names. Paste into execute_blender_code.
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
ASSIGN_TO = []                      # object names to assign (replaces all slots with this one material)
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
for key, path in TEXTURES.items():
    if key not in ("color", "rough", "metal", "normal"):
        raise ValueError(f"Unknown texture slot {key!r}; use color, rough, metal or normal")
    if not os.path.isfile(bpy.path.abspath(path)):
        raise FileNotFoundError(f"Texture file for {key!r} not found: {path}")

existing_mat = bpy.data.materials.get(NAME)
if existing_mat is not None:
    print(f"Updating existing material {NAME!r} (Principled values are overwritten).")
mat = existing_mat or bpy.data.materials.new(NAME)
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
# Set alpha and render method. Blender 4.2+ removed the old Alpha Clip render mode;
# reproduce it with a Greater Than node, as recommended by Blender's migration docs.
set_input(bsdf, ["Alpha"], ALPHA)
if hasattr(mat, "surface_render_method"):                      # Blender 4.2+
    if ALPHA < 1.0 and ALPHA_MODE == "BLEND":
        mat.surface_render_method = 'BLENDED'
    else:
        mat.surface_render_method = 'DITHERED'
    if ALPHA < 1.0 and ALPHA_MODE == "CLIP":
        clip = nodes.new('ShaderNodeMath')
        clip.operation = 'GREATER_THAN'
        clip.inputs[0].default_value = ALPHA
        clip.inputs[1].default_value = ALPHA_THRESHOLD
        clip.location = (-250, 250)
        clip.label = "Alpha Clip Threshold"
        clip["_blender_mcp_generated"] = True
        replace_input_link(clip.outputs[0], bsdf.inputs["Alpha"])
elif hasattr(mat, "blend_method"):                             # Blender 4.1 and older
    mat.alpha_threshold = ALPHA_THRESHOLD
    if ALPHA < 1.0:
        mat.blend_method = 'BLEND' if ALPHA_MODE == "BLEND" else ('HASHED' if ALPHA_MODE == "DITHERED" else 'CLIP')
    else:
        mat.blend_method = 'OPAQUE'


def add_tex(path, label, noncolor, x, y):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = 'Non-Color' if noncolor else 'sRGB'
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


if TEXTURES:
    if "color" in TEXTURES:
        n = add_tex(TEXTURES["color"], "Base Color", False, -600, 300)
        replace_input_link(n.outputs['Color'], bsdf.inputs['Base Color'])
    if "rough" in TEXTURES:
        n = add_tex(TEXTURES["rough"], "Roughness", True, -600, 0)
        replace_input_link(n.outputs['Color'], bsdf.inputs['Roughness'])
    if "metal" in TEXTURES:
        n = add_tex(TEXTURES["metal"], "Metallic", True, -600, -300)
        replace_input_link(n.outputs['Color'], bsdf.inputs['Metallic'])
    if "normal" in TEXTURES:
        n = add_tex(TEXTURES["normal"], "Normal", True, -900, -600)
        nm = nodes.new('ShaderNodeNormalMap')
        nm["_blender_mcp_generated"] = True
        nm.location = (-300, -600)
        replace_input_link(n.outputs['Color'], nm.inputs['Color'])
        replace_input_link(nm.outputs['Normal'], bsdf.inputs['Normal'])

for name in ASSIGN_TO:
    ob = bpy.data.objects.get(name)
    if ob is None or ob.type != 'MESH':
        print("skip", name)
        continue
    if ob.data.users > 1:
        print(f"WARNING: {name} shares mesh data with {ob.data.users - 1} other user(s); they get this material too.")
    ob.data.materials.clear()
    ob.data.materials.append(mat)
    print(f"assigned {NAME} -> {name}")

print(f"Material '{NAME}' ready: color={tuple(round(c,3) for c in BASE_COLOR)} metallic={METALLIC} roughness={ROUGHNESS} users={mat.users}")
if mat.users == 0:
    mat.use_fake_user = True
    print("note: no users yet, fake user set so it is kept when saving. Assign it to an object.")
