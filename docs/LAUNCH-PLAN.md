# Blender MCP Master — 1.0 release and community launch plan

This is a **launch checklist**, not evidence that the skill has already passed artistic or cross-agent benchmarks.

## Positioning

**For:** Blender artists, game developers, and AI-agent developers who use a separate Blender-control MCP server.

**Claim we can support:** The Agent Skill provides modeling methods, explicit scene-safety guidance and technical validation scripts. It is **not** an autonomous Blender-control addon, universal 3D generator, or a guarantee of professional art.

**Product sentence:** "Blender MCP Master helps AI agents plan, build, inspect and safely refine Blender assets with measurable checks and honest delivery reports."

**Current working document:** [1.0 evidence ledger](RELEASE-1.0-EVIDENCE.md). Do not require T10 for the 1.0 decision; the detector is experimental. No comparative token/agent advantage is verified yet because the T08 trial lost an unsaved Blender scene. No package version bump, public Release or npm publication is authorized by a passing automated preflight.

## Minimal 1.0 release gate (maintainer-approved scope)

- [x] PRs #29–#32 integrated; #28 functionality included without reintroducing the old SKILL.md.
- [x] Integrated `main` Python, Blender bpy 4.2/4.5/5.0/5.1/5.2, npm and regression CI passed.
- [ ] Run a **clean, isolated ZIP skill installation** from the candidate with SHA256 verification; inspect its JSON smoke report.
- [ ] Confirm ZIP/README/release notes and advertised limitations are accurate on the final candidate commit.
- [ ] Obtain explicit maintainer authorization for any stable tag, GitHub Release or npm publication.

**Not release blockers by maintainer decision:** two-agent acceptance,
actual engine import, independent artistic review, repeated A/B token
benchmark, Blender 3.x CI and T10. These remain **NOT VERIFIED** where
not actually tested. The automated isolated directory installation does
not demonstrate real client discovery or Blender-control MCP connectivity.
Never claim those capabilities were validated merely because CI passed.

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
