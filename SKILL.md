---
name: blender-mcp-master
description: Use for planning, creating, editing, inspecting, texturing, rigging, optimizing or exporting 3D assets through Blender and a connected Blender-control MCP. Handles hard-surface, organic, low-poly, architecture, characters, materials/UV and game-ready delivery; prioritizes preserved scenes, design clarification and evidence-backed checks.
---

# Blender MCP Master

Agent Skill for Blender workflows; **not** a Blender-control MCP server. Execute bpy only in a compatible Blender runtime. The optional MCP resource server is read-only. **Load task-specific guides on demand**, not the whole index.

## Non-negotiable gates

1. **Clarify before you build.** Use the GENERAL KICKOFF **multi-question design interview** once for new projects: 2–3 relevant questions for a simple prop, typically 4–6 for complex assets, about genuinely unknown appearance, reference, shape, materials, use and technical constraints. **Do not repeat answered requirements.** Honor explicitly delegated artistic choices and never replace design questions with “may I proceed?”. See `references/clarification-gate.md`.
2. **Protect the scene.** Inspect actual tool schemas, Blender version, existing objects, scene ownership and checkpoint identity before scene edits. Never alter unrelated/protected objects. Request approval for destructive edits, global changes, overwrites or paid actions. If recovery after a crash is uncertain, STOP. See `references/p0-integrity.md` and `references/crash-recovery-and-baselines.md`.
3. **Plan to the destination.** Define silhouette, proportions, owned collection, technique, units, evaluated triangle/material/texture budgets, reference and acceptance evidence. Do not invent engine limits.
4. **Edit reversibly.** Use named targets and owned/duplicated geometry; avoid scene-wide fallback, shared-mesh surprises, blind booleans and unsafe cleanup. **Avoid global orphan purges.** Follow `references/autonomous-execution-policy.md`: AUTO for read-only/reversible owned work, ASK for consequential or unowned edits, STOP when scene identity is uncertain.
5. **Inspect at meaningful gates.** Check blockout silhouette and proportions before detail; inspect actual front, side, three-quarter views after substantial shape/shading changes. No images means visual result NOT VERIFIED. Use `references/modeling-quality-loop.md` and `references/visual-inspection.md`.
6. **Prove technical facts.** Inspect evaluated geometry, real intended fit, normals, UV, shading and export budgets with scoped scripts. AABB/BVH candidate is not proof of exact penetration; convex-hull silhouette proxies are not artistic PASS. Review scene integrity after edits.
7. **Correct with evidence.** Record defect → source/view → hypothesis → minimal owned correction → same check. After two ineffective attempts change method rather than looping.
8. **Report truthfully.** Technical/visual/export: **PASS / ISSUE / N/A / NOT VERIFIED**, supported by actual observations and paths. Blender round-trip is not real engine import. See `references/quality-checklist.md`.

## Fast execution route

```text
CLARIFY -> PROBE -> PLAN -> BLOCK -> LOOK -> REFINE -> VERIFY -> CORRECT -> DELIVER
```

**Minimal load:** read `SKILL.md` once; use **one** primary discipline guide and the smallest relevant safety or inspection excerpt. For complex assets, add `references/modeling-decision-framework.md`, `references/evidence-first-workflow.md` or `references/workflow-director.md` **only when that choice is needed**, not automatically together. Read `references/token-efficient-agent-execution.md` when optimizing an agent/session.

| Task | First guide | Add only if necessary |
| --- | --- | --- |
| Measured props / machinery | `references/hard-surface.md` | `references/measured-proportion-recipes.md` |
| Organic / vegetation | `references/organic.md` | `references/sculpting-highpoly.md` |
| Stylized / voxel | `references/stylized-lowpoly.md` | `references/voxel-atlas-recipe.md` |
| Architecture / modular | `references/modular-modeling.md` | `references/architecture-interiors.md` |
| Character / deformation | `references/character-rig.md` | `references/advanced-retopology.md` |
| UV / materials | `references/uv-baking.md` | `references/materials.md` |
| Game optimization / export | `references/game-ready-export.md` | `references/model-performance-strategy.md` |
| Bug / unknown API | `references/troubleshooting.md` | `references/capability-mapping.md` |

**Context-saving behavior:** discover MCP capabilities once while session identity remains stable. Prefer native tool responses, bounded summaries, read-only batching and targeted excerpts (`get_blender_reference_outline` / `get_blender_reference_excerpt`) over full-document reads. Reuse already-read state and answers. Do not resend long script bodies when the active MCP supports running an inspected, pinned script by reference with explicit arguments; otherwise inspect the full mutating script before execution. Keep mutation scopes small. Never skip safety/evidence to save tokens.

