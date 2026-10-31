# Game Asset Optimization

Practical, evidence-driven optimization for static and real-time game assets. This guide is intentionally conservative: a lower triangle count is not automatically a better asset. Preserve silhouette, shading, UVs, material assignments, deformation, collision behavior, and readability at the intended camera distance.

## 1. Optimize the actual bottleneck

Measure before changing anything. Record per-object and total:
- evaluated triangles (including visible modifiers), vertices, edges, polygons;
- object count, mesh datablock users, material slots and unique materials;
- texture dimensions and estimated memory where available;
- modifier stack, shape keys, armatures, animation/deformation dependencies;
- intended viewing distance, target platform, collision needs and whether the asset repeats.

Do not optimize by a generic universal triangle target. Set a budget from the game's camera, platform, asset importance, scene density, and profiling results. Roblox-specific performance also depends on draw calls, materials, texture memory, physics, scripts, and instance count.

## 2. Safe geometry cleanup

Apply only after inspecting the target and creating a recoverable backup.

| Technique | What it does | Main caveat |
|---|---|---|
| Join objects (Ctrl+J) | Combines selected objects into one object | Does not weld vertices or remove internal faces; can harm modularity and material organization |
| Merge by Distance | Welds coincident/nearby vertices | A large threshold can collapse intentional gaps, thin parts, UV seams or hard edges |
| Delete Loose | Removes vertices/edges/faces not connected to useful surface | Open meshes and wire details can be intentional |
| Degenerate Dissolve | Removes zero/near-zero-area geometry | Inspect tiny bevels and thin details afterwards |
| Limited Dissolve | Removes redundant edges on nearly coplanar surfaces | Can change triangulation, UV interpolation and shading boundaries |
| Decimate | Reduces polygon count by collapsing edges or planar dissolution | Can damage silhouette, UVs, normals, material borders and thin features |
| Retopology | Rebuilds topology for predictable flow and deformation | Higher labor; best for deforming or badly structured meshes |

Recommended order for static props:
1. Remove truly loose/degenerate geometry.
2. Weld only verified duplicate vertices with a small, scale-aware threshold.
3. Dissolve redundant coplanar edges only where the result remains visually and UV-correct.
4. Consider Decimate only on a duplicate or with a recoverable backup; inspect multiple views.
5. Recalculate/inspect normals and validate the final mesh.

Do not run Merge by Distance across unrelated objects indiscriminately. Join first only when a single object is actually useful, then weld only vertices that should be connected.

## 3. Hidden and internal faces

There is no universally safe automatic rule that identifies every invisible face. A face hidden from the current camera may become visible when the asset rotates, is viewed from below, or is used in a different scene.

Safe candidates:
- faces fully enclosed inside a watertight solid;
- coincident surfaces that occupy the same space and serve no distinct purpose;
- faces between intersecting components only when they are guaranteed never to be exposed and do not affect shading, UVs, normals, or material behavior.

Unsafe candidates:
- backfaces on thin sheets, leaves, cards, cloth or open surfaces;
- faces hidden only from one camera angle;
- surfaces needed for cavities, holes, transparency, interior views, animation or collision;
- faces at material boundaries or UV seams without checking the bake and texture result.

For overlapping primitive assemblies, prefer modeling the final outer shell or using a controlled Boolean union, then inspect topology and shading. Boolean union can create n-gons and messy topology; it is not a free optimization. If uncertain, keep the faces.

## 4. Reduce draw and scene overhead

- Reuse mesh datablocks or linked duplicates for repeated identical props. Do not make unique mesh copies unless variation requires them.
- Keep object separation where it supports modularity, animation, interaction, visibility, or independent materials. Fewer objects is not always better.
- Reduce unique materials and material slots where practical; use shared materials and texture atlases when this suits the art direction.
- Avoid needless modifier stacks and excessive subdivision on runtime assets.
- Use simple, separate collision proxies for physics when appropriate. Do not use the render mesh as a complex collider by default.
- For repeated foliage, rocks, props and modular pieces, test instancing and the target engine's batching behavior.

## 5. LOD strategy

Create LODs only when assets are viewed at enough distance for the saved work to matter. Set transition distances using the target engine and camera, not a universal number. Preserve the silhouette first; remove small surface details before major forms. Verify each LOD in motion and at its actual screen size. Avoid popping, material changes and shadow discontinuities.

## 6. Roblox-specific considerations

For Roblox, evaluate the full cost:
- mesh triangle/vertex complexity and visual fidelity;
- number of instances and unique mesh/material combinations;
- texture resolution and memory;
- collision fidelity and physics workload;
- streaming, visibility and repeated asset behavior;
- whether LOD or simpler distant variants are worthwhile.

Use Roblox Studio's current import settings and engine documentation as the authority for supported limits and behavior. Do not hard-code platform limits in this skill. A simple collision shape can be more valuable than aggressively reducing render triangles. Repeated identical assets should reuse the same mesh asset where possible.

## 7. Workflow and acceptance criteria

1. **Scope:** identify exact target objects by name; never silently fall back to the whole scene for destructive work.
2. **Baseline:** record counts, dependencies, modifiers, materials, UV layers, shape keys and mesh datablock users.
3. **Risk gate:** skip linked/library data, shared mesh data, shape-key meshes, and objects with deformation dependencies unless the workflow explicitly supports them.
4. **Backup:** preserve the original object and mesh data before destructive edits. Do not overwrite the user's source file.
5. **Conservative pass:** remove only confirmed loose and degenerate geometry; use a very small merge distance only when explicitly enabled.
6. **Optional simplification:** use Limited Dissolve or Decimate on a recoverable copy. Do not auto-delete internal faces.
7. **Visual QA:** inspect front, side, rear, top, bottom and three-quarter views; compare silhouette, shading, UVs, materials and thin details.
8. **Technical QA:** compare before/after triangle counts and percent change; check non-manifold edges, boundaries, zero-area faces, loose geometry, normals, UVs and modifiers. Interpret open boundaries in context.
9. **Report:** state exact objects, operations, counts before/after, percentage change, backup names, skipped targets and unverified checks.

Accept only when the asset still meets its visual and functional requirements. If the reduction is negligible or quality regresses, revert the operation.

## 8. Bundled optimizer

Use `scripts/optimize_mesh.py` as a configurable template. It is dry-run by default. Set explicit `TARGETS`, inspect the report, then deliberately set `APPLY = True`. It creates a hidden backup collection before editing. It skips shape-key meshes, shared mesh datablocks, linked data and unsupported dependency cases by default. The script performs cleanup only; it does not guess which faces are internal. Optional Decimate is added as a non-destructive modifier and must be visually reviewed.

Run `scripts/validate_asset.py` before and after. Runtime-test the script in the Blender versions supported by this repository before relying on it in production.
