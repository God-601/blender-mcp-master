# Official Blender documentation — agent reference map

**Purpose:** give Blender MCP Master an authoritative starting point when a modeling operation, UI property, Blender Python API, or exporter behavior is uncertain. This is an index, **not** a copy of the Blender Manual or a promise to cover every tool.

**Primary sources**

- [Blender Reference Manual](https://docs.blender.org/manual/en/latest/) — complete official user-facing documentation (modeling, sculpting, painting, modifiers, nodes, materials, rendering, animation, import/export).
- [Blender Python API](https://docs.blender.org/api/current/) — reference for scripts and `bpy` types, properties, operators and context.
- [Blender manual in Portuguese](https://docs.blender.org/manual/pt/latest/) — localized entry point; verify translation completeness against English where precision matters.

> **Version gate:** `latest` and `current` move as Blender develops. Before using a named API, modifier parameter, node socket or exporter option, determine the actual `bpy.app.version` / Blender runtime version, then consult its matching documentation. Don't apply current-version instructions blindly to Blender 3.x or 4.x.

## Model-building reference map

| Modeling decision | Official documentation | Related guidance in this repository | Evidence to collect |
| --- | --- | --- | --- |
| Object/Edit/Sculpt mode and mesh fundamentals | [Mesh modeling introduction](https://docs.blender.org/manual/en/latest/modeling/meshes/introduction.html) | `modeling-foundations.md` | Object types, mode, named mesh targets |
| Cleanup, disconnected/degenerate meshes, coincident vertices | [Mesh cleanup](https://docs.blender.org/manual/en/latest/modeling/meshes/editing/mesh/cleanup.html) | `mesh-operations.md`, `topology-retopology.md` | Before/after counts; visually inspect defects |
| Reversible geometry with modifiers | [Modifier concepts](https://docs.blender.org/manual/en/latest/modeling/modifiers/introduction.html), [Bevel modifier](https://docs.blender.org/manual/en/5.1/modeling/modifiers/generate/bevel.html) | `hard-surface.md`, `mesh-operations.md` | Stack order, evaluated topology, shading |
| Procedural geometry / Geometry Nodes | [Geometry Node Editor](https://docs.blender.org/manual/en/latest/editors/geometry_node.html), [Fields](https://docs.blender.org/manual/en/latest/modeling/geometry_nodes/fields.html) | `parametric-geometry-nodes.md`, `geometry-engine.md` | Group inputs, dependencies, realized/evaluated geometry |
| UV unwrapping and layout | [UV workflow](https://docs.blender.org/manual/en/latest/modeling/meshes/uv/unwrapping/introduction.html), [seams](https://docs.blender.org/manual/en/5.2/modeling/meshes/uv/unwrapping/seams.html) | `uv-baking.md` | Islands, bounds, padding, distortion/overlap where testable |
| PBR materials and shader realism | [Blender Manual](https://docs.blender.org/manual/en/latest/) → Rendering → Shader Nodes | `materials.md`, `shading-recipes.md` | Actual node links, texture color spaces, render under neutral light |
| Game and interchange export | [FBX import/export](https://docs.blender.org/manual/en/latest/files/import_export/fbx.html), [Blender Manual](https://docs.blender.org/manual/en/latest/) → Files → Import/Export | `game-ready-export.md`, `p1-production-pipeline.md` | Format, axes, scale, supported materials, re-import where possible |
| Python-based scene/model inspection | [Blender Python API](https://docs.blender.org/api/current/) → `bpy.types.Object`, `bpy.types.Mesh`, `bpy.types.Depsgraph` | `inspection-policies.md`, `scripts/inspect_geometry.py` | Actual version, ownership, base vs evaluated mesh evidence |
| Sculpting, retopology, deformation | [Blender Manual](https://docs.blender.org/manual/en/latest/) → Sculpting & Painting, Modeling | `sculpting-highpoly.md`, `topology-retopology.md`, `character-rig.md` | Silhouette, edge flow, deforming-pose tests |

## Agent research protocol

1. **Name the uncertainty.** Example: "Does this Blender version support the requested modifier property?" Do not search aimlessly.
2. **Inspect the live environment** using read-only Blender MCP tools and/or `bpy.app.version`. Don't assume that an example for the latest API works in Blender 3.1.
3. **Find the matching official reference.** Prefer the specific operator, property or modifier page over forum advice. Record which Blender version the page describes.
4. **Run a minimal, non-destructive probe** in a scratch or separately owned collection. Capture success/failure, output, and unexpected scene changes.
5. **Select the modeling operation from the result**, not from a memorized recipe. Prefer the least destructive option meeting the task's acceptance criteria.
6. **Verify twice when needed:** machine-readable mesh checks and actual screenshots/preview for visual issues. Export must be checked separately if the task requires it.
7. **Report evidence level.** A source page establishes expected behavior; it does not prove that a specific script or operation worked in the user's Blender session.

## Version-sensitive examples

- Blender 3.1 and older: verify whether operator overrides and color-data APIs from newer examples exist before running them.
- Blender 4.0–4.2: shader sockets, normal handling, and EEVEE changes require explicit version checks.
- Geometry Nodes: node identifiers, socket names and group interfaces can evolve; inspect rather than hard-code expectations.
- Exporters: available operators and flags depend on the runtime and installed addons.

Use [the main skill](../SKILL.md) for this project's actual compatibility guidance. This index is for **source verification and choosing the right manual chapter**, not for changing package dependencies, overriding existing scene data, or claiming that all Blender versions have been tested.

*Official docs checked as research references on 2026-11-02. Follow the version-specific pages at execution time.*
