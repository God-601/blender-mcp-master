# Parametric Geometry Nodes

## Current executable example

scripts/geometry_nodes_builder.py creates a Geometry Nodes object that instances a cylinder along a Mesh Line and realizes the instances. The modifier exposes four editable inputs:

| Input | Meaning |
|---|---|
| Count | Number of posts |
| Spacing | Distance between post centers |
| Height | Post length |
| Radius | Post radius |

The generated object and node group use explicit ownership tags. Existing object, collection, or unrelated node-group names are not overwritten.

## Workflow

1. Probe Blender version and Geometry Nodes availability with scripts/capability_probe.py.
2. Run the builder in a clean test scene or a dedicated asset collection.
3. Change the modifier inputs to adjust the assembly.
4. Inspect the generated geometry and bounding dimensions.
5. Add downstream modifiers or use the generated assembly as a reusable module.

## Compatibility and limits

- The builder uses the Geometry Nodes node-group interface API when available and an older group input/output fallback otherwise.
- Runtime tests currently cover bpy 4.2.23, 4.5.15, 5.0.1, 5.1.2, and 5.2.3.
- This is a focused procedural array example, not a general-purpose node-group authoring framework.
- Curve instancing, distributed assets, nested groups, fields-based deformation, and automatic node-group regeneration from arbitrary user parameters remain future work.
- An object with a Geometry Nodes modifier must be evaluated through Blender's dependency graph to inspect its generated mesh.
