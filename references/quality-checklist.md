# Universal 3D Asset Quality Checklist

Use this checklist for every asset, then load the discipline-specific reference guide and add checks for the task. The checklist is a decision aid, not a demand that every asset satisfy every technical rule.

For each applicable item, report one status:

- **PASS** — checked and acceptable for the stated target.
- **ISSUE** — checked and a relevant defect remains.
- **N/A** — not applicable to this asset or workflow.
- **NOT VERIFIED** — the check could not be performed or evidence is insufficient.

Never mark an item PASS based only on an assumption. When a check produces a warning, interpret it in context and record the reason if it is acceptable.

## 1. Requirements and planning

- [ ] Purpose and destination are known or reasonable assumptions are stated.
- [ ] Style, silhouette, scale, orientation, and expected viewing distance are understood.
- [ ] Deliverables and export formats are identified.
- [ ] Relevant budgets are chosen where they matter: triangles, texture resolution, materials, scene complexity, render time, or file size.
- [ ] A task-appropriate workflow and relevant reference modules were selected before substantial modeling.

## 2. Visual quality

- [ ] The primary silhouette and proportions match the brief or reference.
- [ ] The asset reads clearly from the views and distance appropriate to its use.
- [ ] Primary, secondary, and tertiary details have a deliberate hierarchy.
- [ ] No unintended floating parts, intersections, coplanar surfaces, or distracting gaps remain.
- [ ] Style is consistent across shapes, edge treatment, materials, textures, and presentation.
- [ ] Lighting and camera reveal the form rather than conceal defects.

## 3. Geometry and topology

- [ ] Geometry density is appropriate for the target and intended deformation/subdivision.
- [ ] Normals and shading have been inspected for visible artifacts.
- [ ] Loose or duplicate geometry has been investigated.
- [ ] Degenerate faces and zero-area geometry have been investigated.
- [ ] Non-manifold edges and open boundaries have been evaluated in context; they are not automatically defects on intentionally open surfaces, foliage, cloth, or similar assets.
- [ ] N-gons are appropriate for the surface and workflow; curved, subdivided, or deforming regions receive extra scrutiny.
- [ ] Bevels, supporting loops, and sharp edges suit the scale and visual style.
- [ ] Rigging, shape keys, modifiers, and shared mesh data are preserved when relevant.

## 4. UVs, textures, and materials

- [ ] UVs exist when required by the target workflow.
- [ ] UV overlap, padding, texel density, and UV bounds are suitable for the chosen texture workflow; tiling and UDIMs may intentionally exceed 0–1.
- [ ] Required texture maps are present, correctly assigned, and saved or packed as needed.
- [ ] Baking artifacts, skewing, seams, gradients, and projection issues have been checked when baking is part of the pipeline.
- [ ] Material names and assignments are intentional.
- [ ] PBR values, procedural nodes, toon shading, or hand-painted colors suit the intended style and renderer.
- [ ] Unsupported nodes or procedural dependencies are identified before export.

## 5. Scene organization and transforms

- [ ] New work is grouped in a dedicated collection or otherwise clearly isolated.
- [ ] Objects, collections, materials, images, and exported files have meaningful names.
- [ ] Origin/pivot, scale, rotation, axes, and ground placement suit the target.
- [ ] Transforms are applied only when appropriate for the workflow and without damaging user-owned content.
- [ ] No unrelated user objects were changed or deleted.
- [ ] Temporary helpers and cutters are excluded from delivery unless intentionally required.

## 6. Performance and destination

- [ ] Triangle count and mesh complexity are appropriate for the target.
- [ ] Material slots, texture sizes, transparency, modifiers, and draw-call implications are considered where relevant.
- [ ] LODs, collision meshes, simplified variants, or instancing are supplied when required.
- [ ] Units, orientation, naming, UVs, materials, and supported features match the target format or engine.
- [ ] Export includes only intended objects and required dependencies.
- [ ] The exported file is reopened or otherwise checked when possible. If the target application is unavailable, state that in the report.

## 7. Delivery and evidence

- [ ] The requested native project and/or exports exist at the reported paths.
- [ ] Validation scripts and relevant checks were run when available.
- [ ] Visual inspection was performed after meaningful changes when the tools support it.
- [ ] Failed, skipped, and unverified checks are disclosed.
- [ ] Remaining defects and limitations are stated plainly.
- [ ] Imported assets have appropriate licensing/attribution recorded where required.

## Adapt by asset type

- **Game-ready prop:** prioritize silhouette, triangle/material budgets, pivots, UVs, texture dependencies, LOD/collision needs, and export verification.
- **Character or deformable asset:** add anatomy, deformation topology, joint placement, weights, shape keys, and animation checks.
- **Hand-painted asset:** add palette/readability, baked lighting policy, texel density, seams, texture resolution, and map/export checks.
- **Hard-surface asset:** add bevel consistency, planar shading, boolean cleanup, edge highlights, and mechanical proportions.
- **Organic/sculpted asset:** add form flow, anatomy/structure where applicable, silhouette from multiple angles, sculpt-to-retopo workflow, and normal baking.
- **Environment/architecture:** add scale consistency, modularity, scene organization, light readability, collision/walkability, and performance.
- **CAD/3D printing:** add dimensional tolerances, manifold/watertight checks where required, wall thickness, units, and file-format verification.
- **Stylized/low-poly/retro:** judge against the chosen style rather than photorealistic standards; verify deliberate facet density, palette, silhouette, and target texture limits.
- **Materials/render-only asset:** add shader correctness, render-engine compatibility, lighting, color management, render settings, and output resolution.

## Final report template

```text
Asset:
Purpose / target:
Visual review: PASS / FAIL / NOT VERIFIED
Technical validation: PASS / FAIL / NOT VERIFIED
Export validation: PASS / FAIL / N/A / NOT VERIFIED
Known defects:
Unverified checks:
Files / paths:
```
