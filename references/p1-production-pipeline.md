# P1 Production Pipeline: Materials, UVs, LODs and Export

This module connects the existing material, LOD and export utilities into one repeatable game-asset handoff. It is guidance, not a claim that an asset has been tested in a target engine.

## 1. Materials: build for the destination

1. Confirm whether the asset is untextured, vertex-colored, atlas-textured or uses separate texture sets.
2. Prefer a small number of named, reusable materials. For props, start with one material and use two only when there is a clear visual or technical reason.
3. Use Principled BSDF values as the Blender authoring source, but do not assume every engine reproduces every node or parameter.
4. For image textures, use sRGB for base color/emission color and Non-Color for roughness, metallic, normal and AO data.
5. Normal maps must use a Normal Map node. Confirm the target's tangent-space convention; DirectX/OpenGL green-channel direction can differ.
6. Alpha is expensive and engine-specific. Choose opaque unless transparency is necessary; distinguish cutout foliage from blended glass/particles.
7. Avoid relying on procedural nodes for real-time export. Bake the intended result to images, reconnect a simple Principled material, then inspect the exported asset.

Use `scripts/pbr_material.py` for a basic material setup. It can update a material with the configured name; read its config before running. When `ASSIGN_TO` is set, assignment replaces all material slots on those objects. Confirm the object list and shared mesh-data implications first.

## 2. UV production checklist

- Create a deliberate UV map for every textured mesh; name it clearly (for example `UV_Main`).
- Keep texel density consistent across assets that appear together.
- Place seams on hidden, sharp or natural boundaries where possible.
- Avoid unintended overlap for unique baked textures. Mirrored overlap is valid only when mirrored details are acceptable.
- Leave enough padding for the final texture resolution and mipmapping. A 4 px gutter is a starting point, not a universal guarantee; use larger margins for lower-resolution/mip-heavy assets.
- Check stretching with a checker texture and inspect seams at the intended viewing distance.
- 0-1 bounds are expected for a single-tile workflow. Tiling and UDIM workflows are intentional exceptions.
- Verify that UVs survive Decimate/LOD generation and triangulation. A valid UV layer alone does not prove the unwrap is good.

Run `scripts/validate_uvs.py` for bounds and zero-area diagnostics.
For **optional UV-area overlap and texel-density measurements**, run
`scripts/uv_diagnostics.py` with explicit `TARGETS`, intended texture
resolution and policy flags. Positive-area triangle overlap is distinguished
from shared-border contact. `ALLOW_STACKING=True` reports intentional
mirroring/stacking as REVIEW rather than falsely passing a unique bake.

The new inspector analyzes base mesh UVs, not evaluated Geometry Nodes output.
Its pairwise overlap scan is capped; exceeding the cap reports NOT VERIFIED.
Its density numbers are pixels per scene length unit, **not automatically
pixels/meter**. It does **not** certify actual UV island padding, texture
distortion, baking, post-modifier UVs or engine import. Always use Blender's UV
Editor/checker texture and actual export/import checks when relevant.

## 3. LOD production

Use LODs only when the asset's projected screen size and repetition justify them. Establish LOD0 as the quality baseline, then remove small details before changing primary silhouette.

Suggested starting ratios (not fixed rules):
- LOD0: 100%
- LOD1: about 50%
- LOD2: about 25%
- LOD3: about 10%

Use `scripts/make_lods.py` on a named static mesh. It creates independent copies and does not delete existing objects. It applies the source's evaluated modifier result to each generated LOD; modifiers, armature deformation and shape keys are not preserved as a live rigged workflow. Treat warnings about rigging/shape keys as a reason to stop and use a dedicated character pipeline.

After generation:
1. Compare triangle counts and inspect front, side, rear and three-quarter silhouettes.
2. Check thin parts, shading, UV seams, material borders and normals.
3. Confirm the lower LODs remain readable at the actual camera distance.
4. Set transition distances and cross-fade behavior in the destination engine; Blender does not determine these.
5. Remove or reposition preview copies only after confirming which objects belong to the LOD run.

## 4. Export contract

Before export, define:
- exact object names (children are not implicitly included by the bundled exporter);
- format and target engine;
- unit and scale convention;
- whether modifiers should be baked and whether triangulation is required;
- output path and overwrite permission;
- texture embedding/sidecar expectations.

Use `scripts/export_asset.py` only after reading its config. It creates temporary evaluated copies so the original mesh data is not destructively modified. It refuses to overwrite by default and reports success only when the output exists. The current utility is for static mesh export; do not use it as a rigged/animated character exporter.

### Format guidance

- **FBX:** common for Unity, Unreal and Roblox pipelines; axis and scale settings are destination-specific. Verify import scale and orientation in the engine.
- **GLB:** suitable for glTF consumers and Godot/web pipelines; verify material extensions and texture packing in the target.
- **OBJ:** geometry-focused interchange; material/texture sidecars need to remain together. It is not a replacement for a rigged animation format.

### Engine-specific handoff

- **Roblox:** import into Studio and verify studs scale, mesh appearance, SurfaceAppearance/texture behavior, collision fidelity and platform limits. Do not assume Blender material nodes map one-to-one to Roblox.
- **Unity:** verify FBX scale, forward/up orientation, material remapping, normals/tangents and texture import settings.
- **Unreal:** verify FBX orientation, smoothing/normals, material slots, collision setup and Nanite/LOD choices in the project context.
- **Godot:** GLB is a useful default; verify imported materials, transforms, collision and mesh resource settings.

## 5. Acceptance report

Report each item as PASS, ISSUE, N/A or NOT VERIFIED:
- material count and texture dimensions;
- UV layer names, bounds, overlap/stretch checks and exceptions;
- LOD triangle counts and silhouette review;
- export format, path, object list and file existence;
- target-engine import and in-engine visual/scale checks.

A file existing on disk is not proof that the target engine imports it correctly. Never claim engine compatibility without an actual import test.
