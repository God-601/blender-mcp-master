# Blender MCP Master — 1.0 release and community launch plan

This is a **launch checklist**, not evidence that the skill has already passed artistic or cross-agent benchmarks.

## Positioning

**For:** Blender artists, game developers, and AI-agent developers who use a separate Blender-control MCP server.

**Claim we can support:** The Agent Skill provides modeling methods, explicit scene-safety guidance and technical validation scripts. It is **not** an autonomous Blender-control addon, universal 3D generator, or a guarantee of professional art.

**Product sentence:** "Blender MCP Master helps AI agents plan, build, inspect and safely refine Blender assets with measurable checks and honest delivery reports."

**Current working document:** [1.0 evidence ledger](RELEASE-1.0-EVIDENCE.md). Do not require T10 for the 1.0 decision; the detector is experimental. No comparative token/agent advantage is verified yet because the T08 trial lost an unsaved Blender scene. No package version bump, public Release or npm publication is authorized by a passing automated preflight.

## Release gate (do not mark without evidence)

- [ ] All required CI jobs green on the exact release commit, including Python static, the supported bpy matrix, npm, packaging and the targeted mutation campaign.
- [ ] A clean-install test of the candidate ZIP, the bundled directory structure, SHA-256 check, and discovery by at least one supported agent (the preflight workflow is NOT a Release).
- [ ] At least 5 real modeling benchmark assets: chair, sword, house, rock/tree and character or hard-surface panel.
- [ ] Save the actual .blend and front/side/three-quarter screenshots; store versions of Blender, agent and Blender-control MCP.
- [ ] Test scene protection by placing unrelated user-owned objects before the run.
- [ ] For one requested game-ready asset, import a produced FBX/GLB into an actual target engine and inspect scale, pivot, material/texture and topology.
- [ ] Compare at least one fixed benchmark with **skill enabled** versus **without skill** using the same prompt and scene, without cherry-picking.
- [ ] Have an independent reviewer assess actual visual quality; do not infer an artistic grade from a successful bpy script.
- [ ] Document known limitations and ensure install instructions accurately separate skill, optional read-only MCP resources and Blender-control MCP.
- [ ] Confirm the final release matches the capabilities listed in the README.

## Demo kit

1. Short screen recording (about 60–90 seconds): brief → agent kickoff question → blockout → real inspection → targeted correction → final Blender views.
2. Full reproducible session: unedited task prompt, run logs, .blend file, Blender/MCP/agent versions and screenshots.
3. Comparison showing same reference, same scene, same agent, with and without the skill. Label unverified claims honestly.
4. One-page install image or text: `npx skills add God-601/blender-mcp-master -g`, direct ZIP link and requirement for independent Blender-control MCP.
5. Minimal issue template for testers to report Blender version, agent, MCP, model, error logs, before/after files and expected result.

## Channels and timing

| When | Where | What to show |
| --- | --- | --- |
| Before release | Small Discord/Blender developer groups (with permission) | Ask for feedback on a real modeling benchmark |
| Release day | GitHub Release, README and skills.sh | Reproducible install, verified feature list, checksums |
| Release week | Blender Artists in an appropriate resource category | One real asset breakdown with screenshots, limitations and feedback request |
| Release week | Reddit/agent communities where permitted | A focused with/without demonstration, not mass cross-posting |
| Following weeks | YouTube, developer communities, issue tracker | Technical walkthrough, fixes, new verified agents, user-submitted examples |

Use current community rules before posting. Blender Artists has a self-promotion limit (see [policy](https://blenderartists.org/t/new-policy-on-self-promotion/1416473)); avoid repeating promotional posts. The [Skills CLI directory](https://skills.sh/) is relevant to agent skills. The [Blender Extensions platform](https://extensions.blender.org/about/) distributes a different product type (Blender extensions), and the current MIT skill is not the same as a GPL-compliant Blender addon.

## Concise launch text (English)

> Blender MCP Master 1.0 is an open-source Agent Skill for improving Blender modeling workflows. It guides connected AI agents through project clarification, staged modeling, scene-safe changes and measured geometry checks. It needs a separately installed Blender-control MCP. The release includes reproducible examples and a clear list of verified workflows and current limitations. Source, installation and feedback: https://github.com/God-601/blender-mcp-master

**Use this text only after 1.0 is truly released, and edit any claims that are not supported by test evidence.**
