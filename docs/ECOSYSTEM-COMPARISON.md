# What we can learn from other prominent Agent Skills

Snapshot reviewed **2026-11-01**. This compares **documented design
patterns**, not independent benchmarks of artistic model quality. We did not
run competing agents on the same machine/reference, so performance rankings
are **NOT VERIFIED**.

| Project / pattern | What it does particularly well | Existing Blender MCP Master strength | Improvement we adopt |
|---|---|---|---|
| [arjun988/blender-skills](https://github.com/arjun988/blender-skills) | Broad **94-specialist** taxonomy; `blender-director` routes workflows, with explicit art/style and engine stages | One portable skill with detailed technical QA, evaluated geometry scripts and ownership checks | Lightweight workflow director and decision-specific loading; **do not replicate 94 standalone prompts** |
| [Anthropic skills / skill-creator](https://github.com/anthropics/skills) | Repeatable skill examples and evaluation of trigger behavior; with/without skill tests and reviewer evidence | Existing fixed Blender benchmark tasks, mutation suite and clear NOT VERIFIED statuses | Add paired skill-on/skill-off evaluation protocol and report template |
| [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) | Impact-prioritized task rules, concise guidance, fast installation, versioned discovery/release artifacts | Domain-specific modeling recipes, focused reference files, CI | Public quickstart, release ZIP checksums, ranked modeling QA and changelog |
| [obra/superpowers](https://github.com/obra/superpowers) | Controlled implementation flow, root-cause debugging and verification before completion | Regression tests, rollback safeguards, result-based geometry inspections | Add practical failure-triage rule and explicit correction/no-regression record |
| [Agent Skills open specification](https://agentskills.io/specification) | Small SKILL entrypoint with progressive disclosure and self-contained scripts/references | Already conforms to YAML frontmatter and split reference design | Keep new specialist content **in references**, not inside an oversized SKILL.md |

## Strategy choices

1. **Do not measure skill quality by skill count.** A hundred instruction
   folders cannot guarantee a better model than ten rigorously tested
   procedures. Adopt an intelligent *routing index* without duplicate prompts.
2. **Emphasize what we can actually test.** Technical mesh assertions, UV
   checks, scene integrity, export round trips and mutation tests are a
   distinctive advantage. Do not advertise visual quality based on CI.
3. **Add a measurable behavioral benchmark.** Evaluate whether an agent asks
   needed questions, avoids needless ones, uses safe collection isolation,
   corrects failed geometry, and reports uncertainty.
4. **Prefer original adaptations.** These guides are written for this
   repository's own Blender MCP tools, test harness and constraints. Links
   attribute inspirations; no third-party code or copyrighted instructions
   are copied.
5. **Avoid shipping hidden MCP configurations.** Users may have a different
   Blender-control addon, port, client or Blender version. Probe first,
   document what was verified, and never quietly replace their connection.

## Recommended order

- **Beta release:** install ZIP, docs, checksums and optional npm package.
- **P1:** read-only UV overlap/texel-density checks and real export validation.
- **P2:** controlled with/without skill, multi-client behavioral trials.
- **P3:** visual rubric and independent reviewers of actual .blend/render
  assets versus references.

See `references/workflow-director.md` and
`references/skill-evaluation-protocol.md` for the two immediate adaptations.
