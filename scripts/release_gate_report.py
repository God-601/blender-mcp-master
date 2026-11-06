"""Pure-Python nonpublishing release decision receipt for proposed v1.5..v2.0.

The result is *always* advisory and no GitHub tag, npm package or ZIP is
created here. Self-reported evidence must still be verified independently.
"""
import json
import re

INPUT = {"version": "", "commit_sha": "", "checks": {}}
GATES = (
    "python_static", "blender_runtime", "npm_package",
    "zip_clean_install", "godot_import",
    "agent_live_modeling", "scene_integrity", "visual_review",
    "destination_validation", "usage_quality_benchmark",
)
STATUS = {"PASS", "FAIL", "NOT VERIFIED", "N/A"}


def evaluate(record):
    if not isinstance(record, dict):
        raise ValueError("Release evidence must be an object")
    version = record.get("version")
    sha = record.get("commit_sha")
    if not isinstance(version, str) or not re.fullmatch(r"(?:1\.[5-9]\.\d+|2\.0\.\d+)(?:-rc\.\d+)?", version):
        raise ValueError("Explicit supported milestone version is required")
    if not isinstance(sha, str) or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise ValueError("Exact 40-character Git commit SHA is required")
    checks = record.get("checks")
    if not isinstance(checks, dict) or set(checks) - set(GATES):
        raise ValueError("Unexpected release checks")
    evaluated = {}
    for key in GATES:
        check = checks.get(key, {})
        if not isinstance(check, dict):
            raise ValueError("Each check must be an object")
        state = check.get("status", "NOT VERIFIED")
        refs = check.get("evidence", [])
        if state not in STATUS:
            raise ValueError("Invalid check status")
        if not isinstance(refs, list) or any(not isinstance(x, str) or not x.strip() for x in refs):
            raise ValueError("Each evidence entry must name a nonempty artifact")
        if state == "PASS" and not refs:
            state = "NOT VERIFIED"
        if state == "N/A" and not check.get("reason"):
            state = "NOT VERIFIED"
        evaluated[key] = {"status": state, "evidence": list(refs)}
    blockers = [key for key, details in evaluated.items()
                if details["status"] in ("FAIL", "NOT VERIFIED")]
    # Even a complete declared record is not automatically proof of real
    # agent, image or engine behavior. Never publish on this script's output.
    return {
        "version": version, "commit_sha": sha,
        "checks": evaluated, "blockers": blockers,
        "reported_gate_status": "REVIEW" if not blockers else "HOLD",
        "publication_authorized": False,
        "actual_live_evidence_verified": "NOT VERIFIED",
        "limits": [
            "The report is user-supplied metadata; verify every referenced artifact independently.",
            "A release also requires intentional publisher authorization and exact-SHA integrity.",
            "Do not equate CI evidence with real client model quality or engine material fidelity.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(INPUT), indent=2, ensure_ascii=False, sort_keys=True))
