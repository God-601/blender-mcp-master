# Architecture and Interior Environments

Use this guide for buildings, rooms, architectural visualization, interior layouts, modular game environments, and readable scene blockouts. For large game levels, also read references/environment.md; for dimension-driven components and tolerances, read references/cad-technical.md.

## 1. Establish a brief and coordinate standard

Before building, define:
- Intended use: architectural visualization, interactive walkthrough, game level, product/interior scene, or schematic blockout.
- Units, building footprint, story height, wall thickness, openings, circulation, and major dimensions.
- Camera positions, target viewpoints, lighting mood, and whether the output must be a dimensionally credible layout or only a visual concept.
- Module grid, origin convention, material strategy, and performance target.
- Which dimensions are requirements and which are early assumptions.

Do not invent building-code compliance or claim construction-ready documentation from a visual model. Regulatory, structural, accessibility, and safety requirements must be verified against the applicable jurisdiction and qualified source.

## 2. Block out space before detailing

1. Draw or encode the footprint, main axes, room zones, entrances, circulation, and vertical connections.
2. Place simple walls, slabs, columns, doors, windows, and stairs at the intended scale.
3. Check sightlines and navigation from the planned camera or walkthrough height.
4. Verify doors, corridors, furniture clearances, stair runs, and intersections against the brief.
5. Correct spatial problems before adding trim, bevels, props, materials, or decorative detail.

Use a consistent grid for modular construction. Door and corridor dimensions in an example scene are assumptions, not universal code requirements.

## 3. Modular architecture

- Define reusable modules for walls, corners, columns, floors, ceilings, windows, doors, trims, and stairs.
- Give modules consistent grid increments, pivots, naming, and orientation.
- Share materials and linked mesh data when repeating identical geometry.
- Use trim sheets or atlases when many pieces share one material.
- Separate structural shell, fixtures, furniture, lighting, and decorative dressing into named collections.
- Avoid overlapping coplanar faces. Use designed joints, bevel gaps, or decals instead of z-fighting.

## 4. Interior materials and lighting

- Keep material scale consistent on adjacent walls, floors, and trim.
- Distinguish roughness and reflectance by material type rather than using one generic surface for the whole room.
- Use a neutral lighting pass to inspect proportions, material errors, and light leaks before styling the final render.
- Check exposure, color management, reflections, shadows, and visibility at actual camera positions.
- For game environments, bake only when it suits the lighting pipeline and ensure baked lighting does not contradict dynamic lights.

## 5. Technical and performance checks

- Inspect wall/floor/ceiling intersections for gaps and light leaks.
- Check that doors, windows, stairs, and repeated modules align with the grid.
- Confirm dimensions and object origins for modular pieces.
- Use instances for repeated props and vegetation; track instance count and estimated triangle count.
- Use LODs and simplified collision where the target requires them.
- Remove hidden geometry only after confirming it is not needed for reflections, visibility from another room, or expected future edits.

## 6. Deliverables

State whether the output is a visual scene, blockout, modular kit, or dimension-driven model. Report dimensions and assumptions, note any code/compliance checks that were not performed, and identify if camera/render output or in-engine navigation was actually tested.
