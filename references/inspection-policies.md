# Professional geometry inspection — configuration recipes

`scripts/inspect_geometry.py` is a **read-only evidence tool**. Paste it into Blender via an available MCP code-execution tool and edit only the three configuration constants at the top. Do not run it with default target names on unrelated scenes.

## Example: rigid seat and four supports

```python
TARGET_NAMES = [
    "Chair_Seat", "Chair_Leg_FL", "Chair_Leg_FR",
    "Chair_Leg_RL", "Chair_Leg_RR",
]
POLICIES = {
    "Chair_Seat": {
        "solid": True, "single_shell": True, "positive_volume": True,
        "dimensions": (0.48, 0.45, 0.06), "dimension_tolerance": 0.04,
        "max_triangles": 1000,
    },
    "Chair_Leg_FL": {
        "solid": True, "positive_volume": True,
        "ground_z": 0.0, "ground_tolerance": 0.005,
    },
    "Chair_Leg_FR": {
        "solid": True, "positive_volume": True,
        "ground_z": 0.0, "ground_tolerance": 0.005,
    },
    "Chair_Leg_RL": {
        "solid": True, "positive_volume": True,
        "ground_z": 0.0, "ground_tolerance": 0.005,
    },
    "Chair_Leg_RR": {
        "solid": True, "positive_volume": True,
        "ground_z": 0.0, "ground_tolerance": 0.005,
    },
}
RELATIONSHIPS = [
    {"type": "max_aabb_gap", "a": leg, "b": "Chair_Seat", "max_gap": 0.01}
    for leg in ("Chair_Leg_FL", "Chair_Leg_FR", "Chair_Leg_RL", "Chair_Leg_RR")
]
```

The numbers are **example dimensions**, not universal chair engineering specifications. Respect the actual scene units, design and brief. Configure `positive_volume` only for intended closed solids with outward shell winding. Separate pieces are legitimate for many chairs; do not demand a single connected mesh for the complete asset.

## What the checks mean

| Check | Evidence it supplies | It does **not** prove |
|---|---|---|
| `solid` | evaluated mesh has no open/boundary/wire/non-manifold edges and no loose vertices | collision-free, wall thickness, printability |
| `positive_volume` | signed shell volume when closed; negative often indicates reversed winding | surface normals all correct in mixed/nested shells |
| `single_shell` | evaluated edge-connected face island count | different objects are physically attached |
| `dimensions` | world-space evaluated axis-aligned bounds relative to target | silhouette or reference fidelity |
| `ground_z` | evaluated minimum vertex Z near desired plane | stable support or walkability |
| `max_triangles` | evaluated triangulated polygon count | acceptable frame rate |
| `max_aabb_gap` | definite separation between bounding boxes exceeds allowed gap | actual surface contact when boxes are near |
| `no_aabb_overlap` | definitely disjoint AABBs | exact mesh interpenetration when AABBs overlap |

AABB overlap triggers **REVIEW** rather than a fabricated collision diagnosis. Missing targets, unsupported modifiers and inconclusive metrics become **NOT VERIFIED**. A model can pass all technical checks and still have terrible proportions, shading, reference fidelity, UVs or animation. Capture actual viewport images and perform target-specific reviews separately.

## Feedback cycle

1. Define target names, dimensions and **intentional** assembly connections.
2. Execute the inspector and read `MCP_PROFESSIONAL_INSPECTION_BEGIN/END` JSON.
3. Fix clear structural ISSUEs in a duplicate or owned collection and rerun.
4. Review ambiguous AABB/polygon findings in appropriate viewport views.
5. Run specialized UV/material/export/animation tests as needed.
6. Record final statuses with evidence, including visual NOT VERIFIED if the image tool is unavailable.

Compatibility is tied to the active Blender build and MCP client. See `references/agent-compatibility.md`.
