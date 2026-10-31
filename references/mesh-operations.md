# Mesh operations and safe refinement

## Contract

scripts/mesh_operations.py accepts explicit source object names and output names. It duplicates the source object and mesh data, then adds non-destructive modifiers or applies topology edits to the duplicate. The source object is never modified. Output names and cutter names must be unused.

## Modifier operations

| Operation | Parameters | Behavior |
|---|---|---|
| bevel | width, segments | Adds an angle-limited Bevel modifier |
| weighted_normal | — | Adds Weighted Normal shading modifier |
| solidify | thickness | Adds a Solidify modifier |
| triangulate | — | Adds a Triangulate modifier |
| decimate | ratio | Adds a Decimate modifier; does not apply it |
| mirror | axes, use_clip | Adds a Mirror modifier |
| subdivision | levels, render_levels | Adds a Subdivision Surface modifier |
| boolean_difference | dimensions, location, cutter_name | Creates a hidden owned box cutter and a Difference modifier |

## Topology operations

These operate on the duplicated mesh data, not the source:
- inset_faces: requires explicit face_indices and positive thickness; optional depth and even offset
- extrude_faces: requires explicit face_indices and a non-zero 3D offset

Face indices refer to the source mesh's BMesh face ordering at the time the duplicate is processed. Use a technical inspection or a known construction script to identify faces; do not guess indices on an arbitrary production mesh.

## Example

    TARGETS = [
      {
        "source": "Panel",
        "output": "Panel_Refined",
        "operations": [
          {"type": "inset_faces", "face_indices": [0], "thickness": 0.08},
          {"type": "extrude_faces", "face_indices": [1], "offset": (0, 0, 0.12)},
          {"type": "bevel", "width": 0.02, "segments": 3},
          {"type": "weighted_normal"}
        ]
      }
    ]

For complex operations, split stages into separate runs and inspect the output between stages. The current tool does not provide robust face-selection by semantic region, edge-loop bridge, automatic hole filling, retopology, or complex boolean cleanup.

## Safety and validation

- Do not point output at the source name.
- Keep the source object and source mesh unchanged.
- Inspect boolean cutter placement and evaluated modifier output.
- Run scripts/inspection_report.py on the duplicate.
- Visual inspection is still required for silhouette, pinching, shading, and unintended intersections.
- Decimate remains a modifier and must not be applied automatically.
