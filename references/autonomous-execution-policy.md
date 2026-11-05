# Autonomous execution policy — v1.3.0

This is a **decision policy for agents**, not a new Blender-control API. A connected MCP and the client's permissions determine actual execution capability.

## Decision tiers

| Tier | Examples | Agent behavior |
| --- | --- | --- |
| AUTO / read-only | Discover scene, tool schemas and version; inspect named objects; calculate budgets; capture safe views | Proceed, record observations, avoid duplicate discovery |
| AUTO / reversible owned edits | Create new objects in the explicitly owned collection, adjust a newly created duplicate, non-destructive modifiers on owned copies | Proceed after the new-project design interview, checkpoint and plan; verify at meaningful gates |
| ASK / consequential | Modify existing unowned objects, apply destructive modifiers, overwrite files, purge data, change global scene/render settings affecting other assets, paid operations or external publishing | Stop and ask for the specific decision; no blanket permission |
| STOP / unsafe or unclear | MCP returns unknown target, unexpected scene change, failed baseline, post-crash unsaved-scene uncertainty, unavailable required checkpoint | Do not retry mutation; inspect or recover read-only and escalate |

A user explicitly requesting an edit is **not** permission to alter unrelated objects. A general "work autonomously" instruction never overrides the ASK/STOP tiers. Do not make arbitrary assumptions about budget, target engine or artistic reference if these would materially change the result.

## State ledger (keep short, session-local)

Maintain the following facts internally or in an owned, non-destructive project note:

- Brief ID; whether GENERAL KICKOFF was already completed; answered requirements and delegated defaults
- Blender and Blender-control MCP versions and schema discovery fingerprint
- Source scene checkpoint path/identity and protected-object baseline status (never fabricate)
- Owned collection/object identifiers, target output path and destination
- Current stage, last verified observation, unresolved ISSUE / NOT VERIFIED and next action
- Attempt count for a specific failure and exact evidence for a changed plan

Do not assume this ledger persists across agents or restarts. Re-read the minimum necessary evidence when identity is uncertain; never treat the agent's memory as proof of scene preservation.

## Execution loop

1. **Clarify only missing design choices on a new project** (normally 2–3 simple / 4–6 complex questions). If all choices are explicitly delegated, document editable defaults and proceed; never ask a generic permission question.
2. **Discover once, invalidate when needed.** Inspect available tool schemas, Blender version, active scene and object ownership. Re-discover after reconnect, change of client/MCP/version, a schema error or evidence of scene replacement.
3. **Plan one measurable milestone.** Define affected owned objects, changes, acceptance checks and rollback/checkpoint. Separate technical evidence from image-based judgement.
4. **Execute a small bounded operation.** A single logical mutation per step, unless a safely reversible operation requires an atomic group. Never chain a blind series of destructive operations to save tokens.
5. **Validate after meaningful changes.** Inspect proportions and evaluated mesh after blockout; real views for visual quality; export and destination check for destination claims. If no real images or engine import, say NOT VERIFIED.
6. **Handle failures deliberately.** For transient tool failures, make at most one non-mutating retry after verifying scene identity. For a failed mutation, do not replay until the object state and checkpoint are checked. After two failed correction approaches, change technique or ask for a critical missing input.
7. **Deliver with evidence.** PASS / ISSUE / N/A / NOT VERIFIED for technical, visual and destination results, measured budgets, output path actually confirmed, and any unverified capability.

## Avoid redundant work without skipping proof

- Reuse answers from the current brief; do not interview again on corrections or follow-ups.
- Route to relevant guides only; use bounded read-only reference excerpts.
- Cache schema discovery only while session identity remains stable.
- Prefer existing inspection scripts over copying long logs; read the *entire* mutating script before execution.
- Batch related read-only observations when tool semantics permit; keep scene mutations bounded and reversible.
- Trigger visual inspection at major checkpoints, not on unchanged frames.
- Never optimize by suppressing an incident, bypassing safeguards, or declaring a quality PASS without evidence.

## Failure injection / manual acceptance

Exercise these cases in a saved scratch scene:

1. New complex asset → targeted interview once; no repeat after an answer.
2. User delegates every artistic choice → editable defaults, no unnecessary questions.
3. User requests change to owned copy → edit with checkpoint and recheck.
4. User requests destructive edit of protected source → ASK with exact object and risk.
5. MCP timeout after potentially successful mutation → inspect scene identity and objects before deciding whether retry is safe.
6. Blender crash with unsaved scene → STOP; never infer recovery from default objects.
7. Blender-control MCP schema changes mid-session → discard cached schema and re-discover.
8. No visual capture/real engine importer → technical measurements may PASS, visual/engine remain NOT VERIFIED.

**Evidence status:** Policy cases above are acceptance scenarios, not results of live agent testing. See `docs/AGENT-1.3-EVALUATION.md`.
