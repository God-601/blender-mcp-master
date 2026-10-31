# Blender MCP Master — target architecture

## Purpose

The skill is an agent-side modeling system that coordinates planning, Blender capabilities,
visual inspection, and evidence-based correction. It is not the Blender MCP server itself.
Keep three things distinct:

1. **Skill:** instructions, routing, decision policy, and knowledge.
2. **MCP adapter:** discovers and invokes the tools exposed by the active integration.
3. **Capabilities:** scripts and Blender operations that actually construct or inspect assets.

The architecture must improve real modeling outcomes, not merely increase documentation volume.

## System layers

| Layer | Responsibility | Existing foundation |
|---|---|---|
| Agent interface | Read skill and invoke tools | Agent Skills-compatible SKILL.md |
| Universal capability discovery | Map available MCP tools to semantic capabilities | Quality-loop guidance; needs a formal matrix |
| Modeling intelligence | Analyze request, decompose object, select techniques, plan stages | Planning gate in SKILL.md |
| Geometry engine | Construct primitives, profiles, beams, meshes, procedural and modular forms | geometry_builder.py, modular_builder.py, hard_surface_builder.py, organic builders |
| Mesh operations | Refine explicit targets with non-destructive modifiers and duplicate-first corrections | mesh_operations.py, localized_correction.py |
| Parametric systems | Expose editable parameters through Geometry Nodes where supported | geometry_nodes_builder.py |
| Technical inspection | Produce read-only topology and scene metrics | inspection_report.py, validate_asset.py |
| Knowledge/history | Store execution records in the current project | technique_history.py |
| Benchmark evidence | Collect reproducible technical metrics and fixed prompts | benchmark_report.py, benchmark-prompts.md |
| Artistic direction | Silhouette, proportions, style, composition, materials | Specialist references |
| Scene management | Scope objects, collections, ownership, preserve user scene | setup_scene.py and safety rules |
| Visual engine | Multi-angle inspection and reference comparison | MCP look guidance |
| Quality system | Geometry diagnostics, visual review, localized correction | validate_asset.py and modeling quality loop |
| Execution runtime | Execute operations, report errors, protect state | MCP executor and scripts |
| Knowledge and feedback | Reusable technique records and benchmark history | To be developed |
| Benchmark | Repeatable visual and technical evaluation | benchmark_report.py collects technical evidence; visual review and cross-agent runs remain external/manual |

## Dependency direction

- The skill routes work; it must not depend on one specific MCP implementation.
- Intelligence chooses capabilities; it must not contain low-level Blender operator code.
- Geometry capabilities create or modify Blender data; they must not decide artistic acceptance alone.
- Visual inspection and technical validation provide evidence to the planner.
- Knowledge stores tested techniques and limitations; unverified claims remain marked unverified.
- Export and optimization are downstream concerns, not substitutes for modeling capability.

## Core workflow

1. Discover available tools and Blender version.
2. Inspect the existing scene and identify user-owned content.
3. Analyze the task, style, destination, scale, and acceptance criteria.
4. Decompose the object into parts and dependencies.
5. Select construction methods and produce a compact staged plan.
6. Build primary forms using explicit, named targets.
7. Inspect silhouette and proportions from relevant views.
8. Refine geometry, topology, materials, and details.
9. Run technical diagnostics and visual review.
10. Correct the highest-impact defects locally.
11. Reinspect and report measured evidence plus unverified items.

The workflow is adaptive: inspection can return the task to decomposition, planning, or a specific construction stage.

## Module boundaries

### Intelligence
Task analysis, object decomposition, technique selection, modeling plan, and adaptive refinement.

### Geometry
Primitive construction, mesh operations, hard-surface construction, organic construction,
curves and profiles, procedural and parametric construction, modular systems, and Geometry Nodes.

### Artistic
Silhouette and negative-space review, proportion systems, style constraints, composition, and materials.

### Scene
Object and collection ownership, naming and hierarchy, references, helpers, and safe cleanup boundaries.

### Visual
Inspection view generation, neutral presentation, render capture, and reference comparison.

### Quality
Geometry validation, visual acceptance, diagnostic classification, and local correction recommendations.

### Execution
Capability adapter, Blender version checks, script execution, error/result reporting, and safe operation boundaries.

### Knowledge
Technique specifications, compatibility notes, verified examples, execution history, and feedback.

## Non-goals

- Reimplementing the Blender MCP server.
- Requiring a paid external model-generation API.
- Treating a successful Python call as proof of visual quality.
- Creating a giant monolithic script or a giant SKILL.md.
- Claiming universal compatibility without agent/runtime tests.
- Replacing artistic judgment with a single numeric quality score.

## Implementation strategy

Implemented vertical slices on the feature branch:
1. Declarative geometry, organic and modular builders.
2. Duplicate-first mesh operations and hard-surface construction.
3. Editable Geometry Nodes panel generator.
4. Read-only technical inspection and localized correction copies.
5. Blender-side capability probe, in-project technique history, and technical benchmark report.

Still requiring external execution or further implementation:
- Actual multi-agent runs in Codex, Claude, Cursor, OpenCode, and Kilo Code.
- MCP visual capture and reference-image comparison (the skill routes to the client's visual tool; scripts cannot fabricate that evidence).
- Automated defect recognition from images and closed-loop artistic correction.
- Broader Geometry Nodes systems, advanced topology operations (robust inset/bridge/retopology), and larger parametric kits.
- Technique retrieval/ranking and feedback-driven learning beyond append-only history.

Do not create empty directories or placeholder modules just to match a diagram. Add a module when it has
a defined contract, an implementation or useful guidance, and a verification path.
