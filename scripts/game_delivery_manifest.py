"""Evaluate supplied game-asset budgets and import receipts, without scene/file access.

This helper NEVER performs import, measures FPS, or certifies artistic fidelity.
It keeps technical budget compliance separate from independent engine evidence.
"""
import json
import math

INPUT = {
    "asset": "",
    "destination": "GODOT",
    "technical": {},
    "limits": {},
    "import_receipt": {},
}
DESTINATIONS = {"ROBLOX", "GODOT", "UNITY", "UNREAL", "GENERIC"}
BUDGETS = {
    "triangles": ("max_triangles", int),
    "material_slots": ("max_material_slots", int),
    "texture_bytes": ("max_texture_bytes", int),
}
VALID_IMPORT_FIELDS = ("engine", "engine_version", "asset_sha256",
                       "evidence_path", "import_status")


def _positive_int(value):
    return type(value) is int and value > 0


def _sha(value):
    return (isinstance(value, str) and len(value) == 64 and
            all(c in "0123456789abcdef" for c in value.lower()))


def evaluate(record):
    if not isinstance(record, dict):
        raise ValueError("Record must be a JSON object")
    asset = record.get("asset")
    destination = record.get("destination")
    if not isinstance(asset, str) or not asset.strip():
        raise ValueError("Explicit asset is required")
    if destination not in DESTINATIONS:
        raise ValueError("Explicit supported destination is required")
    technical, limits = record.get("technical"), record.get("limits")
    if not isinstance(technical, dict) or not isinstance(limits, dict):
        raise ValueError("technical and limits must be objects")
    if set(technical) - set(BUDGETS) or set(limits) - {x[0] for x in BUDGETS.values()}:
        raise ValueError("Unknown budget metric")
    results = {}
    for measurement, (limit, _) in BUDGETS.items():
        observed, ceiling = technical.get(measurement), limits.get(limit)
        if observed is None or ceiling is None:
            results[measurement] = {"status": "NOT VERIFIED"}
        elif type(observed) is not int or observed < 0 or not _positive_int(ceiling):
            raise ValueError("Budget values must be exact nonnegative measured integers and positive limits")
        else:
            results[measurement] = {
                "measured": observed, "project_budget": ceiling,
                "status": "ISSUE" if observed > ceiling else "MEASURED",
            }
    receipt = record.get("import_receipt", {})
    if not isinstance(receipt, dict):
        raise ValueError("import_receipt must be an object")
    if set(receipt) - set(VALID_IMPORT_FIELDS):
        raise ValueError("Unrecognized import receipt fields")
    source = receipt.get("engine")
    version = receipt.get("engine_version")
    digest = receipt.get("asset_sha256")
    evidence = receipt.get("evidence_path")
    status = receipt.get("import_status")
    if status is not None and status not in ("IMPORTED_GEOMETRY", "FAILED", "NOT VERIFIED"):
        raise ValueError("Invalid import status")
    complete = (
        source == destination and
        isinstance(version, str) and bool(version.strip()) and
        _sha(digest) and
        isinstance(evidence, str) and bool(evidence.strip()) and
        status in ("IMPORTED_GEOMETRY", "FAILED")
    )
    import_observation = ("REVIEW_RECEIPT" if complete and status == "IMPORTED_GEOMETRY"
                          else "ISSUE" if complete and status == "FAILED"
                          else "NOT VERIFIED")
    overall = ("ISSUE" if "ISSUE" in (x["status"] for x in results.values()) or
               import_observation == "ISSUE" else "NOT VERIFIED" if
               "NOT VERIFIED" in (x["status"] for x in results.values()) else "REVIEW")
    return {
        "asset": asset.strip(), "destination": destination,
        "budget_checks": results, "overall_technical_budget_status": overall,
        "import_receipt_status": import_observation,
        "import_source_claim": dict(receipt),
        "real_engine_import_certified": "NOT VERIFIED",
        "rendered_material_fidelity": "NOT VERIFIED",
        "physical_collision": "NOT VERIFIED",
        "runtime_performance": "NOT VERIFIED",
        "limits": [
            "Budgets are user-authored goals, not official hard engine ceilings.",
            "A receipt is user-supplied metadata until its log, checksum and exact engine session are independently checked.",
            "Neither Blender roundtrip nor a single engine smoke certifies other platforms.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(INPUT), ensure_ascii=False, indent=2, sort_keys=True))
