# Universal MCP capability mapping

## Principle

The skill must reason about capabilities, not hard-coded tool names. Different MCP servers and
agents expose different names, argument schemas, and feature subsets. The agent must inspect the
tools actually available in its session and map only verified tools.

The repository does not implement or replace a Blender-control MCP server.

## Capability matrix

| Semantic capability | Typical purpose | Known example | Required? |
|---|---|---|---|
| addon.status | Blender/addon version and health | get_addon_status | Recommended |
| scene.inspect | Query objects, transforms, topology, materials | get_scene_info | Required before scene edits when available |
| visual.inspect | Capture viewport/render views | look | Required for visual claims |
| geometry.execute | Run Blender Python or operations | execute_blender_code | Required for scripted construction |
| asset.search | Search external/local asset libraries | search_assets | Optional |
| asset.import | Import selected assets | import_asset | Optional |
| asset.generate | Generate external base meshes | generate_3d | Optional; may consume quota |
| scene.save | Save project state | varies by integration | Only when available and authorized |

## Discovery procedure

1. Enumerate tools exposed by the active agent.
2. Inspect descriptions and parameter schemas; do not infer from names alone.
3. Map each available tool to one or more semantic capabilities.
4. Record exact invocation name and required parameters for the current task.
5. Probe addon status and scene state if those capabilities exist.
6. Mark missing capabilities as unavailable and select a documented fallback.
7. Never claim visual inspection if only code execution is available.

## Fallback behavior

- No addon status: inspect scene and query Blender version through code execution if possible.
- No scene-info tool: query bpy.data.objects and scene settings through code execution.
- No visual tool: render or capture only if the environment supports it; otherwise mark visual inspection NOT VERIFIED.
- No code execution: do not claim the skill can build geometry in the current session.
- No asset search/import: construct locally or explain the missing external resource capability.
- No external generator: do not block procedural or manual construction.

## Invocation discipline

- Preserve the actual schema and argument names of the selected tool.
- Do not send arguments from one MCP implementation to another.
- Keep tool-specific knowledge in the current session, not as a universal assumption.
- Re-discover after changing MCP server, agent, or session.
- Report which capabilities were available when delivering the asset.

`scripts/capability_probe.py` can report Blender-side API availability (mesh datablocks, curves, Geometry Nodes, modifiers, and save operator). It cannot discover the agent MCP tool list, prove that a client can invoke a tool, or capture images. The active agent must still enumerate its tools and map their actual schemas to the semantic capabilities above.

## Compatibility evidence

A compatibility claim must identify:
- agent/client
- skill installation method
- MCP server and version
- Blender version
- capabilities tested
- benchmark task
- pass/fail evidence

A skill file being readable by an agent is not proof that the agent can control Blender.
