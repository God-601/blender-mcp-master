"""Read-only, explicit Blender reopen/reconnection identity gate.

Run after a Blender crash or MCP reconnection and BEFORE any mutating call.
A matching file path / scene name / protected object names means the right
checkpoint appears to be loaded. It NEVER proves unchanged scene contents.
Compare pre-crash and post-crash protected-object snapshots separately.
"""
import bpy
import json
import os
from pathlib import Path

# ---- Required verification input -------------------------------------------
EXPECTED_BLEND_FILE = ""  # Full path of an already saved, trusted .blend checkpoint.
EXPECTED_SCENE_NAME = ""  # Optional exact scene name.
PROTECTED_OBJECTS = []  # [{"name":"USER_Keep_Mesh","type":"MESH"}]
MAX_PROTECTED = 100
# -----------------------------------------------------------------------------


def _normal_path(path):
    return os.path.normcase(os.path.normpath(str(Path(path).expanduser().resolve())))


def probe():
    report = {
        "status": "NOT VERIFIED",
        "checkpoint_loaded": False,
        "blender_version": bpy.app.version_string,
        "actual_blend_file": bpy.data.filepath or None,
        "actual_scene_name": bpy.context.scene.name if bpy.context.scene else None,
        "protected_object_checks": [],
        "original_scene_integrity": "NOT VERIFIED",
        "all_properties_unchanged": "NOT VERIFIED",
        "errors": [],
        "limitations": [
            "Matching names and file paths do not prove this is the original unsaved scene.",
            "Run scripts/scene_baseline_snapshot.py and compare_scene_baselines.py using an archived pre-crash baseline.",
            "No autosave recovery, file opening, object edits, deletion, or checkpoint writing occurs.",
        ],
    }
    if not isinstance(EXPECTED_BLEND_FILE, str) or not EXPECTED_BLEND_FILE.strip():
        report["errors"].append("Set an explicit full path to the saved .blend checkpoint")
        return report
    if not Path(EXPECTED_BLEND_FILE).is_absolute():
        report["errors"].append("Expected checkpoint path must be absolute")
        return report
    if not isinstance(PROTECTED_OBJECTS, list) or not 1 <= len(PROTECTED_OBJECTS) <= MAX_PROTECTED:
        report["errors"].append("Set 1..100 explicit protected name/type pairs")
        return report
    if not bpy.data.filepath:
        report["errors"].append("Current Blender scene is unsaved or freshly reset")
        return report
    try:
        if _normal_path(EXPECTED_BLEND_FILE) != _normal_path(bpy.data.filepath):
            report["errors"].append("Loaded filepath differs from expected checkpoint")
        if not Path(bpy.data.filepath).is_file():
            report["errors"].append("Loaded checkpoint file is missing from the filesystem")
    except (OSError, ValueError) as exc:
        report["errors"].append("Could not verify checkpoint path: " + str(exc))
    if EXPECTED_SCENE_NAME and report["actual_scene_name"] != EXPECTED_SCENE_NAME:
        report["errors"].append("Loaded scene name differs from expected checkpoint")
    seen = set()
    for spec in PROTECTED_OBJECTS:
        if not isinstance(spec, dict):
            report["errors"].append("Each protected object must have a name and type")
            continue
        name, kind = spec.get("name"), spec.get("type")
        if (not isinstance(name, str) or not name.strip()
                or not isinstance(kind, str) or not kind.strip()
                or name in seen):
            report["errors"].append("Invalid or duplicate protected name/type")
            continue
        seen.add(name)
        obj = bpy.data.objects.get(name)
        matched = obj is not None and obj.type == kind
        report["protected_object_checks"].append({
            "name": name, "expected_type": kind,
            "actual_type": obj.type if obj else None,
            "identity_present": matched,
        })
        if not matched:
            report["errors"].append("Missing or mismatched protected object: " + name)
    if not report["errors"]:
        report["checkpoint_loaded"] = True
        report["status"] = "READY_FOR_BASELINE_COMPARISON"
    return report


def main():
    print("MCP_SCENE_RECOVERY_PROBE_BEGIN")
    print(json.dumps(probe(), sort_keys=True, indent=2, ensure_ascii=False))
    print("MCP_SCENE_RECOVERY_PROBE_END")


if __name__ == "__main__":
    main()
