# Blender MCP Master v1.4.0

This release consolidates the quality/safety infrastructure implemented since
v1.3.0. It includes foundations for future v1.5–v1.9 milestones, **not**
finished or separately published versions of those milestones.

## Highlights
- Progressive skill routing and compact main instruction file; more references
  can be loaded on demand. This does not prove actual model-token savings.
- Advisory MCP workflow planning, conservative evaluated component fit and
  potential solid-containment diagnostics. Reports candidates, never guarantees
  that an arbitrary joint is correctly manufactured.
- Reference-mask silhouette comparison (IoU, bounds, centroid) and a real-image
  review procedure. No automated artistic-quality certification.
- PBR channel/UV color-space diagnostics; explicit static game-mesh budgets,
  export safety and evidence-gated modeling and specialist reports.
- Godot 4.4.1 headless GLB importer CI against a **Blender-exported** static
  UV/material mesh; actual Blender Cycles emission bake tested, PNG saved and
  pixel values inspected. These are reproducible fixture tests, not full
  production artistic review.
- Read-only Roblox Studio MeshPart inspector. A user tested a Sofa V3 with
  LOD0 3,860, LOD1 1,930 and LOD2 964 triangles in Blender 3.1.2, then
  confirmed three MeshParts with four PBR map slots in Roblox Studio 0.746
  and reported satisfactory visual appearance. This is user-reported
  acceptance of **that asset**, not a general certification of all imports.
- More robust PNG safety bounds, Node >=20 dependency support, npm documentation
  packaging and version-derived clean-install ZIP preflight.

## Installation

Download `blender-mcp-master-1.4.0.zip` from this GitHub release, verify
`SHA256SUMS.txt`, and install the uncompressed skill directory in your
agent's supported skills directory. The optional MCP resource server can be
run from the npm tarball using Node >=20; **it does not itself control Blender**.
See [QUICKSTART](../docs/QUICKSTART.md) in the source tree.

## Verified scope and limits

**Repository CI:** tests on bpy 4.2.23, 4.5.15, 5.0.1, 5.1.2 and 5.2.3;
Node/npm, package checks and isolated ZIP install; real Godot importer and
Cycles fixture. CI on the release SHA must be green before publication.

**External user observation:** Sofa V3 looked good in Roblox Studio and
exposed 3 MeshParts with SurfaceAppearance maps. The supplied Blender report
claims source geometry integrity, no non-manifold edges and GLB roundtrip PASS.
These are supplied observations; the release pipeline does not reexecute
the user's local Blender 3.1.2 file.

**Not independently verified:** universal Roblox Studio/Unity/Unreal support,
in-game collision and frame-rate improvement, full normal/AO atlas baking
fidelity, real Codex/Claude usage-token savings, live autonomous subagent
orchestration or precise collision detection for arbitrary meshes.

Future 1.5–1.9 and v2 milestones remain described in
[docs/V1.5-V2.0-MILESTONES.md](V1.5-V2.0-MILESTONES.md).

No npm registry publication is part of this GitHub release.
