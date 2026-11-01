# Stylized, Fantasy, Low-Poly, Voxel, and Retro Art Direction

Use this guide when intentional simplification, color blocking, facets, exaggeration, or a distinctive visual language matters more than photorealism.

## 1. Lock the art direction first

Define:
- Silhouette language: rounded, angular, chunky, tapered, exaggerated, or deliberately awkward.
- Proportion rules: head/hand size, thickness, bevel scale, limb shape, and how forms simplify.
- Palette and value range, material count, outline policy, lighting style, and texture resolution.
- Camera distance and target platform. Judge details at the real viewing size.
- Whether the style is low-poly geometry, hand-painted texture, voxel/studs, PS1/retro, toon, or a hybrid.

## 2. Core principles

- Silhouette and large color groups carry the design.
- Consistency is more important than local detail: match bevel width, facet density, color contrast, texel density, and roughness across related assets.
- Every edge should support silhouette, a plane change, shading, or a designed facet.
- Use flat shading for deliberate faceting and smooth shading only where the chosen style needs rounded forms. A mixed style can work if the transitions are intentional.
- Exaggerate small features when real dimensions would become unreadable at the target camera distance.

## 3. Low-poly and fantasy workflow

1. Block out major volumes with modest primitive segment counts.
2. Establish a strong silhouette and a small number of clear secondary shapes.
3. Choose which bevels and facets define the style, then apply those rules consistently.
4. Use broad color regions and controlled highlights before adding tiny ornaments.
5. For fantasy objects, make the focal feature readable: blade shape, crystal, rune, antler, magical core, or distinctive silhouette.
6. Remove detail that does not affect silhouette, gameplay readability, or close-up presentation.

## 4. Palette atlas and hand-painted assets

- Use a palette atlas for families of props that can share colors and materials.
- Use vertex colors only when mesh density and target import support the intended gradients.
- Use hand-painted textures for gradients, plane accents, edge highlights, and unique storytelling details.
- Read references/hand-painted-pipeline.md for the full painting sequence and references/uv-baking.md when UVs or bakes are needed.
- Avoid adding procedural noise as a shortcut for painterly detail; it often produces a dirty, uniform surface rather than deliberate brushwork.

See `references/voxel-atlas-recipe.md` for a reproducible voxel-grid example with exposed-face culling and a **64x8** texture atlas. Historical **0.28 m** grid values are suggestions, never mandatory.

## 5. Voxel, studs, and block-based construction

- Define the grid unit and snap all relevant dimensions to it.
- Use instancing for repeated studs, blocks, foliage, and other identical parts.
- Merge visible surfaces only when the target needs a combined mesh; remove interior faces carefully and preserve modular parts that must remain swappable.
- For grid-based mesh generation, emit only exposed faces when possible rather than retaining all interior cube faces.
- Check silhouette, normals, and material boundaries after merging.

## 6. PS1 and retro low-resolution looks

- Limit geometry according to silhouette and camera framing, not by a fixed universal polygon count.
- Consider low-resolution textures, nearest/intentional filtering where the engine allows it, vertex lighting, constrained palettes, and simple materials.
- Affine texture warping and vertex jitter are engine/render-pipeline effects, not guaranteed Blender mesh properties; don't promise them from a model-only workflow.
- Keep texture seams, mipmapping, and target-engine filtering in mind. A retro-looking viewport is not proof the asset will look the same in the target game.
- Favor distinctive large shapes and strong value grouping over dense micro-detail.

## 7. Toon and stylized materials

- Toon ramps, outlines, and shader-to-RGB approaches depend on the render engine. Check compatibility before choosing them.
- Blender-specific node setups may not export to a game engine. For real-time targets, plan the equivalent engine material or bake supported channels when appropriate.
- Read references/materials.md for PBR, procedural, toon, and shader diagnostics.

## 8. Review

- Does the object read in silhouette and at game distance?
- Is the visual language consistent with the rest of the project?
- Are facets, palette regions, texture brushwork, and highlights deliberate?
- Do the final target engine and texture pipeline preserve the intended look?
