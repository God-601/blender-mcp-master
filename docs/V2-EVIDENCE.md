# V2 engineering evidence

The follow-up [recorded campaign](V2-CAMPAIGN-2026-11-08.md) now includes 30
actual constrained agent generations, five canonical fixtures, Godot imports,
real crash/restart and addon reconnect tests, and Roblox material/collision
checks. Its scope and unresolved model/quality limits remain explicit.

The [2.0.0 release notes](release-notes-2.0.md) state the shipped scope. The
entries below preserve the engineering campaign, including what each run
established and the production acceptance work still open.

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

## Published release and remaining validation

GitHub published [v2.0.0](https://github.com/God-601/blender-mcp-master/releases/tag/v2.0.0)
on 2026-11-13 at commit `478a6920666cb131a6e870b604b64e83b236f7a2`.
The release includes the ZIP, SHA256SUMS.txt and clean-install-report.json.
The publisher is [.github/workflows/release-stable-2.0.yml](https://github.com/God-601/blender-mcp-master/blob/v2.0.0/.github/workflows/release-stable-2.0.yml).
It checks the authorized merge subject and the CI results for that commit.

| Area | Recorded result | Remaining evidence |
| --- | --- | --- |
| Clients | Codex completed a scoped Blender modeling task. Claude Code discovered the skill. | Authenticated Claude execution and end-to-end runs for Cursor, OpenCode and Kilo Code. |
| Recovery | A real background Blender recovered its checkpoint. One GUI addon reconnect passed. | Two GUI repeats timed out before readiness. Reproduce startup and reconnect on the affected host. |
| Geometry and materials | Blender fixtures cover selected topology, UV, bakes and preservation checks. | More production meshes, reviewed renders and deforming poses. |
| Destination | Godot imported tested GLBs. Earlier Roblox assets have scoped Studio evidence. | Bind Studio appearance, PBR and playtest collision to the specific release-test GLB. Unity and Unreal need separate trials. |
| Efficiency | 15 trials per arm used 525,606 tokens without the skill and 558,384 with it. | Repeat with a recorded model, comparable cache use and independent quality scoring. |

The [campaign report](V2-CAMPAIGN-2026-11-08.md) records the fixtures and failed attempts.
The optional release evidence evaluator requires per-check source SHAs and matching
artifact hashes. A complete packet returns REVIEW for a human decision.

## Review follow-up: actual native production

The merge review found and fixed two further defects: task-specific guides
were omitted from specialist handoffs, and missing later capabilities could
be discovered after an earlier write. All required capabilities are now
preflighted; capability loss after writes requires recovery inspection.

The bundled `integrations/agents/blender_native_host.py` now provides actual
bpy probes, saved-copy checkpoints/stage files, a per-scene writer lease,
ownership/dependency checks and selected-property read-stage audits.
Regression tests use actual Blender save/reopen, competing writers, shared
mesh/image data, omitted protected objects, read-stage geometry edits,
protected modifier edits and world-content edits. This is selected-property
damage detection with explicit limits, not arbitrary Python isolation or
complete .blend equivalence.

A real live Blender MCP 3.1.2 run completed a controlled six-part chair:
four legs, 72 triangles, UV coordinates, four saved constant-color PBR PNGs,
GLB export and front/side/three-quarter captures. The actual independent
Codex reviewer `01a1bd7a-2444-7153-abf9-263f1c2579cd` returned PASS for the
explicitly scoped report/image audit. The coordinator returned REVIEW, with
artistic quality and universal engine fidelity still NOT VERIFIED. Existing
objects' captured properties and the original Blender filepath were preserved;
the original active scene was restored.

The exact exported chair GLB was also imported by an actual local Godot
4.4.1 process: 72 triangle primitives, one UV surface and one material surface.
This is actual geometry import, not a visual/PBR/physics certification.

The live run used the working review source, not a final release-tagged SHA;
it is integration evidence, not a replacement for final-commit release gates.
Earlier attempts are retained: an invalid model evidence path stopped the
first run; a subsequent scoped PASS containing uncertainty in `errors` was
downgraded to NOT VERIFIED. The output contract now restricts evidence to
actual supplied paths, separates scoped notes from errors and persists parsed
responses and provider usage. The successful reviewer reported 33,281 input
and 438 output tokens. These are actual single-run usage values, **not** an
A/B savings claim. The subsequent [five-fixture campaign](V2-CAMPAIGN-2026-11-08.md)
supplies bounded generation, recovery and engine evidence, including retained
failures. Broader freeform-agent and production acceptance work remains open.
