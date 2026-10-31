# UV Mapping and Texture Baking

Use this guide when creating image-textured assets, painting maps, transferring high-poly detail, baking procedural materials, or preparing assets for real-time engines. Blender's current manual and older 3.x manuals both document image-target baking; available targets and UI/API details vary by Blender version. See the official manual: https://docs.blender.org/manual/en/latest/render/cycles/baking.html

## 1. Plan the map set

Before unwrapping, establish:
- Asset purpose, engine, final texture dimensions, and whether the map is unique, shared, tiled, mirrored, or UDIM-based.
- Required maps: base color, tangent-space normal, roughness, metallic, AO, emissive, opacity, or displacement only if the target needs them.
- Texel density and priority areas. Reserve more UV space for surfaces that occupy more screen space or carry unique detail.
- Whether the source is a single mesh, multiple material regions, a high/low pair, or a procedural material that must be baked.

Do not create every possible map by default. Generate only what the shader, art direction, and destination actually use.

## 2. UV unwrap and packing

1. Apply or account for transforms where the workflow requires them; preserve the original scene objects when a destructive change is unnecessary.
2. Mark seams at hidden edges, sharp mechanical breaks, natural boundaries, or areas that can tolerate a paint seam.
3. Unwrap using a method appropriate to the shape. Smart UV projection is a useful starting point for blocky props, not a universal final solution.
4. Inspect stretch with a checker pattern. Fix obvious distortion on focal and curved surfaces.
5. Pack islands with a margin suitable for the final texture size, filtering, mipmaps, and the target's compression. A few pixels of padding may be insufficient for large atlases or heavy downscaling.
6. Check island overlap, UV bounds, texel density, and island orientation. Overlap may be intentional for mirrored/tiled workflows; document those exceptions.
7. Reinspect the UV layout after topology changes, triangulation changes, or a modifier is applied.

UV coordinates outside 0–1 may be correct for tiling or UDIM workflows. Do not force all UVs into one square unless that is the intended texture layout.

## 3. Prepare image targets for baking

For image-based baking, create the target image and ensure the correct Image Texture node is active/selected for each relevant material. The node used as the bake target must point to the intended image. Save the baked image explicitly after baking; a generated image datablock is not proof that a file was written.

Baking normally requires a UV map. Blender's Cycles baking workflow uses render settings, so choose sampling and denoising according to the desired quality and cost. Check the current manual for the installed Blender version before automating version-sensitive settings.

## 4. High-poly to low-poly bake

1. Keep the high-poly source and low-poly target clearly named and organized in separate collections or groups.
2. Ensure their scale, alignment, and intended correspondence are correct. Do not assume unrelated or badly intersecting meshes will project cleanly.
3. Finish the low-poly silhouette, normals, triangulation policy, and UVs before baking.
4. Create the target images and material slots needed by the low-poly object.
5. Use Selected to Active with the low-poly object active and high-poly source selected, or use a cage when simple ray extrusion cannot capture the surface cleanly.
6. Start with a small test bake. Tune ray distance/extrusion and cage shape to avoid projection onto the wrong surface.
7. Bake one map type at a time while troubleshooting. Normal, AO, and color maps have different interpretation and color-space requirements.
8. Inspect seams, hard edges, concave corners, thin details, and mirrored regions. Fix the projection problem rather than hiding every artifact in the texture.
9. Save all outputs, reconnect image textures to the final material, and verify the result in the intended renderer/engine.

A cage used for a Selected-to-Active bake must correspond to the target mesh's topology and face order. If a cage is edited independently, verify this correspondence rather than assuming any inflated mesh is suitable.

## 5. Normal maps

- Tangent-space normal maps are the usual choice for animated or game assets; the baking and material interpretation must use matching tangent-space conventions.
- Use a Normal Map node rather than connecting a normal image directly to the shader normal input.
- Set normal images as Non-Color data.
- Confirm the target engine's tangent basis and green-channel convention. Do not flip the green channel blindly; perform an in-engine test or use the exporter's documented conversion.
- Sharp smoothing splits, hard edges, and UV seams should be planned together. Inconsistent vertex normals or UV splits can cause gradients and dark seams.

## 6. Data-map color space

- Base color/albedo is color data and normally uses the appropriate display color space such as sRGB.
- Normal, roughness, metallic, height, masks, and AO are numerical data and should use Non-Color interpretation unless a particular pipeline explicitly defines otherwise.
- Do not combine AO into base color automatically. The art direction may require dynamic lighting or a hand-painted map without baked occlusion.

## 7. Diagnosing bake artifacts

| Symptom | Likely causes | Useful checks |
|---|---|---|
| Black or missing bake | No active target image node, wrong active image, unsupported bake target, wrong engine | Confirm the selected Image Texture target, UVs, engine, and bake type |
| Skewed or stretched detail | Poor UVs, mismatched low/high topology, target normals, projection distance | Inspect wireframe and checker; rebake a simple region |
| Dark edge halos | Excessive extrusion, intersecting source meshes, cage mismatch, hard-normal splits | Reduce ray distance, isolate sources, inspect cage and smoothing |
| Seams or color bleeding | Insufficient island margin, UV overlap, low padding after mipmaps/compression | Increase padding, inspect mirrored islands, test at target resolution |
| Inverted-looking normals | Incorrect map interpretation, tangent convention mismatch, color-space error | Recheck Normal Map node, Non-Color setting, and target-engine convention |
| Detail disappears in game | Excessive downscaling, compression, weak normal intensity, wrong material import | Test at actual texture size and target viewing distance |

## 8. Before delivery

- Open the saved images and check the actual files, not only the Blender preview.
- Confirm material assignments, UV maps, map naming, dimensions, color spaces, and packing.
- Test the exported asset in the target application when possible. If it was not tested in-engine, report that limitation explicitly.
- Record intentional overlap, tiling, UDIMs, or missing maps that are not required by the destination.
