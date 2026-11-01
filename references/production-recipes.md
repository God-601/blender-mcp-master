# Production recipes — component contracts, not magic macros

Use these as **decision and inspection recipes**. They supplement existing executable scripts, not replace visual modeling. Numbers are examples in meters for conventionally scaled scenes; scale for the actual brief. Every recipe demands a visual reference check before artistic approval.

## R01 — Chair / furniture (hard surface or stylized)

- Typical starting sizes: seat height about 0.45 m, overall width 0.42–0.55 m, depth 0.40–0.55 m; adjust for stated brief/reference.
- Components: seat, four legs or designed support, backrest, optional rails/arms. Name by function rather than primitive.
- Plan: silhouette blockout from front/side/three-quarter, build supports, set joins, bevel according to local thickness, UV/material pass.
- **Must verify:** legs share ground plane within stated tolerance, no unintended floating support, backrest structurally reaches seat/rails, symmetry only when design calls for it; pivot and evaluated triangle budget.
- Do not mark leg-to-seat physical contact PASS from bounding boxes alone: use visual geometry and, when required, exact intersection/mesh checks.

## R02 — Fictional sword / rigid prop

- Components: blade profile, bevel/edge zone, guard, grip, pommel; define a common longitudinal axis.
- Plan: silhouette in orthographic front view first, taper via explicit profile, separate guard/grip pivots where needed, shading with conservative bevel.
- **Must verify:** blade/handle axial alignment, no unintended negative space at assembly junctions, thickness suits artistic brief, bevel doesn't collapse the thin blade, material roughness distinguishes regions.
- A decorative sword does not need manufacturing-ready structural calculations.

## R03 — Small modular house / stylized architecture

- Components: foundation, walls, door opening, windows, roof planes, optional trim.
- Plan: blockout measured wall thickness and floor height; reusable trim modules; consistent snapping and pivots; inspect roof/wall junctions.
- **Must verify:** door and window clearances if walkable, scale consistency, roof collision/overlap intentional, no zero-area mesh from overlarge bevels, reasonable evaluated budget/LOD.

## R04 — Stylized tree / organic prop

- Components: tapered trunk, attached main branches, canopy clusters/foliage cards; define plausible branching and taper.
- Plan: primary mass and crown silhouette, branch hierarchy, canopy variation following design, material/UV solution for destination.
- **Must verify:** every intended branch meets trunk or a parent branch, canopy sits on supports, leaf-card boundaries are allowed, connected shell is *not* required when branches/leaves are intentionally separate, wind/deformation only if requested.

## R05 — Deformable character / creature

- Components: torso, pelvis, head, limbs, hands/feet or equivalent anatomy, articulation joints.
- Plan: front/side proportion references → blockout → major volume critique → deformation-aware edge flow → weights/rig → bend and twist pose tests → lookdev.
- **Must verify:** proportions from agreed reference, joints have deformation loops, volume loss/collisions inspected in extreme poses, modifier ordering doesn't break weights, no automatic retopo promise.
- A neutral standing pose passing a geometry validator is not evidence of animation quality.

## R06 — Mechanical panel / hard-surface hero asset

- Components: main slab, recess/cutter, trim, repeated fasteners.
- Plan: explicit slab thickness → BOOLEAN DIFFERENCE → bevel below local gap/clearance → weighted normals if appropriate.
- **Must verify:** actual evaluated cut removes volume (not UNION), no tiny degenerate polygons, symmetric fastener positions, bevel highlights read under neutral lighting. Confirm cutter not exported.

## Recipe acceptance record

For any recipe, record `component_id, target_dimensions, real_dimensions, relationship_checks, expected_topology, target_views, result, evidence`. Use `scripts/inspect_geometry.py` for measurable checks and `references/visual-inspection.md` for artistic review. Label incomplete checks NOT VERIFIED. Expand recipes by testing a *real example asset*, not by adding untested parameter tables.
