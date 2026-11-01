# Blender MCP Master v0.2.0-beta.1

**First public beta.** This is an Agent Skill for guiding AI agents in Blender
modeling, plus an **optional read-only MCP resource server**.
It does **not** control Blender directly. Use a separate Blender-control MCP.

## Choose the correct install path

**Agent Skill ZIP:** download `blender-mcp-master-0.2.0-beta.1.zip`, verify
`SHA256SUMS.txt`, extract the contained `blender-mcp-master` directory into
your agent's supported skills path. Read
[Quick start](https://github.com/God-601/blender-mcp-master/blob/main/docs/QUICKSTART.md).

**GitHub Skills CLI:** `npx skills add God-601/blender-mcp-master -g`.
Uses GitHub and does not depend on publishing this repo's npm package.

**npm resource server, if published:** `npx -y blender-mcp-master@0.2.0-beta.1`.
Provides read-only text resources over stdio MCP, **not** Blender control.

## Evidence and limitations

- 185+ Python tests across five supported Blender bpy versions in CI and Node
  package tests across Node 18/20/22 (see current GitHub Actions run).
- Geometric checks, copy-first edits, object ownership checks and explicit
  unverifiable outcomes are included.
- Blender 3.x, actual mixed-agent live MCP sessions, artistic quality,
  animation/rig export and game-engine-specific imports are **NOT VERIFIED**.
- No claim that every asset looks professional or passes downstream production.

## Changes since initial prototype

- Revised professional guides, clarification gate and safe scene-edit policies.
- Read-only evaluated geometry inspections, mutation tests and controlled examples.
- Source-backed proportion and voxel atlas demonstration scripts.
- Standalone ZIP + npm tarball, verification checksums, Windows-first install docs.
- Briefly documented comparable agent-skill patterns and evaluation guidance.

This is a beta intended for reproducible user feedback, not a finished
Blender-control addon or animation engine.
