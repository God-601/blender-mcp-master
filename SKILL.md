---
name: blender-mcp-master
description: Use when an agent plans, creates, inspects, textures, shades, lights, rigs, optimizes, validates, or exports any kind of 3D asset in Blender through MCP. Covers hard-surface, organic, characters, hand-painted, stylized/fantasy, low-poly/retro, PBR/procedural/toon materials, environments, architecture, CAD, sculpting, UVs/baking, retopology, game-ready assets, LODs, and rendering. Requires task-first planning, evidence-based quality checks, safe scene edits, and transparent delivery.
---

# Blender MCP Master

A portable Agent Skill for AI-driven Blender modeling. It is **not a Blender-control MCP server or addon**. To modify a live Blender scene, connect an independent Blender-control MCP. The optional MCP resource server in this repo serves read-only documentation and script templates. Scripts using `bpy` run inside a compatible Blender runtime, not generic host Python.

## Core rules — always apply

1. **Clarify before you build.** New-project GENERAL KICKOFF is mandatory; read `references/clarification-gate.md` before changing the scene.
2. **Protect existing work.** Discover objects, mesh owners, settings, actual tool schemas and Blender version. Edit explicitly named targets in an owned collection; preserve all unrelated user objects. Follow `references/p0-integrity.md`.
3. **Plan by destination.** State asset purpose, visual reference, scale/units, component structure, technical constraints, triangle/material/texture budgets and how quality will be verified. Do not invent platform limits.
4. **Small reversible operations.** Prefer duplicate-first mesh edits and modifiers, a single logical code operation per step, and concise actual observations. Ask permission for destructive/in-place edits, overwrites and paid operations.
5. **Visual checkpoints.** Inspect actual front/side/three-quarter views after blockout and major geometry or material changes; no visual tool means visual quality is NOT VERIFIED.
6. **Measured technical checks.** Validate evaluated geometry, UVs, object contact, material assignments and budgets for the real destination. No broad scene-wide fallback on missing targets.
7. **Diagnose defects first.** Capture actual evidence, isolate the cause, fix only the affected owned copy, recheck original and nearby geometry. After two failed attempts, change method or seek a critical reference.
8. **Honest delivery.** State PASS / ISSUE / N/A / NOT VERIFIED for relevant acceptance criteria, exact file paths actually confirmed, measured results and remaining limitations. A passing Python test is not a professional art-quality certificate.

**Avoid global orphan purges.** Do not globally delete objects, overwrite user files or apply modifiers to someone else's mesh. Use `references/professional-modeling-standards.md` and `references/quality-checklist.md` for substantial assets. Distinguish real image evidence from mere geometry metrics.

### GENERAL KICKOFF — one question on each NEW project

Summarize all known information and ask **one general open-ended question** about desired look or final priorities **even when the technical brief is complete**. Allow "pode seguir" to continue. **do not repeat answered requirements**; combine essential blockers into the first question when practical. Await the answer before scene mutations. Read-only discovery may happen while waiting. **Do not restart the interview** when continuing an existing project, refining an asset or recovering from tool errors.

## Core workflow

~~~text
CLARIFY -> GENERAL KICKOFF, blockers, priorities and reference
PROBE   -> MCP tool/schema discovery; Blender version, units and existing scene
PLAN    -> task-specific technique, owner collection, budget and acceptance
BLOCK   -> named primary parts, accurate proportions, grounded geometry
LOOK    -> actual views; front/side/three-quarter and reference comparison
REFINE  -> reversible operations, measured data, targeted detail
DELIVER -> UV/material/lighting/LOD/export only where relevant
VERIFY  -> technical + visual + destination evidence, source protection
CORRECT -> one minimal change, same check repeated; then report
~~~

For nontrivial assets read `references/modeling-quality-loop.md`, `references/modeling-decision-framework.md`, `references/evidence-first-workflow.md`. A simple prop needs only a concise plan; a complex multi-specialist project also loads `references/workflow-director.md`. Never claim a visual PASS without actual inspected images, nor an engine PASS without a real importer/test.

## Route by task — load only relevant files

| Work | Load on demand |
| --- | --- |
| Hard-surface props or measured vehicles | `references/hard-surface.md`, `references/mesh-operations.md`, `references/measured-proportion-recipes.md` |
| Characters and animation | `references/character-rig.md`, `references/topology-retopology.md` |
| Guided retopology edits | `references/advanced-retopology.md`, `scripts/retopology_advanced.py` |
| Organic, sculpt, trees and rocks | `references/organic.md`, `references/sculpting-highpoly.md` |
| Low-poly, voxel, hand-painted | `references/stylized-lowpoly.md`, `references/voxel-atlas-recipe.md`, `references/hand-painted-pipeline.md` |
| Architecture, CAD and modular scenes | `references/architecture-interiors.md`, `references/cad-technical.md`, `references/modular-modeling.md` |
| Geometry Nodes and procedural generation | `references/geometry-engine.md`, `references/parametric-geometry-nodes.md` |
| UV, textures, baking, materials | `references/uv-baking.md`, `references/materials.md`, `references/shading-recipes.md` |
| Game asset optimization and export | `references/game-asset-optimization.md`, `references/p1-production-pipeline.md`, `references/game-ready-export.md` |
| Measured 3D geometry/material/texture cost | `references/model-performance-strategy.md`, `scripts/asset_performance_audit.py` |
| Token/context and tool efficiency | `references/token-efficient-agent-execution.md` |
| Version-dependent Blender API or MCP mismatch | `references/official-blender-documentation.md`, `references/capability-mapping.md` |
| Local reusable records / reviewers | `references/technique-registry.md`, `scripts/technique_registry.py`, `scripts/visual_review_report.py` |

