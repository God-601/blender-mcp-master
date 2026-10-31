# Geometry engine

## Goal

Provide reusable construction primitives and composable operations so the agent can build objects
from a plan rather than relying on one-off code. This module creates geometry; cleanup, validation,
optimization, and export remain separate concerns.

## Initial executable capability: declarative builder

scripts/geometry_builder.py creates named components from a configuration list. It currently supports:
- box
- UV sphere
- icosphere
- cylinder
- cone
- torus
- beam between two 3D points
- extruded 2D profile
- lathed radius/Z profile
- lofted matching cross-sections across multiple Z levels

The builder creates new objects in a dedicated collection and tags ownership. It does not silently
replace an existing object. Configure dimensions in Blender units and use explicit names.

### Example: low-poly stylized sword parts

    COMPONENTS = [
      {"name": "Blade", "type": "extruded_profile",
       "profile": [(-0.10, 0), (0.10, 0), (0.07, 1.8), (0, 2.1), (-0.07, 1.8)],
       "height": 0.06},
      {"name": "Guard", "type": "beam",
       "start": (-0.42, 0, 2.0), "end": (0.42, 0, 2.0),
       "radius": 0.055, "vertices": 8},
      {"name": "Grip", "type": "cylinder",
       "location": (0, 0, -0.28), "radius": 0.075, "depth": 0.55,
       "vertices": 8},
      {"name": "Pommel", "type": "ico_sphere",
       "location": (0, 0, -0.62), "radius": 0.13, "subdivisions": 1}
    ]

This is a geometry blockout example, not a finished sword recipe. The agent must inspect orientation,
proportions, intersections, silhouette, and refine the mesh.

## Organic construction example

scripts/organic_rock_builder.py creates a deterministic stylized rock from an icosphere base using seeded smooth radial deformation and an optional flattened bottom. It creates a new object in an owned collection and refuses unrelated name collisions. This is a base-form generator; the agent must inspect the silhouette and refine it for the target style.

## Additional executable construction and refinement

- `scripts/mesh_operations.py` duplicates explicitly named source meshes and adds non-destructive bevel, weighted-normal, solidify, triangulate, decimate, mirror, subdivision, or boolean-difference modifiers. The source is preserved; output names must be unused.
- `scripts/hard_surface_builder.py` creates a mechanical panel, a boolean pocket cutter, and four fasteners. The boolean remains a modifier; inspect the evaluated result in Blender.
- `scripts/geometry_nodes_builder.py` creates a parametric repeated-post node group with exposed Count, Spacing, Height, and Radius inputs. This requires a Blender version with the Geometry Nodes API; runtime support must be checked before use.
- `scripts/organic_tree_builder.py` builds a deterministic stylized tree from a tapered trunk, branch meshes, and clustered icospheres.

## Geometry family roadmap

### Primitive and profile construction
Configurable primitives, beam/connector construction, extruded profiles, lathed profiles, lofted profiles,
polygon and cross-section validation.

### Mesh operations
Extrude/inset, bridge and loft, bevel and chamfer, boolean cutter workflows, merge/dissolve,
topology-aware cleanup, normals, and shading operations.

### Hard surface
Panels, recesses, holes, ribs, fasteners, mirrored parts, radial construction, mechanical
assemblies, pivots, and non-destructive modifier stacks.

### Organic
Controlled deformation, seeded noise/displacement, branching and curve growth, volume composition,
remeshing, and stylized shape language.

### Modular and parametric
Snap points, grid conventions, reusable modules, linked instances, dimension-driven components,
editable parameters, and deterministic regeneration.

### Geometry Nodes
Reusable node-group strategies, instancing/distribution, curve and volume workflows, and
version-aware node setup with runtime tests.

## Quality gates

1. Validate parameter types and ranges before creating datablocks.
2. Use deterministic naming and explicit collection ownership.
3. Never overwrite an unrelated object.
4. Report created objects and geometry counts.
5. Add runtime tests for valid, invalid, and repeated execution.
6. Inspect representative output in Blender; static parsing is insufficient.
7. Document version support only after runtime verification.

## Current limitations

- The initial builder is a blockout/construction foundation, not a full CAD or topology toolkit.
- extruded_profile expects a simple polygon; it does not detect arbitrary self-intersections or holes.
- lathe creates side quads and end caps; profile topology and winding should be checked for the intended shape.
- loft requires the same number of points in each section and strictly increasing Z; it does not currently detect self-intersections or twist between profiles.
- No automated visual inspection is performed by the script.
- The Geometry Nodes generator currently exposes one parametric mesh primitive; it is not yet a general node-group library.
- Boolean construction is currently a non-destructive modifier workflow with an explicit cutter object; complex boolean cleanup is not automated.
- Robust inset/bridge operations, retopology, sculpt workflows, and arbitrary profile self-intersection handling remain future capabilities.
