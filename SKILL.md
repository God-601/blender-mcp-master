---
name: blender-mcp-master
description: Use for planning, creating, editing, inspecting, texturing, rigging, optimizing or exporting 3D assets through Blender and a connected Blender-control MCP. Handles hard-surface, organic, low-poly, architecture, characters, materials/UV and game-ready delivery; prioritizes preserved scenes, design clarification and evidence-backed checks.
---

# Blender MCP Master

Agent Skill for Blender workflows; **not** a Blender-control MCP server. Execute bpy only in a compatible Blender runtime. The optional MCP resource server is read-only. **Load task-specific guides on demand**, not the whole index.

## Non-negotiable gates

1. **Clarify before you build.** Use the GENERAL KICKOFF **multi-question design interview** once for new projects: ask several meaningful, nonredundant questions; 2–3 relevant questions for a simple prop, typically 4–6 for complex assets, about genuinely unknown appearance, reference, shape, materials, use and technical constraints. **Do not repeat answered requirements.** Honor explicitly delegated artistic choices and never replace design questions with “posso seguir?” / “may I proceed?”. See `references/clarification-gate.md`.
2. **Protect the scene.** Inspect actual tool schemas, Blender version, existing objects, scene ownership and checkpoint identity before scene edits. Never alter unrelated/protected objects. Request approval for destructive edits, global changes, overwrites or paid actions. If recovery after a crash is uncertain, STOP. See `references/p0-integrity.md` and `references/crash-recovery-and-baselines.md`.
3. **Plan to the destination.** Define silhouette, proportions, owned collection, technique, units, evaluated triangle/material/texture budgets, reference and acceptance evidence. Do not invent engine limits.
4. **Edit reversibly.** Use named targets and owned/duplicated geometry; avoid scene-wide fallback, shared-mesh surprises, blind booleans and unsafe cleanup. **Avoid global orphan purges.** Follow `references/autonomous-execution-policy.md`: AUTO for read-only/reversible owned work, ASK for consequential or unowned edits, STOP when scene identity is uncertain.
5. **Inspect at meaningful gates.** Check blockout silhouette and proportions before detail; inspect actual front, side, three-quarter views after substantial shape/shading changes. When user reference images exist, compare their visible landmarks against actual captured model views using `references/multimodal-reference-review.md`; no images means visual result NOT VERIFIED. Use `references/modeling-quality-loop.md` and `references/visual-inspection.md`.
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

For measured A/B experiments use `references/skill-evaluation-protocol.md`; defer test procedures unless running a benchmark.

For a selected task, if the optional resource MCP exposes `plan_blender_workflow`, call it once to select the smallest relevant guides and missing brief topics; it does not replace the design conversation or live scene probing. For complex geometric joints load `scripts/solid_overlap_probe.py` only when needed; BVH/ray results are REVIEW, not automatic collision certification. For real Godot GLB import testing see `integrations/godot/README.md`.

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

For less common guides and Python scripts, consult `references/resource-catalog.md` **only when needed**, or use `list_blender_resources` from the optional MCP resource server. Do not preload the catalog.
