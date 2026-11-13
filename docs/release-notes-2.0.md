# Blender MCP Master 2.0.0

Blender MCP Master 2.0 brings the 1.5–1.9 development milestones into one
installable Agent Skill. It helps an agent plan, build, inspect and deliver
Blender assets. Live editing requires a separately configured Blender-control
MCP and addon.

## What's included

- Seven specialist modules for modeling, retopology, optimization, UVs,
  materials, export and validation. Plans load task-specific guides and
  support independent, evidence-backed reviews.
- Protected-object comparisons, exclusive writer leases and recovery
  checkpoints. Stage files pack supported dependencies in an isolated Blender
  process. Writes stop when a dependency is missing, unpackable or has unsaved
  image pixels.
- UV/PBR diagnostics and scoped GLB, FBX and OBJ export. The UV audit catches
  folded faces and positive-area overlaps along aligned edges. FBX embeds
  supported image textures. Export rejects directories and symlinks as output
  destinations.
- A read-only MCP resource server with bounded reference excerpts and task
  routing. Material and UV requests follow the same route as the Python CLI.
- Reproducible validation tools for game imports, visual corrections and A/B
  comparisons. See the [milestone ledger](V1.5-V2.0-MILESTONES.md).

## Install or upgrade

Download **blender-mcp-master-2.0.0.zip** and **SHA256SUMS.txt** from the
[GitHub release](https://github.com/God-601/blender-mcp-master/releases/tag/v2.0.0).
Compare the ZIP's SHA-256 with the checksum file, extract it and install its
inner `blender-mcp-master` folder in your client's skills directory. Back up
your previous skill folder before replacing it. The
[quickstart](QUICKSTART.md) covers Windows and setup for Blender control.

For the Skills CLI, install the tagged source:

```sh
npx skills add God-601/blender-mcp-master@v2.0.0 --skill blender-mcp-master -g
```

The optional read-only resource server runs from the same GitHub tag:

```sh
npx -y "github:God-601/blender-mcp-master#v2.0.0"
```

This release is distributed on GitHub. Roll back by restoring your backed-up
skill folder or reinstalling the [v1.4.0 ZIP](https://github.com/God-601/blender-mcp-master/releases/download/v1.4.0/blender-mcp-master-1.4.0.zip).
To recover a scene after an interruption, use its verified checkpoint and
compare the protected-object snapshot before resuming.

## Verification scope

The release build requires successful Blender, Node, Godot and installation
checks for its exact source commit. The archive includes the skill and its
bundled resources. The GitHub release attaches the checksum and a clean-install
report.

Live acceptance has covered a scoped workflow in Blender 3.1.2 with the
Blender-control MCP, including a Codex client creating a mesh, checking protected
objects, and validating the result. A practical GLB also imported into Godot
4.6.3. These observations apply to the tested operations and assets.

Claude Code discovered the skill, with model execution pending authentication.
The latest Roblox GLB was checked in Blender. A physical collision, PBR and
appearance check in Studio remains open for that asset. The previous Studio
campaign provides separate evidence for earlier assets. The controlled A/B
campaign established comparable technical results and did not demonstrate
token savings. The [engineering evidence](V2-EVIDENCE.md) describes the
remaining production and client acceptance work.

## Review a preflight archive

The [preflight workflow](https://github.com/God-601/blender-mcp-master/actions/workflows/release-readiness.yml)
produces a ZIP for isolated source review. Keep its ZIP, checksum and
clean-install report together. Record the workflow's checked-out commit and
verify the archive using `scripts/clean_install_smoke.py` from that revision.
