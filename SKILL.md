---
name: blender-mcp-master
description: Use when an agent plans, creates, inspects, textures, shades, lights, rigs, optimizes, validates, or exports any kind of 3D asset in Blender through MCP. Covers hard-surface, organic, characters, hand-painted, stylized/fantasy, low-poly/retro, PBR/procedural/toon materials, environments, architecture, CAD, sculpting, UVs/baking, retopology, game-ready assets, LODs, and rendering. Requires task-first planning, evidence-based quality checks, safe scene edits, and transparent delivery.
---

# Blender MCP Master

A skill for agents that drive a **live Blender session through MCP**. Goal: produce very good results across 3D disciplines by choosing a task-appropriate workflow, planning before modeling, validating with evidence, and correcting high-impact defects without unnecessary iteration.

Works with any agent that can read this file (Claude, Codex, Cursor, Gemini CLI, etc.). Tool names below are the MCP Blender server's; if your agent exposes them with a prefix, use the prefixed name.

## 0. The 8 golden rules (read these even if you read nothing else)

1. **Probe before you build.** Call `get_addon_status` once, then `get_scene_info`. Never assume Blender version, units, or what is already in the scene.
2. **Small steps, print everything.** One logical operation per `execute_blender_code` call. Always `print()` what you need to verify (counts, dimensions, names). Never write a 300-line script blind.
3. **Inspect, then correct.** Use `look` after changes that affect silhouette, shading, topology or composition; inspect multiple angles before adding detail and before delivery. See `references/modeling-quality-loop.md`.
4. **Never leave the scene dirty.** Don't delete or modify user objects you didn't create. Work in a dedicated collection named after the asset. Prefix or tag your objects.
5. **Explicit scale and transforms.** Treat 1 Blender unit as 1 m only when the scene/workflow uses metric units; confirm the destination's scale convention (especially Roblox). Apply transforms when required for UVs, baking, rigging or export, without destructively changing user-owned objects.
6. **Non-destructive first, destructive last.** Use modifiers (Bevel, Mirror, Array, Subdivision, Boolean) while iterating; apply only when finishing or when export requires it.
7. **Budget before detail.** Decide the target (triangles, texture size, material count) from the target use *before* modeling (see `references/budgets.md`) and state it in the plan. Detail beyond the chosen budget is a bug; a platform's hard limit is never exceeded, while the default numbers are adjustable starting points.
8. **Verify, then report.** Finish with measurable facts (tri count, dimensions, materials, issues found/fixed), not adjectives.

### Professional production contract (required for substantial assets)

A model is **not** production-ready because code executed or a topology check passed. Read `references/professional-modeling-standards.md` and `references/professional-agent-playbook.md` before nontrivial modeling. Use `references/modeling-decision-framework.md` to choose techniques and `references/production-recipes.md` for component/acceptance examples. Separate measurable geometry evidence from actual visual inspection and destination import evidence. Never mark visual quality PASS without inspecting real viewport images. Treat missing evidence as NOT VERIFIED; preserve all unrelated scene objects.

## 1. Session start checklist

```
1. get_addon_status        -> Blender version, enabled asset libraries / generators
2. get_scene_info(fields=["size","ground","materials","modifiers","details"], settings included)
3. Ask the user ONLY what you cannot infer: target use (game / render / print / animation),
   style (realistic / stylized / low-poly / voxel), budget (tris, platform), reference images.
4. Pick the pipeline in section 2, load the matching reference file(s).
```

If the user gave a clear target, do not ask: choose sensible defaults, state them in one line, and proceed.

### Version compatibility (check `blender_version` from `get_addon_status`)

| Blender | Differences that break scripts |
|---|---|
| 3.1 and older | No `context.temp_override` (use the dict override `bpy.ops.x({"object": ob}, ...)`), no `mesh.color_attributes` (use `vertex_colors`), no `wm.obj_export` (use `export_scene.obj`), `mesh.use_auto_smooth` exists |
| 3.2 to 4.0 | `temp_override` available; `use_auto_smooth` exists |
| 4.1+ | `use_auto_smooth` removed (use Smooth by Angle / sharp edges); Principled socket renames since 4.0 |
| 4.2+ | EEVEE Next (`BLENDER_EEVEE_NEXT`), `surface_render_method` replaces `blend_method` |

