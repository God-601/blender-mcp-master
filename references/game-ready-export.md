# Game-ready assets and export (Roblox, Unity, Unreal, Godot, glTF)

## Pre-export checklist (all engines)
1. Transforms applied (scale 1, rotation 0). Origin at a sensible point. Correct real-world scale.
2. Modifiers applied or intentionally exported (Mirror, Bevel, Boolean, Array, Weighted Normal: apply). Hide cutters first, delete them.
3. Geometry clean: no loose verts, doubles, interior faces, zero-area faces, non-manifold edges where it matters; normals consistent (recalculate outside).
4. Triangulate (modifier at export, or `Triangulate` applied with `quad_method='BEAUTY'`, `ngon_method='BEAUTY'`) - do this consistently, ideally BEFORE baking normals.
5. UVs: one non-overlapping layout (unless intentionally mirrored), margins set, inside 0 to 1 (unless tiling textures).
6. Materials: minimal count, named, Principled BSDF with image textures only (no procedural nodes, no unsupported nodes).
7. Names: no spaces or special characters; unique; no `.001` suffixes. Consider `_LOD0`, `_LOD1`, `UCX_` (Unreal collision) conventions.
8. Collision: provide simple collision (box/convex hulls) when the engine needs it; never rely on the render mesh for complex physics.
9. Budget check against `budgets.md`.
10. Run `validate_asset.py`.

## LODs
- LOD0 100 percent, LOD1 about 50 percent, LOD2 about 25 percent, LOD3 about 10 percent (`make_lods.py`). Keep UVs and silhouette. Verify with `look(shading="wireframe")`. Skip LODs for small props or cheap meshes (under about 500 tris).

## Axis / unit settings (Blender FBX exporter)
- Unity: `apply_scale_options='FBX_SCALE_ALL'`, `axis_forward='-Z'`, `axis_up='Y'`, `apply_unit_scale=True`.
- Unreal: `apply_scale_options='FBX_SCALE_NONE'`, `axis_forward='-Y'`, `axis_up='Z'`, `global_scale=1.0`, add smoothing groups: `mesh_smooth_type='FACE'`.
- Godot: prefer glTF 2.0 (`.glb`), Y-up conversion is on by default.
- Roblox: FBX or OBJ into Studio via the Asset/Avatar Importer; Studio expects meters-to-studs conversions, so confirm scale in Studio after import; MeshPart cap 21,844 tris, keep textures <= 1024 for props (up to 2048 for hero), single material/texture per mesh is the cheapest. Don't rely on vertex-color support; use textures or the surface appearance. For "studs" assets keep grid-aligned dimensions so pieces snap in Studio.

## glTF / GLB
- Best for web, Godot, three.js, Roblox-adjacent workflows with PBR. Export with `export_format='GLB'`, `export_apply=True` (apply modifiers), `export_texcoords=True`, `export_normals=True`, `export_materials='EXPORT'`, `export_yup=True`.
- Pack textures into the GLB or export beside it.

## Baking (high to low)
- Low poly with clean UVs + high poly (or procedural material) -> bake Normal, AO, Base Color, Roughness at the budgeted size. Cage extrusion about 0.01 to 0.05. Cycles required for bake. Use margin 8 to 16 px, `use_selected_to_active=True`, then reconnect the baked images in a simple Principled setup before export.

## Using `scripts/export_asset.py`
Set `OBJECTS`, `PATH`, `FORMAT`, `ENGINE` at the top; the script exports only listed objects, triangulates copies if requested, and prints the file size. Always report the exported path and tri count to the user.

## Don't
- Don't export with hidden helpers/cutters selected.
- Don't change the user's .blend objects destructively to export: use temporary duplicates (the script does).
- Don't claim the model works in an engine you did not test; say what you verified (tris, UVs, materials, scale).
