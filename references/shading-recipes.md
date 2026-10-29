# Shading recipes: normals, bevel highlights, toon and outline (tested bpy snippets)

Companion to `references/materials.md` (PBR, procedural, toon diagnostics). This file adds the **normal-handling rules** and **runnable recipes**; every code block is executed by `tests/test_reference_recipes.py` on the Blender version provided by `bpy`. Passing means the code runs and creates the expected datablocks, not that the result looks right: check with `look`. Most ugly models are not bad geometry, they are bad normals.

## Decide the shading style first
| Style | Normals | Shader |
|---|---|---|
| Hard-surface / realistic | Smooth + sharp edges by angle, small bevels, weighted normals | Principled BSDF |
| Organic | Fully smooth (or Subdivision) | Principled, SSS where needed |
| Low-poly faceted | Flat | Principled, rough, or unlit-looking |
| Toon / cel | Smooth normals, clean | Ramp-based shader + optional outline |

## Normal rules
1. Never use plain "Shade Smooth" on a hard-surface mesh with large flat faces: it produces gradients and dark smears. Use smooth + **sharp edges by angle** (30 degrees default).
2. **Bevels catch light.** A bevel of 0.5 to 2 percent of the object's size with 2 to 3 segments, plus Weighted Normal, gives clean highlights without custom normals.
3. Fix shading with normals, not with extra geometry.
4. Flat shading is a style decision; apply it deliberately (`polygon.use_smooth = False`), not as a leftover.
5. Scale must be applied (or uniform) before Weighted Normal / baking, or shading skews.
6. Mirrored meshes: check the seam in the middle (look at the mirror line from two angles).

## Version differences
- **Before 4.1:** `mesh.use_auto_smooth = True` and `mesh.auto_smooth_angle` are required for sharp edges to take effect; custom normals need auto smooth.
- **4.1 and later:** auto smooth is gone. Sharp edges are an attribute (`edge.smooth = False` in bmesh), custom normals work directly, and "Smooth by Angle" is a modifier / operator.
- `scripts/bevel_and_shade.py` already handles both. Prefer running it over rewriting this logic.

## Snippets (standalone, active mesh object)

### Sharp edges by angle
```python
import bpy, bmesh, math
obj = bpy.context.active_object
me = obj.data
angle = math.radians(30)
for p in me.polygons:
    p.use_smooth = True
bm = bmesh.new()
bm.from_mesh(me)
hard = 0
for e in bm.edges:
    if len(e.link_faces) == 2 and e.calc_face_angle(0.0) >= angle:
        e.smooth = False
        hard += 1
    else:
        e.smooth = True
bm.to_mesh(me)
bm.free()
if bpy.app.version < (4, 1, 0):
    me.use_auto_smooth = True
    me.auto_smooth_angle = angle
me.update()
print("sharp edges:", hard)
```

### Bevel + Weighted Normal (clean highlights on hard-surface)
```python
import bpy, math
obj = bpy.context.active_object
size = max(obj.dimensions) or 1.0
bev = obj.modifiers.new("Bevel", 'BEVEL')
bev.width = size * 0.01
bev.segments = 3
bev.limit_method = 'ANGLE'
bev.angle_limit = math.radians(30)
wn = obj.modifiers.new("WeightedNormal", 'WEIGHTED_NORMAL')
wn.keep_sharp = True
wn.weight = 50
print([m.name for m in obj.modifiers])
```
Weighted Normal must come after Bevel in the stack. On Blender before 4.1, enable auto smooth on the mesh as above.

### Toon material (cel ramp), EEVEE
```python
import bpy
mat = bpy.data.materials.new("MAT_Toon")
if mat.node_tree is None or bpy.app.version < (5, 0, 0):
    mat.use_nodes = True   # required before 5.0, deprecated after
nt = mat.node_tree
nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputMaterial')
emit = nt.nodes.new('ShaderNodeEmission')
ramp = nt.nodes.new('ShaderNodeValToRGB')
diff = nt.nodes.new('ShaderNodeBsdfDiffuse')
s2r = nt.nodes.new('ShaderNodeShaderToRGB')   # EEVEE only, not Cycles
ramp.color_ramp.interpolation = 'CONSTANT'
ramp.color_ramp.elements[0].color = (0.25, 0.28, 0.45, 1)   # shadow (cool)
ramp.color_ramp.elements[1].position = 0.5
ramp.color_ramp.elements[1].color = (0.95, 0.85, 0.65, 1)   # light (warm)
nt.links.new(diff.outputs['BSDF'], s2r.inputs['Shader'])
nt.links.new(s2r.outputs['Color'], ramp.inputs['Fac'])
nt.links.new(ramp.outputs['Color'], emit.inputs['Color'])
nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
print("toon material ready")
```
Shader to RGB works only in EEVEE. For Cycles or engine export, bake the result to a texture instead. Toon shaders do not export to FBX/glTF, so a game pipeline needs a baked or engine-side shader.

### Outline (inverted hull)
```python
import bpy
obj = bpy.context.active_object
mat = bpy.data.materials.new("MAT_Outline")
if mat.node_tree is None or bpy.app.version < (5, 0, 0):
    mat.use_nodes = True   # required before 5.0, deprecated after
mat.use_backface_culling = True            # show only the flipped back faces
mat.diffuse_color = (0.02, 0.02, 0.03, 1)
mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.02, 0.02, 0.03, 1)
obj.data.materials.append(mat)
sol = obj.modifiers.new("Outline", 'SOLIDIFY')
sol.thickness = max(obj.dimensions) * 0.01
sol.offset = 1.0
sol.use_flip_normals = True
sol.material_offset = len(obj.data.materials) - 1
print("outline slot", sol.material_offset)
```
Inverted hull doubles the triangles; do not use it on game assets without budget for that (many engines have a post-process outline instead).

## Baking normals from high to low poly
See `references/uv-baking.md`. Rule: the low poly needs clean UVs and hard edges where UV seams are; flat bevels baked into a normal map replace real bevel geometry.

## Diagnostics
- Dark smears on flat faces: sharp-by-angle missing, or non-applied scale.
- Faceted look on a curved surface: not smooth-shaded, or angle threshold too low.
- Jagged highlight on bevels: too few segments, or Weighted Normal before Bevel.
- Inside-out look: flipped normals; use the face orientation overlay (`look` with a render view will show black faces), then recalculate normals outside.

## Done when
No gradient smears on flat faces, bevels read as clean highlights, smooth surfaces are smooth, shading style is consistent across the whole asset and matches the target engine's capabilities.
