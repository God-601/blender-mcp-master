# Contributing

Blender MCP Master is a beta Agent Skill intended for reproducible modeling
experiments. Contributions should improve actual outcomes, not inflate the
number of files or list of supported agents.

## Before submitting a PR

1. Describe the modeling failure and the intended user-facing behavior.
2. Work on a branch; preserve existing scene objects and scripts.
3. Add a **behavioral regression** (e.g. incorrect winding/UV/material output,
   unsafe side effect, failed export) that detects the issue before the fix.
4. Run `python -m unittest discover -s tests -v`, `npm ci`, `npm test`,
   `npm pack --dry-run`. Runtime tests require a compatible installed bpy.
5. Include actual command/output evidence. Do not claim visual quality or
   client compatibility without a live Blender capture and artifact.
6. Maintain the explicit copy-first/no-global-destructive defaults, avoid
   embedding secrets, and attribute adapted external ideas.
7. Re-check documentation links and release compatibility before publishing.

## Reports worth filing

A minimal prompt, Blender & addon/client versions, scene setup and saved
sample .blend (without private data), screenshots, expected versus observed
geometry, redacted logs, and how the issue can be reproduced. If a test
wasn't run, label it NOT VERIFIED.

MIT licensed. Third-party asset packs, sample textures, software packages
and code remain subject to their own licensing.
