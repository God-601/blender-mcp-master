# Voxel grid + palette atlas — executable example

This guide restores the *illustrative* grid and atlas choices from
[`references/stylized-lowpoly.md` before PR #5](https://github.com/God-601/blender-mcp-master/blob/2bc6ab6841d28ea71aced74487481c5c5cce6ba5/references/stylized-lowpoly.md).
The older guide gave **0.28 m**, **0.25 m** and **0.10 m** as possible grid units,
and **64×8** or **256×256** as atlas examples. These are **not universal voxel,
Roblox or Blender requirements**. Project scale and texture filtering come first.

## Measurable minimal asset

Run `scripts/voxel_atlas_example.py` via Blender MCP in a safe scene. Defaults:
- `GRID_UNIT = 0.28` meters, and cells in a stepped 3×2×2 occupancy envelope.
- One mesh with shared corner vertices, containing **only exposed quads**;
  internal faces between adjacent occupied cells are never generated.
- One generated color image, **64×8 pixels**: eight 8×8 color tiles in one
  horizontal row. Each face gets UV coordinates inset half a pixel from its
  tile edges; nearest filtering is set inside the Blender material.
- Six directions map to six of the palette tiles; the last two are available
  for accents. The same tile may intentionally be reused on multiple faces.

The result is a basic **static** demonstration, not a voxel sculpt/greedy
mesher or a finished texture atlas workflow. Exposed-face culling is not the
same as merging coplanar quads into large greedy rectangles.

## Art direction and engine decisions

1. Ask which game/renderer, scale convention, palette and camera distance the
   user wants. Do not assume 0.28 m is correct just because "Roblox" is named.
2. Align cell centers, origins, pivots and materials to the selected grid.
3. Keep swappable pieces separate when gameplay needs them. Combine surfaces
   when they are static and sharing the atlas is beneficial.
4. Check face orientation, boundaries, UV locations and texture sampling.
   Small 64×8 atlases are susceptible to **mipmap color bleed** after filtering
   or compression, especially when tiles share borders. Half-pixel inset and
   nearest filtering in Blender alone do not guarantee artifact-free exports.
   For production, add texture padding/dilated gutters or choose a larger atlas.
5. The generated image is in the Blender scene. Confirm it is packed/saved in
   the actual `.blend` and preserved by the target exporter; this script does
   not claim that an external PNG was written.
6. Test transparency, material settings, LOD, draw calls and visual readability
   in the intended engine. No universal platform pixel/triangle limit is
   inferred from this example.

## Acceptance

Run `tests/test_measured_recipes_runtime.py` against a compatible `bpy`.
Verify grid bounds are exact multiples of `GRID_UNIT`, every expected exposed
face exists, internal voxel faces are absent, UV coordinates remain inside
the intended atlas tile, and existing user data is not overwritten.

**IMPORTANT:** A numerical/Python PASS cannot certify actual render style,
color bleed under mipmapping, a game importer or a live Blender MCP session.
