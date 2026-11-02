# Blender MCP Master v1.0.0

**First stable release of the Blender MCP Master Agent Skill.**

Blender MCP Master guides AI agents that already have access to a separate
**Blender-control MCP**. It supplies modeling workflows, geometry/UV checks,
copy-first scene protection, validation scripts and clear limits on what was
actually verified. It is **not** a Blender addon or a Blender-control MCP server.

## Highlights

- Focused agent kickoff, task planning, blockout, modeling and inspection.
- Read-only checks for evaluated geometry, materials, UV overlap/density and
  component fit candidates, with real `PASS / ISSUE / REVIEW / NOT VERIFIED`
  distinctions.
- Guided retopology with source-copy preservation and failure rollback.
- Protected-object snapshots, before/after comparison, crash-safe checkpoint
  guidance and measured optimization workflows.
- Clear distinction between editable Blender faces and the triangulation
  and per-seam vertex splits expected in GLB/glTF.
- An optional **read-only MCP resource server** for guides and scripts.
- Standalone ZIP distribution with SHA-256 checks, link verification and
  isolated clean-install validation in CI.

## Installation

**Agent Skill:** Download
[`blender-mcp-master-1.0.0.zip`](https://github.com/God-601/blender-mcp-master/releases/download/v1.0.0/blender-mcp-master-1.0.0.zip)
with [`SHA256SUMS.txt`](https://github.com/God-601/blender-mcp-master/releases/download/v1.0.0/SHA256SUMS.txt).
Verify the hash and extract the inner `blender-mcp-master` folder into
your supported agent skills path, such as
`~/.agents/skills/blender-mcp-master/` on Codex.

**Skills CLI:**

```bash
npx skills add God-601/blender-mcp-master -g
```

**Optional npm resource server:** The GitHub Release also includes
`blender-mcp-master-1.0.0.tgz`. If npm's separate publication succeeds,
`npx -y blender-mcp-master@1.0.0` serves the references over stdio.
Neither the npm package nor the ZIP controls Blender directly.

See [Quickstart](https://github.com/God-601/blender-mcp-master/blob/v1.0.0/docs/QUICKSTART.md).

## What has been tested

- Python and mutation/regression tests on Blender `bpy` 4.2, 4.5, 5.0,
  5.1 and 5.2, plus Node/npm package tests.
- Checksum-verified ZIP extraction into a clean isolated agent-style home,
  skill metadata and bundled resource checks, and execution of a read-only
  helper after installation.
- Practical modeling scenarios T01–T09 reported from a Blender 3.1.2
  environment, with known limitations documented in the
  [evidence ledger](https://github.com/God-601/blender-mcp-master/blob/v1.0.0/docs/RELEASE-1.0-EVIDENCE.md).

## Known limitations

- The isolated ZIP install test does **not** prove that a live Codex/Claude
  application discovered the skill or connected to a Blender-control MCP.
- Blender 3.1.2 was used in reported user tests but is not certified by the
  official CI version matrix.
- UV padding, baking, full solid-intersection checks, mechanical fit,
  downstream game-engine imports and artistic scoring remain unverified.
- The T08 skill-on/off efficiency comparison was **inconclusive** after an
  interrupted unsaved Blender session. No measured token savings, FPS gains
  or superior artistic output are claimed.
- The four-triangle planar X-fan inspector is a narrow experimental
  diagnostic; T10 was not part of the release criteria.

For updates and planned next steps, see
[post-1.0 roadmap](https://github.com/God-601/blender-mcp-master/blob/v1.0.0/docs/ROADMAP-NEXT.md).
