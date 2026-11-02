"""Safely compare two read-only, explicitly scoped Blender baseline JSON captures.

CLI: python scripts/compare_scene_baselines.py before.json after.json
Files are snapshots printed by scripts/scene_baseline_snapshot.py.
Exit 0 = PASS; 1 = ISSUE or NOT VERIFIED; 2 = input error.
"""
import argparse
import json
from pathlib import Path

SCOPE = "explicit_protected_objects_selected_properties"


def compare(before, after):
    result = {
        "status": "NOT VERIFIED",
        "protected_objects": [],
        "unchanged": [],
        "changed": [],
        "removed_or_missing": [],
        "added_to_scope": [],
        "reason": [],
        "scope": SCOPE,
        "scene_global_integrity": "NOT VERIFIED",
        "visual_integrity": "NOT VERIFIED",
    }
    if not isinstance(before, dict) or not isinstance(after, dict):
        result["reason"].append("Two JSON object snapshots are required")
        return result
    if any(record.get("scope") != SCOPE or record.get("schema_version") != 1
           or record.get("status") != "MEASURED" for record in (before, after)):
        result["reason"].append("Missing, incomplete, or incompatible baseline snapshot")
        return result
    for stage, record in (("before", before), ("after", after)):
        if record.get("missing_names") or record.get("errors"):
            result["reason"].append(stage + " snapshot has missing names or capture errors")
            return result
    original = before.get("objects")
    final = after.get("objects")
    if not isinstance(original, list) or not isinstance(final, list) or not original:
        result["reason"].append("Expected nonempty object lists")
        return result
    names_a = [x.get("name") for x in original if isinstance(x, dict)]
    names_b = [x.get("name") for x in final if isinstance(x, dict)]
    if (len(names_a) != len(original) or len(names_b) != len(final)
            or len(set(names_a)) != len(original) or len(set(names_b)) != len(final)
            or any(not isinstance(name, str) or not name for name in names_a + names_b)
            or any(not isinstance(x.get("fingerprint_sha256"), str)
                   or len(x["fingerprint_sha256"]) != 64 for x in original + final)):
        result["reason"].append("Invalid object entry, duplicate name or fingerprint")
        return result
    by_name_a = {x["name"]: x for x in original}
    by_name_b = {x["name"]: x for x in final}
    result["protected_objects"] = sorted(by_name_a)
    result["added_to_scope"] = sorted(set(by_name_b) - set(by_name_a))
    result["removed_or_missing"] = sorted(set(by_name_a) - set(by_name_b))
    for name in sorted(set(by_name_a) & set(by_name_b)):
        if by_name_a[name]["fingerprint_sha256"] == by_name_b[name]["fingerprint_sha256"]:
            result["unchanged"].append(name)
        else:
            result["changed"].append(name)
    if result["added_to_scope"]:
        # Adding new tracked names is not proof of preexisting-object damage,
        # but it can conceal mistaken target selection and requires a recheck.
        result["reason"].append("The protected-name set changed between snapshots")
    if result["removed_or_missing"] or result["changed"]:
        result["status"] = "ISSUE"
        result["reason"].append("At least one protected object is missing or has changed")
    elif result["added_to_scope"]:
        result["status"] = "NOT VERIFIED"
    else:
        result["status"] = "PASS"
        result["reason"].append("All captured protected-object properties match")
    return result


def read_snapshot(path):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > 16_000_000:
        raise ValueError("Missing or oversized baseline JSON file: " + str(p))
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Each snapshot must be a JSON object")
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before")
    parser.add_argument("after")
    args = parser.parse_args()
    try:
        result = compare(read_snapshot(args.before), read_snapshot(args.after))
    except (ValueError, OSError, json.JSONDecodeError) as error:
        print(json.dumps({"status": "NOT VERIFIED", "error": str(error)}, indent=2))
        return 2
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
