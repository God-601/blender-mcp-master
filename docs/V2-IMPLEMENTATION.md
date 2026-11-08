# V2 implementation plan and scope

The current request authorizes implementation and staged PRs. Stable version
stays 1.4.0 until the full acceptance campaign passes. The user's follow-up
authorizes review and merge; publication remains subject to the evidence gates.

Baseline inspected: `2affc0b0cfa2eff5743270b2e61c4b0cd2787641` (main).
Existing builders, scoped mutation guards, UV/PBR/geometry audits, visual
iteration checks, engine probes and read-only MCP tools remain supported.

## Architecture and stages

- [x] Stage 1: machine-readable seven-module registry reusing existing scripts
  and guides, deterministic on-demand planner, read-only MCP discovery.
  Test actual resource resolution, simple single-agent routing, complex module
  selection and invalid briefs. No duplicated specialist manuals.
- [x] Stage 2: host-adapter execution, sequential scene writer, independent QA,
  explicit capabilities, scene/checkpoint identity, local evidence hashes,
  default dry-run, fail-stop and structured handoffs. Test real subprocess
  dispatch with deterministic workers, malformed/missing evidence, timeout,
  scene drift and unavailable adapters. Test doubles are not live AI trials.
- [x] Stage 3: CI evidence artifacts, exact-SHA release gate coverage,
  distribution checks, README/roadmap and reproducible integration instructions.
  Keep pending live agent, visual, target-engine and cost gates explicit.

## Agency Agents adaptation

Inspected upstream commit `b859c515d813efcfc4755d3471dd9e7686c7706d`:

- [Orchestrator](https://github.com/msitarzewski/agency-agents/blob/b859c515d813efcfc4755d3471dd9e7686c7706d/specialized/agents-orchestrator.md): explicit ownership, staged dependencies, bounded correction loops.
- [Handoffs](https://github.com/msitarzewski/agency-agents/blob/b859c515d813efcfc4755d3471dd9e7686c7706d/strategy/coordination/handoff-templates.md): task IDs, acceptance criteria, evidence and concrete errors.
- [Evidence Collector](https://github.com/msitarzewski/agency-agents/blob/b859c515d813efcfc4755d3471dd9e7686c7706d/testing/testing-evidence-collector.md): match evidence to claims; report untested scope honestly.
- [Reality Checker](https://github.com/msitarzewski/agency-agents/blob/b859c515d813efcfc4755d3471dd9e7686c7706d/testing/testing-reality-checker.md): separate final review from implementation.

These are design references, not executable agent infrastructure. No upstream
agent persona, website-specific command, quality quota or universal swarm is
copied. Local host adapters must actually launch specialists and expose their
identities; a role label alone is not a separate agent.

## Review focus

Missing/stale artifacts cannot pass; reconnect invalidates scene identity;
unowned changes stop execution; unavailable delegation stays NOT VERIFIED;
dry-run never invokes the host. No automatic retries of mutations, global
rollback or arbitrary commands from an untrusted brief. Existing install and
MCP entrypoints must still work.
