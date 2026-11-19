# Manual acceptance prompts

Use a disposable scene or a saved copy. Connect a separate Blender-control MCP and record the revision under test. Run prompts in the user's language. [Português](manual-acceptance-prompts.pt-BR.md).

## Session preflight

> Activate Blender MCP Master. Inspect the current Blender version, available control tools and existing objects read-only. Resolve consequential design gaps before editing.

Record the observed session and tools. If a required connection or object is missing, mark the affected case NOT VERIFIED.

## T01 — Low-poly chair

> Make a medieval wooden game chair with four legs, a backrest, seat height 0.45 m, width 0.5 m and a 1,500-triangle budget. Deliver a .blend and preserve existing objects.

Check that the agent resolves open design decisions such as backrest shape and uses the answers. Repeat with those choices specified or delegated. Expect zero design questions on that variant.

## T02 — Castle and visual review

> Make a low-poly medieval castle with a gate, two towers and walls. Check blockout proportions and alignment before detailing. Inspect actual front, side and three-quarter views.

Check hierarchy, contact and visual evidence. Record unavailable views.

## T03 — Scene integrity

> Add a sci-fi panel in a new collection. Preserve USER_Keep_Mesh and USER_Keep_Light. On failure remove only your temporary copies and compare the scene before and after.

Confirm both sentinels exist in the same session before any mutation. Otherwise stop and mark NOT VERIFIED. Inspect named panel fasteners, plates and brackets using the component-fit guide and close-up views. Verify names and data after success and failure.

## T04 — Guided retopology

> Build a disposable mesh with two quad boundary loops. Inspect actual indices and bridge on a copy using scripts/retopology_advanced.py. Check quads, normals and the source. Repeat with invalid indices.

Expect the invalid operation to leave no failed output and the original to remain intact.

## T05 — UVs

> Compare separate UV islands with an overlapping variant using scripts/uv_diagnostics.py on explicit TARGETS. Inspect overlap and texel density read-only.

Distinguish edge contact from positive-area overlap. Report only measured properties.

## T06 — Optimization

> Compare a cube with a subdivision variant using scripts/asset_performance_audit.py on named objects. Record base and evaluated triangles, materials and textures. Optimize only on a copy.

Verify modifier effects and source preservation. FPS, draw calls and VRAM require separate measurements.

## T07 — Export

> Make a stylized sword with materials and UVs. Export GLB or FBX, reimport in a test scene and inspect scale, pivot, topology and materials.

Check the actual file and imported object. Mark target-engine compatibility NOT VERIFIED if the engine was unavailable.

## T08 — Token comparison

> Run T01 with and without the skill from identical scenes using the same client, model and MCP. Capture Bash/MCP calls and provider token counts when available. Use scripts/agent_efficiency_compare.py and the efficiency benchmark protocol.

Retain reproducible inputs, failures and quality measurements alongside costs.

## T09 — Structural joints

> Build a chair with a seat, four legs and two stretchers. Plan the leg-to-seat and stretcher-to-post contact planes. Document any intentional recess and depth. Inspect front, side, underside and three-quarter views before and after beveling. Use scripts/inspect_component_fit.py on separate named pairs. Inspect internal islands visually if parts were joined. Make corrections on owned copies.

Record close-ups, transforms and before/after evidence. A sacrificial beam passing through a wall should trigger REVIEW or ISSUE. AABB/BVH alone cannot approve a joint.

## T10 — Flat-panel triangulation

> Create three named planar fixtures covering the same quad-shaped patch. A uses one quad, B two triangles sharing a diagonal, and C four triangles meeting at a center vertex. Run scripts/topology_face_diagnostics.py with explicit TARGETS. Report editable faces and render triangles separately.

Expect 1/2, 2/2 and 4/4 faces/triangles respectively. Only C is an X-fan candidate. Inspect it in Edit Mode and remove the redundant center only on an owned copy if shape, normals and UVs are preserved. Verify shading and UVs before/after or record NOT VERIFIED.

## Evidence per run

Record scenario, client/model, Blender and MCP versions, prompt, initial scene, resulting .blend, front/side/three-quarter captures, error logs, owned changes, technical measurements, visual result and export status. Use PASS, ISSUE, N/A or NOT VERIFIED with evidence. Keep authentication tokens and private data out of reports.
