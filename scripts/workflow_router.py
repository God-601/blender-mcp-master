"""Deterministic, pure-Python guide router; no scene access or external calls.

The router suggests what to read, never silently loads guides. Agent remains
responsible for design interviews and actual tool capability discovery.
"""
import json

TASK = {"category": "hard_surface", "destination": "render", "needs": []}
PRIMARY = {
    "hard_surface": "references/hard-surface.md",
    "organic": "references/organic.md",
    "stylized": "references/stylized-lowpoly.md",
    "architecture": "references/modular-modeling.md",
    "character": "references/character-rig.md",
    "materials": "references/uv-baking.md",
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
    if category not in PRIMARY:
        raise ValueError("category must be one of: " + ", ".join(PRIMARY))
    destination = task.get("destination", "other")
    if destination not in ALLOWED_DESTINATIONS:
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
    if task.get("continuation", False) not in (True, False):
        raise ValueError("continuation must be bool")
    if task.get("continuation", False):
        questions = []
    else:
        questions = [topic for topic in QUESTION_TOPICS if topic not in known and topic not in delegated]
    primary = PRIMARY[category]
    secondary = []
    for need in needs:
        guide = EXTRAS[need]
        if guide != primary and guide not in secondary:
            secondary.append(guide)
    if destination in ("roblox", "unity", "godot", "unreal") and primary != EXTRAS["export"] and "export" in needs:
        # Already included above. Never infer export simply from the engine label:
        # a user may just be editing a Blender asset for a future game.
        pass
    return {
        "category": category, "destination": destination,
        "primary": primary, "optional": secondary,
        "questions_to_consider": questions,
        "questions_already_known_or_delegated": sorted(set(known) | set(delegated)),
        "loaded_reference_count": 0,
        "limits": "Routing is advisory, not verification of asset, client or MCP capabilities.",
    }


if __name__ == "__main__":
    print(json.dumps(route(TASK), ensure_ascii=False, indent=2, sort_keys=True))
