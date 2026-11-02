# 1.0 candidate evidence ledger (NOT A RELEASE)

**Last updated:** 2026-11-02. This document distinguishes measured,
agent-reported and missing evidence for the pre-1.0 acceptance decision.
It does NOT announce Blender MCP Master v1.0. The published version is
`v0.2.0-beta.1`; the improvements described below remain on review branches.
No merge, stable tag, npm publish or GitHub Release is authorized by this ledger.

## Real modeling exercises reported by a Codex user

These observations are contextual evidence, NOT a controlled benchmark or an
independent Blender 3.1.2 runtime certification. User provided Blender outputs
in a testing conversation; source chat logs/screenshots and the live Blender
MCP configurations have not been checked into the repository. Some .blend
structures received independent binary inspection. Do not convert those checks
to a verified live-agent compatibility matrix without auditable artifacts.

| Test | Scenario | Observed / reported | Outstanding limitations |
| --- | --- | --- | --- |
| T01 | Medieval chair | 616 tris, scene preserved as reported; plausible dimensions | Multiview aesthetic scoring and exact scene baseline incomplete |
| T02 | Low-poly castle | 56 meshes, 708 tris, two 12 m towers and planned footprint | Visual review incomplete; explicit floor/engine checks absent |
| T03 | Sci-fi mechanical panel | 25 owned meshes, 428 tris, protected mesh/light/camera still present | Original protected-property baseline file not independently archived |
| T04 | Guided 4-face bridge | 4 new quads; invalid index 99 rolled back without owned debris (agent report) | Source/output .blend and error logs not independently attached |
| T05 | UV overlap/density | A separate: 0; B true overlap: 2 candidate triangle pairs; C border contact: 0; density 256 px/scene-unit uniform | Padding, bake, modifier-evaluated UVs and engine unknown |
| T06 | Comparative chest/LOD | Original 380, subdivision 5,520, optimized 268 evaluated triangles; 29.5% reduction | Optimized silhouette became more faceted and lost detail; no automatic visual PASS |
| T07 | Sword GLB round-trip | 180-triangle original; imported GLB triangles/vertex splits observed; gap correction copied | GLB not independently audited; grip/guard joint may now deliberately overlap; target engine untested |
| T08 | Without/with skill medieval table | Both met 1.20 × 0.70 × 0.75 m; 968 and 836 tris; 12 direct/14 nested vs 17 external/21 internal operations | **INCONCLUSIVE**: dissimilar call accounting; provider tokens missing; one Blender run crashed, source scene was unsaved and recreated; assignment to skill-on/off and matched source fixture not independently proven |
| T09 | Chair mating joints | 13 components, 156 tris, 18 explicit pairs REVIEW rather than false PASS | Close-up underside incomplete; actual mechanical/collision fit NOT VERIFIED |

**T10 is explicitly excluded from 1.0 acceptance on user instruction.**
The optional four-triangle planar X-fan diagnostic is an experimental assist,
supported by automated bpy tests; there is no T10 real-agent signoff and it
must NOT be marketed as a comprehensive automatic retopology/topology fix.

## Regression changes made from these exercises

- **G2 intentional joins:** `references/component-fit-and-joints.md`
  documents mating planes/socket depths. `scripts/inspect_component_fit.py`
  performs conservative opt-in read-only object-pair AABB/BVH checks. It cannot
  prove full 3D solid intersection or correct assembly from bounds alone.
- **G3 editable topology:** separate native Blender editable faces from
  GPU/glTF triangulation. Do not auto-merge legitimate UV/normal seams.
- **T03/T08 preservation and recovery:** require a saved preflight checkpoint
  for risky unsaved work; compare explicit protected names via
  `scripts/scene_baseline_snapshot.py` and
  `scripts/compare_scene_baselines.py`. Missing initial baseline cannot PASS.
  `scripts/agent_efficiency_compare.py` excludes crashed, incomplete and
  preservation-unverified runs from paired performance claims.
- **T06 cost versus quality:** preserve before/after variants; require
  silhouette, curvature, fittings and detail review before endorsing a
  lower triangle count. No invented game FPS/draw calls/VRAM.
- **T07 round-trip:** a GLB with split vertices at seams can be valid.
  Verify target material/UV/normals, welding requirements and actual engine
  separately. Do not claim engine validation from Blender-only reimport.

## Non-negotiable gates for a stable 1.0

| Gate | Status as of this record | How to close it |
| --- | --- | --- |
| Integrate PR stack without duplicate UV patch | **OPEN** | Review #28–#32 dependency/diff; merge in dependency-safe order after CI and authorization |
| Python + bpy matrix, npm, security audit, package integrity | **AUTOMATED in review**, not release commit | All required checks pass on exact final release candidate commit; test ZIP hash / manifest |
| 3.1.2 support claim | **LIMITED / NOT VERIFIED by CI** | Run exact tests headless in Blender 3.1.2 or explicitly state 3.x is experimental |
| Real tests on at least 2 declared clients | **OPEN** | Save client/MCP versions, logs, actual assets and images for Codex and another client |
| Real downstream engine import | **OPEN** | Import an actual exported model into a selected engine and inspect units, material, pivot, UV and collider |
| Independent artistic quality | **PARTIAL** | Review captured original renders, avoid subjective PASS without visuals; run controlled attempts |
| Crash-safe paired efficiency evidence | **OPEN** | Repeat both matched variants with saved identical starting scene, normalized tool counts and honest token availability |
| Clean install of candidate ZIP | **OPEN** | Extract verified hash, install in new agent home, check skill discovery and live Blender-control MCP |
| User release approval | **OPEN** | Explicit signoff after final acceptance; publication remains a separate authorized step |

**Scope discipline:** Completing manual gate results may reveal real new bugs.
Fix those and rerun the relevant CI. Adding untested features to get a bigger
1.0 feature list is not a release requirement. T10 must stay out of the
stable release gate unless the user changes scope.

## Integration plan and nonpublishing candidate procedure

1. Reconcile #28 UV work against the equivalent files included in #32.
   Integrate #29 → #30 → #31 → #32 in dependency order, with a fresh final
   review and no implicit PR closing or publishing.
2. Run static, bpy 4.2/4.5/5.x matrix, Node 18/20/22, mutation checks and
   `.github/workflows/release-readiness.yml` on the exact target commit.
3. Download `blender-mcp-master-1.0-PREFLIGHT-NOT-A-RELEASE.zip` from CI,
   verify `SHA256SUMS.txt`, and smoke-test on a clean Codex or Claude
   installation with a separately installed Blender-control MCP. No live
   tools are provided by the Agent Skill ZIP.
4. Obtain external validation above. Prepare reviewed `v1.0.0-rc.1`
   release notes and change package version / lockfile together **only when
   accepted**; check fresh installation again.
5. After human authorization, publish a correctly tagged GitHub prerelease
   candidate; test the exact distributed asset. Final `v1.0.0` and
   optional npm publish require another explicit approval.
6. Update README/QUICKSTART and docs that currently refer to the public beta,
   and add the verified compatibility/engine matrix. Do not advertise
   unverified 3.x or cross-agent behavior.

## References

- [1.0 roadmap](ROADMAP-1.0.md)
- [Release and community plan](LAUNCH-PLAN.md)
- [Crash recovery baseline protocol](../references/crash-recovery-and-baselines.md)
- [Efficiency protocol](EFFICIENCY-BENCHMARK.md)
- [Open issues #18–#20](https://github.com/God-601/blender-mcp-master/issues)
