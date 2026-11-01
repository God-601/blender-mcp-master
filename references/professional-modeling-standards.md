# Professional 3D modeling standards for agents

This is a **production contract**, not an aesthetic score or a promise that a script is a professional artist. Apply it to substantial assets together with the discipline-specific references. A task is done only when its **stated** acceptance criteria have supporting evidence, or its remaining limitations are explicitly disclosed.

## 1. Production brief (write before construction)

Record these fields, with `unknown` rather than inventing a specification:

| Field | Required decision |
|---|---|
| Intended use | still render / real-time game / animation / 3D print / architecture / CAD / blockout |
| Visual specification | references and their provenance, silhouette, style, focal points, intended camera distance |
| Geometry specification | world scale/units, up/forward axes, dimensions and tolerances, primary components, joints/pivots |
| Deliverable | editable .blend, FBX/glTF/OBJ/STL, texture files, preview renders, variants |
| Downstream contract | topology/deformation, materials/UVs/bakes, destination renderer/engine |
| Cost limits | triangles after modifiers, material slots/draw calls, texel density, time and tool availability |
| Acceptance | measurable shape/technical checks, visual viewpoints, export round trip, human approval if critical |

**P0 clarification gate:** apply `references/clarification-gate.md` before substantial work. Ask a focused question if the brief has a BLOCKER (missing/contradictory requirements) or a QUALITY-RISK choice that will materially change a complex asset. For an exploratory routine prop, pick only safe OPTIONAL defaults and label assumptions. Do not interrogate the user for implementation trivia or details already given. Confirm critical fit/print/rig dimensions before destructive or irreversible work.

## 2. Quality gates and proof obligations

**G0 — Preflight:** discover the actual Blender MCP tool schemas and version; inspect the scene, ownership and units. Protect unrelated objects and files. Record missing tools as NOT VERIFIED.

**G1 — Primary blockout:** build to named dimensions and verify front/side/three-quarter silhouette and major negative spaces. Do not polish if the main forms are wrong. Stop and redesign when proportions contradict the brief.

**G2 — Construction:** component attachment, symmetry or intentional asymmetry, clearances, thickness, pivots, component names and separation for movement. A bounding-box overlap is not proof of a Boolean intersection or attachment.

**G3 — Mesh:** evaluate *final* modifier output. Test for loose/degenerate geometry and deliberate winding. Closed solids should usually have consistently outward-facing normals and positive signed volume; intentional internal cavities may use opposite shell orientation. Open cards/cloth may have boundaries by design. Treat watertightness as a target-dependent requirement, not a universal rule.

**G4 — Look:** neutral-lighting shape check before stylized lighting. Inspect at target distance and close enough for shading defects; verify textures/UVs when relevant. The agent must see actual images to claim a visual PASS.

**G5 — Destination:** re-evaluate triangles, materials, transforms, supported nodes and export scope. Export with a safe path only if requested and, where possible, re-import into a clean scene or target application. Saving a file alone does not verify its contents.

**G6 — Delivery:** report measured PASS/ISSUE/NOT VERIFIED/N/A for each relevant gate. Provide exact outputs, known defects, unresolved assumptions and evidence. A successful bpy command proves execution only, not art quality.

## 3. Technical standards by use

| Task | Topology decision | Additional checks |
|---|---|---|
| Static game prop | tris allowed; density where silhouette or shading requires | evaluated triangle budget, UV, texture packing, pivots, engine export |
| Hero render / subdivision | support loops/quads as needed, controlled creases | surface continuity, silhouette, clean highlights under neutral light |
| Character/creature animation | deformation-aware edge flow around joints; separate rigid parts as needed | bend and twist pose tests, weight interpolation, intersections |
| Stylized/low-poly | intentional faceting and readable planes, not an all-quad mandate | silhouette at final screen size, consistent facet scale/material language |
| Architecture | dimensioned modular units, axes and snapped pivots | walkable openings, alignment, repeated-piece consistency |
| Mechanical/CAD | dimension-driven surfaces, clearance and tolerance policy | named datums, fits, local thin-wall constraints; Blender is not a CAD fit certificate |
| 3D print | manifold closed solid where required | volume orientation, minimum wall thickness, no unplanned intersections, printer/material-specific checks |

No hard-coded polygon budget is universally professional. Set a task-specific budget and explain its tradeoff.

## 4. Geometry integrity and limits

- Inspect **evaluated** geometry after modifiers when practical; base mesh validation alone can miss broken booleans and extreme bevels.
- A negative signed volume for a single consistently oriented watertight shell signals likely inverted winding (also account for mirrored object transforms). Open meshes have no meaningful signed solid volume.
- Distinguish **boundary edges** from **non-manifold edges excluding boundary**; report both separately. A leaf card is not a broken solid.
- Reject genuinely degenerate faces, unintended zero-width slivers and loose vertices in deliverables. Preserve intentional empty construction helpers when out of export scope.
- Bevel width must fit **local features**, not just object overall dimensions; clamp_overlap is a safeguard, not proof. Inspect evaluated area and highlights.
- AABB proximity is only a **broad-phase test**. It can identify certain definite gaps; it does not prove connected surfaces or detect all penetrations.
- Negative scale, reversed normals in nested cavity shells, non-planar n-gons and triangulation can require manual context. Never use a center-to-normal heuristic as a universal winding test.

## 5. Professional judgment and iteration

Classify any defect by **severity** (critical/high/medium/low), **confidence** (measured/visually observed/inferred), **scope** (which components), and **cost of correction**. Fix silhouette, structure and proportions before topology, shading and polish. Choose the smallest change; preserve editability. Capture consistent before/after evidence and rerun the failed gate. If two attempts do not improve the relevant metric or view, change the technique or ask for a reference instead of adding arbitrary detail.

Record successful techniques only after **actual review**, with Blender/version/reference context. Unreviewed history is not a training signal. Avoid overclaiming quality by calling a piece 'professional' solely because tests pass.

## 6. Reviewer handoff template

```text
Asset / specification / target:
Blender + MCP tools actually available:
Working collection and object names:
G0 Preflight: PASS | ISSUE | NOT VERIFIED
G1 Silhouette and dimensions: PASS | ISSUE | NOT VERIFIED  [evidence]
G2 Assembly and pivots: PASS | ISSUE | NOT VERIFIED       [evidence]
G3 Evaluated topology: PASS | ISSUE | NOT VERIFIED       [counts]
G4 Visual/material/UV: PASS | ISSUE | N/A | NOT VERIFIED [views]
G5 Export and round-trip: PASS | ISSUE | N/A | NOT VERIFIED [artifact/path]
Remaining defects with severity:
Assumptions, limitations and next actions:
```

See `references/modeling-decision-framework.md`, `references/professional-agent-playbook.md`, `references/production-recipes.md`, `scripts/inspect_geometry.py` and `references/visual-inspection.md`.
