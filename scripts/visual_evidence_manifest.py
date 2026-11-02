"""Record real file-backed Blender review captures without judging image content.

This tool reads explicitly named PNG/JPEG files from a designated evidence
directory, validates size/basic signatures and computes SHA-256 hashes. It
does NOT open/render Blender, decode pixels, inspect artwork or certify that
a capture is from a specific scene. An agent/reviewer must inspect each image
separately. No file/scene mutation occurs.

Edit EVIDENCE_ROOT and CAPTURES before running with local Python.
"""
import hashlib
import json
from pathlib import Path

# ---- Explicit opt-in; do not scan the current directory or a whole scene ----
EVIDENCE_ROOT = ""
CAPTURES = []  # [{"view": "front", "file": "front.png", "reviewer": "person_or_agent"}]
MAX_CAPTURES = 30
MAX_IMAGE_BYTES = 25 * 1024 * 1024
REQUIRED_VIEWS = {"front", "side", "three_quarter"}
ALLOWED_VIEWS = REQUIRED_VIEWS | {"top", "back", "wireframe", "detail", "material"}
# -----------------------------------------------------------------------------


def _hash_capture(root, record):
    if not isinstance(record, dict):
        raise ValueError("Capture must be a dictionary")
    view = record.get("view")
    rel = record.get("file")
    reviewer = record.get("reviewer")
    if view not in ALLOWED_VIEWS:
        raise ValueError("Unsupported capture view")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise ValueError("Capture needs actual reviewer identifier")
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError("Capture needs explicit relative file")
    subpath = Path(rel)
    if subpath.is_absolute() or any(p in ("..", "") for p in subpath.parts):
        raise ValueError("Absolute or traversal capture path rejected")
    filename = (root / subpath).resolve()
    if not filename.is_relative_to(root):
        raise ValueError("Capture path resolves outside evidence root")
    if not filename.is_file():
        raise ValueError("Capture file missing")
    size = filename.stat().st_size
    if size < 16 or size > MAX_IMAGE_BYTES:
        raise ValueError("Capture file outside size limits")
    digest = hashlib.sha256()
    with filename.open("rb") as handle:
        header = handle.read(12)
        if header[:8] == b"\x89PNG\r\n\x1a\n":
            suffix = "PNG"
        elif header[:3] == b"\xff\xd8\xff":
            suffix = "JPEG"
        else:
            raise ValueError("Capture must be PNG or JPEG by file signature")
        digest.update(header)
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return {
        "view": view, "file": rel, "reviewer": reviewer,
        "bytes": size, "sha256": digest.hexdigest(), "format_signature": suffix,
        "pixel_content_reviewed_by_tool": False,
    }


def assess():
    result = {
        "status": "NOT VERIFIED", "captures": [], "errors": [],
        "missing_views": sorted(REQUIRED_VIEWS),
        "actual_visual_quality": "NOT VERIFIED",
        "blender_scene_identity": "NOT VERIFIED",
        "limits": [
            "Hashes prove only the bytes read, not artistic quality or provenance.",
            "Images are NOT decoded and no pixel inspection is performed.",
            "Actual reviewers must compare matching views before and after edits.",
        ],
    }
    if not isinstance(EVIDENCE_ROOT, str) or not EVIDENCE_ROOT.strip():
        result["errors"].append("Configure explicit EVIDENCE_ROOT directory")
        return result
    if not isinstance(CAPTURES, list) or not 1 <= len(CAPTURES) <= MAX_CAPTURES:
        result["errors"].append("Provide 1..30 explicit CAPTURES")
        return result
    root = Path(EVIDENCE_ROOT).expanduser().resolve()
    if not root.is_dir():
        result["errors"].append("Evidence root must exist and be a directory")
        return result
    encountered = set()
    for record in CAPTURES:
        try:
            item = _hash_capture(root, record)
            key = (item["view"], item["file"])
            if key in encountered:
                raise ValueError("Duplicate capture view/path pair")
            encountered.add(key)
            result["captures"].append(item)
        except (OSError, ValueError) as exc:
            result["errors"].append(str(exc))
    reviewed = {c["view"] for c in result["captures"]}
    result["missing_views"] = sorted(REQUIRED_VIEWS - reviewed)
    if not result["errors"] and not result["missing_views"]:
        result["status"] = "FILES_HASHED_REVIEW_REQUIRED"
    return result


def main():
    print("MCP_VISUAL_EVIDENCE_BEGIN")
    print(json.dumps(assess(), sort_keys=True, indent=2))
    print("MCP_VISUAL_EVIDENCE_END")


if __name__ == "__main__":
    main()
