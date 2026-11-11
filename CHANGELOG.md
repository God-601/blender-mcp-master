# Changelog

## Unreleased — 2.0.0 candidate

- Consolidates modeling, retopology, optimization, UV, materials, export and
  validation specialists with scoped handoffs, stage checkpoints and a native
  Blender host. The installed skill retains its existing name and entrypoint.
- Includes the 1.5–1.9 engineering milestones for PBR/UV, destination delivery,
  independent reviews, matched A/B metrics and release evidence.
- Adds a reviewed agent-authored stage runner and a Godot probe for imported
  bone motion. Stage approval binds ownership and exact input bytes. Benchmark
  retries preserve prior artifacts and verify any reused generation and log.
- See [candidate notes and migration](docs/release-notes-2.0.md) for acceptance
  scope and instructions for reviewing a preflight archive.

## 1.4.0 — verified quality gates and safe asset delivery (2026-11-06)

- Introduced task-oriented MCP workflow guidance, conservative geometry/solid-containment diagnostics, and PNG silhouette reference measurements.
- Added PBR/UV channel review, game budgets, specialist review receipts, paired benchmark summarization and versioned release evidence checks. Foundations for later milestones; these tools do not independently certify artistic quality or agent orchestration.
- CI now runs real Godot 4.4.1 GLB import of an asset exported by Blender, plus real Cycles texture bake fixture with PNG pixel checks.
- User-tested Sofa V3 in Blender 3.1.2 and Roblox Studio: reported 3 LODs (3,860/1,930/964 tris), actual MeshParts and SurfaceAppearance channels detected, and user approval of visible result.
- Fixed Node >=20 metadata, ZIP/npm documentation and integration contents, PNG decoding bounds and clean-install package naming.

**Limits:** Sofa V3 user observations are not universal game-engine certification. Exact solid collision, Codex/Claude token savings, full game PBR material fidelity and autonomous specialist sessions are not independently demonstrated. See `docs/release-notes-1.4.md`.

## 1.3.0 — autonomous agent policy and measurable evaluation (candidate, 2026-11-04)

- Added tiered autonomous decision rules: safe read-only and owned reversible work, explicit approval for destructive/unowned edits, and stop conditions after ambiguous crashes or MCP tool failures.
- Added a compact session state ledger, schema rediscovery triggers and bounded retries without duplicate scene mutations.
- Added A13-01–A13-10 acceptance cases and a multi-client matched-trial protocol with clear evidence requirements for meaningful efficiency comparisons.
- Linked the policy to the skill entry point and existing progressive-reference and portability guides.

**Limitations:** live agent behavior, actual token reduction, multi-client compatibility, engine import and visual quality are NOT VERIFIED; protocol and documentation are not test results. No npm publication or public GitHub release is implied.

## 1.2.0 — game assets and design interviews (2026-11-04)

- Replaced the generic single-question modeling kickoff with an adaptive
  multi-question design interview, usually 2–6 relevant questions about
  missing visual style, silhouette, reference, materials and intended use.
  Never repeat specified constraints or restart on follow-up edits.
- Added read-only game asset preflight for evaluated triangles, scene-scale
  bounds, origin/pivot, UVs, material slots and missing texture files.
- Added conservative per-UV-island AABB gutter distance estimates in
  authored texture pixels with explicit REVIEW instead of claiming bakes pass.
- Expanded Blender GLB roundtrip tests to verify geometry dimensions,
  origin, UV channel and material presence without claiming game-engine import.
- Updated game export/UV/LOD guidance and added regression suites.

**Limitations:** game-engine import, normals/tangents in target, collision,
true texture baking and live-agent question behavior remain NOT VERIFIED.
See `docs/RELEASE-1.2-EVIDENCE.md`.

## 1.1.0 — safer geometric review and evidence (2026-11-02)

- Detect edge/corner/diagonal-only AABB proximity that cannot support a
  face-area surface joint; keep plausible face contact as REVIEW rather
  than inventing solid-intersection proof.
- Flag UV seams, material boundaries and shape keys in coplanar editable
  four-triangle X-fan candidates; do not auto-dissolve.
- Compare evaluated front/side/top/three-quarter convex-hull silhouette
  proxies on explicit original/optimized pairs before accepting polygon
  reductions; detail/artistic quality still needs inspected images.
- Verify the presence, names, formats and SHA-256 of real PNG/JPEG evidence
  files; never confuse image receipt checks with pixel analysis.
- Verify the expected saved .blend checkpoint and protected object names
  after reconnecting, before comparing archived protected property hashes.
- Add regression fixtures and expanded route documentation.

**Limitations:** no comprehensive 3D Boolean intersection solver,
automatic retopology repair, artistic/pixel inspection or certification
of Blender 3.x/engine imports. See `docs/RELEASE-1.1-EVIDENCE.md`.

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
