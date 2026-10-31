# Modeling benchmark suite

## Goal

Measure whether changes improve actual asset construction across styles and agents. A script creating
objects is not sufficient evidence of model quality.

## Benchmark controls

Every run must use:
- versioned prompt and reference images
- known empty or standardized starting scene
- fixed Blender version and render settings
- declared MCP capabilities
- declared agent/client
- fixed inspection angles and framing
- technical checks appropriate to the task
- the same visual rubric

Record model/agent identifiers only when the environment exposes them. Do not invent them.

## Initial benchmark tasks

| ID | Asset | Primary skills |
|---|---|---|
| B01 | Stylized chair | proportions, symmetry, multi-part hard surface |
| B02 | Fantasy sword | silhouette, profile extrusion, bevels, assembly |
| B03 | Organic rock | deformation, irregular volumes, seeded variation |
| B04 | Low-poly house | modular construction, roof/wall composition |
| B05 | Stylized creature | decomposition, organic forms, proportion |

`scripts/benchmark_report.py` collects technical metrics for explicit target names and emits a machine-readable JSON report. It intentionally sets `visual_scores` to null and `visual_status` to `NOT VERIFIED`; use the fixed task prompts in `references/benchmark-prompts.md` and attach actual front, side, and three-quarter captures before scoring.

## Evaluation rubric

Score each category from 0 to 4 and attach reviewer notes:
- silhouette/readability
- proportion
- component completeness
- geometric correctness
- topology/shading
- style consistency
- material/presentation

A score of 0 means absent or unusable; 2 means recognizable but with clear defects; 4 means meets
the reference and acceptance criteria. Scores must be accompanied by evidence, not adjectives.

## Technical evidence

Capture object count, dimensions, vertex/edge/face or triangle counts, modifier stack, material slots,
and relevant validation results. Include explicit target names.

## Visual evidence

Capture front, side, and three-quarter views at minimum where applicable. Add detail and wireframe views
when the task requires them. Keep the same framing and lighting between compared runs.

## Regression policy

A change should not be considered an improvement if it raises one category while introducing a critical
regression in another. Preserve the prior output and compare side-by-side.

## Agent portability runs

Run the same tasks in each supported agent/client. Record:
- skill loaded successfully
- MCP tools discovered and mapped
- geometry execution completed
- visual inspection completed or unavailable
- quality checks performed
- final asset and limitations

A compatibility matrix is only updated after an actual run. `scripts/capability_probe.py` reports Blender-side API availability, but it does not prove that an agent/client can discover or invoke the MCP tools. Do not mark Codex, Claude, Cursor, OpenCode, or Kilo Code as verified until a real session completes the same task.
