# Token-efficient agent execution (tool-first, evidence-first)

**Goal:** reduce unnecessary context, shell calls and repeated work without weakening the Blender MCP Master safety or quality gates. This is an agent policy, not a runtime token counter. The skill cannot measure actual API billing unless the client exposes token usage.

## Preferred workflow

1. **GENERAL KICKOFF stays mandatory once per NEW modeling project.** Reuse the user's known brief and ask one nonredundant open question. Do not restart the interview for refinements or retries.
2. **Discover once per client/session:** Blender version, MCP tools/schema, scene state and ownership. Repeat discovery only after a relevant environment change.
3. **Route before reading:** choose only the relevant modeling discipline and one cross-cutting validation/safety guide. Don't load all of `references/` or unrelated Blender manuals.
4. **Prefer semantic tools to generic Bash:**
   - Connected Blender-control MCP tools for scene inspection and safe edits.
   - Native file read/search/patch tools for repository files when available.
   - `get_blender_reference_outline` followed by `get_blender_reference_excerpt` when using this repository's optional read-only MCP resource server.
   - Shell/Bash only where it is the appropriate tool, and then use targeted paths, bounded output, and small reproducible commands; don't pipe the entire source tree into the model.
5. **Use deterministic scripts for repeated mechanics:** existing safe `scripts/` for evaluated counts, UV, export, geometry and optimization. Read the *complete script* and its configuration/safety contract before executing a script that mutates Blender.
6. **Keep concise state:** record known requirements, owned objects, last successful checkpoint, actual observations, blocked/unverified checks and exact next action. Do not reprint unchanged logs or code after every tool call.
7. **Bound routine output:** only object names, relevant dimensions/counts, statuses and warnings for success paths. On failure, capture tracebacks as necessary for root-cause analysis; never hide errors or prematurely truncate evidence.
8. **Inspect at meaningful gates:** initial blockout, geometry-changing refinement, visual/material changes and delivery. Don't call image capture after a trivial no-op, but never skip required visual validation to save tokens.
9. **One mutation per logical step** remains the default. Token savings do not authorize a giant blind Python script or destructive batching.

## Reference reads with the read-only MCP resource server

The package retains backward-compatible full-document tools. For an uncertain issue, prefer:

- `get_blender_reference_outline(name)` → headings and exact 1-based line numbers.
- `get_blender_reference_excerpt(name, startLine, maxLines)` → bounded line window (1–80 lines, max 6000 displayed characters); read more only if required.
- `get_blender_reference(name)` → entire file when the complete context is actually needed.

These resource tools only serve files. They do **not** call Blender, execute scripts, inspect images or bypass user approval.

## Efficiency evaluation, not slogans

For the same prompt, model, Blender scene, MCP and tool permission set, compare baseline versus tool-first workflow. Record:

| Metric | Why |
| --- | --- |
| Actual input/output/billed tokens, if exposed | Only reliable way to quantify token savings |
| Number of reference bytes loaded | Approximate context pressure, **not** billed tokens |
| Shell calls and total MCP/tool calls | Diagnostic, not an optimization target by itself |
| Repeated file reads and repeated questions | Avoidable waste |
| Geometry errors, failed gate count, time, and output quality | Prevents false efficiency from skipped work |
| Preserved user objects and actual visual evidence | Non-negotiable safety and quality |

Do not invent percentage reductions or infer token usage from character counts. Tokenization and tool wrappers differ among agents.

## Research basis

- [Anthropic Agent Skills: progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Vercel: Agent Skills explained, scripts and on-demand references](https://vercel.com/blog/agent-skills-explained-an-faq)
- [OpenAI: shell + skills + compaction practices](https://developers.openai.com/blog/skills-shell-tips)
- [Skills.sh: Agents Progressive Disclosure](https://www.skills.sh/caph-dev/agents-progressive-disclosure/agents-progressive-disclosure)
- [Skills.sh: Token Optimization](https://www.skills.sh/i-onlabs/claude-code-skills/token-optimization)

Read existing modeling standards and P0 scene integrity even when aggressively reducing context. Context efficiency cannot justify missing evidence.
