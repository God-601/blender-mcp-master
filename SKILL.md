---
name: blender-mcp-master
description: Use for planning, creating, editing, inspecting, texturing, rigging, optimizing or exporting 3D assets through Blender and a connected Blender-control MCP. Handles hard-surface, organic, low-poly, architecture, characters, materials/UV and game-ready delivery; prioritizes preserved scenes, design clarification and evidence-backed checks.
---

# Blender MCP Master

Live edits require a separate Blender-control MCP. Run bpy in a compatible Blender runtime. The optional resource MCP serves documentation and scripts.

## Non-negotiable gates

1. **Clarify before you build.** Use a GENERAL KICKOFF multi-question design interview when multiple consequential choices are unresolved. Wait for necessary answers before edits. Ask zero questions when the brief resolves the meaningful choices or delegates them. **Do not repeat answered requirements.** Skip “posso seguir?” and reuse the brief on follow-ups. For question selection, use `references/clarification-gate.md`.
2. **Protect the scene.** Discover actual tool schemas, Blender version, objects and ownership. Before edits, verify scene identity and the saved checkpoint and record a protected-scene baseline. Never alter unrelated/protected objects. Request approval for destructive edits, global changes, overwrites or paid actions. STOP if recovery or scene identity is uncertain. For ownership or recovery details, consult `references/p0-integrity.md` or `references/crash-recovery-and-baselines.md` as needed.
3. **Plan to the destination.** Define silhouette, proportions, owned collection, technique, units, evaluated triangle/material/texture budgets, reference and acceptance evidence. Do not invent engine limits.
4. **Edit reversibly.** Use named targets and owned/duplicated geometry. Avoid scene-wide fallback, shared-mesh surprises, blind booleans and unsafe cleanup. **Avoid global orphan purges.** Proceed with scoped read-only or reversible owned work. For permission tiers or retry handling, consult `references/autonomous-execution-policy.md`.
5. **Inspect at meaningful gates.** Check blockout silhouette and proportions before detail. Inspect actual front, side and three-quarter model captures after substantial shape or shading changes. Without inspected model captures, visual quality is **NOT VERIFIED**. When the user supplies reference images, compare their visible landmarks with the model captures. See `references/multimodal-reference-review.md` for reference comparison, `references/visual-inspection.md` for capture guidance or `references/modeling-quality-loop.md` for iterative review.
6. **Prove technical facts.** Inspect evaluated geometry, intended fit, normals, UVs, shading and export budgets with scoped scripts. AABB/BVH and convex-hull silhouette checks provide evidence for review. Exact penetration and artistic quality require their own evidence. Compare the protected-scene baseline after edits.
7. **Correct with evidence.** Record defect → source/view → hypothesis → minimal owned correction → same check. After two ineffective attempts change method rather than looping.
8. **Report truthfully.** Technical, visual and export results use **PASS / ISSUE / N/A / NOT VERIFIED**, with actual observations and paths. Engine claims require an actual destination import. Consult `references/quality-checklist.md` when defining additional acceptance checks.

## Fast execution route

```text
CLARIFY -> PROBE -> PLAN -> BLOCK -> LOOK -> REFINE -> VERIFY -> CORRECT -> DELIVER
```

**Minimal load:** apply the gates above and start with **one** primary discipline guide. Gate links and the last column are lookups. Read only the section your task needs. For complex decisions, consult `references/modeling-decision-framework.md`, `references/evidence-first-workflow.md` or `references/workflow-director.md` as applicable. For session optimization, see `references/token-efficient-agent-execution.md`.

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

A/B experiments: `references/skill-evaluation-protocol.md`. Visual correction evidence: `scripts/visual_iteration_gate.py`. Five-fixture plan: `docs/V2-ACCEPTANCE-CAMPAIGN.md`.

For advisory routing, use `python scripts/workflow_router.py brief.json` or `plan_blender_workflow` if the optional resource MCP exposes it. The route suggests relevant guides and missing brief topics. Resolve consequential gaps and probe the live scene before execution. For complex joints, see `scripts/solid_overlap_probe.py`. For real Godot GLB import testing, see `integrations/godot/README.md`.

**Context-saving behavior:** reuse discovery while session identity is stable. Prefer bounded summaries and scoped read-only batches. For excerpts, use local file reads or the optional resource MCP's `get_blender_reference_outline` and `get_blender_reference_excerpt`. Inspect the full mutating script before execution. If supported, run the inspected, pinned script by reference with explicit arguments. Keep mutations small and retain required safety and evidence.

**Common read-only helpers:** `scripts/inspect_geometry.py`, `scripts/asset_performance_audit.py`, `scripts/validate_asset.py`, `scripts/validate_uvs.py` and `scripts/inspect_component_fit.py`. Supply explicit named targets for scene checks. For other diagnostics and how to run them, use the resource catalog below.

## Delivery receipt

Delegation: `references/specialist-orchestration.md`.

```text
Asset / Blender + MCP versions / destination:
Original objects preserved / owned changes:
Measured geometry, UV/materials and budgets:
Actual inspected image views:
Technical | Visual | Engine: PASS / ISSUE / N/A / NOT VERIFIED
Confirmed output paths, open defects and uncertainty:
```

For less common guides and Python scripts, consult `references/resource-catalog.md` **only when needed**, or use `list_blender_resources` from the optional MCP resource server. Do not preload the catalog.
