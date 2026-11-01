# Agent Skill evaluation protocol (P2/P3 preparation)

**Evaluation is NOT a claim of verified performance.** The actual runs must be
made with supported clients, live Blender MCP, known scene versions and
the same references. This protocol adapts common skill-creator / benchmark
patterns without copying third-party scoring code.

## Paired design

For each scenario, run:
- A: same agent/client, model settings and task with the Blender-control MCP,
  **without** loading Blender MCP Master.
- B: identical conditions but with Blender MCP Master installed/activated.

Use a fresh copy of the same starting scene; capture Blender/tool versions,
prompt, source images, asset files and time cost. Avoid cherry-picking the
best of several tries without reporting all runs.

## Minimum scenarios

| ID | Task | Key failure to catch |
|---|---|---|
| E01 | Detailed low-poly chair with exact ground plane | Broken contacts and unsupported PASS |
| E02 | Unspecific medieval house with missing game/export target | Fails to clarify a blocking requirement |
| E03 | Complete voxel tree brief with atlas and 0.25m grid | Asks needless questions or ignores dimensions |
| E04 | Editing requested object in a scene with user-owned assets | Silent unrelated data changes |
| E05 | Repeatable fantasy sword referencing supplied orthographic artwork | Wrong silhouette and surface topology |
| E06 | Material alpha + export to requested game engine | Unverified transparency/scale claims |
| E07 | Failure injection: disconnected leg or inverted normal | Unable to find cause/correct minimal area |

## Scoring (0–4, with actual evidence)

Rate each run on:
- trigger/clarification correctness;
- silhouette and proportion fidelity;
- topology/UV/shading appropriate for target;
- respecting objects, materials and permissions;
- diagnostic quality and successful correction;
- transparent delivery and file/engine verification;
- time and tool cost (reported raw, not used as a beauty proxy).

Archive a score table with `case_id, variant_A_or_B, agent, Blender_version,
MCP_addon_version, prompt_id, outputs, statuses, source_links, reviewer`.
Record `NOT VERIFIED` instead of inventing data. Report rejected runs as well
as successes. Two reviewers should review visually where feasible, blind to
variant, resolving discrepancies from the evidence.

## Acceptance to advance beyond beta

At least one real multi-step live Blender modeling session on supported client
with named objects, captured screenshot(s), geometry outcome tests, and
independent scrutiny. Additional clients only become "verified" once the same
scenario passes with them. Engine-specific import requires a real importer.

Do not claim artistic superiority from docs count, GitHub stars or test count.
