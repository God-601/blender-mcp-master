# 1.0 candidate evidence ledger (NOT A RELEASE)

**Last updated:** 2026-11-02. This document distinguishes measured,
agent-reported and missing evidence for the pre-1.0 acceptance decision.
It does NOT announce Blender MCP Master v1.0. The published version remains
`v0.2.0-beta.1`. PRs #29–#32 are merged into `main`; PR #28 was closed as
superseded because its UV implementation was included exactly in #32.
No stable tag, npm publish or GitHub Release is authorized by this ledger.

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

## Updated maintainer scope — only clean install remains to be validated

**Release acceptance:** integrated PRs + green Python/bpy/npm checks + independently
packaged SHA256-verified ZIP **installed into a clean isolated agent-style
home** + accurate public limitations + final maintainer publication
authorization. The new CI smoke uses `scripts/clean_install_smoke.py`; its
report must be checked on the exact candidate commit. It validates files
and helper behavior, **not actual Codex/Claude discovery or live Blender**.

| Item | Result or policy |
| --- | --- |
| PR integration | **PASS**: #29, #30, #31, #32 merged. #28 closed as fully incorporated via #32 |
| Integrated CI | **PASS**: [main Python + Blender](https://github.com/God-601/blender-mcp-master/actions/runs/41493641047) and [main npm](https://github.com/God-601/blender-mcp-master/actions/runs/41493641037) |
| Fresh standalone ZIP installation | **PASS on PR #33** ([CI evidence](https://github.com/God-601/blender-mcp-master/actions/runs/41495964213)): SHA256, fresh installed skills root, 39 scripts parsed, 26 README links checked, protected scene comparator PASS. Automated main rerun scheduled by workflow trigger |
| User release approval | **PENDING**, separate authorization required before tagging/publishing |
| Blender 3.1.2 CI and live Codex/Claude discovery | **NOT VERIFIED**; optional after 1.0 and not claimed |
| Real second-agent end-to-end modeling | **NOT VERIFIED**; optional after 1.0 |
| Engine import | **NOT VERIFIED**; optional after 1.0; do not advertise compatibility as tested |
| Independent artistic scoring / token savings | **NOT VERIFIED / INCONCLUSIVE**; optional after 1.0; no superiority claim |
| T10 real-agent test | **EXCLUDED** from 1.0 by maintainer choice; experimental narrow diagnostic only |

This is an explicit acceptance-risk decision, **not a declaration that the
omitted tests passed**. Future users must see the known limitations.

### Nonpublishing procedure

1. Create a candidate ZIP from the desired release commit; verify checksums,
   archive safety and install into an empty temporary `.agents/skills` home.
2. Check the produced clean-install JSON and existing CI matrix on that commit.
3. Verify accurate draft release notes, current package version and install
   links before any final release.
4. Obtain explicit authorization to tag or publish. Do not automatically
   publish npm or GitHub releases.

## References

- [1.0 roadmap](ROADMAP-1.0.md)
- [Release and community plan](LAUNCH-PLAN.md)
- [Crash recovery baseline protocol](../references/crash-recovery-and-baselines.md)
- [Efficiency protocol](EFFICIENCY-BENCHMARK.md)
- [Open issues #18–#20](https://github.com/God-601/blender-mcp-master/issues)
