# Modeling intelligence

## Responsibility

The intelligence layer converts a user request into a build strategy. It chooses and sequences
capabilities; it does not implement low-level geometry operations itself.

## Task analysis

Extract:
- object category and intended use
- visual style and reference constraints
- primary silhouette and negative spaces
- major components and their relationships
- scale, units, orientation, and pivot
- topology/deformation requirements
- geometry, material, UV, and performance budgets
- acceptance criteria and unresolved assumptions

Do not ask for details that can be safely inferred. Ask when ambiguity changes the construction strategy
or when an irreversible choice requires approval.

## Decomposition

Represent an object as a dependency graph rather than a flat checklist.

Each component records:
- stable ID and Blender object name
- parent/child or attachment relationships
- approximate dimensions and relative proportions
- symmetry and repetition rules
- construction method candidates
- dependencies and build order
- inspection criteria

Prioritize silhouette-defining components. Decorative details must not precede primary form approval.

## Technique selection

Choose methods using these factors:
1. shape and curvature
2. required topology and deformation
3. target use and export constraints
4. editability and expected revisions
5. geometric complexity
6. Blender version and available MCP capabilities
7. reliability and verification cost

Example decision rules:
- rigid planar parts: profile extrusion or hard-surface mesh operations
- repeated radial parts: rotational construction or instancing
- long connectors: beams, curves, or swept profiles
- rotationally symmetric objects: lathe/revolve
- irregular rocks: icosphere base plus deterministic deformation
- modular architecture: reusable dimensioned components and snap rules
- deforming characters: topology and rigging requirements take precedence over raw speed

The agent must state when a selected method is an approximation.

## Staged plan

For each stage specify:
- goal
- component targets
- operation or capability
- parameters
- dependencies
- expected geometry/result
- inspection gate
- rollback or recovery approach

Keep the plan compact for simple assets. Complex assets should have explicit checkpoints.

## Adaptive refinement

After each meaningful inspection:
1. classify defects
2. rank by impact on acceptance criteria
3. identify the smallest responsible component set
4. select a local correction
5. execute and inspect again
6. stop if repeated iterations fail to improve the result

Do not use a numeric score as the only decision signal. Preserve reviewer notes and unverified criteria.

## Definition of done

A task is complete only when:
- required components exist
- silhouette and proportions satisfy the brief
- technical constraints are checked
- visual inspection has been performed when available
- remaining issues and unverified checks are reported
- user-owned scene content remains protected
