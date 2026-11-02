# v1.1.0 evidence ledger — implementation and limitations

**Scope:** improvements integrated from PR #36, plus a versioned release
candidate. This document tracks measurable CI checks; it is not a claim
of independent visual inspection, physical collision or live-agent quality.

## What has actually been implemented

| Area | Concrete behavior | Verification scope |
| --- | --- | --- |
| Component joins | Read-only G2 AABB classification identifies face-plane support vs edge/corner contact; missing face-area support on surface joints is ISSUE | bpy runtime fixtures: two touching cubes, edge-only contact, diagonal near gap, separated and overlapping objects; **does not** prove polygon-level 3D contact |
| Editable topology | Read-only coplanar degree-four X-fan candidates include UV seam, mixed material IDs and shape-key flags | bpy square/quad/diagonal/fan fixture and seam/material tests; no automatic removal or generic retopo claims |
| Optimized silhouette | Read-only front/side/top/three-quarter **convex-hull projection** comparison, evaluated triangle delta and authored tolerances | bpy matched/different-size/modifier tests; silhouettes with holes or concavity and actual art quality are NOT VERIFIED |
| Visual image evidence | Named PNG/JPEG files must exist, fit size limits and stay within explicit evidence root; hash bytes | Pure Python tests for valid/missing/bad/traversal files; **pixels/provenance are NOT judged** |
| Crash reconnection | Expected saved checkpoint filepath, scene and protected object names/types must agree before proceeding to baseline comparison | bpy tests for unsaved/wrong/missing/saved scenes; matching identity does not prove unchanged scene content |
| Installation and compatibility | Standalone ZIP signature, checksum, local skill routing, links and helper in clean isolated home; npm reference MCP | GitHub Actions Python, bpy 4.2/4.5/5.0/5.1/5.2, Node 18/20/22 and preflight on exact release commit |

## Actual client/visual limits

- AABB edge/corner detection is a **necessary-contact-box** test and not a
  watertight Boolean/physics intersection solver. Containment and non-convex
  mesh contacts require more investigation. Plausible face contact is REVIEW.
- Convex hull projections cannot see holes, removed rivets, concave
  changes, shading damage, textures or hidden components.
- PNG/JPEG hash checks cannot identify whether the picture really shows
  the requested asset. Real screenshot review is needed.
- Reopened scenes matching the checkpoint path still require the explicit
  protected-object before/after baseline comparison and separate review.
- Real Codex/Claude discovery, Blender 3.1.2 certification, target-engine
  import, quantified token gains and independent artistic benchmarks remain
  NOT VERIFIED. The T10 live-agent diagnostic has not been signed off.

## Version process

1. PR #36 includes code and regression tests; merge only after the full
   Python/bpy and npm preflight matrix passes.
2. Release branch updates package manifest/lockfile, changelog, README and
   Windows setup paths to 1.1.0, with this evidence ledger and release notes.
3. Final release workflow must verify its **exact main SHA** across all
   required passing workflows, run clean ZIP installation on the versioned
   ZIP, and attach checksums before publishing.
4. GitHub Release and npm are distinct; npm is optional and requires an
   authorized NPM_TOKEN. Never claim npm is published if the credential is
   absent.

Follow-up improvements and proper geometric/visual verification are recorded
in [the roadmap](ROADMAP-NEXT.md).
