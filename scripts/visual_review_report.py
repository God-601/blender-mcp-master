"""Read-only visual review receipt validator and defect triage.

This records evidence supplied by an actual reviewer/agent. It does NOT
inspect image pixels, capture Blender views, or certify artistic quality.
It never reports visual PASS automatically.
"""
import json

REVIEW = {
    "asset": "",
    "captures": [],
    "defects": [],
}

REQUIRED_VIEWS = ("front", "side", "three_quarter")
DEFECT_TYPES = {"silhouette", "proportion", "attachment", "shading", "topology",
                "material", "uv", "texture", "composition", "export"}
SEVERITIES = {"minor", "major", "critical"}


def assess_review(report):
    if not isinstance(report, dict):
        raise ValueError("review must be a dictionary")
    if not isinstance(report.get("asset"), str) or not report["asset"].strip():
        raise ValueError("review requires the actual asset name")
    captures = report.get("captures")
    defects = report.get("defects")
    if not isinstance(captures, list) or not isinstance(defects, list):
        raise ValueError("captures and defects must be arrays")
    verified_views = set()
    for cap in captures:
        if not isinstance(cap, dict):
            raise ValueError("capture entry must be a dictionary")
        view = cap.get("view")
        if view not in REQUIRED_VIEWS and view not in ("top", "back", "wireframe", "detail", "material"):
            raise ValueError("unsupported view type: " + str(view))
        # Metadata alone cannot prove pixel contents. Only record a reviewer-provided receipt.
        if (isinstance(cap.get("artifact"), str) and cap["artifact"].strip()
                and isinstance(cap.get("reviewer"), str) and cap["reviewer"].strip()):
            verified_views.add(view)
    open_defects = []
    for defect in defects:
        if not isinstance(defect, dict):
            raise ValueError("defect must be a dictionary")
        if defect.get("type") not in DEFECT_TYPES or defect.get("severity") not in SEVERITIES:
            raise ValueError("defect requires known type and severity")
        if not isinstance(defect.get("object"), str) or not defect["object"].strip():
            raise ValueError("defect requires the specific object name")
        if not isinstance(defect.get("description"), str) or not defect["description"].strip():
            raise ValueError("defect requires a description")
        if not isinstance(defect.get("resolved"), bool):
            raise ValueError("defect resolution must be explicitly true or false")
        if not defect["resolved"]:
            open_defects.append(dict(defect))
    missing_views = sorted(set(REQUIRED_VIEWS) - verified_views)
    next_steps = []
    for defect in sorted(open_defects, key=lambda x: ("critical", "major", "minor").index(x["severity"])):
        next_steps.append(
            "Inspect " + defect["type"] + " issue on " + defect["object"] +
            ": " + defect["description"] +
            "; reproduce with the actual image and make one reversible correction before re-check."
        )
    if missing_views:
        next_steps.append("Capture and review real " + ", ".join(missing_views) + " Blender views.")
    if open_defects:
        status = "ISSUE"
    elif missing_views:
        status = "NOT VERIFIED"
    else:
        status = "REVIEW_RECORDED"
    return {
        "asset": report["asset"],
        "visual_status": status,
        "missing_views": missing_views,
        "reviewed_views": sorted(verified_views),
        "open_defects": open_defects,
        "next_steps": next_steps,
        "artistic_quality": "NOT VERIFIED",
        "limits": "Review receipts are not pixel verification or independent artistic assessment.",
    }


def main():
    print(json.dumps(assess_review(REVIEW), ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
