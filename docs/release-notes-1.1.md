# Blender MCP Master v1.1.0 — Safer Geometry & Quality Checks

Blender MCP Master is an open-source Agent Skill that helps AI agents plan,
model, inspect and validate 3D assets. **It is not a Blender-control MCP
server or Blender addon.** A separate, compatible Blender-control MCP is
needed for editing a live Blender scene.

## Changes since v1.0.0

- **More reliable joint candidates:** explicit `surface_joint` checks
  now reject bounds that only meet at an edge/corner or diagonal. Plausible
  face-area contact remains REVIEW, not falsely certified.
- **Topology review:** planar four-triangle X-fans now identify potential
  UV seams, material boundaries and shape-key constraints so agents know
  when they must preserve geometry until a human reviews it.
- **Optimization guard:** new `compare_asset_silhouettes.py` measures
  before/after evaluated convex-hull projection area and extents across
  front, side, top and three-quarter views. It warns about changes but
  cannot judge lost details or real artistic quality.
- **Visual review receipts:** new `visual_evidence_manifest.py` verifies
  explicitly named real PNG/JPEG image files, safe paths and SHA-256 hashes.
  It never pretends that file checks equal visual inspection.
- **Safer crash recovery:** `scene_recovery_probe.py` checks an expected
  saved checkpoint path and explicitly protected object names/types after
  reconnecting. The scene still requires a separate before/after integrity
  comparison.
- Expanded Blender runtime regressions, docs and task routing.

## Installation

Get [`blender-mcp-master-1.1.0.zip`](https://github.com/God-601/blender-mcp-master/releases/download/v1.1.0/blender-mcp-master-1.1.0.zip)
and [`SHA256SUMS.txt`](https://github.com/God-601/blender-mcp-master/releases/download/v1.1.0/SHA256SUMS.txt)
from the same GitHub Release. Verify the checksum, extract the included
`blender-mcp-master` folder and install it under your client's skills
directory, for example `~/.agents/skills/blender-mcp-master/`.

Alternative with the [Skills CLI](https://skills.sh/):

```bash
npx skills add God-601/blender-mcp-master -g
```

Optional read-only MCP resource server: a `.tgz` archive is attached
to the GitHub Release. Only use `npx -y blender-mcp-master@1.1.0` if
that version is separately published on npm. The skill itself does not
need npm publication.

Detailed setup: [QUICKSTART](https://github.com/God-601/blender-mcp-master/blob/v1.1.0/docs/QUICKSTART.md).

## Evidence and limitations

Automated tests cover Python static/regression checks, the Blender bpy
4.2/4.5/5.0/5.1/5.2 matrix and the Node/npm resource-server package.
A SHA256-verified standalone ZIP is extracted into a clean isolated
skills directory and a safe installed helper is executed.

These checks **do not** certify support for every agent or Blender 3.x,
correct rendered images, 3D solid/Boolean penetrations, actual destination
game-engine imports or token savings. Edge/corner vs face detection uses
**world-space AABB bounds** and is not an exact mesh-to-mesh intersection
solver; the silhouette guard is based on **convex hulls**, which cannot
detect missing interior/concave details. File hashes are not image
recognition. Actual visual review and relevant export tests remain
necessary for delivery claims.

The real-agent T10 editable X-fan exercise is not claimed to have passed
unless externally exercised. Existing T08 efficiency results were
inconclusive and no measured speed/token gains are advertised.

See [v1.1 evidence and scope](https://github.com/God-601/blender-mcp-master/blob/v1.1.0/docs/RELEASE-1.1-EVIDENCE.md)
and [next-version roadmap](https://github.com/God-601/blender-mcp-master/blob/v1.1.0/docs/ROADMAP-NEXT.md).
