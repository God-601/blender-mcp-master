# Hand-painting recipes (tested bpy snippets)

Companion to `references/hand-painted-pipeline.md` (workflow and art direction) and `references/uv-baking.md` (UV and bake theory). This file only adds **runnable recipes** that prepare a painted-look asset through MCP: curvature, painted marks, ambient occlusion and UV checks. Each code block is executed by `tests/test_reference_recipes.py` against the Blender version provided by `bpy`; passing means "runs without error and produces the expected datablocks", not "looks good". Judge the look with `look` and the checklist.

## What makes it read as painted
1. **Value first:** the grayscale render must already separate forms.
2. **Few hues, shifted shadows:** 4 to 8 base colors; shadows cooler and more saturated, highlights warmer. Never darken by mixing with black.
3. **One baked light direction** (usually top, slightly front), plus a soft bounce at the bottom.
4. **Edges tell the form:** light rim on convex edges, darker cavities and contact lines. This is the biggest single gain.
5. **Controlled variation:** large soft shifts and a few brush-like marks; avoid uniform noise and pure black or white.

## Recipe order
```
1. UV unwrap with consistent texel density          -> recipe D
2. Flat base colors per region (material or vertex color)
3. Masks: curvature (A) and ambient occlusion (C)
4. Compose in the shader: base * AO tint + edge highlight from curvature
5. Bake the composed result into one image (Emission bake), or add painted marks (B)
6. look at 3 angles, adjust, re-bake; save the image to disk
```
For true brush work, tell the user to continue in Texture Paint mode: the agent prepares UVs, colors, masks and material so painting starts mostly done.

## Palette helper
Pick a ramp per material instead of a single color. Example for "mossy stone": shadow `(0.18, 0.20, 0.26)`, mid `(0.42, 0.44, 0.45)`, light `(0.70, 0.68, 0.58)`, accent `(0.35, 0.50, 0.25)`. Values are linear RGBA when set on shader sockets, so convert hex from sRGB first (`color ** 2.2` as an approximation per channel).

## Snippets
Each block is standalone: it works on the active mesh object.

### A. Curvature to vertex color (convex = light, concave = dark; no Cycles needed)
```python
import bpy, bmesh
obj = bpy.context.active_object
me = obj.data
bm = bmesh.new()
bm.from_mesh(me)
values = []
for v in bm.verts:
    angles = [e.calc_face_angle_signed(0.0) for e in v.link_edges]   # + convex, - concave
    c = sum(angles) / len(angles) if angles else 0.0
    values.append(max(0.0, min(1.0, 0.5 + c * 0.5)))
bm.free()
attr = me.color_attributes.get("Curvature") or me.color_attributes.new("Curvature", 'FLOAT_COLOR', 'POINT')
flat = []
for g in values:
    flat += [g, g, g, 1.0]
attr.data.foreach_set("color", flat)
me.update()
print("curvature range", round(min(values), 3), round(max(values), 3), "verts", len(values))
```
Needs enough geometry near edges (bevels or a subdivision level) to be meaningful. In the material, read it with an Attribute node named `Curvature` and a Color Ramp for the highlight.

### B. Painted marks: soft brush stamps into an image (numpy, one pass)
```python
import bpy
import numpy as np
import random

def paint_stamps(img, stamps):
    """stamps: list of (u, v, radius_px, (r, g, b), opacity, hardness). u, v are 0-1."""
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(h, w, 4)
    yy, xx = np.mgrid[0:h, 0:w]
    for u, v, rad, rgb, opacity, hardness in stamps:
        d = np.sqrt((xx - u * w) ** 2 + (yy - v * h) ** 2) / max(rad, 1e-6)
        mask = np.clip((1.0 - d) / max(1.0 - hardness, 1e-3), 0.0, 1.0) * opacity
        for i in range(3):
            px[..., i] = px[..., i] * (1 - mask) + rgb[i] * mask
    img.pixels.foreach_set(px.ravel())
    img.update()

img = bpy.data.images.new("T_Paint_Test", 128, 128, alpha=False)
img.generated_color = (0.4, 0.4, 0.4, 1.0)
random.seed(7)
marks = [(random.random(), random.random(), random.uniform(4, 14), (0.6, 0.5, 0.3), 0.35, 0.3) for _ in range(30)]
paint_stamps(img, marks)
print("painted", img.name, img.size[:])
```
Keep stamp counts modest (tens to low hundreds) on 1024 px images; each stamp is a full-image numpy pass. Restrict the window to the stamp's bounding box if you need thousands.

