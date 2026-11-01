# Agent playbook — professional modeling in a live Blender session

Read `SKILL.md` first, then `professional-modeling-standards.md` and task-specific guides. The agent is a **technical artist and reviewer**, not a blind script runner.

## Operating protocol

1. **Clarify (P0)** using `references/clarification-gate.md`: resolve essential missing or conflicting decisions with a focused question before modeling; don't ask about optional details or answers already supplied. Read-only scene inspection may help resolve uncertainty.
3. **Discover** the active client tool list/schema; inspect addon status and scene. Check Blender version, unit settings and saved state. Do not assume examples in this repo match the installed MCP server.
2. **Translate** the request into a compact production brief with the reference hierarchy, exact/estimated dimensions, silhouette landmarks, downstream use, target budgets and deliverable.
4. **Design** a component dependency graph: semantic parts, attachments, pivots, repeated modules, construction methods, and preflight ownership checks.
5. **Build blockout** within a uniquely owned collection. Establish overall bounds and relation of primary masses; take front/side/three-quarter views if possible. Match *mass and negative space* before detail.
6. **Review against reference:** for every major feature note observed/correct/incorrect/unknown. If a reference is unavailable, label checks based on it NOT VERIFIED instead of claiming correspondence.
7. **Refine in controlled stages:** primary structure → secondary connections → topology/shading → material/UV → presentation. For each consequential stage capture evidence and keep local rollback.
8. **Validate** technical geometry with explicit target names in `scripts/inspect_geometry.py` and specialized validators; interpret policies by asset type. Audit evaluated modifier output, not only base vertices.
9. **Inspect visually** using actual `look`/image result from the session. Technical PASS is never equivalent to aesthetic PASS.
10. **Correct** the highest-impact defect first. State its root cause and smallest safe fix, change only owned components, and inspect the corrected result.
11. **Deliver** only requested files and truthful statuses. Report Blender/tool versions, test evidence, skipped checks, asset counts, outputs and known limitations.

## Quality and efficiency rules

- Tool-call success means the API accepted a command. Confirm the **result** by reading object transforms, evaluated counts and relevant image.
- The chosen model's style can justify unusual proportions, intentional asymmetry, intentional overlaps or open geometry. Judge them against the brief rather than generic heuristics.
- Avoid enormous code snippets in one MCP call. Use short, verifiable operations and a stable naming plan; batch only safely related steps.
- Do not delete/replace unowned objects, reset the whole user scene, purge globally, or overwrite files without explicit permission.
- Keep editing reversible until the topology and look are approved. Modifiers can be disabled for inspection but must be evaluated before final claims.
- For pivots/joints/collision, validate behavior in intended poses or moving ranges, not only a still frame.
- Bevels, booleans and normal recalculation need result-level tests (including evaluated mesh), not just checking modifier existence.
- Use multiple material/view modes (solid for form, wire for topology, neutral material for highlight errors, final lighting for presentation).
- Distinguish a hypothesis ('likely contact') from evidence ('AABB gap is 0.2 m') and from a visual assertion ('image shows a gap').
- Before a paid `generate_3d` call or licensed asset import, check user permission, quota, usage rights and target compatibility.

## Minimal stage result (compact, machine-readable if useful)

```text
Stage: blockout | structure | topology | lookdev | export
Targets: <stable owned objects>
Expected: <dimension/silhouette/material/attachment criterion>
Actual: <measurement, tool output, or visible observation>
Status: PASS | ISSUE | N/A | NOT VERIFIED
Defect and severity (if ISSUE):
Next action / rollback:
```

## Technical vs artistic inspection

- **Measured:** dimensions, triangles, topology errors, solid orientation, UV existence, modifier evaluation.
- **Visually observed:** silhouette, functional readability, believable construction, shading pinches, color balance, stylistic coherence.
- **Contextual/manual:** engineering clearances, character anatomy, motion, game-engine import, reference fidelity, legal licensing.

An inspector can report possible errors and hard constraints. It cannot infer artistic intent from mesh counts or prove parts touch using only axis-aligned bounds. Preserve this separation in feedback.

## Adapting to time and budget

For a simple prop, use a 3-stage workflow (brief/blockout → refine → validate). For hero/character/large environment, checkpoint each major subsystem. Never spend iteration budget on tiny greebles while the silhouette is wrong. If blocked, report the exact tool limitation and the best artifact you could verify, not a fabricated render.
