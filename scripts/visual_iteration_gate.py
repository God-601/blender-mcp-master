"""Evidence-only gate for a visual correction round.

Combine TWO outputs from reference_silhouette_compare.compare_masks (before
and after), a protected-object compare_scene_baselines receipt and an optional
visual_review_report assessment. This does not open Blender, edit a scene,
judge aesthetics, or authenticate user-supplied JSON / camera alignment.
"""
import argparse
import json
import math
from pathlib import Path

VIEWS = ("front", "side", "three_quarter")
MAX_VIEWS = 5
MAX_JSON_BYTES = 2_000_000


def _items(packet):
    if not isinstance(packet, dict) or not isinstance(packet.get("results"), list):
        raise ValueError("Expected silhouette comparison result object with results")
    rows = packet["results"]
    if not 1 <= len(rows) <= MAX_VIEWS:
        raise ValueError("Expected 1..5 comparison views")
    by_view = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid comparison entry")
        view = row.get("view")
        if view not in ("front", "side", "three_quarter", "top", "back") or view in by_view:
            raise ValueError("Unknown or duplicate view")
        by_view[view] = row
    return by_view


def _score(row):
    value = row.get("silhouette_iou")
    if (row.get("status") != "MEASURED_REVIEW_REQUIRED" or
            type(value) not in (int, float) or not math.isfinite(value)
            or not 0 <= value <= 1):
        return None
    digest = row.get("reference_sha256")
    render = row.get("render_sha256")
    resolution = row.get("resolution")
    if (not isinstance(digest, str) or len(digest) != 64 or
            not all(c in "0123456789abcdef" for c in digest) or
            not isinstance(render, str) or len(render) != 64 or
            not all(c in "0123456789abcdef" for c in render) or
            not isinstance(resolution, list) or len(resolution) != 2 or
            any(type(n) is not int or n <= 0 for n in resolution)):
        return None
    return value


def evaluate(before, after, scene_check=None, visual_review=None,
             required_views=VIEWS, minimum_gain=0.005, max_view_regression=0.005):
    if (not isinstance(required_views, (list, tuple)) or not required_views
            or len(set(required_views)) != len(required_views)
            or any(v not in VIEWS for v in required_views)):
        raise ValueError("required_views must be unique standard views")
    if (any(type(n) not in (int, float) or not math.isfinite(n) or n < 0
            for n in (minimum_gain, max_view_regression))):
        raise ValueError("thresholds must be finite and nonnegative")
    old, new = _items(before), _items(after)
    reasons, compared, regressions = [], [], []
    missing = sorted(set(required_views) - set(old) | set(required_views) - set(new))
    if missing:
        reasons.append("missing_required_views: " + ", ".join(missing))
    for view in sorted(set(old) & set(new)):
        a, b = old[view], new[view]
        x, y = _score(a), _score(b)
        if x is None or y is None:
            reasons.append(view + ": missing_or_invalid_pixel_measurement")
            continue
        if (a["reference_sha256"] != b["reference_sha256"] or
                a["resolution"] != b["resolution"]):
            reasons.append(view + ": reference_or_resolution_changed")
            continue
        if a["render_sha256"] == b["render_sha256"]:
            reasons.append(view + ": identical_before_after_render")
            continue
        delta = round(y - x, 6)
        compared.append({"view": view, "before_iou": x, "after_iou": y,
                         "delta_iou": delta,
                         "reference_sha256": a["reference_sha256"],
                         "before_render_sha256": a["render_sha256"],
                         "after_render_sha256": b["render_sha256"]})
        if delta < -max_view_regression:
            regressions.append(view)
    if isinstance(scene_check, dict) and scene_check.get("status") == "ISSUE":
        reasons.append("protected_scene_integrity_issue")
    elif not isinstance(scene_check, dict) or scene_check.get("status") != "PASS":
        reasons.append("protected_scene_integrity_not_verified")
    if visual_review is not None:
        if not isinstance(visual_review, dict):
            raise ValueError("visual_review must be a reviewed assessment object")
        if visual_review.get("visual_status") == "ISSUE" or visual_review.get("open_defects"):
            reasons.append("unresolved_visual_defects")
        elif visual_review.get("visual_status") != "REVIEW_RECORDED":
            reasons.append("review_incomplete")
    elif visual_review is None:
        reasons.append("independent_visual_review_missing")
    if regressions:
        reasons.append("regressed_views: " + ", ".join(regressions))
    required_compared = set(required_views).issubset({x["view"] for x in compared})
    if not required_compared:
        reasons.append("required_views_not_comparable")
    gain = round(sum(x["delta_iou"] for x in compared) / len(compared), 6) if compared else None
    if gain is None or gain < minimum_gain:
        reasons.append("no_demonstrated_mean_iou_improvement")

    issue = ("protected_scene_integrity_issue" in reasons or
             "unresolved_visual_defects" in reasons or bool(regressions))
    status = "ISSUE" if issue else "REVIEW_REQUIRED" if not reasons else "NOT VERIFIED"
    return {
        "status": status,
        "visual_quality": "NOT VERIFIED",
        "recommendation": ("REVERT_OR_INSPECT_OWNED_COPY" if issue else
                           "INDEPENDENT_REVIEW_BEFORE_ACCEPT" if status == "REVIEW_REQUIRED"
                           else "DO_NOT_ACCEPT_UNTIL_EVIDENCE_COMPLETE"),
        "compared_views": compared,
        "mean_iou_delta": gain,
        "reasons": reasons,
        "limitations": [
            "Camera, framing, provenance, scene ownership and JSON authenticity must be independently checked.",
            "Silhouette IoU cannot measure material fidelity, shading, contact, UV quality or aesthetics.",
            "Even REVIEW_REQUIRED is never an automatic artistic PASS or permission to mutate a scene.",
        ],
    }


def _read(path):
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_JSON_BYTES:
        raise ValueError("Missing or oversized JSON input")
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", help="Prior reference_silhouette_compare output JSON")
    parser.add_argument("after", help="Post-correction comparison output JSON")
    parser.add_argument("--scene-check", help="compare_scene_baselines result JSON")
    parser.add_argument("--visual-review", help="visual_review_report assessment JSON")
    args = parser.parse_args()
    try:
        result = evaluate(_read(args.before), _read(args.after),
                          _read(args.scene_check) if args.scene_check else None,
                          _read(args.visual_review) if args.visual_review else None)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "NOT VERIFIED", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result["status"] == "REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
