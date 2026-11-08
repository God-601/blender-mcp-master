# V2 acceptance campaign — execute, measure, then promote

Status: **engineering test protocol, NOT a passed end-to-end Blender/agent
campaign**. v1.4.0 is the latest stable release. This record does not create
v1.5–2.0 release tags or give an agent permission to edit someone's scene.

## Order of execution and safety

1. **PBR/geometric groundwork (v1.5):** on an owned copy, inspect UV channels,
   padding/density, non-manifold/degenerate geometry, scale, baking output and
   source preservation with `pbr_channel_audit.py`,
   `uv_island_gutter_audit.py`, and a real Cycles bake. Verify baked image
   pixels and inspect real front/side/three-quarter captures. Mark absent
   measurements NOT VERIFIED.
2. **Visual defect loop (v2 Phase 1):** photograph the *same camera/framing*
   before and after a *small owned-copy correction*. Capture a fixed reference,
   front, side and three-quarter **RGBA silhouette masks** for both attempts.
   Run `reference_silhouette_compare.py` on old and new masks against that
   reference. Independently review real images; record unresolved defects with
   `visual_review_report.py`. Compare protected-object baseline snapshots with
   `compare_scene_baselines.py`. Supply all receipts to
   `visual_iteration_gate.py`. Regression, changed reference, missing
   evidence and unowned edits block acceptance. The gate never edits Blender.
3. **Game delivery (v1.6):** use `game_asset_preflight.py` and
   `game_delivery_manifest.py`; export explicitly selected final objects.
   Open the exact exported file in Godot or Roblox Studio. Inspect normals,
   pivots, PBR maps, LOD counts, collision and material rendering. Record actual
   engine version, asset digest and screenshot/log. Do not confuse Studio
   existence with exact texture or physics certification.
4. **Specialist QA (v1.7):** use the executable [host contract](../references/specialist-orchestration.md)
   and `scripts/specialist_orchestrator.py` (dry-run by default). When connected client tools explicitly support it,
   assign independent geometry, visual, material and export reviews. Verify
   reviewers inspect the actual artifacts; run `specialist_review_gate.py`
   to catch unsupported self-approval. Without a configured live host note
   orchestration NOT VERIFIED. Deterministic subprocess tests and an actual
   CLI launch are separate from successful live Blender specialist work.
5. **A/B trials (v1.8) and release readiness (v1.9):** for each case below run
   baseline vs skill **three times each**, same model, prompt, initial scene,
   Blender and MCP versions. Preserve failed trials, real provider usage and
   any crashes. Use `benchmark_suite_summary.py`. Token consumption is
   NOT VERIFIED where the provider offers no usage receipts. Promote a stable
   release only after exact-commit green CI and actual user acceptance.

## Visual iteration gate format

Produce `before_compare.json` and `after_compare.json` as **complete**
outputs of `reference_silhouette_compare.compare_masks(root, pairs)` (the
three views must reference the same reference PNG bytes and resolution).
Collect `scene_check.json` from
`compare_scene_baselines.compare(before_snapshot, after_snapshot)`, and
`visual_review.json` from `visual_review_report.assess_review(report)`.
The latter records reviewer claims; it does not independently authenticate them.

```bash
python scripts/visual_iteration_gate.py before_compare.json after_compare.json \
  --scene-check scene_check.json --visual-review visual_review.json
```

- `REVIEW_REQUIRED`: matching references, three measured views, positive mean
  IoU gain, no material view regression, source protection receipt PASS,
  complete human/reviewer receipts. **Still not an artistic PASS**.
- `ISSUE`: view regression, open defect or protected scene change. Revert or
  inspect the owned copy; never edit or roll back unrelated user objects.
- `NOT VERIFIED`: missing views/receipts, different reference/resolution,
  unchanged image bytes, no demonstrated improvement or invalid data.
- This is a conservative **measurement audit**, not pixel-based artistic
  judgment, camera verification, automatic retopology or proof of engine import.

## One-command full evidence audit (recommended)

Instead of manually generating four separate JSON assessments, prepare a
`manifest.json` containing three views (same camera/framing, before and after)
and real captured source-protection and independent reviewer input. This is
**read-only**; it never opens Blender, requests mutations or generates imagery.

```json
{
  "asset": "Sofa",
  "views": [
    {"view": "front", "reference": "front_ref.png", "before": "front_before.png", "after": "front_after.png"},
    {"view": "side", "reference": "side_ref.png", "before": "side_before.png", "after": "side_after.png"},
    {"view": "three_quarter", "reference": "three_quarter_ref.png", "before": "three_quarter_before.png", "after": "three_quarter_after.png"}
  ]
}
```

```bash
python scripts/visual_iteration_audit.py manifest.json --evidence-root ./views \
  --scene-before scene_before.json --scene-after scene_after.json \
  --review reviewer_report.json
```

The scene files are from `scene_baseline_snapshot.py` **before and after
editing**. The reviewer report is the *raw* `visual_review_report.py` input,
with front/side/three-quarter capture receipts and unresolved defect records.
The output includes the PNG SHA-256 values, measured IoUs, selected protected
scene comparison, reviewer triage, and an explicit `NOT VERIFIED` artistic
result. In CI, this command is tested with actual generated transparent PNGs
and both preserved and damaged scene snapshots; it is **not** a real Blender
visual correction session or a camera-alignment verifier.

## Five controlled acceptance fixtures

| Case | Main success criterion | Real positive/negative checks |
| --- | --- | --- |
| Chair | Four legs, measured proportions, silhouette | Correct leg spacing vs injected missing/floating leg |
| Sword | Consistent blade silhouette and bevels | Clean shading vs injected bevel pinch or mirrored UV defect |
| Tree (Roblox) | User-authored triangle limit, PBR and Studio import | Correct LOD/material vs intentionally missing normal map |
| Modular medieval wall | Clear joints, scene preservation, dimensions | Valid contact vs injected edge-only / interpenetrating joint |
| Retopo or rigged character | Deformation loops and preserved source | Correct loops vs invalid weights/shape key or source mutation |

Run against a **scratch copy**. Include image references with attribution,
exact asset hashes, blender/runtime versions, original user constraints,
user ownership, final file checksums, and explicit before/after visual views.

## Release blockers and signoff

- No **automatic** artistic PASS from IoU or a JSON report.
- No actual multi-agent execution from specialist review receipts alone.
- Godot CI is a real headless importer test, not proof that every asset works
  in Roblox/Unity/Unreal. A user acceptance of Sofa V3 is evidence for that
  one asset only, not the whole v1.6 milestone.
- A `PASS` on selected protected-object hashes does not certify the entire
  Blender scene or every image byte.
- Versioned releases require separate approved action. Add test logs/receipts
  and a signed reviewer verdict before claiming a milestone complete.

Reference: [full roadmap](ROADMAP-V2.md) and
[release ladder](V1.5-V2.0-MILESTONES.md).