Guard version-specific code with `bpy.app.version >= (x, y, z)` or `hasattr`. If `get_addon_status` says the addon protocol is outdated, tell the user once how to update (`uvx mcp-for-blender install-addon`, then re-enable the addon) and continue; basic tools still work.

## 2. Route by model type (load only what you need)

| Request | Pipeline | Read |
|---|---|---|
| Furniture, tools, weapons, vehicles, machines, rigid props | Hard-surface modeling | `references/hard-surface.md` |
| Creatures, plants, rocks, terrain, food, organic forms | Organic modeling; add sculpt/high-poly when needed | `references/organic.md`; `references/sculpting-highpoly.md` when relevant |
| Characters, anatomy, deformation, rigging, animation | Character + deformation topology | `references/character-rig.md`; `references/topology-retopology.md` |
| Rooms, buildings, streets, levels, modular scenery | Environment | `references/environment.md` |
| Architecture, interiors, walkthroughs, spatial blockouts | Architecture/interiors | `references/architecture-interiors.md` |
| Dimension-driven parts, CAD-like meshes, 3D printing | Technical modeling | `references/cad-technical.md` |
| Low-poly, stylized, fantasy, voxel, retro/PS1, Roblox-like blockiness | Stylized art direction | `references/stylized-lowpoly.md` |
| Hand-painted textures, painterly highlights, color atlases | Hand-painted pipeline | `references/hand-painted-pipeline.md`; add `references/uv-baking.md` when texturing/baking is involved; runnable snippets in `references/handpaint-recipes.md` |
| UV layout, texture painting setup, baking maps, high-to-low projection | UV and baking | `references/uv-baking.md` |
| Edge flow, mesh density, cleanup strategy, retopology | Topology and retopology | `references/topology-retopology.md` |
| Sculpting, high-poly detail, remesh, high-to-low production | Sculpt/high-poly | `references/sculpting-highpoly.md` |
| PBR, procedural nodes, toon shading, material diagnostics | Shading and materials | `references/materials.md` |
| Smooth/sharp normals, bevel highlights, toon ramp, outline | Shading recipes | `references/shading-recipes.md` |
| Render, lighting, camera, turntable | Lighting/render | `references/lighting-render.md` |
| Game engine target (Roblox, Unity, Unreal, Godot) | Game-ready + export | `references/game-ready-export.md`; add `references/uv-baking.md` for texture workflows |
| Slow viewport, heavy scene, crashes | Performance | `references/performance.md` |
| Something looks wrong | Troubleshooting | `references/troubleshooting.md` |
| Need triangle / texture / scale numbers | Budgets | `references/budgets.md` |
| Geometry construction from components, profiles, or lathed forms | Geometry engine | `references/geometry-engine.md` |
| Explicit mesh refinement, face inset/extrusion, booleans, bevels, normals, and modifier stacks | Mesh operations | `references/mesh-operations.md`, `scripts/mesh_operations.py` |
| Recessed panels, fasteners, and mechanical blockouts | Hard surface | `scripts/hard_surface_builder.py` |
| Editable dimension-driven Geometry Nodes object | Parametric geometry | `scripts/geometry_nodes_builder.py` |
| Organic rocks, trees, branches, and clustered foliage | Organic modeling | `scripts/organic_rock_builder.py`, `scripts/organic_tree_builder.py` |
| Parametric architecture, repeated modules, stairs, and arches | Modular modeling | `references/modular-modeling.md` |
| Module boundaries, semantic MCP capabilities, and evidence contracts | Architecture | `references/architecture.md`, `references/module-contracts.md` |
| Mapping different MCP tools to common functions | Capability discovery | `references/capability-mapping.md` |
| Decomposing complex objects and choosing modeling techniques | Modeling intelligence | `references/modeling-intelligence.md` |
| Visual inspection and localized corrections | Visual review | `references/visual-inspection.md`, `scripts/inspection_report.py`, `scripts/localized_correction.py` |
| Cross-agent support evidence | Agent compatibility | `references/agent-compatibility.md` |
| Store tested technique executions in the current .blend | Technique history | `scripts/technique_history.py` |
| Collect technical benchmark evidence | Benchmarking | `references/benchmarking.md`, `references/benchmark-prompts.md`, `scripts/benchmark_report.py` |
| Probe Blender-side API capabilities | Runtime capability probe | `scripts/capability_probe.py` |
| Repeatable asset and cross-agent evaluation | Benchmarking | `references/benchmarking.md` |
| Optimize game assets, mesh topology, draw overhead, LOD or Roblox performance | Game asset optimization | `references/game-asset-optimization.md` |
| Shared modeling standards, topology and operation selection | Modeling foundations | `references/modeling-foundations.md` |
| Professional agent quality and process | Production standards | `references/professional-modeling-standards.md`, `references/professional-agent-playbook.md` |
| Contextual technique selection and failure recovery | Decision framework | `references/modeling-decision-framework.md` |
| Reference-oriented chairs, props, architecture, characters and trees | Production recipes | `references/production-recipes.md` |
| Read-only evaluated geometry, solid orientation and explicit fit/ground checks | Professional geometry inspection | `scripts/inspect_geometry.py`, `references/inspection-policies.md` |
| Quality loop, visual review, contextual validation | Modeling QA | `references/modeling-quality-loop.md`; `references/quality-checklist.md` |

