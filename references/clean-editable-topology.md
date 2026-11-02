# Clean editable face topology vs intentional triangulation

**G3 / art-quality review.** A common agent-generated mesh problem is a flat
panel split into four triangular faces by a center vertex, creating an apparent
"X" across what should have been a simple editable quad. This can create
avoidable topology complexity, complicate modeling and alter normal/UV seams.

## What is and is not a defect

- A **native Blender quad** is ONE editable face with four vertices, even
  though rendering and glTF represent that surface using TWO triangles.
- A planar quad split on a **single diagonal** consists of TWO editable
  triangles but usually the SAME two render triangles. Removing the diagonal
  improves editability, not triangle count or guaranteed FPS.
- A planar quad with a **center vertex and four triangular faces** creates
  FOUR render triangles. When the center is not needed for shape, shading,
  UVs, deformation or detail, this is a candidate for simplification.
- Curved, creased, hard-surface bevel, triangle-tip, silhouette,
  subdivision, UV/seam and animation topology can require triangles.
- A **single ngon** is not automatically superior; a nonplanar/concave ngon
  may triangulate unpredictably. Use quads where appropriate and preserve
  silhouette and normals. Do not globally dissolve all edges.
- glTF/GLB commonly exports triangles and duplicates vertex records at UV,
  normal or material seams. That does NOT prove a visually broken mesh or
  a connectivity-preserving round trip. Separately test weldability/collision
  requirements and preserve normals/UV/material splits as required.

## Required workflow (before and after export)

1. Identify the intended surface: flat plate, curved panel, blade tip,
   bevel, movable joint or tessellated game mesh.
2. Inspect native **base editable faces** (triangles/quads/ngons), evaluated
   triangle count after modifiers, and exported triangle/vertex counts as
   DIFFERENT measurements.
3. Optionally run read-only `scripts/topology_face_diagnostics.py` on
   explicit named objects. It detects a narrow class of coplanar four-triangle
   vertex fans and reports REVIEW rather than changing the mesh. No finding
   only passes this **specific pattern**, not all possible excess diagonals.
4. Examine candidate faces in Edit Mode with edges visible; check front,
   back, side and grazing angles, normal shading, UV seams, materials and
   shape keys. A quad reduction should not be applied unless the patch is
   truly planar and the inner edges are unnecessary.
5. On an owned COPY, use deliberate limited dissolve / edge dissolve /
   merge of redundant center vertex as appropriate. Avoid a destructive
   whole-object triangulate-untriangulate cycle and preserve source mesh.
6. Verify face layout and render triangles before/after, detect degenerate
   faces and shading changes; inspect any UV seams/material/vertex normal
   differences and re-export/reimport a copy when relevant.
7. If the agent cannot visually confirm the changed face or cannot prove
   UV/normal preservation, report REVIEW/NOT VERIFIED and do not claim an
   unqualified topology-quality PASS.

## Controlled example

An otherwise flat square uses four corner vertices.
- Native quad: **1 editable quad / 2 render triangles**.
- Single diagonal: **2 editable triangles / 2 render triangles**.
- Center vertex with four diagonal spokes (X): **4 editable triangles /
  4 render triangles**.

A single-center fan can be artistically purposeful when the center controls
surface deformation, highlights or UV topology. Determine why it exists
rather than deleting it unconditionally.

**Related:** `references/topology-retopology.md`,
`references/component-fit-and-joints.md`,
`references/quality-checklist.md`,
`scripts/inspect_geometry.py`.

## v1.1 — Boundary-aware X-fan audit

`scripts/topology_face_diagnostics.py` now adds, **for each candidate**,
`material_boundary`, `uv_seam_candidate` and `shape_keys_present`.
If any flag is present it recommends `PRESERVE_UNTIL_REVIEW`; otherwise
`REVIEW_FOR_CLEAN_QUAD_ON_COPY`. Both are guidance only; the script
NEVER dissolves edges, changes materials or repairs UVs.

An observed four-triangle fan does not prove waste. Shared vertices in
editable meshes can have per-loop UV discontinuities, and shape keys can
make a seemingly flat edit destructive. Check normals, UV boundaries,
material IDs and deformation before considering a copy-first cleanup.
T10 remains an optional live-agent test rather than a certified automatic
retopology promise.
