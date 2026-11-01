# Lightweight workflow director

Use this after the core clarification/planning gate. It adapts a useful
specialist-routing idea to a **single portable skill** without duplicating
dozens of long instructions.

## Route from deliverable, not superficial keywords

| Main constraint | Primary reading | Cross-cutting gates |
|---|---|---|
| Static game prop or vehicle | `hard-surface.md` or `measured-proportion-recipes.md` | UV, evaluated budget, material, engine import |
| Deformable character or animated prop | `character-rig.md`, `topology-retopology.md` | Pose stress tests, weights, rig export, no static exporter |
| Stylized voxel foliage | `stylized-lowpoly.md`, `voxel-atlas-recipe.md` | Palette/UV continuity, camera-distance readability |
| Architectural kit | `modular-modeling.md`, `architecture-interiors.md` | Snap/pivot, doorway clearance, adjoining face checks |
| Image/reference match | `visual-inspection.md`, `modeling-quality-loop.md` | Camera framing, silhouettes and orthographic views |
| Materials/baking | `materials.md`, `uv-baking.md` | Correct colorspace, UV padding, saved textures |
| Bug or unexpected result | `troubleshooting.md`, `modeling-decision-framework.md` | Root cause before changing geometry |

## Task contract

A meaningful modeling plan records:
`target, destination, reference, measurements, inferred assumptions,
critical unknowns, output object names, stage checkpoints, acceptance evidence`.

Stages:
**Clarify → scene probe → blockout → reference/shape check → technical pass →
material/export check → independent final review**.

Skip irrelevant stages (e.g. do not require UVs on an untextured concept model).
If no image was supplied, don't fabricate reference-based fidelity scores.

## Failure rule: diagnose, make one correction, inspect again

When a model looks wrong or a validator fails:

1. Reproduce the exact failure and isolate the affected named objects.
2. Decide whether the cause is proportions, transforms, topology, modifiers,
   material/UVs, camera or export convention.
3. Choose one minimal reversible fix; preserve the previous result.
4. Repeat the *same* inspection. State what changed and what still fails.
5. After two unsuccessful attempts, change method or seek the missing fact
   instead of repeatedly adding details.

Sample record:
`ISSUE: leg floats 0.03m -> evidence: bounds and screenshot ->
change: leg height in owned copy -> measured gap 0.00m ->
visual contact: NOT VERIFIED until screenshot`.

Avoid converting bounds overlap into confirmed physical fit.
