# Guided advanced retopology (copy-first)

This is the source-backed reference for `scripts/retopology_advanced.py`. It provides **explicit** bridge loops, planar hole filling and interior vertex relaxation. It does **not** perform unconstrained QuadriFlow, automatic character retopology, semantic loop extraction, shape-key preservation, rig deformation, or texture rebaking.

## Preconditions

1. Run the GENERAL KICKOFF for a new project, then identify the requested topology outcome and required deformation / export constraints.
2. Use read-only scene inspection first. `TARGETS` must name mesh objects explicitly. The script has no fallback to selected objects or all scene meshes.
3. Provide ordered vertex indices from the **base mesh**, confirmed in Blender. Never guess vertices from screen coordinates.
4. Input meshes must be in Object mode, with no modifiers or shape keys. To use a modifier result, create an owned, inspected applied intermediate first.
5. Inspect the source object before retopology. Confirm the destination object name is unused.

## Supported operations

| Action | Parameters | Safety & limitations |
| --- | --- | --- |
| `bridge_loops` | `loops`: two ordered vertex-index loops | Equal counts, distinct vertices, existing boundary edges; bridge creates quads; no auto-alignment |
| `fill_hole` | `loop`: ordered boundary cycle; optional `planarity_tolerance` | Planar input only, max 64 vertices, creates an n-gon; unsuitable as final deforming topology |
| `relax_vertices` | `vertices`, `factor` (0–1], `iterations` (1–20), `preserve_boundary` | Laplacian smoothing; boundaries are preserved by default; may shrink features and lose silhouette |

Configuration example for two ordered square rings:

```python
TARGETS = [
    {
        "source": "Rings",
        "output": "Rings_Bridged",
        "operations": [
            {"type": "bridge_loops", "loops": [[0, 1, 2, 3], [4, 5, 6, 7]]},
        ],
    },
]
```

The output is a **new** mesh object in an owned collection. Failures remove the failed output copy; the original mesh is preserved. A batch containing multiple targets can complete some targets while rejecting others — inspect `status` and `errors` rather than assuming a whole-batch rollback.

## Quality acceptance

- Preserve the original object's mesh vertices, polygons, materials and modifiers.
- Bridge: check connected seam geometry, face orientation, n-gons, and unintended twisting. Two ordered loops must follow compatible orientations. A valid face count is not proof of desired edge flow.
- Fill: confirm planar tolerance and whether an n-gon is acceptable. For animated regions, replace the cap with a purpose-built quad topology.
- Relax: compare silhouette and clearances before/after, especially for narrow or mechanical parts.
- Inspect actual front, side, and three-quarter views. Use `inspect_geometry.py` for read-only evaluated topology and `validate_asset.py` for technical budget reports.
- Run joint bend/twist tests **only after** creating a suitable deformation topology; this script by itself cannot make deformation quality PASS.
- On failure, diagnose before changing another operation and perform local no-regression checks.

### Status boundaries

`SUCCESS` means the requested code operations executed. All **visual quality, animation readiness, UV retention, and export compatibility** are still **NOT VERIFIED** until separately checked. If the input has a rig, shape keys or unsupported stack, don't bypass the guard.

See [Topology and retopology](topology-retopology.md), [Quality loop](modeling-quality-loop.md), and [Safe scene editing](p0-integrity.md).
