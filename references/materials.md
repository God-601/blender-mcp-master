# Shading, Materials, and Texture Diagnostics

Use this guide for PBR, procedural materials, stylized/toon shading, material creation, texture assignment, and troubleshooting visual surface problems.

## 1. Choose the shading model

- **PBR:** best when surfaces must respond plausibly to changing lights in a physically based renderer or game engine.
- **Procedural:** useful for repeatable surface variation and authoring inside Blender. It may need baking before export to engines that do not support Blender's node graph.
- **Toon/stylized:** useful when the project needs controlled bands, outlines, or a simplified light response. The approach depends on the render engine and may not be exportable as-is.
- **Hand-painted:** uses deliberate color, gradients, highlights, and material cues in texture maps. Read references/hand-painted-pipeline.md.
- **Vertex color/palette:** useful for low-poly assets when mesh density and target import support are sufficient.

Do not choose complexity first. Choose the simplest shading model that achieves the intended look and works at the destination.

## 2. PBR starting points

These values are starting ranges, not universal physical measurements:
- Plastic: metallic 0, roughness about 0.3–0.5.
- Rubber: metallic 0, roughness about 0.8–0.95.
- Raw wood: metallic 0, roughness about 0.6–0.8.
- Painted metal: usually metallic 0 for the paint layer; roughness depends on finish.
- Bare steel: metallic 1, roughness about 0.2–0.5.
- Concrete: metallic 0, roughness about 0.8–0.95.
- Fabric: metallic 0, roughness about 0.7–0.95; sheen is renderer-dependent.
- Glass: use transmission and IOR appropriate to the renderer and decide whether the target supports the expected transparency workflow.

Metallic is generally reserved for actual metal regions; values between 0 and 1 need a reason such as mixed coverage, oxidation, or an intentionally blended workflow.

## 3. Material construction and naming

- Reuse a suitable material before creating another copy.
- Use consistent names such as MAT_Wood_Oak or MAT_Metal_Painted.
- Keep node graphs organized around the essential inputs and label generated nodes when scripts create them.
- Reuse shared materials across related assets when it does not compromise the intended visual differences.
- Keep unused slots and datablocks under control, but never run global orphan purges during routine asset creation. Remove only datablocks created by the current task after verifying they have no users.
- Before replacing or bulk-assigning materials, identify the exact target objects and preserve existing user assignments unless they are part of the requested edit.

## 4. Texture maps and color space

- Base color/albedo is color data and normally uses sRGB interpretation.
- Normal, roughness, metallic, masks, AO, and height are numerical data and generally use Non-Color interpretation.
- Use a Normal Map node for normal textures; do not connect a normal image directly to the shader normal socket.
- Verify tangent-space convention and green-channel orientation with the target pipeline instead of flipping channels blindly.
- Keep image filenames and map roles explicit; save or pack images according to the deliverable format.
- UVs and baking are a separate pipeline with its own failure modes; use references/uv-baking.md.

## 5. Procedural realism

- Build variation around the material's real scale and use. Large cloudy noise across a tiny surface often looks artificial.
- Separate base color, roughness, bump/normal, and geometry effects. Roughness variation often communicates material better than adding strong color noise.
- Use object coordinates or UV coordinates deliberately; changes to scale and transforms can affect procedural appearance.
- Add detail through a hierarchy: large material regions, medium variation, then subtle surface breakup.
- Inspect at close range and at the intended viewing distance; remove noise that disappears into aliasing.

## 6. Stylized and toon materials

- Use a limited, deliberate palette and consistent roughness rather than applying one generic glossy finish.
- Toon ramps, outlines, and Shader-to-RGB techniques are render-engine dependent. Confirm availability in the active renderer; do not assume a Blender material graph can be exported to Unity, Unreal, Godot, or Roblox unchanged.
- Hand-painted highlights and shadows may deliberately override physical light response. Keep that choice consistent with the project style.
- If a target engine cannot reproduce the material, translate the look to its shader system or bake supported channels, then state what was tested.

## 7. Blender version compatibility

Principled BSDF socket names and shading features can change between Blender versions. Detect available sockets or capabilities before assigning values rather than assuming a single name. Older versions may expose different color-attribute APIs; check capability/version before using them in scripts.

## 8. Validation

- Inspect material names, slot assignments, node links, image references, color-space settings, and missing textures.
- Use neutral lighting to diagnose color, normals, roughness, and shading separately from final presentation lighting.
- Verify that each required image exists on disk or is packed as expected.
- If exporting, confirm which nodes, textures, and shader features are supported by the target format and destination renderer.
- Report unsupported features or checks that were not performed.