**Tool-first:** Prefer the connected Blender MCP's structured tools and the agent's native file-search/read/edit tools over generic Bash when available. Bash is valid if it better serves a reproducible task. The optional read-only resource MCP supports `get_blender_reference_outline` and `get_blender_reference_excerpt` to fetch small source-backed sections; use full-document reads only when actually necessary. Always inspect the whole script and safety configuration before executing a mutating Blender script. Save concise checkpoints rather than repeating logs. Do not trade away safety or the mandatory kickoff for fewer tokens.

Use `scripts/inspect_geometry.py`, `scripts/validate_asset.py`, `scripts/validate_uvs.py` for read-only checks. Note that material slots are not exact draw calls; texture dimensions do not prove VRAM and Blender audits do not measure game FPS. Guided retopology is not a universal automatic quad remesher. The visual review receipt is not an image classifier. Cross-agent compatibility, artistic quality and performance improvements must have real test evidence: `references/benchmarking.md`, `references/benchmark-prompts.md`, `references/skill-evaluation-protocol.md`.

## Delivery template

~~~text
Asset, destination, Blender + MCP versions:
Objects created or edited / originals preserved:
Measured dimensions, evaluated triangles, material/UV facts:
Screenshot views actually inspected:
Technical quality: PASS / ISSUE / N/A / NOT VERIFIED
Visual quality: PASS / ISSUE / N/A / NOT VERIFIED
Engine/export: PASS / ISSUE / N/A / NOT VERIFIED
Actual output files and paths:
Known defects and unresolved verification:
~~~

## Full path index — discover, do NOT load everything

Select a guide by the route above. The names below make scripts and specialist manuals discoverable even when not used in the current task.


### Additional references

`references/advanced-retopology.md` · `references/agent-compatibility.md` · `references/architecture-interiors.md` · `references/architecture.md`

`references/benchmark-prompts.md` · `references/benchmarking.md` · `references/budgets.md` · `references/cad-technical.md`

`references/capability-mapping.md` · `references/character-rig.md` · `references/clarification-gate.md` · `references/environment.md`

`references/evidence-first-workflow.md` · `references/game-asset-optimization.md` · `references/game-ready-export.md` · `references/geometry-engine.md`

`references/hand-painted-pipeline.md` · `references/handpaint-recipes.md` · `references/hard-surface.md` · `references/inspection-policies.md`

`references/lighting-render.md` · `references/materials.md` · `references/measured-proportion-recipes.md` · `references/mesh-operations.md`

`references/model-performance-strategy.md` · `references/modeling-decision-framework.md` · `references/modeling-foundations.md` · `references/modeling-intelligence.md`

`references/modeling-quality-loop.md` · `references/modular-modeling.md` · `references/module-contracts.md` · `references/mutation-testing.md`

`references/official-blender-documentation.md` · `references/organic.md` · `references/p0-integrity.md` · `references/p1-production-pipeline.md`

`references/parametric-geometry-nodes.md` · `references/performance.md` · `references/production-recipes.md` · `references/professional-agent-playbook.md`

`references/professional-modeling-standards.md` · `references/quality-checklist.md` · `references/sculpting-highpoly.md` · `references/shading-recipes.md`

`references/skill-evaluation-protocol.md` · `references/stylized-lowpoly.md` · `references/technique-registry.md` · `references/token-efficient-agent-execution.md`

`references/topology-retopology.md` · `references/troubleshooting.md` · `references/uv-baking.md` · `references/visual-inspection.md`

`references/voxel-atlas-recipe.md` · `references/workflow-director.md`

### Available scripts (Blender bpy unless documented otherwise)

`scripts/agent_efficiency_compare.py` — pure-Python read-only comparison of matching run metrics; no billed-token or artistic-quality claims without source evidence.

`scripts/apply_and_origin.py` · `scripts/asset_performance_audit.py` · `scripts/benchmark_report.py` · `scripts/bevel_and_shade.py`

`scripts/capability_probe.py` · `scripts/cleanup_mesh.py` · `scripts/export_asset.py` · `scripts/geometry_builder.py`

`scripts/geometry_nodes_builder.py` · `scripts/hard_surface_builder.py` · `scripts/inspect_geometry.py` · `scripts/inspection_report.py`

`scripts/localized_correction.py` · `scripts/make_lods.py` · `scripts/mesh_operations.py` · `scripts/modular_builder.py`

`scripts/optimize_mesh.py` · `scripts/organic_rock_builder.py` · `scripts/organic_tree_builder.py` · `scripts/pbr_material.py`

`scripts/prop_proportion_example.py` · `scripts/retopology_advanced.py` · `scripts/setup_scene.py` · `scripts/technique_feedback.py`

`scripts/technique_history.py` · `scripts/technique_history_query.py` · `scripts/technique_registry.py` · `scripts/validate_asset.py`

`scripts/validate_uvs.py` · `scripts/vehicle_proportion_example.py` · `scripts/visual_review_report.py` · `scripts/voxel_atlas_example.py`

Release gates are tracked in `docs/ROADMAP-1.0.md`. Installed skills, code execution and CI alone cannot prove live Blender MCP connectivity or final artistic quality.
