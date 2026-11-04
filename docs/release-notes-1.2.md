# Blender MCP Master v1.2.0 — Game Asset Workflow & Design Interview

Blender MCP Master is an open-source Agent Skill for guiding AI-assisted
Blender modeling; it is NOT a Blender-control MCP server or Blender addon.
A separate Blender-control MCP is needed for live scene interaction.

## What changed since v1.1.0

### Design clarification that actually understands your model

The agent now asks **several focused design questions** for new modeling
projects instead of only "Can I proceed?" or "Posso seguir?". Questions
cover visual references, silhouette, proportions, material/palette,
important details, game/animation use, and missing constraints. The
number adapts to the asset's complexity (normally 2–3 for simple props,
4–6 for more detailed work). Previously supplied answers are reused;
users who delegate creative direction are not forced into a questionnaire.
Follow-up edits do NOT restart the interview.

### Static asset preflight for games

The new read-only `scripts/game_asset_preflight.py` measures **evaluated**
triangle counts, dimensions, origins/pivot locations, mesh UV presence,
material-slot counts and texture image-file availability. It uses explicit
named targets and **project budgets, not invented engine limits**.
Blender scripts never claim real Roblox, Godot, Unity or Unreal validation.

### UV island spacing

The new `scripts/uv_island_gutter_audit.py` groups UV-continuous polygons
into islands and measures conservative UV-island AABB gutter distance in
pixels for an authored atlas size. It flags close island pairs for REVIEW
without changing UVs. A measured adequate bound is not an image bake,
shader-quality or mipmap certification. Use `uv_diagnostics.py` separately
for actual UV positive-area overlap and texel density.

### Stronger GLB checks

Blender runtime tests exercise export to GLB followed by reimport into a
clean Blender scene, comparing world bounds, origin, UV map, evaluated
triangles and material presence. This verifies **Blender-to-Blender**
parseability and selected static data, not an import to a game engine.
Other FBX, normal/tangent-space, colliders and LOD behaviors must still
be verified in the real destination.

## Installation

Download `blender-mcp-master-1.2.0.zip` and `SHA256SUMS.txt` from the
[GitHub v1.2.0 Release](https://github.com/God-601/blender-mcp-master/releases/tag/v1.2.0).
Verify SHA-256 and install the included `blender-mcp-master` folder in
your agent's supported skills directory.

Or use the Skills CLI (not dependent on a separately published npm package):

```bash
npx skills add God-601/blender-mcp-master -g
```

The optional read-only npm MCP resource-server archive `.tgz` is attached
to the GitHub Release. Only use `npx -y blender-mcp-master@1.2.0` if that
specific version has been separately published to npm.

See [QUICKSTART](https://github.com/God-601/blender-mcp-master/blob/v1.2.0/docs/QUICKSTART.md)
and [v1.2 evidence](https://github.com/God-601/blender-mcp-master/blob/v1.2.0/docs/RELEASE-1.2-EVIDENCE.md).

## Measured scope and limitations

The automated matrix targets Blender `bpy` 4.2, 4.5, 5.0, 5.1 and 5.2,
plus Python and Node/npm checks and SHA256-verified isolated ZIP installation.
These tests do not certify:
- actual engine import, real GPU FPS, draw calls, engine collision or LOD;
- Blender 3.1.2 support, every agent client and every MCP provider;
- artistic output quality or real texture-baking/gutter correctness;
- guaranteed polygon/contact validity based only on AABB geometry.

An agent still needs to review the model visually and check the actual
destination before making a game-ready PASS claim.

The versioned ZIP and checksum are the primary release deliverables.
