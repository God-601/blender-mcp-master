# Hand-Painted 3D Asset Pipeline

Use this guide for stylized props, fantasy equipment, characters, vegetation, and game assets whose color design is painted rather than derived entirely from physically based procedural materials. Pair it with the UV and baking guide when the asset uses image textures or baked maps.

## 1. Choose the painting model

Choose deliberately before modeling:
- **Texture-paint atlas:** best for visible brushwork, gradients, graphic highlights, color variation, and controlled edge accents.
- **Palette atlas:** best for low-poly, retro, and modular assets that share a small set of colors.
- **Vertex colors:** useful for broad gradients and meshes with enough vertex density; inspect target-engine import support first.
- **Hybrid:** painted base color plus restrained normal/AO or roughness maps when the target and style benefit from them.

Do not add PBR maps simply because they are available. Some hand-painted styles deliberately use a simple diffuse/albedo texture and dynamic lighting.

## 2. Plan before creating the mesh

Record:
- Target engine, camera distance, texture resolution, and approximate texel density.
- Whether lighting and shadows are painted into the texture or supplied dynamically by the engine.
- UV layout strategy, number of materials, texture atlas ownership, and whether mirroring/overlap is acceptable.
- The style rules: outline policy, palette size, contrast, edge-highlight strength, brush shape, and how much surface detail is visible at gameplay distance.

For a small prop, test a low-resolution draft first. A higher resolution does not fix unclear shape design or weak value separation.

## 3. Shape and UV preparation

1. Finish the primary silhouette and major forms before painting small marks.
2. Establish consistent bevels and face planes where they create readable painted edges.
3. Create UVs with enough room for important front-facing areas and seams in visually quiet locations.
4. Keep consistent texel density across an asset family, but give hero surfaces more area when their screen space justifies it.
5. Leave padding between islands for filtering and mipmaps. The margin depends on final resolution and target platform.
6. Use overlapping mirrored UVs only when both sides can share identical paint. Unique labels, asymmetry, damage, or baked directional lighting require separate UV space.

See references/uv-baking.md for unwrap, packing, and bake preparation.

## 4. A reliable painting order

1. **Base colors:** establish large color regions and material separation before detail.
2. **Large form gradients:** use broad light/dark transitions to explain volume and direct attention.
3. **Contact and recess accents:** paint sparingly under handles, overlapping parts, seams, folds, and inset shapes.
4. **Edge highlights:** follow the main form and light direction. Keep them selective; outlining every edge flattens the object.
5. **Material cues:** vary marks by material—broad strokes for worn wood, narrow specular accents for metal, soft transitions for skin or cloth.
6. **Story details:** scratches, chips, dirt, magical markings, labels, and ornament belong after the base form reads.
7. **Distance pass:** inspect the asset at its expected in-game size and remove details that turn into noise.

The light direction must be consistent across the whole asset if lighting is painted into the texture. If the engine provides dynamic lighting, keep painted light accents intentional but avoid making them contradict the scene so strongly that the object appears self-lit.

## 5. Baking: use it as support, not as a substitute for painting

Possible helper maps:
- AO for subtle contact and recess guidance.
- Normal maps for secondary high-poly detail when the target supports them.
- Curvature or cavity masks for selecting edge accents, only when a reliable bake workflow is available.
- Diffuse/base-color transfer when an existing source material or high-poly paint already contains the desired color.

Inspect bakes before blending them into the painted texture. Strong black AO, hard halos, or fully baked directional light commonly make a stylized asset muddy or visually inconsistent. Use references/uv-baking.md for high-to-low projection and troubleshooting.

## 6. Color and texture hygiene

- Separate color layers from temporary guides, baked helpers, and annotations.
- Keep color textures in the appropriate color space for the painting/export pipeline; non-color data such as AO, roughness, and normal maps must not be treated as ordinary display color.
- Avoid painting razor-thin details that disappear at the target mip level.
- Keep a clean version of the base color map without accidental viewport lighting or selection overlays.
- Save image files to explicit paths or pack them only when the delivery format supports packed images. Do not assume a texture saved in a painting session was written to disk.
- Use naming that includes asset, map type, and resolution when useful.

## 7. Review checklist

- Does the silhouette read before texture details are visible?
- Are large color groups and value contrast readable at the intended distance?
- Are edge highlights consistent with shape and light direction?
- Are seams, mirrored regions, and texture padding acceptable?
- Do textures survive mipmapping without flickering or muddy color?
- Does the material remain consistent with the project's lighting and palette?
- Are all required image files present, and was export/import actually checked?

## 8. Common failure modes

- **Looks noisy:** remove micro-scratches and reduce the number of competing accents; restore large color groups.
- **Looks flat:** strengthen value separation on major planes before adding more outlines.
- **Looks overly metallic:** reduce bright uniform highlights and paint material-specific reflections rather than using a generic white rim everywhere.
- **Looks dirty:** reduce baked AO, check its color space, and paint recess accents selectively.
- **Seams show in-engine:** revisit UV padding, bake margin, and mipmap behavior at the actual target resolution.
- **Paint disappears in game:** check the imported texture, material assignment, color space, compression, and mip levels.
