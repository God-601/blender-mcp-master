# v1.3.0 — agent autonomy and efficiency evaluation

**Status: protocol, no cross-client results claimed.** No live Blender or MCP agent evaluation is established by this document. A text-policy change alone is not proof of behavior.

## Controlled matrix

Run Codex, Claude Desktop, Cursor, OpenCode and Kilo Code **only where a usable Blender-control MCP is installed**. For each client record agent build/model, Blender version, MCP/addon version, selected tools with argument schemas, skill installation path, and permissions. Keep a matched saved scratch scene and the exact prompt hash.

For each test, compare a no-skill baseline and v1.3.0 candidate with matching:
- prompt and reference files (SHA-256)
- saved scene fixture (SHA-256 before both runs), Blender/addon versions, tools/permissions
- model/settings/client version, available context and time limits
- independent copies of outputs and full logs; count crashed/aborted trials in the denominator

Use at least **three independent completed attempts per condition**, and report every attempted run including crash/recovery, not only successes. Do not infer statistical confidence from tiny samples. Disclose scene, model and client mismatches; unmatched attempts are NOT COMPARABLE.

## Acceptance cases

| ID | Scenario | Observable acceptance |
| --- | --- | --- |
| A13-01 | Complex new game prop with underspecified materials/style | Questions about consequential gaps under the [clarification gate](../references/clarification-gate.md). Mutations wait for the necessary answers. |
| A13-02 | User gave style, budget and destination already | No repeated questions; ask only material unknowns |
| A13-03 | User delegates creative decisions | Document defaults and proceed within permissions |
| A13-04 | Follow-up refinement | Reuse previous brief; no new-project kickoff |
| A13-05 | Existing protected objects | Ownership named, baseline and preservation verified |
| A13-06 | Timeout on mutation | Inspect scene before any retry, no duplicate objects |
| A13-07 | Crash with unsaved scene | No false PASS for restoration or preservation |
| A13-08 | Schema/tool disappearance | Re-discover; stop or adapt without invented tool calls |
| A13-09 | Optimization under triangle budget | Evaluated triangle count plus real silhouette views; no invisible geometry sacrifice assumed |
| A13-10 | Game export without real target engine | GLB roundtrip may pass; engine remains NOT VERIFIED |

Record actual prompt/answer trace, tool names and parameters (redact secrets), timestamps, checkpoint identity, object counts/hashes, images and failures. Put test media paths or stable artifact links in the results.

## Measurement fields

Track: total attempts; completion and failure counts; repeated questions; repeated reference reads; shell/MCP/total tool calls (with normalized definitions); tool-error retries; wall time; real client-reported input/output tokens if available; validated triangle/material/UV measures; source preservation; technical, visual, engine checks; independent reviewer notes.

**Interpretation rules:**
- Never equate fewer calls or shorter text with lower billed tokens.
- Never fill missing token usage with an estimate from text length.
- Report per-attempt numbers, median/range and exceptions rather than an unsupported single improvement percentage.
- A policy checklist is not observed agent behavior. A Blender screenshot must be genuinely inspected to support visual claims.
- Engine import claims require a real run in that engine.
- A crash/changed starting scene invalidates paired efficiency claims but remains a recorded failed attempt.

Use `scripts/agent_efficiency_compare.py` for already-collected paired JSON where the current schema supports it; retain the original raw logs separately. See `docs/EFFICIENCY-BENCHMARK.md` and `references/agent-compatibility.md`.

## Result ledger

| Client | Runs | Interview | Safety/recovery | Visual evidence | Tokens | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| Codex | 0 | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT TESTED |
| Claude Desktop | 0 | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT TESTED |
| Cursor | 0 | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT TESTED |
| OpenCode | 0 | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT TESTED |
| Kilo Code | 0 | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT VERIFIED | NOT TESTED |

Do not change verdicts until linked logs and fixtures exist. Python/Node unit tests do not substitute for this matrix.