Always also follow sections 3 to 6 below. For shared topology and operation standards, load `references/modeling-foundations.md`; for cross-cutting visual review and reliable MCP iteration, load `references/modeling-quality-loop.md`. For game-ready material/UV/LOD/export work, load `references/p1-production-pipeline.md` alongside `references/materials.md` and `references/game-ready-export.md`.



## 2A. Required planning gate

Before substantial modeling, write a compact plan that identifies:

1. **Purpose and destination:** game engine, animation, still render, 3D printing, architecture, CAD, or another use.
2. **Visual direction:** reference, style, silhouette, material language, and intended viewing distance.
3. **Technical constraints:** Blender version, units/scale, topology needs, triangle and texture budgets when relevant, materials, UVs, performance, and export format.
4. **Selected workflow:** the modeling and look-development methods plus the reference modules needed. Choose freely between procedural modeling, direct mesh editing, sculpting, external/reference assets, or a hybrid approach based on task fit and available tools.
5. **Acceptance criteria:** how visual quality, technical validity, and delivery will be checked.

Do not turn this into a long essay. If the request is clear, infer sensible defaults, state important assumptions briefly, and proceed. Ask the user only when an ambiguity could materially change the result or when a critical, irreversible choice requires approval. Research relevant documentation or references when available if a method or API is uncertain; distinguish verified facts from assumptions.

After planning, inspect the scene and tools before modifying anything. Complete a primary-form blockout and inspect it before adding fine detail. For a complex task, divide execution into small stages with checkpoints. For a simple task, keep the plan proportionately short.

## 2B. Universal quality gate

Use `references/quality-checklist.md` for the common acceptance checklist, then add the relevant discipline-specific checks. Mark each check as **PASS**, **ISSUE**, **N/A**, or **NOT VERIFIED**. Never present an unverified check as passed. Interpret warnings in the context of the asset and target pipeline; a warning is not automatically a defect.

At delivery, fix high-impact defects when feasible. If the asset is usable but not excellent, deliver it with a concise, honest list of known issues and what was not verified rather than hiding defects or iterating indefinitely.

## 3. The core loop

```
PLAN   -> state target, budget, units, and the 3-6 build steps (1 short paragraph, no essay)
BLOCK  -> blockout with primitives at correct proportions; look (angles) BEFORE any detail
REFINE -> bevels, secondary forms, details; look (solid + wireframe)
UV     -> only if textured or exported to a game
MATERIAL -> PBR materials, named, shared where possible
OPTIMIZE -> for game assets, load references/game-asset-optimization.md; baseline, dry-run, backup, clean conservatively, inspect, compare
VALIDATE -> set explicit TARGETS in scripts/validate_asset.py (or select only intended meshes); fix each WARN or justify it; re-run
DELIVER -> save/export if asked; report facts
```

**Blockout gate:** do not add detail until the silhouette reads correctly from front, side and three-quarter views. Most bad models are wrong proportions, not missing detail. Follow `references/modeling-quality-loop.md` for the visual review and correction cycle.

## 4. How to call the MCP tools well

