# Draft release notes — Blender MCP Master 1.0 (NOT PUBLISHED)

> **Preparation only.** This file is a draft for maintainer review.
> There is no `v1.0.0` tag, stable GitHub Release or verified npm stable
> publication. The publicly distributed version remains `v0.2.0-beta.1`.
> Confirm each release claim on the exact final commit before publishing.

## What Blender MCP Master does

Blender MCP Master is an open-source **Agent Skill** that guides AI agents
using a separate Blender-control MCP. It provides task-specific references,
scene-safe workflows and read-only inspection scripts. It is **not** the
Blender MCP server, a Blender addon, or a guaranteed automatic modeler.

### Proposed 1.0 highlights

- New-project general kickoff, followed by a clear permission/ownership
  boundary, measured blockout and scoped correction loop.
- Read-only geometry, object relationship, UV overlap/texel-density and
  materials/texture-workload auditing.
- Explicit-pair conservative checks for deliberate surface joints versus
  problematic overlapping assemblies. These nominate visual REVIEW
  candidates; they do not prove all real-solid intersections.
- Safe, limited retopology primitives with source-copy preservation and
  transactional failure cleanup; NOT a generic automatic quad remesher.
- Protected-object baseline fingerprints and comparison, plus saved-scene
  checkpoint and crash-recovery guidance.
- Documented evaluated triangle count vs native editable face topology
  and intentional glTF/GLB vertex splits.
- Model optimization guidance that considers material quality, silhouette,
  shading and joint integrity, not only raw triangle reductions.
- Optional read-only MCP resource server for bounded reference/script reads,
  and a reproducible paired-run benchmark helper.

### Verification and compatibility disclosure

CI checks cover Python static, Blender `bpy` 4.2/4.5/5.0/5.1/5.2,
npm Node 18/20/22, regression/mutation tests, and package archive integrity
**on the tested commit only**. Blender 3.1.2 has been used for a range of
user-reported live-agent tests but has no equivalent official CI matrix;
do not describe it as fully certified.

The optional script for coplanar X-fan detection is a narrow experimental
audit and **T10 is not a stable 1.0 acceptance requirement**.

Results from T01–T09 show meaningful scene-safe modeling checks. The paired
T08 efficiency result is **inconclusive** because a Blender session crashed,
its unsaved original fixture was lost, and provider token counts were absent.
No measured token reduction, general artistic superiority or engine FPS
benefit may be claimed.

### Installation (provisional)

Before 1.0: use the existing public beta ZIP from GitHub Releases or the
review artifact for manual testing. The release-day README must link to the
actual SHA256-verified `v1.0.0` asset, not this draft. The install target
for Codex is `~/.agents/skills/blender-mcp-master/SKILL.md`, with the
remaining references and scripts in the same skill directory.

The separately installed Blender-control MCP and its addon remain required
for live scene edits. Installing the skill or optional npm server alone
does not control Blender.

### Known limitations to publish prominently

- No automatic aesthetic/artistic certificate: real front/side/three-quarter
  captures and human assessment are required.
- Boundary-touching, intentionally overlapping or contained parts cannot
  be fully classified by AABB or surface BVH candidate checks.
- Export/reimport in Blender does not imply import success in Unity,
  Unreal, Roblox, Godot or another engine.
- glTF triangle and vertex splits by normal/UV/material seam are normal;
  topology/welding requirements must be checked per destination.
- No certified 3.x CI runtime, no guarantee of all-agent compatibility,
  no automatic UV padding/bake certification or runtime FPS measurement.
- Material/scene snapshot hashes cover selected properties only; always
  preserve saved source files and use external backup practices.

## Must be completed before removing DRAFT

- [ ] Merge reviewed PR changes in correct order; reconcile duplicate UV patch.
- [ ] CI green for exact candidate commit, including 1.0 readiness package
  and integrity checksum.
- [ ] Clean skill discovery/install and real Blender-control MCP smoke test.
- [ ] At least two documented agent clients, real model files and images.
- [ ] Real engine import of a representative exported asset.
- [ ] Independent artistic review / objective asset acceptance.
- [ ] Sign off remaining T08 limitations or repeat an uninterrupted pair
  if comparative efficiency is claimed.
- [ ] Bump package, lock and release asset names together **after approval**.
- [ ] Confirm Release workflow authorization, GitHub tag, release notes,
  legal/README paths and optional npm ownership.
- [ ] Obtain explicit maintainer authorization for publishing.

Evidence: [RELEASE-1.0-EVIDENCE.md](RELEASE-1.0-EVIDENCE.md).
