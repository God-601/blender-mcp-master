# V2 engineering evidence and release hold

Status: staged implementation, **not a 2.0 release or complete production
acceptance**. Review the stages in order: [#69](https://github.com/God-601/blender-mcp-master/pull/69),
[#70](https://github.com/God-601/blender-mcp-master/pull/70), then the evidence/gates PR.
Stable manifest and lock remain 1.4.0. No release tags, npm publication or
merges are part of this delivery.

## Reproduce engineering checks

```sh
python -X utf8 -m unittest discover -s tests -v
python -X utf8 tests/run_v2_evidence.py --output v2-evidence.json
npm ci --ignore-scripts
npm test
npm pack --dry-run --ignore-scripts
```

Without bpy, runtime tests skip explicitly. The existing Static checks CI
runs real bpy 4.2/4.5/5.0/5.1/5.2, plus mutation testing; Godot CI imports
both synthetic GLB and Blender-authored GLB. The V2 JSON artifact records the
actual checked-out SHA (PR merge SHA may differ from the branch head), dirty
tracked state, test counts, platform and unverified scope. It never fabricates
provider usage or live asset quality. The npm matrix covers supported Node
20/22/24 on Linux and Node 22 on Windows; packaging invokes npm without a
Windows shell-spawning dependency. ZIP clean-install executes the installed
planner and verifies the new module/adapter files.

## Observed checks on 2026-11-08

- Stage 1 head `f273d4498253d7a61272bfd548c345dd709cf649`: all four
  [PR workflows passed](https://github.com/God-601/blender-mcp-master/pull/69/checks).
- Stage 2 head `b144a8c01279e739d4d3969bfd6a90deedce1550`: all four
  [PR workflows passed](https://github.com/God-601/blender-mcp-master/pull/70/checks),
  including Blender fixtures and real Godot importer smoke.
- Local Python before stage 3: 395 tests, 177 passed, 218 bpy-dependent tests
  skipped. New cases exercise planner selection, real subprocess JSON
  transport/timeout, malformed output, unavailable host/delegation, write
  failures, protected drift, fresh evidence binding, independent QA and stage
  ordering. Unit-test scene fingerprints and checkpoints are **synthetic**.
- Independent code review found defects in missing task/destination in
  handoffs, stale evidence, recovery flag on pre-dispatch drift and export
  ordering, mutation of prior evidence, and exact-checkout provenance.
  Fixes have regression tests. Simple plans use one coordinator including
  technical validation and explicitly leave independent review NOT VERIFIED.
- A real Codex reviewer was launched via the concrete CLI worker in an
  isolated synthetic fixture. Actual thread identity:
  `01a1bd38-642f-7162-8fa3-c57a0cbf3e07`. It returned NOT VERIFIED because
  execution policy blocked reading `audit.json`. No file inspection or
  Blender/engine quality was passed. An earlier attempt outside a trusted
  Git folder was rejected; retry used an isolated Git fixture without
  bypassing safety controls. This demonstrates launch/receipt handling only.
- Local full Node suite after the Windows npm fix: 17 tests passed.

## Remaining acceptance gates

| Claim | Current scope | Required before 2.0 acceptance |
| --- | --- | --- |
| Agent collaboration | Executable host bridge, deterministic transport tests, real CLI launch | Configured native host with actual specialists completing assets through Blender MCP |
| Scene safety/recovery | Scoped probes, checkpoint hashes, drift/failure fixtures | Real save/reopen, crash/reconnect, shared datablock and writer-lease trials |
| Topology/UV/PBR/retopo | Existing Blender runtime fixtures | Varied production assets, actual saved bakes, pose tests and reviewed renders |
| Proportions/fit/collision | Existing measurements and conservative probes | Reference views, exact intended contact checks; BVH candidates are not collision certification |
| Engines | Existing Godot fixture imports | Real assets with inspected materials/pivots/LODs in each claimed target; Roblox/Unity/Unreal not certified here |
| Cost/efficiency | Bounded planning and concise handoffs | A/B provider-usage receipts, all failed trials retained, comparable quality |
| Release | Exact-source evidence gates, no publisher added | All mandatory gates, independent evidence review and explicit publication authorization |

For 2.0, `release_gate_report.evaluate(record, evidence_root=...)` now requires
every core gate including `specialist_orchestration`, exact per-check source
SHA and matching local artifact SHA256s. N/A cannot waive core gates. A
complete, hash-valid packet returns REVIEW, **never publication authorization**.
File integrity and identity checks cannot authenticate whether an external
host actually ran Blender or whether an artistic assessment is correct.
Legacy release workflows already restrict their own historical versions;
there is deliberately no 2.0 publishing workflow to bypass this hold.
