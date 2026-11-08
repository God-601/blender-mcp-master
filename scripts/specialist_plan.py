"""Pure module planner; no scene edits, agent launches or eager guide loading."""
import argparse
import json
from pathlib import Path

from workflow_router import route

REGISTRY = Path(__file__).resolve().parents[1] / "references/specialist-modules.json"


def load_modules():
    return json.loads(REGISTRY.read_text(encoding="utf-8"))["modules"]


def build_plan(task):
    routed = route(task)
    modules = load_modules()
    primary = {"materials": "materials", "retopology": "retopology"}.get(routed["category"], "modeling")
    selected = [primary]
    for need in task.get("needs", []):
        module = {"pbr": "materials", "uv": "uv", "optimization": "optimization", "export": "export"}.get(need)
        if module and module not in selected:
            selected.append(module)
    selected = [m for m in ('modeling', 'retopology', 'uv', 'materials', 'optimization', 'export') if m in selected]
    selected.append("validation")
    steps = []
    for module in selected:
        steps.append({
            "id": module, "module": module,
            "depends_on": [steps[-1]["id"]] if steps else [],
            "access": "read" if module == "validation" else "write",
            "acceptance": modules[module]["acceptance"],
            "guides": modules[module]["guides"], "scripts": modules[module]["scripts"],
        })
    return {"schema_version": 1, "mode": "delegated" if len(selected) > 3 else "single",
            "destination": routed["destination"], "route": routed, "steps": steps}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path, help="JSON brief accepted by workflow_router.route")
    args = parser.parse_args()
    print(json.dumps(build_plan(json.loads(args.task.read_text(encoding="utf-8"))), indent=2))


if __name__ == "__main__":
    main()
