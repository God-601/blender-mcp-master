# Stylized, low-poly, voxel and "studs" looks

## Principles
- **Silhouette and color carry the design.** Few shapes, strong readability at small size.
- **Consistency beats detail**: same bevel size, same palette, same texel density, same level of simplification across all assets.
- **Flat shading or hard-edged smoothing** on faceted styles; **smooth shading** on soft cartoon styles. Pick one per project.
- **Palette discipline**: 5 to 8 main colors per asset; use a shared palette texture or vertex colors, so many assets share one material.

## Low-poly workflow
1. Blockout with primitives using low segment counts (cylinders 6 to 12 sides, spheres 8x6 to 12x8).
2. Use non-destructive Mirror/Array, then apply before export.
3. Keep tris intentional: every edge must define silhouette or a color break.
4. Color via **palette atlas**: a tiny texture (e.g. 64x8 or 256x256) of swatches; map UV islands onto swatches. Or per-face material slots if the engine handles it, but atlas is cheaper.
5. Optional: single-color vertex colors (`mesh.color_attributes`) when the engine supports them.

## Voxel / "studs" style (blocky, brick-like, Roblox-like)
- Define a **grid unit** (e.g. 1 stud = 0.28 m or 0.25 m, or just 0.1 m) and make all dimensions integer multiples of it.
- Build from cubes snapped to the grid; for organic subjects (plants, animals) voxelize: sample a shape (sphere, cone, noise) on the grid and place only the surface cubes.
- Studs: small cylinders (8 to 12 sides, height about 0.2 of the stud width) on top faces; for performance use ONE stud mesh with instances, or a tileable normal/stud texture on flat surfaces instead of geometry.
- Merge all voxels into one mesh at the end (`join`), remove interior faces (cubes touching cubes), `remove_doubles`, so a 1000-cube plant is a few hundred visible faces, not 12,000.
- Use `bmesh` to build: iterate grid cells, create a face only where the neighbor cell is empty (greedy surface extraction). This yields the minimal visible surface instantly. See `scripts/` snippet idea in `performance.md` ("bulk geometry").
- Colors: one flat color per voxel group via palette atlas or vertex colors; keep Roughness around 0.6 to 0.9, Metallic 0 unless specified.
- Pot/planter separate from the plant if the game needs to swap them.

## Cartoon / toon shading (render)
- Use Principled with low specular, or Shader to RGB -> ColorRamp (constant interpolation) for cel shading in EEVEE. Add outline via Solidify (flipped normals, black emission material, thickness small) or Freestyle. Game engines will need their own toon shader; say so.

## Hand-painted look
- Gradient/AO baked into a 256 to 1024 px texture with soft color; avoid strong specular; keep normal maps off or very subtle.

## Checks
- Wireframe view must look intentional (no tiny faces).
- Compare at game camera distance: shrink the `look` max_size to 256 to test readability.
