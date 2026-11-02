# Blender MCP Master — release 1.0 execution backlog

**Status date:** 2026-11-02. This is an execution ledger, not a declaration that a beta feature is production-ready. Update status and attach actual evidence before checking an item complete.

Definitions:
- **Implemented (PR)** = code and docs exist on a non-main branch; requires CI and review before landing.
- **CI verified** = all named automated jobs passed for the exact commit; not equivalent to artistic or live MCP verification.
- **External validation** = a real Blender MCP client, human visual reviewer or actual engine importer is necessary.

## P0 — blockers for a stable public release

| ID | Work | State | Evidence / acceptance |
| --- | --- | --- | --- |
| P0-01 | Resolve docs/readme regressions, ensure accurate architecture + install paths | CI verified on PR #29; merge pending | GitHub Actions logs for PR #29; requires review and integration |
| P0-02 | Correct UV test API and verify overlap/density diagnostics | CI verified on PR #28; integration pending | Tests on bpy matrix, including missing UV layer |
| P0-03 | General kickoff, guided retopology, reviewed registry, visual evidence receipts | CI verified on PR #30; real behavior still pending | Python/bpy/npm checks on exact PR head; actual agent behavior not verified |
| P0-04 | Minimize unnecessary Bash usage/context loading in resource navigation | Implemented in PR #31; Python/bpy CI green, npm rerun pending | MCP bounded excerpt/outline integration tests; no invented token reduction |
| P0-05 | Read-only evaluated mesh, materials and texture workload audit | Implemented in PR #31; Python/bpy CI green | Real bpy tests: evaluated geometry, duplicated datablocks, material warning, read-only behavior |
| P0-06 | Preserve safety + clarify versioned setup and token-conscious workflow | Implemented in PR #31; Python/bpy CI green | Mandatory kickoff + P0 integrity behavior not weakened |
| P0-07 | Real end-to-end Blender MCP project on at least 2 supported clients | **NOT VERIFIED**; external | Exact agents/MCP/Blender versions, full logs, output .blend, views; follow Issue #19 |
| P0-08 | Real engine import/export with one intended target | **NOT VERIFIED**; external | Open exported file in intended engine; verify scale, UV, materials, pivots and geometry; Issue #18 |
| P0-09 | Independent artistic review, controlled with/without-skill comparison | **NOT VERIFIED**; external | At least chair, sword, house, organic and mechanical/character assets, same conditions; Issue #20 |
| P0-10 | Release packaging, ZIP hash, clean install and accurate claims | **NOT VERIFIED** for final release | SHA256SUMS, actual agent install, tagged beta-to-stable process with approved release commit |

**No merge, version bump, npm publish or stable-release announcement should occur simply because this backlog exists.**

## P1 — improve reliability and quality

- [ ] Replace the oversized root \`SKILL.md\` with a shorter progressive-disclosure entrypoint without losing safety/routing or breaking tests. Keep all supported workflows accessible through focused references; benchmark real loaded context and outcome quality.
- [ ] Introduce deterministic benchmarks of token use where the agent exposes token metrics; otherwise report reference bytes and tool calls only, not "saved tokens".
- [ ] Extend guided retopology with semantic boundary extraction, topology repairs, deformation-aware edge flow and pose-tested results; reject arbitrary automatic quad-remesh claims.
- [ ] Implement actual image analysis loop only in clients that support visual inspection; capture before/after and preserve sources. A metadata receipt does not analyze an image.
- [ ] Improve UV density/overlap, baking maps, LOD/material checks and downstream export tests for real target engines.
- [ ] Validate Blender 3.x compatibility separately from the current CI-supported bpy 4.2/4.5/5.x matrix.
- [ ] Re-run mutation tests and independent security/safety review on the final integration commit.
- [ ] Prepare demo assets, changelog, 1.0 docs and release materials using [Launch plan](LAUNCH-PLAN.md).

## How to execute and measure

1. Land/fix small dependency PRs after CI and explicit review, then rebase dependent branches; do not force changes to main.
2. For every implementation, write a failing behavioral test, implement the smallest viable change, repeat tests on CI and record exact run links.
3. Execute same user brief with and without the skill, on the same client/runtime and a fresh copy of the same scene.
4. Record actual token counts **only if exposed by the client**, together with bytes loaded, Bash calls, MCP calls, runtime, user object preservation, technical and visual outcomes.
5. Do not mark visual quality or compatibility PASS without screenshots, actual agent/tool execution and independent evidence.
6. Publish \`1.0\` only after P0 acceptance, a reviewed release candidate, actual clean-install smoke test and user authorization.

## Relevant project entry points

- [Agent efficiency protocol](../references/token-efficient-agent-execution.md)
- [Performance strategy](../references/model-performance-strategy.md)
- [Benchmark prompts](../references/benchmark-prompts.md)
- [Agent behavior evaluation](../references/skill-evaluation-protocol.md)
- [Release launch plan](LAUNCH-PLAN.md)
- [Issues #18–#20](https://github.com/God-601/blender-mcp-master/issues)