- `execute_blender_code`
  - Always `import bpy, bmesh, math` and `from mathutils import Vector, Matrix` as needed. State does not persist between calls except in the .blend itself, so re-fetch objects by name: `obj = bpy.data.objects["Name"]`.
  - Pass `user_prompt` = the user's own words, verbatim, on every call of the task.
  - Prefer `bpy.data` API and `bmesh` over `bpy.ops`. Operators depend on context (active object, mode, area) and may fail a `poll()` check. Use `bpy.context.temp_override(...)` only when the installed Blender version supports it; older versions require version-appropriate operator handling. If the version-specific override is uncertain, avoid the operator or test it in a small isolated step. Always check the result.
  - Wrap risky steps in `try/except` and print the exception, never let one failure hide the others.
  - Name everything meaningfully (`Chair_Leg_FL`, `MAT_Wood_Oak`). Never leave `Cube.001`.
  - Keep scripts idempotent: running twice must not duplicate objects. Check `bpy.data.objects.get(name)` first or clear your own collection first.
- `get_scene_info`: use `fields=["topology"]` for mesh health, `["weights"]` for rigs, `["ground"]` to catch floating objects, `["details","materials","modifiers"]` for budgets.
- `look`: use `mode="angles"` for models, `mode="camera"` for composition, `shading="wireframe"` for topology, `shading="xray"` for rigs and interior, `mode="frames"` for animation. Smaller `max_size` = cheaper. Use `target=[...]` to frame your asset only.
- `search_assets` / `import_asset`: prefer a real CC0 asset (polyhaven) for HDRIs and PBR textures instead of hand-building noise. For models, check the licence and face count before importing; after import, **always** fix scale (`target_size`), ground it, and look at it.
- `generate_3d`: costs the user money or quota. One call per unique object, duplicate for repeats, never loop it. Always clean up the result afterwards (scale, origin, ground, decimate if needed, materials renamed). Treat the output as a base mesh, not a final asset, if the target is a game.

## 5. Quality bar (what "good" means)

- **Proportions** match the reference or real-world dimensions (see `references/budgets.md` for common sizes).
- **Topology**: quads where it deforms or subdivides; tris are fine for static game meshes. Avoid n-gons on curved/deforming surfaces. Investigate non-manifold edges, loose geometry, zero-area faces, flipped normals and interior faces in context; open surfaces and foliage cards can legitimately have boundaries.
- **Edges catch light**: real objects have bevels. Add small bevels (0.5 to 2 percent of object size) on hard edges; use `harden_normals` or weighted normals to avoid shading artifacts.
- **Shading**: smooth where organic, flat where faceted, use auto-smooth / sharp edges by angle (30 degrees default). No shading artifacts on flat surfaces.
- **Origin and pivot** at a meaningful point (base center for props, hinge for doors, feet for characters).
- **Naming and organization**: collections per asset, clear names, no orphan data.
- **Materials**: few, named, reusable, PBR-correct values (see `references/materials.md`).
- **Silhouette first, detail second, texture third.**

## 6. Performance rules (agent side and Blender side)

Agent side (save time and tokens):
- Batch related edits in one call; don't call `look` after trivial steps.
- Use low `max_size` for checks. Frame with `target`.
- Don't print whole vertex lists; print counts and bounds.
- Don't regenerate things already correct; edit in place.

Blender side:
- Use instances (`obj.copy()` sharing `obj.data`) or linked duplicates for repeats, not unique copies.
- Use `bmesh` for bulk geometry edits, `foreach_set` for large arrays. Avoid per-vertex Python loops with `bpy.ops` inside.
- Disable heavy viewport modifiers (Subdivision level > 2, Array with high counts, Boolean with dense meshes) during iteration via `show_viewport = False`; keep render levels.
- Prefer EEVEE / Workbench for checks. Cycles only for final renders, with denoise and a sample cap.
- Reduce texture sizes to the budget; pack or save images explicitly.
- Avoid global orphan purges during routine cleanup; remove only datablocks created by the current operation and only after confirming they have no users.
- Details in `references/performance.md`.

## 7. Ready-made scripts

Run them by pasting their contents into `execute_blender_code` (they only use bpy/bmesh and print a report). They live in `scripts/`:

