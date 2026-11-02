# Crash recovery, user-owned scene baselines and truthful benchmarks

**P0:** A Blender process crash can destroy unsaved scene work. Seeing
`Cube`, `Camera` or `Light` in a newly created scene does NOT demonstrate
that earlier objects survived. Rebuilding a similar scene is a *new run*, not
a valid scene-preservation PASS for the interrupted run.

## Before substantial changes, baking or rendering

1. Complete the one-time GENERAL KICKOFF. Read-only discovery may precede it.
2. Inspect scene ownership and `bpy.data.filepath`. If the current scene has
   user-owned work and no saved baseline, **do not begin risky mutation**.
   Propose saving a separate uniquely named checkpoint; never overwrite
   existing user files without authorization. For scratch scenes, create a
   checkpoint before substantial geometry and long renders.
3. In a scene-preservation test, make sure the exact protected objects exist
   in the actual Blender MCP session. Missing objects = NOT VERIFIED and stop.
4. Capture read-only before evidence with
   `scripts/scene_baseline_snapshot.py` after configuring explicit
   `TARGET_NAMES = ["USER_Keep_Mesh", "USER_Keep_Light", "Camera"]`.
   Store its JSON between `MCP_SCENE_BASELINE_BEGIN` and
   `MCP_SCENE_BASELINE_END` **outside Blender** as
   `scene_before.json` in your test output folder; use paths under your
   own authorized test directory.
5. Model exclusively in owned collections. Save the output to a DIFFERENT
   .blend. Capture the same protected names as `scene_after.json`.
6. Compare JSON snapshots using:
   `python scripts/compare_scene_baselines.py scene_before.json scene_after.json`.
   PASS means only the selected captured properties agree; it does NOT
   guarantee identical project files, untracked global properties or that
   unrelated unnamed objects were untouched.

## After a crash, disconnect or tool failure

- Stop performing commands against an unknown/new Blender session.
- Record the failure, time, checkpoint and whether the original file was saved.
- Reconnect read-only and confirm the actual file path, scene names, objects,
  ownership and Blender version before any further mutating calls.
- Reopen the last safe checkpoint, or explicitly restart in a fresh copy.
  If the original scene was unsaved or unavailable, original-scene
  preservation is **NOT VERIFIED**. Do not call newly constructed default
  `Cube/Camera/Light` the original objects.
- Preserve the failed run's logs; record the replacement scene as a separate
  run or an **interrupted/recovered** trial rather than quietly continuing
  an efficiency benchmark.
- Reinspect lighting, render configuration and output files after CPU/GPU
  fallback; no runtime/FPS or quality improvement claims without evidence.

## Efficient A/B tests

- Save and fingerprint the **same initial .blend fixture** for both runs.
- Keep prompt, user follow-up answer, exact agent/client/model, permissions,
  Blender version, MCP implementation and available tools fixed.
- Use the same tool-call accounting method. "12 direct + 14 nested" and
  "17 external + 21 internal" are **not automatically comparable**.
- Use actual provider tokens only. When neither run exposes token counts,
  mark them NOT VERIFIED; never derive token savings from calls.
- If either run crashes, changes the fixture, or loses the original protected
  scene, mark the paired efficiency outcome NOT VERIFIED and repeat the
  entire matched pair rather than excluding an inconvenient attempt.
- `scripts/agent_efficiency_compare.py` now refuses comparisons when either
  run lacks `checks.scene_preserved=PASS`, reports incidents, or has a
  non-completed run status. Record incidents even when recovered.

Example JSON metadata (illustrative placeholders, not test evidence):

```json
{
  "case_id": "T08-table",
  "prompt_sha256": "replace-with-real-hash",
  "scene_fixture_sha256": "replace-with-real-hash",
  "agent": "Codex",
  "model": "exact-agent-model",
  "blender_version": "version-reported-by-Blender",
  "mcp_version": "actual-control-mcp-version",
  "run_status": "completed",
  "incidents": [],
  "checks": {
    "scene_preserved": "PASS",
    "technical": "PASS",
    "visual": "NOT VERIFIED"
  },
  "metrics": {"mcp_calls": 0, "bash_calls": 0}
}
```

Only supply hashes and metrics that were truly measured. The comparator
refuses missing/contradictory metadata rather than inventing comparability.

## Limits of the scene baseline script

The tool hashes selected object identity, collection membership, transforms,
mesh vertices/edges/faces, material slot assignments, selected material
node properties, UV coordinates, light/camera essentials and modifier
types/visibility. It does NOT exhaustively fingerprint scene-global settings,
all third-party properties, drivers, animations, linked-library data, image
pixel contents or every possible Blender datablock. Save a .blend fixture and
inspect differences directly for higher-confidence preservation claims.
