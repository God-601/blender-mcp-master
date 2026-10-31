# Cross-agent compatibility verification

## Important distinction

A skill file can be readable by an agent without that agent being able to control Blender. Compatibility requires both the skill and a working Blender-control MCP integration.

## Verification protocol

For each client, use a fresh session and record:

1. Client and version.
2. Skill installation path and whether the agent loaded the skill instructions.
3. Blender-control MCP server/addon and version.
4. Exact tools discovered and their schemas.
5. Results of scripts/capability_probe.py.
6. Scene inspection and geometry execution.
7. Visual inspection using the client's actual image/viewport tool.
8. Run at least B01 or B02 from references/benchmark-prompts.md.
9. Run the technical inspection and benchmark reports.
10. Record failures, limitations, and evidence links.

## Current evidence status

| Client | Skill readable | MCP tools mapped | Blender construction | Visual inspection | Benchmark |
|---|---|---|---|---|---|
| Codex | NOT VERIFIED in this PR | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| Claude Desktop | NOT VERIFIED in this PR | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| Cursor | NOT VERIFIED in this PR | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| OpenCode | NOT VERIFIED in this PR | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |
| Kilo Code | NOT VERIFIED in this PR | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED |

Do not change a cell to PASS based only on installation, documentation, or the presence of a tool with a familiar name. Attach evidence from an actual session.

## Known portability boundary

The scripts in this repository use Blender Python (bpy/bmesh); they are not standalone host-side Python programs. An agent must have a code-execution capability connected to the live Blender process, or a documented equivalent adapter. Tool names and schemas must be discovered per client and session.
