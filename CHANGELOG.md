# Changelog

## 1.0.0 — first stable release (2026-11-02)

- Integrated CI-tested UV diagnostics, copy-first guided retopology,
  mandatory new-project kickoff and conservative material/geometry audits.
- Added explicit-pair fit/penetration candidate checks and contact-plane
  guidance; AABB/BVH cannot alone prove a correct mechanical joint.
- Added a narrow read-only coplanar X-fan diagnostic (experimental;
  T10 intentionally not a 1.0 release gate).
- Added protected-object scene fingerprints and read-only before/after
  comparison; saved-scene checkpoint and Blender crash-recovery guidance.
- Invalidated paired token/efficiency claims when scene-preservation evidence
  is missing or the run is interrupted or reconstructed.
- Clarified glTF reimport seam splits vs real topology loss, and tri-budget
  reductions that visibly damage stylized assets.
- Prepared nonpublishing release-readiness ZIP checks and disabled
  automatic legacy beta publishing on `main/package.json` changes.
- Tracked T01–T09 evidence and known unverified aspects, and added
  isolated ZIP-install smoke checks on the integrated main branch.

**Limitations:** live multi-client discovery, real engine import, independent
artistic scoring, reliable token savings and Blender 3.x CI remain
NOT VERIFIED. Clean isolated ZIP installation passed on main; T10 is
experimental, not a release gate. See `docs/RELEASE-1.0-EVIDENCE.md`.


## 0.2.0-beta.1 — first public beta

- Cross-agent Blender skill with focused model-type and workflow routing.
- Clarification gate, safe copy-first modeling methods, audited material
  and scene protection and error recovery.
- Evaluated mesh inspection, reproducible mutation campaign and five-version
  Blender bpy CI matrix.
- Measured example scripts for voxel atlas, car, table and stylized sword.
- New public quickstart, standalone ZIP release with SHA256 checksums and
  optional npm MCP resource package.
- Ecosystem comparison, workflow director and paired evaluation template.

**Limitations:** no certified live-client Blender MCP execution, artistic output
ratings, 3.x runtime matrix or complete game-engine export testing. The npm
package is optional and does not control Blender.

## 0.1.0 — development prototype

- Source skill and read-only MCP documentation/script resource tools.
