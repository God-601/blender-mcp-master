# Modeling decision framework — choose techniques like a production artist

This is an agent **selection algorithm**. Choose based on downstream needs and observable failure modes, not tool familiarity. Technique names do not guarantee workmanship.

## Step A — decompose the reference

Extract visual masses, negative spaces, symmetry axes, repeated geometry, joints, dimension constraints, silhouette landmarks and likely material families. Assign each component a stable ID, desired pivot and dependency. Mark unknown measurements as estimates, not facts. Keep the full object visible while checking local details.

## Step B — select construction methods

| Geometry / use case | Primary technique | Avoid blindly | Check after construction |
|---|---|---|---|
| Rigid rectilinear furniture/architecture | dimensioned primitives + extruded profiles + modular repeats | smoothing/subdivision everywhere | spans, wall thickness, alignment, contact |
| Smooth radial forms, bottles, poles, vases | lathe or tapered profiles | arbitrary ring ordering/axis duplication | signed volume on closed shell; silhouette; end caps |
| Mechatronics/panels/recesses | Boolean cutters + conservative bevel + normals strategy | unapplied huge bevel / UNION for intended recess | evaluated cut, thin slivers, face direction |
| Curved handles, cables, pipes | curve sweep/bevel or controlled beams | straight cylinders where silhouette requires a bend | path continuity, orientation, thickness |
| Repeated screws/fence/columns | instancing/Geometry Nodes | independent high-poly copies | spacing, counts, evaluated result, export compatibility |
| Rocks/foliage/terrain | sculpt/procedural displacement with style controls | random noise as replacement for recognizable masses | feature hierarchy, silhouette, detached parts |
| Characters/flexible parts | reference blockout then deformation topology/retopology | decimate as final animation topology | articulation deformation tests |
| Stylized assets | controlled large forms, palette and deliberately limited facets | photoreal material noise and blanket bevels | legibility at target size, consistent shape language |
| High-to-low game assets | high-poly detail + dedicated low-poly + cage/UV/bake | direct uninspected export of generator mesh | bake normals, UV seams, triangle/material budgets |
| 3D print | dimensioned watertight solids and tolerance plan | accepting open sheets as 'manifold enough' | negative shells, thickness, intersections, actual slicer |

## Step C — choose by cost and reversibility

Prefer an editable method that meets the acceptance criteria with the fewest fragile topology changes. If the requirement is **dimensionally precise**, explicit numeric mesh construction beats improvising visually. If **artistic shape** dominates, visual blockout and reference comparison beat false numeric precision. If **animation** dominates, test poses before UV polish. If **engine** dominates, optimize after locking silhouette and evaluate post-modifier mesh.

Plan for rollback. Use per-task collections and stable names; do not implicitly overwrite existing objects. For repeated attempts, archive or duplicate only your own work. Before code execution, print planned targets and check object ownership.

## Step D — checkpoint decision rules

1. **Silhouette fails:** rebuild primary masses; do not add detail.
2. **Proportions fail:** measure component bounds/landmarks against the named reference, correct transforms or local geometry.
3. **Normals/volume fail on closed shell:** inspect winding and topology; don't run recalculate_normals on a disconnected/open asset without checking consequences.
4. **Boolean cut fails:** verify operation type (DIFFERENCE vs UNION), evaluated geometry and cutter volume.
5. **Bevel creates degeneracy:** reduce width according to local clearance, alter supporting topology or remove bevel; inspect evaluated mesh.
6. **Parts float:** check explicit attachment contract with measured gap and a visual close-up. Bounding boxes alone cannot prove contact.
7. **Materials fail:** verify texture roles/color spaces and node connections; a normal map must be Non-Color in the expected workflow.
8. **Unverified visual quality:** request actual viewport views; if unavailable, state NOT VERIFIED, not PASS.
9. **Two failed iterations:** change strategy, reduce complexity or solicit a missing visual reference.
10. **Export fails:** validate format settings and re-import into a clean staging scene where available; never silently edit the user's originals.

## Step E — local correction record

Write: `defect -> evidence -> affected IDs -> minimal change -> expected improvement -> post-change evidence -> status`. Changes that do not improve the intended metric should be reverted. No autonomous 'learning' claim without successful independent review.

## Hard boundaries

`look` availability, schemas and Blender versions must be discovered in each live client. This repository's bpy scripts are *templates to execute in Blender*, not portable CLI commands. Avoid assumptions about installed add-ons, generators, paid assets or the user's filesystem. Check import licensing before reuse.