**Read-only core:** `scripts/inspect_geometry.py`, `scripts/asset_performance_audit.py`, `scripts/validate_asset.py`, `scripts/validate_uvs.py`, `scripts/inspect_component_fit.py`, `scripts/modeling_scorecard.py` (evidence-only), `scripts/reference_silhouette_compare.py` (real RGBA PNG alpha-mask IoU; not artistic PASS), and `scripts/workflow_router.py` (pure-Python advisory routing).

## Delivery receipt

```text
Asset / Blender + MCP versions / destination:
Original objects preserved / owned changes:
Measured geometry, UV/materials and budgets:
Actual inspected image views:
Technical | Visual | Engine: PASS / ISSUE / N/A / NOT VERIFIED
Confirmed output paths, open defects and uncertainty:
```

## Lazy index — names only; do not read unless routed

### References

`references/advanced-retopology.md` · `references/agent-compatibility.md` · `references/architecture-interiors.md` · `references/architecture.md` · `references/autonomous-execution-policy.md` · `references/benchmark-prompts.md` · `references/benchmarking.md` · `references/budgets.md` · `references/cad-technical.md` · `references/capability-mapping.md` · `references/character-rig.md` · `references/clarification-gate.md` · `references/clean-editable-topology.md` · `references/component-fit-and-joints.md` · `references/crash-recovery-and-baselines.md` · `references/environment.md` · `references/evidence-first-workflow.md` · `references/game-asset-optimization.md` · `references/game-ready-export.md` · `references/geometry-engine.md` · `references/hand-painted-pipeline.md` · `references/handpaint-recipes.md` · `references/hard-surface.md` · `references/inspection-policies.md` · `references/lighting-render.md` · `references/manual-acceptance-prompts.md` · `references/materials.md` · `references/measured-proportion-recipes.md` · `references/mesh-operations.md` · `references/model-performance-strategy.md` · `references/modeling-decision-framework.md` · `references/modeling-foundations.md` · `references/modeling-intelligence.md` · `references/modeling-quality-loop.md` · `references/modular-modeling.md` · `references/module-contracts.md` · `references/mutation-testing.md` · `references/official-blender-documentation.md` · `references/organic.md` · `references/p0-integrity.md` · `references/p1-production-pipeline.md` · `references/parametric-geometry-nodes.md` · `references/performance.md` · `references/production-recipes.md` · `references/professional-agent-playbook.md` · `references/professional-modeling-standards.md` · `references/quality-checklist.md` · `references/sculpting-highpoly.md` · `references/shading-recipes.md` · `references/skill-evaluation-protocol.md` · `references/stylized-lowpoly.md` · `references/technique-registry.md` · `references/token-efficient-agent-execution.md` · `references/topology-retopology.md` · `references/troubleshooting.md` · `references/uv-baking.md` · `references/visual-inspection.md` · `references/voxel-atlas-recipe.md` · `references/workflow-director.md`

### Scripts

`scripts/agent_efficiency_compare.py` · `scripts/apply_and_origin.py` · `scripts/asset_performance_audit.py` · `scripts/benchmark_report.py` · `scripts/bevel_and_shade.py` · `scripts/capability_probe.py` · `scripts/clean_install_smoke.py` · `scripts/cleanup_mesh.py` · `scripts/compare_asset_silhouettes.py` · `scripts/compare_scene_baselines.py` · `scripts/export_asset.py` · `scripts/game_asset_preflight.py` · `scripts/geometry_builder.py` · `scripts/geometry_nodes_builder.py` · `scripts/hard_surface_builder.py` · `scripts/inspect_component_fit.py` · `scripts/inspect_geometry.py` · `scripts/inspection_report.py` · `scripts/localized_correction.py` · `scripts/make_lods.py` · `scripts/mesh_operations.py` · `scripts/modeling_scorecard.py` · `scripts/modular_builder.py` · `scripts/optimize_mesh.py` · `scripts/organic_rock_builder.py` · `scripts/organic_tree_builder.py` · `scripts/pbr_material.py` · `scripts/prop_proportion_example.py` · `scripts/retopology_advanced.py` · `scripts/scene_baseline_snapshot.py` · `scripts/scene_recovery_probe.py` · `scripts/setup_scene.py` · `scripts/technique_feedback.py` · `scripts/technique_history.py` · `scripts/technique_history_query.py` · `scripts/technique_registry.py` · `scripts/topology_face_diagnostics.py` · `scripts/uv_diagnostics.py` · `scripts/uv_island_gutter_audit.py` · `scripts/validate_asset.py` · `scripts/validate_uvs.py` · `scripts/vehicle_proportion_example.py` · `scripts/visual_evidence_manifest.py` · `scripts/visual_review_report.py` · `scripts/voxel_atlas_example.py`

Additional v1.4 Python utilities: `scripts/workflow_router.py` · `scripts/reference_silhouette_compare.py`.
