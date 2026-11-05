"""Compare controlled skill-off vs skill-on agent runs using supplied metrics.

Pure Python, read-only, no network or Blender dependencies. Results are only as
trustworthy as the input evidence. No hallucinated tokens, timings, art scores.
CLI: python scripts/agent_efficiency_compare.py baseline.json with-skill.json
"""
import argparse
import json
from pathlib import Path

COMPARABLE_FIELDS = (
    "case_id", "prompt_sha256", "scene_fixture_sha256",
    "agent", "model", "blender_version", "mcp_version",
)
USAGE_FIELDS = ("input_tokens", "output_tokens")
METRICS_FIELDS = ("bash_calls", "mcp_calls", "reference_bytes", "full_script_bytes",
                  "repeated_reference_reads", "visual_captures", "failed_tool_calls")


def _nonnegative_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _total_tokens(record):
    usage = record.get("usage")
    if not isinstance(usage, dict):
        return None
    if not all(_nonnegative_int(usage.get(k)) for k in USAGE_FIELDS):
        return None
    total = usage["input_tokens"] + usage["output_tokens"]
    return total if total > 0 else None


def _unreliable_run(record):
    """A crash, reconstructed unsaved scene or missing preservation evidence invalidates the pair."""
    reasons = []
    checks = record.get("checks")
    if not isinstance(checks, dict) or checks.get("scene_preserved") != "PASS":
        reasons.append("scene_preservation_not_proven")
    incidents = record.get("incidents", [])
    if not isinstance(incidents, list):
        reasons.append("invalid_incident_record")
    elif incidents:
        reasons.append("run_incident")
    if record.get("run_status", "completed") != "completed":
        reasons.append("run_not_completed_cleanly")
    return reasons


def compare(baseline, with_skill):
    if not isinstance(baseline, dict) or not isinstance(with_skill, dict):
        raise ValueError("two JSON run objects are required")
    mismatches = []
    for key in COMPARABLE_FIELDS:
        left, right = baseline.get(key), with_skill.get(key)
        if not isinstance(left, str) or not left.strip() or left != right:
            mismatches.append(key)
    for side, run in (("baseline", baseline), ("with_skill", with_skill)):
        for reason in _unreliable_run(run):
            mismatches.append(side + ":" + reason)
    comparable = not mismatches
    result = {
        "case_id": baseline.get("case_id"),
        "comparable": comparable,
        "mismatched_or_missing_fields": mismatches,
        "token_usage": {"status": "NOT VERIFIED"},
        "metrics": {},
        "quality_claim": "NOT VERIFIED",
        "notes": [
            "Counts are supplied by the user/client; no provider billing or image quality was independently verified.",
            "Reduced Bash calls or fewer loaded characters alone do not prove reduced token usage.",
            "Compare scene integrity and technical/visual outcomes before interpreting any efficiency result.",
            "Crash/recovery, missing original scene evidence or incomplete runs block paired comparisons.",
        ],
    }
    if not comparable:
        return result
    left_tokens = _total_tokens(baseline)
    right_tokens = _total_tokens(with_skill)
    if left_tokens is not None and right_tokens is not None:
        change = right_tokens - left_tokens
        result["token_usage"] = {
            "status": "MEASURED",
            "baseline": left_tokens,
            "candidate": right_tokens,
            "delta": change,
            "percent_change": round(change * 100.0 / left_tokens, 3),
        }
    # Raw source-reported quality states are displayed side-by-side, never
    # converted into model-quality superiority by this metrics-only script.
    result["reported_checks"] = {
        "baseline": baseline.get("checks", {}),
        "candidate": with_skill.get("checks", {}),
    }
    b_metrics = baseline.get("metrics", {})
    c_metrics = with_skill.get("metrics", {})
    if not isinstance(b_metrics, dict) or not isinstance(c_metrics, dict):
        b_metrics = c_metrics = {}
    for name in METRICS_FIELDS:
        left, right = b_metrics.get(name), c_metrics.get(name)
        if _nonnegative_int(left) and _nonnegative_int(right):
            result["metrics"][name + "_delta"] = right - left
        else:
            result["metrics"][name + "_status"] = "NOT VERIFIED"
    # Never infer artistic success or performance superiority from JSON flags alone.
    return result


def _load(path):
    p = Path(path)
    if not p.is_file():
        raise ValueError("missing comparison file: " + str(p))
    if p.stat().st_size > 256_000:
        raise ValueError("run metrics JSON is too large")
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("run metrics must be a JSON object")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", help="Unmodified agent run, without the skill")
    parser.add_argument("with_skill", help="Matched agent run, with the skill")
    args = parser.parse_args()
    print(json.dumps(compare(_load(args.baseline), _load(args.with_skill)),
                     indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
