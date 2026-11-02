# Measuring agent efficiency with and without Blender MCP Master

This is a **protocol and input example**, not a real benchmark result. The helper `scripts/agent_efficiency_compare.py` is pure Python and runs without Blender, network access or additional packages.

## Two controlled runs

Run the same prompt and scene twice in the same client/model/Blender-control MCP environment:

- **Baseline:** same agent and MCP, no Blender MCP Master skill activated.
- **Candidate:** same agent and MCP, Blender MCP Master activated.

Use identical scene copies, an identical prompt, the same model settings and matching tool permissions. Save original logs and screenshots separately; never mark missing evidence as PASS.

## Example record format

Create `baseline.json` and `with-skill.json` with fields like the following. These are **fictional example numbers**, never claimed test results:

~~~json
{
  "case_id": "E01",
  "prompt_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "scene_fixture_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "agent": "Codex",
  "model": "the-exact-model",
  "blender_version": "4.5.15",
  "mcp_version": "the-exact-server-version",
  "usage": {"input_tokens": 1000, "output_tokens": 300},
  "metrics": {"bash_calls": 8, "mcp_calls": 12, "reference_bytes": 14000},
  "checks": {"technical": "PASS", "visual": "NOT VERIFIED", "scene_preserved": "PASS"}
}
~~~

**Crash/unsaved-scene gate (T08 regression):** The companion comparator refuses a paired efficiency claim if either run lacks `checks.scene_preserved=PASS`, has nonempty `incidents`, or has `run_status` other than `completed`. These fields are conditions, not a way to erase an unsuccessful attempt. A Blender crash followed by reconstructing `Cube/Camera/Light` does not restore the original scene. Refer to `references/crash-recovery-and-baselines.md` and save identical backed-up scene fixtures before both runs. Record `incidents: []` only when no incident occurred, not as a default to hide an event.

**Known T08 trial (2026-11-02):** Two medieval tables met dimensions and triangle budget (968 versus 836 evaluated tris). First run reported 12 direct/14 nested calls including 3 terminal calls; second run reported 17 external/21 internal operations including 8 terminal operations. Those call categories have not been normalized. One trial crashed and lost an unsaved source scene, then rebuilt from a new default scene. Tokens and confirmed matched start fixture are NOT VERIFIED. **Result: inconclusive, not evidence of skill token savings or superior quality.** No claims about the skill-on/off assignment are made without the original logs.

Do not copy the dummy identifiers into real benchmark files: derive the prompt hash and starting-scene hash from the actual contents. Only fill token counts when your client reports actual counts; otherwise omit `usage` entirely.

## Compare on Windows (PowerShell)

~~~powershell
python .\scripts\agent_efficiency_compare.py .\baseline.json .\with-skill.json
~~~

Interpretation:
- `comparable=false` means at least one required identity differs or is absent. No token comparison is permitted.
- `token_usage.status=MEASURED` means both user-provided records had valid measured token counts; the tool reports the exact difference and percent change.
- `token_usage.status=NOT VERIFIED` means token counts were unavailable, missing or invalid. Fewer Bash calls or fewer reference bytes are not substitutes for actual tokens.
- `quality_claim=NOT VERIFIED` is deliberate: JSON metadata alone does not establish artistic quality.
- Negative `delta` means fewer counted tokens in the candidate **for that matched case only**. Always compare scene safety and model outputs separately.

Run at least the cases in `references/skill-evaluation-protocol.md` and repeat runs before generalizing. Avoid reporting exact economic or quality improvements without matching provider usage data, real Blender captures, or independent review.
