"""Safely compare two read-only, explicitly scoped Blender baseline JSON captures.

CLI: python scripts/compare_scene_baselines.py before.json after.json
Files are snapshots printed by scripts/scene_baseline_snapshot.py.
The JSON status is authoritative; the script does not terminate the Blender host.
"""
import argparse
import json
from pathlib import Path
import re

SCOPE = "explicit_protected_objects_selected_properties"
MATCHED_SCOPE = "PASS (escopo parcial)"
LEGACY_LIMITS = (
    "Legacy schema v1 omits vertex weights, shape key settings, constraints, animation, "
    "rigs, curves, embedded pixels, custom properties and some mesh attributes.",
    "Only the selected properties of the named objects are compared.",
)


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
        "scope_status": "NOT VERIFIED",
        "limitations": [],
        "scene_global_integrity": "NOT VERIFIED",
        "visual_integrity": "NOT VERIFIED",
    }
    if not isinstance(before, dict) or not isinstance(after, dict):
        result["reason"].append("Two JSON object snapshots are required")
        return result
    version = before.get("schema_version")
    if (type(version) is not int or version not in (1, 2)
            or type(after.get("schema_version")) is not int or after["schema_version"] != version
            or any(record.get("scope") != SCOPE for record in (before, after))):
        result["reason"].append("Missing or incompatible baseline schema or scope")
        return result
    if version == 1:
        result["limitations"] = list(LEGACY_LIMITS)
    else:
        blender_version = before.get("blender_version")
        if (not isinstance(blender_version, str) or not blender_version
                or after.get("blender_version") != blender_version):
            result["reason"].append("Schema v2 requires matching Blender versions")
            return result
    for stage, record in (("before", before), ("after", after)):
        limits = record.get("limitations", [])
        if version == 2 and (not isinstance(limits, list) or not limits
                             or any(not isinstance(item, str) or not item.strip() for item in limits)):
            result["reason"].append(stage + " snapshot has no valid coverage limitations")
        elif isinstance(limits, list):
            for item in limits:
                if isinstance(item, str) and item not in result["limitations"]:
                    result["limitations"].append(item)
        for key in ("missing_names", "errors"):
            issues = record.get(key, [])
            if not isinstance(issues, list) or any(not isinstance(item, str) for item in issues):
                result["reason"].append(stage + " snapshot has invalid " + key)
            elif issues:
                result["reason"].extend(stage + " " + key + ": " + item for item in issues)
        if record.get("status") != "MEASURED":
            result["reason"].append(stage + " snapshot did not measure every protected object")
    if result["reason"]:
        return result
    original = before.get("objects")
    final = after.get("objects")
    if not isinstance(original, list) or not isinstance(final, list) or not original:
        result["reason"].append("Expected nonempty object lists")
        return result
    names_a = [x.get("name") for x in original if isinstance(x, dict)]
    names_b = [x.get("name") for x in final if isinstance(x, dict)]
    if (len(names_a) != len(original) or len(names_b) != len(final)
            or any(not isinstance(name, str) or not name.strip() for name in names_a + names_b)
            or len(set(names_a)) != len(original) or len(set(names_b)) != len(final)
            or any(not isinstance(x.get("fingerprint_sha256"), str)
                   or re.fullmatch(r"[0-9a-f]{64}", x["fingerprint_sha256"]) is None
                   for x in original + final)):
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
        result["scope_status"] = "ISSUE"
        result["reason"].append("At least one protected object is missing or has changed")
    elif result["added_to_scope"]:
        result["status"] = "NOT VERIFIED"
    else:
        # Legacy consumers can still read schema v1 receipts. New captures carry
        # partial coverage in the authoritative status as well.
        result["status"] = "PASS" if version == 1 else MATCHED_SCOPE
        result["scope_status"] = MATCHED_SCOPE
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
    return 0 if result["scope_status"] == MATCHED_SCOPE else 1


if __name__ == "__main__":
    main()
