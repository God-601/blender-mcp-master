# Evidence-first modeling workflow

**Inspiration:** [obra/superpowers](https://github.com/obra/superpowers) uses complementary skills for requirements discovery, small-step planning, isolated implementation, systematic debugging, review, and verification before declaring success. This document adapts those **methodological ideas** to 3D modeling; it does not embed Superpowers, use its code, or promise its agent hooks and subagent features.

Read with `professional-modeling-standards.md`, `modeling-quality-loop.md`, `p0-integrity.md` and the discipline guide chosen in `SKILL.md`.

## Why this is different from code development

| Superpowers pattern | Modeling adaptation | Explicit limit |
| --- | --- | --- |
| Clarify and plan before implementing | Record art direction, destination, proportions, reference image and acceptance criteria | Don't interrogate users whose briefs are complete |
| Isolated workspace / small changes | Dedicated owned collection, named objects, duplicate-first operation, staged blockout | A Blender scene is **not** a git worktree; protect all unrelated objects |
| Red/green tests | Define a failing measurable criterion, change a copy, rerun the exact check | No universal automated oracle for artistic quality |
| Review against spec, then quality | First compare silhouette and intended components; next inspect shading, topology, UV and export | A mesh script cannot certify beauty or engine behavior |
| Systematic debugging | Observe symptom → isolate cause → apply minimal correction → recheck for regressions | Avoid repeated speculative destructive edits |
| Verification before completion | Publish evidence and **NOT VERIFIED** items alongside any PASS | A successful tool call is not proof of a finished asset |
| Progressive disclosure | Load a small routing entrypoint, then only task-relevant references | Do not turn `SKILL.md` into a massive copied manual |

## Execution contract

### Gate 0 — Brief + scene preflight

- Identify required visual references and the intended use: static render, game, animation, architectural scale, or 3D print.
- Read the user's constraints already given; ask only for missing **BLOCKER** information or a truly consequential quality decision.
- Query actual Blender version, available MCP tools, units, scale, scene selection and pre-existing object ownership using **read-only** operations.
- Choose a task-specific asset budget and acceptance checks. Write `unknown` when the value cannot be established.

**Exit condition:** a compact plan with target object(s), named stage outputs, measurable checks, visual checkpoints, and required destination verification.

### Gate 1 — Build a minimal proof

- Create **owned** objects in a dedicated collection. Never delete or rewrite unrelated data.
- Construct a rough blockout at the correct dimensions. Inspect the silhouette before any dense detail.
- Use a simple, reversible technique first. Apply modifiers or topology edits only when necessary and authorized.
- Print object names, dimensions and other expected observations from the actual runtime.

**Exit condition:** primary silhouette and proportion checks have evidence. If they fail, revisit the shape instead of polishing.

### Gate 2 — Refine with checkpoints

- Execute one logical operation per step, then inspect the result. Prefer small changes with a clear rollback path.
- Distinguish base mesh from **evaluated** mesh after modifiers.
- At the relevant stage, review normals, topology, materials, UVs, intersection/attachment, deformation, and budgets according to intended use.
- Review the asset twice: **spec fit** (does it match the brief?) then **technical and visual quality** (are defects visible or measurable?). These may require different evidence sources.

**Exit condition:** each acceptance criterion is `PASS`, `ISSUE`, `N/A`, or `NOT VERIFIED` with supporting evidence.

### Gate 3 — Diagnose, correct and recheck

When a check reports a defect:

1. Record the **symptom and evidence** before any edit: screenshot angle, mesh name, dimensions, modifier order or trace.
2. **Reproduce** with the smallest safe selection or scratch copy; confirm a change is actually needed.
3. Propose one **root-cause hypothesis**, then inspect the affected parameters. Don't shotgun bevel, recalculate normals and apply all modifiers blindly.
4. Make the **smallest reversible correction** to an owned copy.
5. Re-run the original check and at least one **no-regression check**: original preservation, adjacent components, geometry budget, UV/material state, or destination output as applicable.
6. Keep the correction only if supported evidence improves; otherwise revert the owned attempt.

If two attempts fail to improve the result, change strategy, reduce the task scope, or ask for a critical missing reference rather than looping indefinitely.

### Gate 4 — Delivery and truthful completion

- Re-evaluate technical data on the actual final object after modifiers.
- Inspect real viewport images before marking visual quality `PASS`; if visual capture is unavailable, mark **NOT VERIFIED**.
- For a requested export, validate scope/scale/format and perform a re-import/target-engine test when possible; otherwise report missing verification.
- State the file path only after confirming it exists. Do not claim Blender engine import or artistic quality from unit tests.
- Report exact measured outcomes and unresolved defects.

## Copyable acceptance record

```text
Asset: [owned object or collection]   Destination: [target]
Blender: [actual version]             Method: [brief technique]
Criterion                   Evidence / observation       Status
Silhouette and proportion   [views, landmarks]           PASS / ISSUE / NOT VERIFIED
Evaluated geometry          [tri count, normals, ...]    PASS / ISSUE / NOT VERIFIED
Materials / UV              [nodes, UV data, screenshots] PASS / ISSUE / N/A / NOT VERIFIED
Scene integrity             [before/after owned objects] PASS / ISSUE / NOT VERIFIED
Export / destination        [output + import evidence]   PASS / ISSUE / N/A / NOT VERIFIED
Unresolved limitations: [...]
```

## Example failure → recovery

**Problem:** a beveled mechanical panel has visible pinching.

- **Observe:** an actual neutral-lit close-up shows distorted highlights, while the evaluated mesh has unexpected dense edge intersections.
- **Isolate:** duplicate the owned panel, disable Bevel on the duplicate, and compare the same view.
- **Hypothesis:** the bevel width exceeds the local clearance near an inset.
- **Correct:** reduce width or revise the local support geometry; don't apply modifiers on the original panel.
- **Verify:** repeat the close-up, evaluated mesh report, and source-object preservation check. If the image is unavailable, visual quality remains **NOT VERIFIED** even if topology passes.

## How to validate the workflow itself

Use [the paired evaluation protocol](skill-evaluation-protocol.md) with the same brief, tool permissions, Blender version, and scene baseline:

- Compare agents **with and without** this workflow guidance.
- Measure unnecessary clarification questions, unowned-object modifications, technical acceptance failures, successful defect corrections, and unsupported PASS claims.
- Review the actual Blender output or render with independent human criteria before making any artistic-quality comparison.

No measured superiority over Superpowers or other 3D agent skills is claimed. See [ecosystem comparison](../docs/ECOSYSTEM-COMPARISON.md) for provenance and scope.
