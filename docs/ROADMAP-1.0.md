# Blender MCP Master — minimal 1.0 release gate

**Updated:** 2026-11-02. Maintainer decision: the 1.0 launch no longer requires T10, a second agent, a game-engine import, independent artistic review, or a repeated paired token benchmark. Those remain honest **NOT VERIFIED** scope limitations and potential post-1.0 improvements, not hidden PASS results.

## Required before a public 1.0

| Gate | Current status | Acceptance |
| --- | --- | --- |
| Integrate pending functional PRs | **PASS** | #29 → #30 → #31 → #32 merged to `main`; #28's identical UV script/tests/reference were carried in #32, and #28 was closed as superseded |
| Python, Blender bpy and npm regression CI | **PASS on integrated main `18f8e713`** | [Python + five bpy versions](https://github.com/God-601/blender-mcp-master/actions/runs/41493641047) and [npm](https://github.com/God-601/blender-mcp-master/actions/runs/41493641037) |
| Clean standalone ZIP installation | **Run in CI from the candidate ZIP** | SHA256 verification, secure extraction into a fresh isolated `~/.agents/skills/blender-mcp-master`, validate frontmatter/linked resource paths, parse scripts and run read-only baseline comparison; publish JSON smoke evidence |
| Honest capability and compatibility disclosure | **In progress** | Do not claim confirmed agent discovery, live Blender MCP control, engine import, 3.1.2 CI support, artistic superiority, token savings or full solid-intersection detection |
| Final candidate packaging | **In progress** | Packaging, SHA256 and smoke succeed on the exact 1.0 candidate commit; `README`, release notes and package manifest agree on released version |
| Owner authorization to tag and publish | **Not requested yet** | Explicit approval; automated preflight alone never tags, publishes npm or creates a public Release |

The automated clean-install test proves the ZIP can be installed **into an isolated agent-style skills directory** and the installed resources work. It does **not** launch the Codex/Claude application, prove its discovery behavior, or connect to Blender. Such testing is optional rather than a v1.0 gate by maintainer choice.

## Implemented and previously evaluated

- Core safety: source ownership, saved checkpoints, read-only protected-object snapshots and failure handling.
- Measured geometry/UV and material audits; evaluated topology includes modifiers.
- Guided retopology with rollback, conservative component-fit candidates and required visual REVIEW when geometry contact is uncertain.
- Reversible optimization, truthful glTF seam/triangulation handling, bounded reference reads, npm MCP resource server.
- Reported field scenarios T01–T09; see [evidence ledger](RELEASE-1.0-EVIDENCE.md). T08 remains **inconclusive** (unsaved Blender scene crashed); no measurable token improvement may be advertised.
- The optional coplanar X-fan inspector is experimental; **T10 is not required**.

## Optional follow-up after v1.0 (not release blockers)

- Verify a second agent and actual agent-client discovery/Blender-control behavior.
- Perform a downstream engine import and independent artistic scoring.
- Repeat the A/B benchmark with identical saved fixtures and genuine token records if making efficiency claims.
- Extend Blender 3.1.2 coverage, UV padding/baking, topology diagnosis, deformation and visual checks.

These items may justify future improvements, but the public 1.0 must explicitly describe them as unverified rather than silently claiming success.

## Release procedure (separate permission)

1. The nonpublishing `.github/workflows/release-readiness.yml` builds a ZIP and checksum and runs `scripts/clean_install_smoke.py`.
2. Review the CI JSON clean-install report on the candidate SHA and verify latest Python/Blender/npm regressions.
3. Confirm actual `v1.0.0` package version, lockfile, links, release notes and artifact checksum, with no mismatched beta instructions.
4. Obtain explicit maintainer authorization before tag/GitHub Release/npm publication. No such publication is triggered by ordinary merges.

[Release evidence](RELEASE-1.0-EVIDENCE.md) · [Launch plan](LAUNCH-PLAN.md) · [Draft release notes](release-notes-1.0-DRAFT.md)
