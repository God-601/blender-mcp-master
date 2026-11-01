# Hard-Surface Modeling

Use this guide for furniture, tools, weapons, vehicles, machinery, armor, props, and other objects defined by controlled edges, planes, joints, and mechanical forms.

For dimensioned examples of a sedan, decorative sword and table, use `references/measured-proportion-recipes.md` and their three scripts. The measurements are **example starting points**, not universal rules.

## 1. Plan the object

- Identify the primary silhouette, functional parts, moving parts, major material regions, and intended viewing distance.
- Choose a geometry budget from the target use, not from habit. A close-up render may justify more segments than a distant game prop.
- Decide which parts should be separate objects for pivots, materials, collisions, modularity, or animation.
- Set scale, coordinate axes, origin conventions, and export target before detailed modeling.

## 2. Build in layers

1. **Blockout:** use simple primitives for the main volumes. Inspect front, side, top, and three-quarter views before adding details.
2. **Primary forms:** establish proportions, thickness, openings, major bevels, and negative spaces.
3. **Secondary forms:** add panel breaks, recesses, rails, handles, seams, and mechanical details that support function or silhouette.
4. **Tertiary detail:** use screws, labels, scratches, and micro-details only when the camera can read them.
5. **Surface pass:** inspect highlights, material breaks, roughness, and shading on a neutral background.
6. **Delivery pass:** validate topology, transforms, pivots, materials, budgets, and exports for the actual target.

If the silhouette is wrong, return to the blockout rather than compensating with detail.

## 3. Modifiers and Booleans

A common editable stack is Mirror/Array → Boolean → Solidify where needed → Bevel → normals/shading correction → export triangulation when required. This is a starting point, not a universal stack.

- Keep cutters simple, clearly named, and isolated from deliverable geometry.
- Use non-destructive modifiers while iterating. Apply them only when required for export or final validation.
- Boolean quality depends on source topology, intersections, scale, and solver; do not assume a Boolean automatically produces clean topology.
- Inspect thin slivers, coplanar faces, internal geometry, and small gaps after Boolean operations.
- Bevel width must fit local geometry. A bevel wider than a nearby gap can collapse or distort the shape.
- Use weighted normals or angle-based smoothing only when the mesh and Blender version support the chosen method.

## 4. Edge treatment and materials

- Bevel edges that should catch light, but do not bevel every edge uniformly.
- Use consistent bevel logic across related assets. Small stylized objects may require exaggerated bevels for readability.
- Place supporting loops based on the curvature and subdivision needs, not as decoration.
- Keep material regions intentional. Painted metal, raw metal, rubber, glass, cloth, and plastic should not share identical roughness by default.
- Make wear and scratches support edges, contact, and use; avoid generic noise over every surface.

## 5. Moving and repeated parts

- Separate doors, lids, wheels, drawers, hinges, and rotating components when they need independent pivots or animation.
- Put each origin at the meaningful pivot for the intended action.
- Use linked duplicates or instances for bolts and repeated components.
- For assemblies, verify clearances and intersections at all expected positions, not just the default pose.

## 6. Game and CAD differences

For game assets, prioritize silhouette, target triangle/material budgets, UVs, texture baking, LODs, and export safety. Read references/game-ready-export.md and references/uv-baking.md when relevant.

For dimension-driven or mating parts, prefer explicit parameters, datums, and tolerance checks. A clean-looking Blender mesh does not prove engineering fit; read references/cad-technical.md when dimensions or manufacturing matter.

## 7. Review checklist

- Does the silhouette read without small details?
- Are bevels consistent and free of shading pinches?
- Are Boolean results and hidden surfaces inspected?
- Are parts, pivots, names, and material boundaries intentional?
- Are triangle count, scale, UVs, and exports checked for the target?
- Are user-owned objects and source geometry preserved?
