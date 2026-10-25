# blender-mcp-master

An agent skill that makes AI agents better at modeling in Blender through MCP: cleaner topology, correct scale, good materials, game-ready exports and fewer wasted tool calls.

- Works with any agent that reads `SKILL.md` (Claude, Codex, Cursor, Gemini CLI, etc.).
- Built for the Blender MCP toolset: `execute_blender_code`, `look`, `get_scene_info`, `get_addon_status`, `search_assets`, `import_asset`, `generate_3d`.

## Structure

```
SKILL.md                 main instructions: golden rules, workflow, quality bar
references/              loaded on demand (hard-surface, organic, character-rig, environment,
                         stylized-lowpoly, materials, lighting-render, game-ready-export,
                         performance, troubleshooting, budgets)
scripts/                 paste-into-Blender utilities (validate, cleanup, origin, bevel/shade,
                         LODs, PBR material, export, scene setup)
```

## Tested

All scripts in `scripts/` were run against a live Blender 3.1.2 through MCP (apply/origin, bevel and shade, cleanup, validation checks, LODs, PBR material, FBX export). Version-specific code paths for Blender 3.2 and 4.x are written defensively but not yet tested on those versions.

## Install

Copy the folder into your agent's skills directory (for example `~/.claude/skills/blender-mcp-master/`), or point your agent at `SKILL.md`.

## License

MIT
