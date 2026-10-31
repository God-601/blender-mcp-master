# Module contracts

These contracts describe responsibilities and data exchanged between the skill's conceptual modules.
They are language-neutral. A module may be implemented as agent instructions, a Blender Python
script, or an MCP capability; do not imply that every contract is already executable.

## 1. Capability discovery

Input: tools exposed by the current agent/MCP session; Blender version and addon status when available.

Output: semantic capability map, exact tool names and argument shapes, missing capabilities, and fallbacks.

Required semantic capabilities:
- scene.inspect
- scene.create_collection
- geometry.execute
- visual.inspect
- asset.search (optional)
- asset.import (optional)
- asset.generate (optional)
- scene.save (only when available and authorized)

Never invent a tool name or parameter. Never infer visual inspection from code execution.
Missing optional capabilities must degrade gracefully and be reported.

## 2. Task analysis

Input: user request, reference images, destination, and constraints.

Output fields:
- asset_type
- style
- destination
- scale_and_units
- required_parts
- technical_constraints
- acceptance_criteria
- unknowns

Ask only when an unknown materially changes the build or creates an irreversible decision.

## 3. Object decomposition

Input: task analysis.

Output: ordered component graph. Each component records:
- stable component ID
- visible name
- parent/dependency IDs
- geometric role
- approximate dimensions or proportions
- symmetry/instance policy
- construction method candidate
- inspection criteria

A decomposition is incomplete if major silhouette-defining parts are missing.

## 4. Technique selection

Input: component graph, style, destination, and Blender capabilities.

Output: selected method per component, alternatives, rationale, and known limitations.

Selection considers geometry shape and topology, deformation needs, editability, complexity,
iteration cost, version/API compatibility, and target platform requirements.

## 5. Geometry operation contract

Every reusable geometry operation documents:
- operation ID and version
- input parameters and defaults
- units and coordinate conventions
- preconditions
- created/modified object names
- ownership/scope behavior
- idempotency or duplicate behavior
- destructive effects
- result metrics
- warnings and errors
- supported Blender versions
- tests and known limitations

Recommended result envelope:

    {
      "success": true,
      "created_objects": ["Asset_Body"],
      "modified_objects": [],
      "skipped_objects": [],
      "metrics": {"vertices": 64, "edges": 96, "faces": 34},
      "warnings": [],
      "errors": []
    }

This is a target reporting shape, not a claim that every existing script already returns JSON.

## 6. Visual inspection contract

Input: explicit target objects, required views and shading modes, acceptance criteria, and optional reference.

Output: captured views or unavailable status; defects grouped by silhouette, proportion, geometry,
shading, material, and composition; severity and confidence; suggested localized correction; unverified criteria.

A screenshot is evidence of appearance from one view, not proof of hidden topology or dimensions.

## 7. Validation contract

Separate technical and artistic evidence.

Technical checks may include object existence/dimensions, mesh counts/topology, non-manifold and
degenerate geometry, modifier/transform state, and UV/material requirements.

Visual checks may include silhouette readability, proportion, component completeness, intersections,
style consistency, and material readability.

Every result must be marked PASS, ISSUE, N/A, or NOT VERIFIED. Missing evidence is not PASS.

## 8. Correction contract

Input: ranked defect list and object ownership map.

Output: exact targets, correction method, expected effect, risk/destructive status, and post-correction checks.

Prefer local edits. Do not rebuild unaffected components. If a correction could alter user-owned data,
stop and request approval.

## 9. Knowledge record

A reusable technique record includes problem/intended use, method/parameters, prerequisites, tested
Blender versions, test evidence, known failures/limitations, example asset or fixture, and revision.

Separate verified runtime facts from recommendations and hypotheses.

## 10. Benchmark record

Each run stores benchmark ID and prompt version, agent/model when available, Blender version, MCP
implementation/capabilities, execution strategy, output artifact reference, standardized view captures,
technical metrics, visual rubric scores/reviewer notes, regressions, and limitations.

Do not compare runs unless prompt, scene fixture, view setup, and scoring rubric are controlled.