### C. Bake ambient occlusion into an image (Cycles)
```python
import bpy
obj = bpy.context.active_object
assert obj and obj.type == 'MESH' and obj.data.uv_layers, "needs an active mesh with UVs"
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 32
scene.render.bake.margin = 8
img = bpy.data.images.new("T_AO", 256, 256, alpha=False)   # use 1024 or 2048 for real output
if not obj.data.materials:
    obj.data.materials.append(bpy.data.materials.new("MAT_BakeTemp"))
mat = obj.active_material
if mat.node_tree is None or bpy.app.version < (5, 0, 0):
    mat.use_nodes = True   # required before 5.0, deprecated after
node = mat.node_tree.nodes.new('ShaderNodeTexImage')
node.image = img
mat.node_tree.nodes.active = node        # bake writes to the ACTIVE image node
bpy.ops.object.bake(type='AO')
img.filepath_raw = "//T_AO.png"          # relative to the saved .blend; save the .blend first
img.file_format = 'PNG'
print("baked", img.name, "mean value", round(sum(img.pixels[:4000:4]) / 1000, 3))
```
Remove the temporary image node and material afterwards if they were not part of the asset. Restore the render engine the user had.

### D. Seams by angle, unwrap, pack and texel-density report
```python
import bpy, bmesh, math, statistics
obj = bpy.context.active_object
me = obj.data
TEX_SIZE = 1024
bm = bmesh.new()
bm.from_mesh(me)
seams = 0
for e in bm.edges:
    if len(e.link_faces) == 2 and e.calc_face_angle(0.0) > math.radians(60):
        e.seam = True
        seams += 1
bm.to_mesh(me)
bm.free()
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.02)
bpy.ops.uv.pack_islands(margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')
# Texel density in pixels per Blender unit (apply scale first, or the numbers are skewed).
bm = bmesh.new()
bm.from_mesh(me)
uv = bm.loops.layers.uv.active
densities = []
for f in bm.faces:
    pts = [l[uv].uv for l in f.loops]
    uv_area = abs(sum(a.x * b.y - b.x * a.y for a, b in zip(pts, pts[1:] + pts[:1]))) / 2.0
    if f.calc_area() > 1e-9 and uv_area > 0:
        densities.append(math.sqrt(uv_area / f.calc_area()) * TEX_SIZE)
bm.free()
print("seams marked:", seams, "| px/unit min/median/max:",
      round(min(densities), 1), round(statistics.median(densities), 1), round(max(densities), 1))
```
Large spread between min and max means uneven texel density: rescale islands before painting. The seam angle (60 degrees here) is a starting point; hide seams where paint can tolerate them.

## Pitfalls
- Baking needs UVs, an active image node and Object Mode; "no valid image" or black output usually means one of those.
- Do not bake lighting that depends on the scene (HDRI, sun) into a game texture unless that is the intent; AO and curvature are safe.
- Linear vs sRGB: color maps are sRGB, masks and normals are Non-Color.
- Nearest-neighbor filtering suits pixel/voxel looks; smooth filtering suits painted looks.

## Done when
Grayscale read is clear, edges are highlighted, cavities darker, palette limited, no pure black/white, one material and one texture (unless the budget allows more), image saved to disk, texture size within the budget.
