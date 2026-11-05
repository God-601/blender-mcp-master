"""Evidence-gated, read-only scorecard for modeling runs (no bpy required).

Provide an explicit record in INPUT. No file I/O, Blender mutation, external
execution, or image inspection. Claims without evidence are NOT VERIFIED.
Visual review receipts do not automatically certify artistic quality.
"""
import json

INPUT = {
    "asset": "",
    "criteria": {},
}
ALLOWED = {"PASS", "ISSUE", "N/A", "NOT VERIFIED"}
CRITERIA = ("silhouette", "proportions", "topology", "component_fit",
            "uv_materials", "optimization", "scene_preservation",
            "export_destination")


def build_scorecard(record):
    if not isinstance(record, dict) or not isinstance(record.get("asset"), str) or not record["asset"].strip():
        raise ValueError("Scorecard requires a non-empty asset name")
    criteria = record.get("criteria")
    if not isinstance(criteria, dict):
        raise ValueError("criteria must be a dictionary")
    unknown = sorted(set(criteria) - set(CRITERIA))
    if unknown:
        raise ValueError("Unknown criteria: " + ", ".join(unknown))
    out = {}
    for name in CRITERIA:
        item = criteria.get(name, {})
        if not isinstance(item, dict):
            raise ValueError(name + " must be a dictionary")
        status = item.get("status", "NOT VERIFIED")
        if status not in ALLOWED:
            raise ValueError("Invalid status for " + name)
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or any(not isinstance(e, str) or not e.strip() for e in evidence):
            raise ValueError("evidence for " + name + " must be a list of non-empty strings")
        # Evidence strings are reviewer-provided references, not verified image contents.
        if status == "PASS" and not evidence:
            status = "NOT VERIFIED"
        out[name] = {"status": status, "evidence": list(evidence)}
        if item.get("status") == "PASS" and status == "NOT VERIFIED":
            out[name]["reason"] = "PASS lacks supporting evidence"
    statuses = {v["status"] for v in out.values()}
    # Issue always outranks incomplete evidence; an overall PASS requires
    # complete independently supplied evidence, not scorecard inference.
    overall = ("ISSUE" if "ISSUE" in statuses else
               "NOT VERIFIED" if "NOT VERIFIED" in statuses else "REVIEW")
    return {
        "asset": record["asset"].strip(),
        "overall": overall,
        "criteria": out,
        "artistic_quality": "NOT VERIFIED",
        "engine_certification": "NOT VERIFIED",
        "limitations": [
            "Scorecard checks only supplied statuses and evidence references.",
            "It does not inspect screenshots or Blender geometry.",
            "Evidence references and reviewer claims require independent verification.",
            "REVIEW means recorded and complete, never automatic asset certification.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(build_scorecard(INPUT), ensure_ascii=False, indent=2, sort_keys=True))
