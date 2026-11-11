# Blender MCP Master 2.0 candidate

The stable distribution remains 1.4.0. This draft covers the integrated 2.0
source and is subject to the [acceptance campaign](V2-ACCEPTANCE-CAMPAIGN.md)
and the [milestone gates](V1.5-V2.0-MILESTONES.md).

## Included engineering milestones

| Milestone | Capability |
| --- | --- |
| 1.5 | UV overlap, texel density and gutters, PBR channel audit and actual bake fixtures |
| 1.6 | Evaluated game budgets, GLB/FBX/OBJ workflows, target receipts and Godot probes |
| 1.7 | Seven specialist modules, bounded planning, independent reviews and recovery |
| 1.8 | Matched A/B harness with timing, provider usage, geometry results and preserved failures |
| 1.9 | Isolated ZIP installation, source and artifact checks, release readiness gates |

Blender 3.1 uses its legacy vertex-color and glTF APIs. The curvature recipe
and animation fixture detect the available API before use.

The native host coordinates protected-object fingerprints, one writer per
source path and a saved checkpoint. Independently inspect real images before
accepting visual quality. The Godot animation probe reports sampled bone
motion in an imported clip. Static GLB inspection handles surfaces with optional
UV and index buffers absent. Roblox evidence applies to the particular assets
and Studio sessions recorded in the [campaign](V2-CAMPAIGN-2026-11-08.md).

## Upgrade and recovery

Keep a copy of the installed 1.4.0 skill folder before trying the candidate.
Verify the archive against the supplied SHA256 checksum, extract its inner
`blender-mcp-master` folder and follow the [quickstart](QUICKSTART.md) for the
client's skill directory. Use a separate project or isolated skill directory
for side-by-side testing. Live scene control still uses the client's separately
configured Blender MCP addon and server. Verify tool availability before writes.

To revert, restore the saved skill folder. Recover an interrupted scene from
its verified checkpoint and compare the protected-object snapshot before
resuming the task. See [scene recovery](../references/crash-recovery-and-baselines.md).

## Final release checks

Require green CI for the candidate source and independent acceptance evidence.
Record exact source and package hashes, target-specific imports, Blender and
client versions, benchmark coverage and any unresolved failures. Confirm the
scope of actual client discovery and clean installation. After those checks,
update the package manifest and lockfile together and rebuild the versioned
ZIP from the final source. Publication requires the maintainer's authorization.
