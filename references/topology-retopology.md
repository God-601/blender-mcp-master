# Topology and Retopology

Topology is a tool for the asset's job, not a beauty score. Choose density and edge flow based on silhouette, deformation, subdivision, shading, simulation, and export needs.

## 1. Pick the topology target

- **Static real-time prop:** triangles are valid; place edges where they affect silhouette, shading, or texture projection.
- **Subdivision surface:** prioritize predictable loops and support edges. Avoid long, narrow faces and pole placements that create pinching on curved areas.
- **Deforming character/creature:** use edge loops that follow anatomy and bending zones, with sufficient loops around shoulders, elbows, hips, knees, fingers, mouth, and eyelids as needed.
- **High-poly sculpt source:** prioritize surface quality and sculptability, not export efficiency.
- **CAD/technical solid:** prioritize dimensional accuracy and clean surface boundaries; quad topology is not always the primary requirement.
- **3D printing:** validate watertightness, normals, wall thickness, and scale according to the printer/material workflow.

## 2. Retopology strategy

Choose the least risky approach that meets the target:
1. **Manual retopology:** best control over edge flow and deformation; may require human visual decisions that cannot be inferred safely from a generic script.
2. **Shrinkwrap-based cage:** create a low-density surface over the high-poly, then use Shrinkwrap to fit it. Inspect distance, offsets, and areas with thin surfaces.
3. **Voxel remesh:** useful for rebuilding a continuous organic sculpt, but may erase sharp details, separate parts, or alter silhouette; it is not a replacement for final animation topology.
4. **Decimation:** useful for static meshes and rough proxies. It does not promise good edge flow, UVs, or deformation.
5. **Quad remeshing or external tools:** use only if the installed Blender build/add-ons provide them. Discover capability and confirm output before relying on the result.

Do not promise perfect automatic retopology from ordinary bpy scripts. Automated methods can make a usable starting point; inspect and correct important forms.

## 3. Build a usable low-poly mesh

- Preserve silhouette at the target camera distance first.
- Add edge loops where they affect deformation, bevel support, curvature, or a visible contour.
- Avoid evenly distributing polygons everywhere when only some areas require curvature.
- Keep poles away from strong deformation and highly curved highlights when practical.
- Avoid dense geometry that will be removed by subdivision, export triangulation, or distant viewing.
- Separate modular/moving parts when their pivots or animation require independent transforms.
- Keep construction helpers and hidden cutters out of the final exported set.
- Track triangle count after the final modifiers and triangulation policy, not only in the editable base mesh.

## 4. High-to-low correspondence

Before baking high-poly detail:
- Freeze the intended low-poly silhouette and UV layout.
- Ensure the high-poly surfaces correspond spatially with the low-poly target.
- Inspect intersecting parts, thin protrusions, cavities, and overlapping surfaces that can cause rays to hit the wrong source.
- Use a matching cage or carefully tuned ray distance if the shape requires it.
- Test a small or low-resolution bake before generating final texture maps.

See references/uv-baking.md for bake setup, map interpretation, and diagnostics.

## 5. Deformation-aware topology

For characters:
- Route loops around shoulders, elbows, hips, knees, wrists, ankles, jaw, lips, eyelids, and fingers according to the planned movement.
- Keep deformation areas dense enough for bending but avoid redundant loops that provide no control.
- Weight paint after the topology is stable, then pose-test the skeleton and inspect collapsing volume, candy-wrapper twist, intersections, and silhouette changes.
- Re-run deformation tests after any topology or modifier change that affects vertex order or count.
- Avoid applying topology-changing modifiers after weights, shape keys, or rig setup unless the consequences have been checked.

## 6. Static validation and visual review

- Review wireframe from multiple angles, not only the front view.
- Check loose geometry, degenerate faces, unexpected non-manifold edges, flipped normals, and interior geometry where applicable.
- Interpret boundaries in context: an intentionally open plane, leaf card, cloth shell, or thin surface is not automatically broken.
- Inspect flat areas for shading artifacts and curved highlights for pinching.
- Compare triangle count and edge placement to the chosen budget and camera distance.
- Mark checks as PASS, ISSUE, N/A, or NOT VERIFIED. A validator warning is evidence to investigate, not a universal verdict.

## 7. Common failure modes

- **Decimated but ugly:** rebuild the silhouette and edge flow instead of raising the polygon count blindly.
- **Pinches under subdivision:** move poles, add supporting loops only where needed, and inspect the modifier stack.
- **Baking errors:** inspect high/low intersections, cage topology, smoothing splits, UV padding, and ray range.
- **Broken deformations:** restore joint loops, inspect weights, and avoid topology-changing operations after rigging.
