# Visual inspection and correction

## Purpose

Visual inspection evaluates the actual visible model. It complements mesh diagnostics; neither replaces
the other.

## Standard inspection set

For a single prop, capture when available:
- front
- side
- rear when relevant
- top when relevant
- three-quarter
- close-up of critical details
- wireframe or edit-mode topology view when topology matters

For environments, inspect establishing, navigation, and detail views. For characters, include front,
side, back, and deformation-critical regions.

## Neutral inspection setup

Use neutral lighting and a plain background before presentation lighting. Frame only the intended asset
when the MCP supports target framing. Keep camera, scale, and view conventions consistent across runs.

## Defect taxonomy

| Class | Examples |
|---|---|
| Silhouette | shape unreadable, missing mass, wrong negative space |
| Proportion | component too long, too thick, unbalanced |
| Completeness | missing handle, fastener, limb, support, or attachment |
| Intersection | floating part, accidental overlap, z-fighting |
| Surface | pinching, shading artifacts, inconsistent bevel |
| Topology | unexpected density, poles in critical areas, open boundaries |
| Material | wrong roughness, unreadable value separation, inconsistent style |
| Composition | poor framing, hidden focal component, imbalance |

## Severity

- Critical: violates the brief or makes the asset unusable.
- High: obvious defect in primary silhouette, proportion, or structure.
- Medium: visible secondary defect.
- Low: polish issue that does not materially affect use.

Record confidence separately from severity. A hidden region may be NOT VERIFIED rather than PASS.

## Correction order

1. missing or incorrect primary forms
2. silhouette and proportion
3. component alignment and intersections
4. topology and shading
5. materials and secondary detail
6. minor polish

Correct the smallest set of objects that can fix the issue. Reinspect after any correction that affects
silhouette, surface, topology, or composition.

## Evidence rules

- A viewport capture proves only what is visible from that view.
- A mesh report does not prove that the model looks correct.
- A successful script call does not prove that the intended geometry was created.
- A render does not prove topology correctness.
- If visual tools are unavailable, report visual inspection as NOT VERIFIED.
- Keep before/after views consistent when comparing iterations.
