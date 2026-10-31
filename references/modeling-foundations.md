# Professional Modeling Foundations

Shared standards for high-quality modeling. Load this guide for substantial assets, then load the relevant hard-surface, organic, character, environment, or stylized module.

## 1. Plan around final use

Establish purpose, target engine/application, style, dimensions, viewing distance, animation/deformation needs, budget, materials, UV requirements, pivot, and export format. Do not ask for details already provided. For simple tasks, infer sensible defaults and state them briefly.

- **Static real-time prop:** triangles are acceptable; prioritize silhouette, shading, low material count, and simple collision.
- **Deforming character:** deliberate edge flow and loops around joints; avoid topology-changing modifiers after skinning.
- **Subdivision/high-quality render:** clean quad flow and support loops where curvature requires them.
- **Architecture/modular environment:** consistent scale, reusable modules, clean pivots, controlled seams.
- **Low-poly/stylized:** intentional planes and silhouette; do not add topology merely to make quads.

## 2. Build in form hierarchy

1. Primary forms establish silhouette and proportion.
2. Secondary forms communicate construction and function.
3. Tertiary details support close inspection only.
4. Materials and textures reinforce form; they should not conceal broken geometry.

Inspect front, side, top, and three-quarter views after blockout. Use wireframe for density and solid/material shading for surface quality. Do not add fine detail until the primary silhouette reads correctly.

## 3. Topology decisions

- Use quads where subdivision or deformation needs predictable edge flow.
- Use triangles on static game meshes when they preserve the intended surface.
- Use n-gons only on suitable planar/static regions; triangulate and inspect before export if required.
- Keep poles away from high-curvature/deformation zones where they cause pinching.
- Avoid long thin triangles, zero-area faces, duplicate coplanar surfaces, and accidental internal shells.
- Do not chase all-quad topology as a universal goal; topology must serve downstream operations.
- Keep hard edges, smoothing, custom normals, bevels and material boundaries intentional.

## 4. Choose operations deliberately

| Operation | Good use | Verify |
|---|---|---|
| Mirror | Symmetric base forms | Seam weld, clipping, centerline |
| Array / linked duplicates | Repeated parts | Instance count, overlap, transforms |
| Boolean | Mechanical cuts/unions | Solver result, n-gons, normals, thin slivers |
| Bevel | Catch-light edges | Width relative to scale, segments, shading |
| Subdivision | Smooth organic/hero forms | Cage flow, support loops, density |
| Remesh | Sculpt-to-base workflows | Lost details, density, scale |
| Decimate | Static/background simplification | Silhouette, UVs, shading, material borders |
| Solidify | Thin surfaces needing thickness | Rim artifacts, normals, thickness at scale |

Keep modifiers non-destructive while exploring. Apply only when needed for export, baking, or a verified downstream step. Do not apply modifiers blindly to rigs, shape keys, or shared data.

## 5. Shading and surface quality

- Flat shading is valid for faceted low-poly styles; smooth shading is valid for curved surfaces. Choose intentionally.
- Use bevels and weighted normals for hard-surface edge highlights, but inspect artifacts and modifier order.
- Recalculate normals only when the mesh supports consistent outward orientation; open and multi-shell meshes need contextual inspection.
- Avoid coplanar overlapping surfaces that cause z-fighting.
- Check the model under neutral lighting before presentation lighting.

## 6. UV and material discipline

- Unwrap only when the target needs UVs; procedural or vertex-color workflows may differ.
- Allocate UV space by visual importance and texel density, not equal island size.
- Preserve padding appropriate to texture resolution and mipmapping.
- Tiling UVs outside 0–1 and overlapping mirrored UVs can be intentional; record that choice.
- Reuse materials where possible; avoid unique materials for tiny components without a reason.
- Bake procedural details when the destination cannot reproduce the shader graph.

## 7. Production handoff

Run scripts/validate_asset.py with explicit targets, inspect multiple views, and use the specialized checklist. Report object names, dimensions, evaluated triangles, base mesh counts, material slots/unique materials, UV and texture status, warnings, skipped checks, known defects, export format, and whether the exported file was reopened/tested.

Do not call a model optimized or production-ready solely because its triangle count is low.
