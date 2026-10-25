# Materials and textures (PBR)

## Principled BSDF values that look right
| Surface | Base Color | Metallic | Roughness | Notes |
|---|---|---|---|---|
| Plastic | any | 0 | 0.3 to 0.5 | |
| Rubber | dark | 0 | 0.8 to 0.95 | |
| Wood (raw) | warm brown | 0 | 0.6 to 0.8 | add grain variation |
| Painted metal | color | 0 | 0.35 to 0.6 | metal under paint is not "metallic" |
| Bare steel | 0.55 to 0.65 gray | 1 | 0.2 to 0.5 | |
| Gold | (1.0, 0.77, 0.34) | 1 | 0.2 to 0.4 | |
| Copper | (0.95, 0.64, 0.54) | 1 | 0.25 to 0.45 | |
| Concrete | mid gray | 0 | 0.8 to 0.95 | |
| Glass | white | 0 | 0 to 0.05 | Transmission 1, IOR 1.45 to 1.5 |
| Skin | warm tone | 0 | 0.4 to 0.6 | Subsurface weight 0.1 to 0.3 |
| Fabric | any | 0 | 0.7 to 0.95 | sheen 0.3 to 0.6 |
| Leaves | green variation | 0 | 0.5 to 0.7 | subsurface subtle, alpha clip |

Rules:
- **Metallic is almost always 0 or 1**, avoid in-between except transitions (rust, dirt edges).
- **Base color is not lighting**: avoid pure black (use about 0.02 to 0.04) and pure white (use up to about 0.9).
- **Roughness variation sells realism**: add noise/scratches to roughness before touching color.
- Non-color data (roughness, metallic, normal, height, AO) textures must use `Non-Color` color space; color textures use `sRGB`.
- Normal maps: Normal Map node, OpenGL (Y+) for Blender/Unity-ish; DirectX (Y-) for Unreal; flip green when exporting if needed.

## Blender 4.x socket names (API differences)
Principled BSDF names changed in 4.0: `Specular IOR Level` (was `Specular`), `Emission Color` (was `Emission`), `Subsurface Weight` (was `Subsurface`), `Coat Weight` (was `Clearcoat`), `Sheen Weight`, `Transmission Weight`. In scripts, set inputs via a helper that tries both names and ignores missing ones (see `scripts/pbr_material.py`).

## Workflow
1. Reuse before creating: `bpy.data.materials.get(name)`.
2. Name: `MAT_<Surface>_<Variant>`.
3. For realism from nothing: use `search_assets(source="polyhaven", asset_type="textures")` and `import_asset(..., apply_to=[...], resolution="2k")` (1k for background, 4k only for hero close-ups; set `min_size_m` when searching for large surfaces).
4. For stylized: flat Base Color, Roughness 0.7 to 0.9, no normal map.
5. For procedural -> game: bake to image textures (Diffuse color only, normal, roughness, AO) at budget size, then rewire the material to the baked images. Engines do not read Blender node graphs.
6. Assign materials by slot; remove unused slots (`bpy.ops.object.material_slot_remove_unused()`), purge orphan materials at the end.

## UV unwrapping
- Hard-surface: mark seams on hidden or sharp edges, then `uv.unwrap(method='ANGLE_BASED', margin=0.02)` or Smart UV Project (`angle_limit` about 66 degrees, `island_margin` 0.02).
- Pack: `uv.pack_islands(margin=0.01)`. Keep margin >= 4 px at the target texture size (margin = 4 / size).
- Check stretching: a checker texture on `look(shading="material")`. Fix visible stretch before painting/baking.
- Mirror-symmetric assets can overlap UV halves to save space (not if baking unique details).
- Keep texel density consistent across the asset family.
- UV operators need Edit Mode + selected faces; use `bmesh` + `bpy.ops.uv.*` inside a `temp_override` or switch modes carefully and always return to Object Mode.

## Vertex colors / palette atlas (cheap and effective)
- Palette atlas: small swatch texture; assign UV islands to swatches. One material for an entire asset family.
- Vertex colors: `mesh.color_attributes.new("Col", 'BYTE_COLOR', 'CORNER')`; check the target engine imports them.
