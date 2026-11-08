"""One-command, read-only end-to-end visual correction evidence audit.

This orchestrates existing pure Python validators. It never edits Blender,
captures images, runs agents or treats mask overlap as artistic certification.

Usage:
 python scripts/visual_iteration_audit.py manifest.json --evidence-root ./views \
  --scene-before before_scene.json --scene-after after_scene.json \
  --review visual_review.json
"""
import argparse
import json
from pathlib import Path

from compare_scene_baselines import compare as compare_scene, read_snapshot
from reference_silhouette_compare import compare_masks
from visual_iteration_gate import evaluate as evaluate_iteration
from visual_review_report import assess_review

MAX_MANIFEST_BYTES = 200_000
ALLOWED_VIEWS = ("front", "side", "three_quarter")


def _load(path, max_bytes=2_000_000):
    filename = Path(path)
    if not filename.is_file() or filename.stat().st_size > max_bytes:
        raise ValueError("Missing or oversized JSON file")
    return json.loads(filename.read_text(encoding="utf-8"))


def run(root, manifest, snapshot_before, snapshot_after, review):
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object")
    asset = manifest.get("asset")
    views = manifest.get("views")
    if not isinstance(asset, str) or not asset.strip():
        raise ValueError("Explicit asset name required")
    if not isinstance(views, list) or len(views) != 3:
        raise ValueError("Exactly front, side and three_quarter views required")
    chosen = []
    before_pairs, after_pairs = [], []
    for entry in views:
        if not isinstance(entry, dict):
            raise ValueError("View entry must be an object")
        view = entry.get("view")
        if view not in ALLOWED_VIEWS or view in chosen:
            raise ValueError("Unique front, side and three_quarter views required")
        chosen.append(view)
        for key in ("reference", "before", "after"):
            if not isinstance(entry.get(key), str) or not entry[key].strip():
                raise ValueError("View requires reference, before and after PNG")
        before_pairs.append({"reference": entry["reference"], "render": entry["before"], "view": view})
        after_pairs.append({"reference": entry["reference"], "render": entry["after"], "view": view})
    if set(chosen) != set(ALLOWED_VIEWS):
        raise ValueError("Missing required comparison view")
    if not isinstance(review, dict) or review.get("asset") != asset:
        raise ValueError("Reviewer report must name same asset")

    before = compare_masks(root, before_pairs)
    after = compare_masks(root, after_pairs)
    scene = compare_scene(snapshot_before, snapshot_after)
    visual = assess_review(review)
    gate = evaluate_iteration(before, after, scene, visual)
    return {
        "asset": asset,
        "result": gate,
        "source_provenance": {
            "before": before, "after": after,
            "scene_check": scene, "review_receipt": visual,
        },
        "inspected_pixels": "RGBA_ALPHA_MASKS_ONLY",
        "material_and_artistic_quality": "NOT VERIFIED",
        "real_blender_correction_executed": "NOT VERIFIED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--evidence-root", required=True)
    parser.add_argument("--scene-before", required=True)
    parser.add_argument("--scene-after", required=True)
    parser.add_argument("--review", required=True)
    args = parser.parse_args()
    try:
        result = run(args.evidence_root, _load(args.manifest, MAX_MANIFEST_BYTES),
                     read_snapshot(args.scene_before), read_snapshot(args.scene_after),
                     _load(args.review))
    except (ValueError, TypeError, OSError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "NOT VERIFIED", "error": str(exc)}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result["result"]["status"] == "REVIEW_REQUIRED" else 1


if __name__ == "__main__":
    main()