| Script | Use |
|---|---|
| `geometry_builder.py` | Declarative construction of named primitives, beams, extruded, lathed, and lofted profiles in a dedicated collection. Creates new objects only; inspect and refine the result |
| `organic_rock_builder.py` | Deterministic stylized rock base mesh from an icosphere with seeded smooth deformation and optional flattened base. Creates a new owned object only |
| `modular_builder.py` | Parametric staircase and masonry arch blockouts with explicit dimensions, named parts, and rollback of partial staircase creation |
| `mesh_operations.py` | Duplicate-first, non-destructive bevel, normals, solidify, triangulate, decimate, mirror, subdivision, and boolean modifier pipeline |
| `hard_surface_builder.py` | Recessed mechanical panel with boolean pocket and four oriented fasteners |
| `geometry_nodes_builder.py` | Editable repeated post array with Count, Spacing, Height, and Radius inputs (requires Geometry Nodes support) |
| `organic_tree_builder.py` | Seeded stylized tree with tapered trunk, branches, and icosphere canopy clusters |
| `inspect_geometry.py` | Read-only evaluated mesh inspection with optional explicit solid, shell, dimensions, ground and relation policies; orientation and gaps are context-sensitive |
| `inspection_report.py` | Read-only technical report for explicit mesh targets; reports topology, bounds, modifiers, and materials |
| `localized_correction.py` | Apply explicit normals, merge-by-distance, scale-bake, bevel, and weighted-normal corrections to duplicates only |
| `technique_history.py` | Append a review-required execution record to a tagged Text datablock in the current .blend; does not save automatically |
| `technique_history_query.py` | Search stored technique/task records by text and return the newest matches |
| `technique_feedback.py` | Attach explicit pass/issue/not-reviewed feedback and a 0–4 score to one history record |
| `capability_probe.py` | Read-only Blender version/API capability report; visual capture remains an MCP-client capability |
| `benchmark_report.py` | Machine-readable technical benchmark metrics; visual scores remain NOT VERIFIED until actual review |
| `optimize_mesh.py` | Dry-run-first, backup-first conservative mesh cleanup; optional balanced dissolve and non-destructive Decimate preview |
| `validate_asset.py` | Read-only report with base/evaluated topology, modifiers, shape keys, UVs, materials, images and target status. Empty TARGETS checks selected meshes only; no scene-wide fallback |
| `validate_uvs.py` | Read-only UV bounds and zero-area diagnostics for explicit targets or selected meshes; does not claim overlap/stretch validation |
| `setup_scene.py` | Clean working collection, metric units, sane clip range, optional studio lighting |
| `cleanup_mesh.py` | Remove doubles, loose geometry, degenerate faces, recalc normals, optional tri/quads conversion |
| `apply_and_origin.py` | Apply transforms, set origin (bottom center / center / custom), ground the object |
| `bevel_and_shade.py` | Bevel hard edges + weighted normals + sharp by angle |
| `make_lods.py` | Generate LOD copies with Decimate and report tri counts |
| `pbr_material.py` | Create a clean Principled BSDF material from simple parameters |
| `export_asset.py` | Export FBX / glTF / OBJ with safe settings for game engines |

Edit the config block at the top of each script (clearly marked) instead of rewriting logic. For geometry construction, load `references/geometry-engine.md`; for module boundaries and capability contracts, load `references/architecture.md` and `references/module-contracts.md`. For cross-agent validation, load `references/agent-compatibility.md`.

## 8. Delivery format

Finish with a short report: what was built, relevant dimensions and triangle count, material/texture details when relevant, validation status, export path if applicable, known defects, and checks not performed. Use measured values only when actually retrieved; do not assume all assets use meters or triangle budgets. Deliver a good usable result when appropriate, but clearly disclose remaining defects instead of claiming perfection.

## 9. Asking the user

Ask only when an ambiguity materially changes the result or a critical decision needs the user's approval. Otherwise choose reasonable defaults, state consequential assumptions briefly, and continue. Avoid repeated questions for information already provided.

## 10. Safety

- Don't overwrite or delete the user's data. If you must change something that existed before you started, say so.
- Before bulk deletes, apply operations or file overwrites, confirm the list of affected objects in the output.
- **Policy for every destructive or bulk operation** (cleanup, apply transforms, origin changes, material assignment, decimate, export, purge):
  1. Identify the exact target objects and print their names.
  2. Detect dependencies first: shape keys, child objects, shared mesh data (several users), existing materials and slots, modifiers, armatures, objects in Edit Mode.
  3. Predict the impact (counts, names, what would move or change) before running.
  4. If the operation is not safe for a target, skip that target and say why instead of forcing it. The bundled scripts do this and print `SKIP:` lines.
  5. Verify afterwards with measured numbers, and never run a global purge (`orphans_purge`) as routine cleanup.
- Save with a new name (`_v2`) instead of overwriting the user's .blend unless asked.
- Respect licences: record CC-BY credits for imported assets.
