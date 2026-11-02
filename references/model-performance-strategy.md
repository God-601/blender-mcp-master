# Model performance strategy — evaluated evidence before optimization

This is a Blender **3D asset** optimization guide, not AI model-weight quantization or LLM inference tuning. All default numbers are **project targets**, not universal platform limits. Measure and verify against the specific game/renderer and version.

## 0. Collect a read-only baseline

Run `scripts/asset_performance_audit.py` after providing explicit mesh object names in `TARGETS`. It reports per-object base/evaluated triangle counts (including modifiers), material slot counts, source mesh sharing, referenced image dimensions and an illustrative RGBA8 texture footprint. It never edits the scene.

**Limits:** material slots are not exact draw calls, evaluated triangles are not screen-space workload, RGBA8 level-0 bytes are not true VRAM, and this audit does **not** benchmark FPS or prove real-time performance. For exact collision, texture, renderer and engine behavior, test in the destination.

## 1. Choose the least destructive optimization

| Symptom / goal | Prefer | Avoid / verify |
| --- | --- | --- |
| Many copies of identical geometry | Linked mesh datablocks, object/Geometry Nodes instances | Realizing/duplicating unique meshes unnecessarily; check instance support in target engine |
| Dense scanned/sculpted static prop | Decimate Collapse on an inspected copy, or a dedicated low-poly retopo | Decimation over a deforming rig or shape-key mesh; inspect silhouette, UV seams, normals |
| Grid-like over-subdivided mesh | Decimate Un-Subdivide when grid construction permits | Arbitrary topology expecting a reversible subdivision |
| Flat mechanical surface with extra coplanar edges | Planar Decimate / limited dissolve with material/UV boundaries protected | Dissolving edge flow near support loops or animation joints |
| Character needing movement | Dedicated edge-flow retopology and actual bend/twist pose tests | Blind decimation or assuming QuadriFlow is animation-ready |
| Large repeated world or background props | Distance-aware LODs; preserve hero silhouette; test actual screen sizes | Generic fixed polygon ratios or premature LOD without evidence |
| Too many heavy materials/textures | Shared materials, atlases, baking targeted static results, right-sized textures | Changing artistic appearance or assuming Blender PBR exports identically |
| Expensive Geometry Nodes | Instancing; minimize Realize Instances; profile heavy nodes and simplify | Applying or realizing without understanding downstream requirements |

Blender's official Decimate modifier supports Collapse, Un-Subdivide and Planar modes. Its reported face ratio is not a universal percentage of visual complexity; evaluate the result in its actual modifier stack.

## 2. Workflow and gates

1. Establish the **target**: Roblox/general mesh or avatar, Unity, Unreal, Godot, still render, animation, printing, etc. Confirm only actual engine limits from the target's official docs.
2. Choose a task-specific per-asset triangle, material and texture target. Don't turn suggestions from `references/budgets.md` into hard engine requirements.
3. Measure actual evaluated geometry from named objects. Snapshot source files and note source/instance relationships.
4. Optimize on **separate, owned copies** using `optimize_mesh.py`, `make_lods.py`, or guided retopology, with dry-run first. Do not bulk-delete unseen faces or alter shared data.
5. Compare the same object/view: front, side, back and three-quarter silhouette, thin parts, UVs, shading, material boundaries and pivots.
6. Re-run measured triangles/materials and inspect whether the target improved without new defects. Any warning about missing targets means **INCOMPLETE**, not success.
7. If exporting, re-import a copy and test in the actual intended engine where available. Measure runtime FPS/frame time there, not in a Blender Python script.
8. Report before/after metrics, reversible steps, any degradation and explicit **NOT VERIFIED** outcomes.

## 3. Advanced guidance

### Geometry Nodes
- Defer Realize Instances when possible. Repeated instanced geometry can use less memory because geometry is evaluated/reused rather than duplicated.
- Reduce unnecessary subdivision and dense procedural intermediate geometry; check profilers/timings in the actual Blender version.
- Keep node trees understandable; don't equate node count alone with evaluation cost.

### Retopology and deformation
- QuadriFlow can create quad-based geometry but is not a perfect solution for animated character edge flow. Plan joint loops and test in extreme poses.
- `scripts/retopology_advanced.py` supports only explicit loop bridge, planar fill and relax on copies. It does not claim fully automatic retopology.

### Textures and draw overhead
- Test atlasing and material consolidation with real shader output; don't delete assets referenced by other objects.
- Distinguish source image dimensions, packed file size, decoded RAM and GPU VRAM.
- Use texture compression, mipmaps and material complexity limits dictated by the actual engine rather than fixed folklore.

## Official source references

- [Blender 5.2 Decimate modifier](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/decimate.html)
- [Blender 4.5 Geometry Nodes instances](https://docs.blender.org/manual/en/4.5/modeling/geometry_nodes/instances.html)
- [Blender remeshing / QuadriFlow](https://docs.blender.org/manual/en/5.0/modeling/meshes/retopology.html)
- [Blender Python API](https://docs.blender.org/api/current/)
- [Roblox model specifications](https://create.roblox.com/docs/art/modeling/specifications)

Keep the Blender documentation version pinned to the actual runtime, and validate import/export on the intended engine.
