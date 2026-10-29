# Environments (rooms, buildings, streets, levels)

For architectural/interior layouts, circulation, and spatial validation, also read references/architecture-interiors.md. For precise mating parts, tolerances, and dimension-driven mesh workflows, read references/cad-technical.md.

## Workflow
1. **Layout in 2D first**: define footprint, grid and key dimensions (print them). Use real metric sizes (corridors >= 1.2 m, doors 0.9 x 2.05, ceilings 2.4 to 2.7).
2. **Modular kit**: build a few modules (wall 4 m, corner, door, window, floor tile 2x2 or 4x4) with consistent pivots on the grid, then assemble with linked duplicates. This is the single biggest win for performance and consistency.
3. **Blockout the whole space** with simple boxes; `look(mode="angles")` plus a `camera` view at eye height (1.6 m). Fix flow, scale, sightlines BEFORE detail.
4. **Dress and detail**: props via instances; vary rotation/scale slightly; clutter in clusters, not uniform spread.
5. **Lighting** (see lighting-render.md); **materials** shared across modules.
6. **Optimize**: merge static meshes that share a material, delete hidden faces, use LODs for repeated large props.

## Rules
- Snap to a grid (0.25 / 0.5 / 1 m) for architecture.
- Walls have thickness (0.15 to 0.3 m) and the outside/inside are different surfaces when seen from both sides; do not use single planes except for foliage cards.
- Floor tiles and walls: UV in world-scale (box projection or per-face with consistent texel density) so textures do not stretch.
- Avoid z-fighting: no coplanar overlapping faces; offset decals by 1 to 2 mm or use proper decal geometry.
- Provide a ground plane / floor at Z=0; place objects with `ground` checks (`get_scene_info(fields=["ground"])` flags floating objects).
- Interiors: close gaps at wall/floor/ceiling junctions (no light leaks).

## Scattering (props, vegetation, debris)
- Use Python with seeded random, minimum spacing, and slope/height rules; use instances (`obj.copy()` with shared data or collection instances), never unique copies.
- Cap counts: print the total instance count and estimated tris (instances x tris).

## Large scenes
- Organize collections: `ENV_Architecture`, `ENV_Props`, `ENV_Foliage`, `ENV_Lights`, `ENV_Cameras`.
- Hide or disable viewport display for distant/heavy collections while working; keep render visibility.
