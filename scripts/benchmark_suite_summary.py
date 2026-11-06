"""Read-only A/B suite summary for explicitly supplied matched trial records.

No provider API, no token estimation, no rendering, no background execution.
Records every failed and inconclusive trial; reports only aggregate totals
for pairs with actually reported comparable usage and verified scene survival.
"""
import json

INPUT = {"trials": []}
MAX_TRIALS = 100


def _valid_tokens(run):
    if not isinstance(run, dict) or not isinstance(run.get("usage"), dict):
        return None
    usage = run["usage"]
    if (type(usage.get("input_tokens")) is not int or
            type(usage.get("output_tokens")) is not int or
            usage["input_tokens"] < 0 or usage["output_tokens"] < 0):
        return None
    value = usage["input_tokens"] + usage["output_tokens"]
    return value if value > 0 else None


def _ready(run):
    return (isinstance(run, dict) and
            run.get("run_status") == "completed" and
            isinstance(run.get("checks"), dict) and
            run["checks"].get("scene_preserved") == "PASS" and
            isinstance(run.get("incidents"), list) and not run["incidents"])


def summarize(packet):
    if not isinstance(packet, dict) or not isinstance(packet.get("trials"), list):
        raise ValueError("Expected trials array")
    trials = packet["trials"]
    if len(trials) > MAX_TRIALS:
        raise ValueError("Trial count exceeds cap")
    evaluated = []
    total_base = total_skill = 0
    comparable = 0
    for i, trial in enumerate(trials):
        if not isinstance(trial, dict):
            raise ValueError("Trial must be an object")
        case_id = trial.get("case_id")
        left, right = trial.get("baseline"), trial.get("with_skill")
        if not isinstance(case_id, str) or not case_id.strip():
            raise ValueError("Each trial needs a case_id")
        identities = ("prompt_sha256", "scene_fixture_sha256", "agent", "model",
                      "blender_version", "mcp_version")
        match = (isinstance(left, dict) and isinstance(right, dict) and
                 all(isinstance(left.get(x), str) and left.get(x) and left[x] == right.get(x)
                     for x in identities))
        tokens = (_valid_tokens(left), _valid_tokens(right))
        passed = bool(match and _ready(left) and _ready(right) and
                      all(x is not None for x in tokens))
        reasons = []
        if not match:
            reasons.append("unmatched_or_missing_fixture_identity")
        if not _ready(left) or not _ready(right):
            reasons.append("incomplete_or_unpreserved_scene_or_incident")
        if any(x is None for x in tokens):
            reasons.append("missing_actual_usage")
        if passed:
            comparable += 1
            total_base += tokens[0]
            total_skill += tokens[1]
        evaluated.append({
            "trial_index": i, "case_id": case_id, "comparable": passed,
            "token_status": "MEASURED" if passed else "NOT VERIFIED",
            "baseline_tokens": tokens[0] if passed else None,
            "skill_tokens": tokens[1] if passed else None,
            "reasons": reasons,
            "baseline_status": left.get("run_status", "NOT VERIFIED") if isinstance(left, dict) else "NOT VERIFIED",
            "skill_status": right.get("run_status", "NOT VERIFIED") if isinstance(right, dict) else "NOT VERIFIED",
        })
    token_delta = total_skill - total_base if comparable else None
    return {
        "trial_count": len(trials), "comparable_trials": comparable,
        "inconclusive_trials": len(trials) - comparable,
        "trials": evaluated,
        "token_usage": {
            "status": "MEASURED_MATCHED_SUBSET" if comparable else "NOT VERIFIED",
            "baseline_total": total_base if comparable else None,
            "candidate_total": total_skill if comparable else None,
            "delta": token_delta,
            "percent_change": round(100 * token_delta / total_base, 3) if comparable and total_base else None,
        },
        "quality": "NOT VERIFIED",
        "generalizable_savings": "NOT VERIFIED",
        "notes": [
            "The paired, matched subset is not a random sample of total usage.",
            "Never erase unsuccessful runs; missing usage cannot count as zero.",
            "Source-reported tokens and preserved-scene flags require provenance verification.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(summarize(INPUT), indent=2, ensure_ascii=False, sort_keys=True))
