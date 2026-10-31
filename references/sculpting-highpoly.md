# Sculpting and High-Poly Workflows

Use this guide for organic detail, creature/character forms, rocks, worn surfaces, ornate props, and source meshes that will later be retopologized or baked. The skill must first discover whether the active Blender MCP integration supports the necessary scene operations; not every integration offers direct sculpt tools.

## 1. Choose the intended result

- **Procedural shape construction:** suitable for repeatable base forms, simple displacement, generated details, and bulk operations.
- **Sculpt session:** better for gesture, anatomy, expressive silhouette, and artistic form decisions that benefit from continuous visual feedback.
- **High-poly source for baking:** use a detailed mesh or sculpt to capture surface information on a separate low-poly target.
- **Final high-poly render asset:** keep the dense mesh if the scene is not constrained by real-time performance, but manage memory and modifier costs.

Do not describe noise displacement or a voxel remesh as equivalent to skilled sculpting. They are tools for specific stages and have predictable limitations.

## 2. Establish forms before surface detail

1. Define silhouette, proportions, pose, and primary masses.
2. Inspect front, side, top, and three-quarter views while shapes remain easy to change.
3. Establish secondary forms: muscle groups, plates, folds, major cracks, large facets, or broad erosion.
4. Add tertiary detail only after primary and secondary forms read clearly.
5. Inspect the model under neutral lighting and from the intended viewing distance; dramatic lighting can hide weak form.

For anatomy, use clear references and treat realistic faces, hands, and deformation anatomy as high-judgment tasks. When a procedural result is only a blockout, report that limitation rather than calling it production-ready.

## 3. Procedural sculpt-like methods

- Use proportional displacement, carefully bounded noise, Displace modifiers, or bmesh operations for controlled variation.
- Keep random seeds fixed when reproducibility matters.
- Protect major silhouette forms by using masks, falloff regions, vertex groups, or separate detail layers where practical.
- Avoid large uniform noise that makes the model look melted or equally rough everywhere.
- Use voxel remesh when the goal is to merge intersecting organic volumes or rebuild a continuous sculpt surface. Expect loss of fine detail and sharp edges; choose voxel size based on the smallest form that must survive.
- Apply remeshing only to dedicated working copies unless the user explicitly requested destructive modification.

## 4. High-poly to game-ready route

1. Keep a clean source/high-poly version and a separate low-poly target.
2. Finalize the target silhouette and decide the triangle and texture budgets.
3. Retopologize the target using references/topology-retopology.md.
4. Create and inspect the target UVs before baking.
5. Bake the maps that are actually needed: often tangent normal and AO; base color, curvature masks, roughness, or displacement only when relevant.
6. Inspect bakes at UV seams, hard edges, thin details, cavities, and overlapping shells.
7. Connect the baked images to a target-compatible material and verify the look under neutral and intended lighting.
8. Export only the low-poly target and its required dependencies unless the destination explicitly needs the high-poly source.

A normal map cannot repair a wrong silhouette, bad UVs, or missing geometry at the asset's expected viewing distance.

## 5. Subdivision and remeshing

- Use Multiresolution when you need multiple sculpt levels and a supported bake path.
- Use Subdivision Surface when smooth surface refinement and predictable control loops are appropriate.
- Use voxel remesh when continuous topology is more important than exact original edge flow.
- Use decimation for static reduction or proxy creation; inspect the result because sharp features and surface quality can be lost.
- Record modifier levels and memory impact for dense assets. Keep preview levels lower than final render levels when the scene becomes slow.

## 6. Review and safety

- Preserve an untouched source or create a clearly named working copy before destructive remesh, decimation, or modifier application.
- Check for lost thin parts, closed cavities, merged limbs, changed dimensions, and accidental silhouette shrinkage.
- Measure triangle count after finishing modifiers and before export.
- Verify that the actual target file or bake was saved; a successful viewport preview is not proof of delivery.
- If a manual sculpting step or add-on is unavailable through MCP, identify that limitation and continue with a suitable blockout or supported alternative.
