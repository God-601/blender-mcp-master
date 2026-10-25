# Organic modeling (creatures, plants, rocks, terrain, food, humans)

## Workflow
1. **Gesture / silhouette**: build the body from a few primitives (spheres, cylinders, metaballs) or a single subdivided cube. Check front/side/top.
2. **Base mesh** with clean quad flow. Use Mirror (X) for symmetric subjects.
3. **Subdivision Surface** (levels 1 viewport / 2 render) for smooth forms. Add support loops only where silhouette needs it.
4. **Sculpt-lite via script**: use proportional displacement with `bmesh`, noise displacement (Displace modifier + Clouds/Voronoi texture), or Shrinkwrap for fitting. For real sculpting, tell the user it is better done by hand and keep the script role to base forms.
5. **Retopology for games**: Decimate (collapse, ratio) is fine for static background; for hero/deforming meshes rebuild with Remesh (voxel) + manual cleanup, or Shrinkwrap a low-poly cage onto the high-poly.
6. **Detail via textures** (normal/AO/curvature) rather than geometry when targeting games.

## By subject

### Rocks / terrain
- Start from an icosphere (subdiv 2 to 3), Displace with Voronoi/Musgrave, then a second smaller noise pass, flatten the bottom, add a few sharp planar cuts for believable erosion.
- Terrain: Grid + Displace (large Clouds noise) + vertex-color or material blend by slope and height. Use geometry nodes only if you know the exact node setup; otherwise Python noise with `mathutils.noise`.
- Vary every instance: random scale (non-uniform small), rotation, and 3 to 5 unique mesh variants.

### Plants / trees
- Trunk: curve with bevel depth (or tapered cylinder), branches as child curves; leaves as cards (planes) with alpha-clipped texture for games, or instances of a few leaf meshes.
- Game-ready: leaf cards 2 to 4 tris each, alpha clip (not blend), 1 shared atlas.
- Keep randomization seeded (`random.seed(n)`) so results are reproducible.

### Food / props with soft shapes
- Subdivision + slight noise displacement; subsurface scattering for skin/fruit/wax; roughness variation is what sells realism.

### Humans / faces
- Do not attempt production-quality realistic humans from scratch via script. Use `search_assets`/`generate_3d` bases when appropriate, then clean up, or produce a stylized character instead. Be explicit about the limit.

## Rules
- No uniform perfection: add subtle asymmetry and variation (scale +/- 5 percent, rotation jitter) after mirrored base.
- Avoid pinching poles (vertices with 5+ edges) in high-curvature areas.
- Keep edge loops following muscle/form flow around eyes, mouth, joints for anything that will deform.
- Bake or procedural: if procedural materials are used for a game target, bake to textures before export.
