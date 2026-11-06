"""Pure read-only specialist QA aggregator for staged Blender agent workflows.

This enforces independent reported roles and evidence *shape*, not truth of
artistic/engineering results. Never launches subagents, Blender or paid tools.
"""
import json

INPUT = {"asset": "", "builder": "", "reviews": [], "required_roles": []}
ROLES = {"geometry", "visual", "materials", "export", "scene_safety"}
STATES = {"PASS", "ISSUE", "NOT VERIFIED", "N/A"}
MAX_REVIEWS = 20


def evaluate(packet):
    if not isinstance(packet, dict):
        raise ValueError("review packet must be an object")
    asset, builder = packet.get("asset"), packet.get("builder")
    if not isinstance(asset, str) or not asset.strip():
        raise ValueError("asset must be specified")
    if not isinstance(builder, str) or not builder.strip():
        raise ValueError("builder must be identified")
    reviews = packet.get("reviews", [])
    required = packet.get("required_roles", [])
    if not isinstance(reviews, list) or len(reviews) > MAX_REVIEWS:
        raise ValueError("reviews must be 0..20 items")
    if not isinstance(required, list) or len(set(required)) != len(required) or any(r not in ROLES for r in required):
        raise ValueError("required_roles must be unique known roles")
    normalized, issues = {}, []
    for item in reviews:
        if not isinstance(item, dict):
            raise ValueError("Every review must be an object")
        role, reviewer, status = item.get("role"), item.get("reviewer"), item.get("status")
        evidence = item.get("evidence", [])
        if role not in ROLES or role in normalized:
            raise ValueError("Duplicate or invalid review role")
        if not isinstance(reviewer, str) or not reviewer.strip():
            raise ValueError("Every review needs a reviewer identity")
        if status not in STATES:
            raise ValueError("Invalid status")
        if not isinstance(evidence, list) or any(not isinstance(x, str) or not x.strip() for x in evidence):
            raise ValueError("evidence must be a list of named artifacts")
        # A separate named reviewer and a supporting file ref are necessary
        # conditions, never a substitute for actual independent inspection.
        if status == "PASS" and (reviewer == builder or not evidence):
            status = "NOT VERIFIED"
            issues.append(role + ": claimed independent PASS lacks independent reviewer/evidence")
        if role == "visual" and status == "PASS":
            # A receipt alone cannot prove that any reviewer inspected image pixels.
            status = "NOT VERIFIED"
            issues.append("visual: independent pixel inspection must be verified outside this script")
        if role == "export" and status == "PASS":
            status = "NOT VERIFIED"
            issues.append("export: real target engine import must be verified externally")
        normalized[role] = {
            "reviewer": reviewer, "status": status, "evidence": list(evidence)
        }
    for role in required:
        if role not in normalized:
            normalized[role] = {"reviewer": None, "status": "NOT VERIFIED", "evidence": []}
            issues.append(role + ": no review provided")
    if any(v["status"] == "ISSUE" for v in normalized.values()):
        overall = "ISSUE"
    elif not required or any(normalized[role]["status"] == "NOT VERIFIED" for role in required):
        overall = "NOT VERIFIED"
    else:
        overall = "REVIEW"
    return {
        "asset": asset.strip(), "overall": overall, "reviews": normalized,
        "warnings": issues,
        "actual_artistic_quality": "NOT VERIFIED",
        "real_engine_import": "NOT VERIFIED",
        "scene_preservation": "NOT VERIFIED",
        "limits": [
            "This file does not create, supervise or verify any live AI specialist.",
            "Reviewer names and evidence paths are user-supplied assertions.",
            "Visual and engine PASS require independently inspected real artifacts.",
            "A reviewed report is not automatic permission for destructive edits.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(INPUT), indent=2, ensure_ascii=False, sort_keys=True))
