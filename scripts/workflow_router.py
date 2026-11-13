"""Deterministic, pure-Python guide router; no scene access or external calls.

The router suggests what to read, never silently loads guides. Agent remains
responsible for design interviews and actual tool capability discovery.
"""
import argparse
import json
from pathlib import Path

PRIMARY = {
    "hard_surface": "references/hard-surface.md",
    "organic": "references/organic.md",
    "stylized": "references/stylized-lowpoly.md",
    "architecture": "references/modular-modeling.md",
    "character": "references/character-rig.md",
    "materials": "references/materials.md",
    "game_asset": "references/game-ready-export.md",
    "retopology": "references/advanced-retopology.md",
}
EXTRAS = {
    "rigging": "references/topology-retopology.md",
    "uv": "references/uv-baking.md",
    "pbr": "references/materials.md",
    "fit": "references/component-fit-and-joints.md",
    "visual": "references/visual-inspection.md",
    "optimization": "references/model-performance-strategy.md",
    "export": "references/game-ready-export.md",
    "measure": "references/measured-proportion-recipes.md",
}
ALLOWED_DESTINATIONS = {"render", "roblox", "unity", "godot", "unreal", "animation", "3d_print", "other"}
QUESTION_TOPICS = ("reference", "silhouette", "materials", "purpose", "technical")


def route(task):
    if not isinstance(task, dict):
        raise ValueError("task must be an object")
    category = task.get("category")
    if not isinstance(category, str) or category not in PRIMARY:
        raise ValueError("category must be one of: " + ", ".join(PRIMARY))
    destination = task.get("destination", "other")
    if not isinstance(destination, str) or destination not in ALLOWED_DESTINATIONS:
        raise ValueError("unsupported destination")
    needs = task.get("needs", [])
    if not isinstance(needs, list) or any(not isinstance(n, str) or n not in EXTRAS for n in needs):
        raise ValueError("needs must contain recognized task requirements")
    if len(needs) != len(set(needs)):
        raise ValueError("needs contains duplicates")
    known = task.get("known", [])
    delegated = task.get("delegated", [])
    for field, value in (("known", known), ("delegated", delegated)):
        if not isinstance(value, list) or any(n not in QUESTION_TOPICS for n in value):
            raise ValueError(field + " contains invalid design topics")
    continuation = task.get("continuation", False)
    if not isinstance(continuation, bool):
        raise ValueError("continuation must be bool")
    if continuation:
        questions = []
    else:
        questions = [topic for topic in QUESTION_TOPICS if topic not in known and topic not in delegated]
    primary = PRIMARY[category]
    secondary = []
    for need in needs:
        guide = EXTRAS[need]
        if guide != primary and guide not in secondary:
            secondary.append(guide)
    return {
        "category": category, "destination": destination,
        "primary": primary, "optional": secondary,
        "questions_to_consider": questions,
        "questions_already_known_or_delegated": sorted(set(known) | set(delegated)),
        "loaded_reference_count": 0,
        "limits": "Routing is advisory, not verification of asset, client or MCP capabilities.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path, help="Path to a UTF-8 JSON task brief")
    args = parser.parse_args()
    try:
        routed = route(json.loads(args.task.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(routed, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
