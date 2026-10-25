# Modeling quality loop: plan, inspect, correct, verify

Use this reference for any asset where the result must be more than a plausible first-pass mesh. It complements the model-specific references; it does not replace them.

## 1. Establish the acceptance criteria first

Before creating geometry, identify:
- **Purpose:** realtime game asset, animation/deformation, still render, 3D print, or blockout.
- **Style and reference:** realistic, stylized, low-poly, voxel/studs, or another named direction.
- **Scale and coordinate convention:** dimensions, units, forward axis, ground plane, and pivot expectations.
- **Budget:** triangle count, material slots, texture dimensions, and scene/render constraints appropriate to the target.
- **Required deliverable:** .blend only, or a specific export format plus any textures.

If the user has already specified these, do not ask again. If a missing detail materially changes the result, ask one concise question; otherwise state a reasonable assumption and proceed.

## 2. Use an explicit quality loop

1. **Inspect:** query addon/MCP status and scene information. Record Blender version, existing objects, units, active collection, and relevant scene state.
2. **Plan:** describe the intended silhouette, major parts, modeling method, and acceptance checks in a few lines.
3. **Block out:** build only primary volumes and establish proportions. Check front, side, top, and three-quarter views before adding detail.
4. **Refine:** add secondary forms, bevels, supporting loops, organic variation, or other details appropriate to the style. Keep operations non-destructive while iterating.
5. **Inspect visually:** request a fresh view after meaningful changes. Use multiple angles for shape, solid/material shading for surface issues, and wireframe for topology. Frame the asset itself where supported.
6. **Validate technically:** run the validation script and relevant model-specific checks. Treat the report as evidence, not as a substitute for looking at the mesh.
7. **Correct:** fix the highest-impact issue first (silhouette/proportion, then geometry/shading, then materials/UVs, then minor polish). Reinspect after corrections.
8. **Deliver:** save/export only when requested. Validate the actual output file or report explicitly that the export itself was not tested.

Do not call visual-inspection tools after every trivial property change. Do call them after changes that can affect silhouette, shading, topology, composition, or export correctness.

## 3. Visual review checklist

### Shape and readability
- Does the silhouette match the request/reference from front, side, and three-quarter views?
- Are major proportions and negative spaces intentional?
- Is the focal feature visible at the intended viewing distance?
- Are parts accidentally intersecting, floating, or coplanar in ways that cause z-fighting?
- Are repeated elements varied only when the design calls for variation?

### Surface and topology
- Are bevel widths consistent with scale and style?
- Are there shading pinches, unexpected hard edges, or smooth areas that should be flat?
- Does wireframe density follow the silhouette and deformation needs?
- Are there loose elements, zero-area faces, unintended duplicate geometry, or non-manifold edges where a closed solid is required?
- Are n-gons appropriate for this static surface, or are they on a curved/deforming area where they may cause problems?

### Materials and presentation
- Are material names and colors intentional and consistent?
- Is roughness appropriate for the material rather than copied across every surface?
- Are texture maps packed/saved if the deliverable depends on them?
- Does lighting reveal the form without hiding defects? Use neutral inspection lighting before adding dramatic presentation lighting.

### Game/export readiness
- Are scale, orientation, origin/pivot, names, UVs, materials, and triangle count appropriate for the destination?
- Are unsupported procedural nodes or modifiers baked/applied only when needed for the target?
- Does the export contain only intended objects and no hidden cutters/helpers?
- If the target application is unavailable, state that the export settings were checked but the in-engine result was not verified.

## 4. Interpret diagnostics in context

A script's PASS/WARN/FAIL is a useful signal, not universal truth:
- **Non-manifold edges:** often an issue for watertight solids and 3D printing; may be expected on planes, foliage cards, cloth shells, or intentionally open surfaces.
- **Boundary edges:** normal for open surfaces; investigate on a closed solid.
- **N-gons:** not automatically wrong on a flat static surface; avoid relying on them on curved, subdivided, or deforming regions.
- **Loose vertices/edges:** remove unless they are deliberate construction helpers excluded from the deliverable.
- **Normals:** use mesh-aware checks and inspect shading. A heuristic that compares face normals to the object's center can misclassify concave or asymmetric meshes; do not treat it as a definitive normal test.
- **Applied transforms:** scale/rotation requirements depend on the workflow. Apply them for export/UV/baking when appropriate, but do not destructively alter user-owned objects merely to make a validator pass.
- **UV bounds:** UVs outside 0–1 can be intentional for tiling or UDIM workflows. Validate against the intended texture workflow, not a universal rule.
- **Triangle/texture/material budgets:** compare against the selected target and expected camera distance; default values are warnings/starting points, not universal production limits.

When a check is ambiguous, inspect the asset and explain why it is acceptable or what remains uncertain.

## 5. MCP reliability and scene safety

- Discover the tools actually exposed by the active MCP server. Tool names and parameters vary between implementations; do not assume another repository's tool list applies.
- Use addon status and scene-info tools when available. If a tool is missing, continue with supported tools and disclose the limitation rather than fabricating a result.
- Prefer direct Blender data API / bmesh access for predictable data edits. Use operators only when an operator is needed; set mode/selection/active object or use a supported context override, then check its result.
- Make scripts repeatable: name outputs, check for existing objects, and scope cleanup to a dedicated collection or clearly identified objects created for this task.
- Before destructive actions, print the exact target objects and ask for confirmation if existing user data could be lost.
- Use Blender version checks and capability checks for APIs that differ across versions.
- Catch errors at the smallest useful step and print the failing operation and exception. Do not silently continue after a failed geometry or export operation.
- Never claim visual inspection, validation, or export succeeded unless the corresponding tool output was actually received and checked.

## 6. Efficient iteration

- Batch related edits into one tool call, but separate risky or hard-to-debug stages.
- Print concise evidence: object names, dimensions, triangle count, material slots, UV count, warnings, and output path. Avoid dumping full vertex/face arrays.
- If the first inspection shows a major shape problem, revise the blockout instead of adding more detail.
- If two consecutive iterations do not improve the stated acceptance criteria, pause and reconsider the method/reference instead of repeating the same operation.
- Use generated/imported meshes as starting points when helpful, but inspect scale, topology, licensing, materials, and target suitability before treating them as final.
