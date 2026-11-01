# Getting started — Blender MCP Master

**What is installed?** An agent skill (`SKILL.md`, `references/`,
`scripts/`, `assets/`) and, optionally, a read-only npm MCP resource server.
**Not** a Blender-control MCP server or Blender addon. Live modeling requires
a separately connected Blender-control MCP provider.

## Windows: install the Agent Skill from ZIP

1. Open [GitHub Releases](https://github.com/God-601/blender-mcp-master/releases)
   and download `blender-mcp-master-0.2.0-beta.1.zip` and `SHA256SUMS.txt`
   from the same tagged release.
2. Verify the SHA256 against the checksum file (PowerShell):

   ```powershell
   (Get-FileHash .\blender-mcp-master-0.2.0-beta.1.zip -Algorithm SHA256).Hash
   ```

   Compare the printed hash with the ZIP's entry in `SHA256SUMS.txt`.
   Do not proceed on a mismatch.

3. Extract the ZIP:

   ```powershell
   Expand-Archive .\blender-mcp-master-0.2.0-beta.1.zip -DestinationPath .\blender-release
   ```

4. Copy the **inner** `blender-mcp-master` folder to a skills root supported by
   your agent. Examples for global Windows installations:

   ```powershell
   $Source = (Resolve-Path ".\blender-release\blender-mcp-master").Path
   $Dest = Join-Path $HOME ".agents\skills\blender-mcp-master"
   New-Item -ItemType Directory -Force (Split-Path $Dest) | Out-Null
   Copy-Item -Path $Source -Destination $Dest -Recurse -Force
   ```

   This example installs in `~\.agents\skills`, a cross-agent convention;
   some clients require a different folder (for example `~\.claude\skills`,
   `~\.cursor\skills`, `~\.config\opencode\skills` or
   `~\.kilocode\skills`). Consult the installed client's documentation
   and verify it discovers the skill. Do not paste the inner folder inside an
   existing `blender-mcp-master` folder.

   To refresh an existing installation safely, back up any local edits before
   replacing the folder. The ZIP contains source scripts, not an executable
   Blender addon.

## Install from GitHub using Skills CLI

```powershell
npx skills add God-601/blender-mcp-master -g
```

This uses the Skills CLI's GitHub source and does **not** need this project's
npm package. Current Skills CLI versions may require Node.js 22.20 or newer;
the ZIP method works without Node.js.

## Optional: start the npm resource server

If `blender-mcp-master` has been published on npm by the maintainer:

```powershell
npx -y blender-mcp-master@0.2.0-beta.1
```

Configure that command in the agent's **MCP server config** as a stdio server
if the agent supports external MCP servers. It exposes reference documents and
scripts, and it does **not** offer any write/control tool for a live Blender scene.
The Node server supports Node >=18.18. Its `skill`, `list`, and `--help`
subcommands work without MCP interaction when installed.

**A first npm publish requires a package owner's authorized npm login/token.**
The Release ZIP and GitHub skill installs are usable independently of npm.

## Set up separate Blender control

1. Choose a Blender-control MCP implementation compatible with your Blender
   version and platform.
2. Install/enable its addon and run its documented connection setup.
3. Check its connection status from the agent. Tool names and versions vary;
   do not blindly assume `look` or `execute_blender_code` is available.
4. Test read-only scene discovery before running any modeling code, and begin
   in a backup/scratch .blend rather than valuable unsaved work.

## First prompts

- "Use Blender MCP Master. Inspect my current scene without modifying it,
  tell me which Blender-control tools are connected, then create a separate
  stylized wooden chair in a new collection. Show orthographic views."
- "Use the measured vehicle recipe as a **starting point only**. Build a
  small low-poly cartoon car for a mobile game, wheelbase 2.1 m, and inspect
  wheel-ground contact without changing my existing objects."
- "Make a voxel tree with my project grid unit of 0.25 m and an 8-color
  palette. Check exposed faces, UV island layout and export warnings."

The agent should ask a focused question only when missing information would
materially change the result.

## What counts as success?

A script completing is not proof of a finished asset. Request measured
dimensions, evaluated triangle counts, explicit property/scene changes,
actual Blender screenshots where available, and test status
`PASS | ISSUE | NOT VERIFIED`. Never infer engine-import or artistic quality
from a successful Python run.

See [SKILL.md](../SKILL.md), [benchmarking](../references/benchmarking.md),
and [P0 scene protection](../references/p0-integrity.md).
