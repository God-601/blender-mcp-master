# Component fit, surface joints and unwanted mesh penetration

**Quality gate G2.** A common automated-modeling failure is letting a leg,
beam, roof, rail, wall or ornament pass *through* another part instead of
constructing a deliberate joint. This may look fine from one camera but creates
bad silhouettes, internal surfaces, clipping, shadow artifacts and poor game
collision. Treat joint design as a modeling operation, not decoration.

## Required workflow

1. **Before building parts:** name adjoining components and specify their
   intended relationship: **flush surface joint**, **intentional embed/tenon**,
   **clearance/no contact**, or **one continuous mesh**. For significant joints
   define a shared datum, mating plane, insertion depth and tolerance using
   actual Blender scene units. If unspecified, preserve editable source
   geometry and select a conservative, visible surface-to-surface joint.
2. **Build to a common reference:** e.g. chair seat bottom =
   seat-center-height minus half thickness; leg top meets that surface.
   For a timber tenon, document the *purposeful insertion depth* and the
   necessary receiving geometry, rather than extending arbitrary blocks
   inside the seat. Door openings should be physically open, not merely
   covered by overlapping dark cubes.
3. **At blockout (G2):** inspect joints at front, side, top/bottom (where
   relevant), and three-quarter views, with neutral lighting and without
   materials concealing the seam. Look for hidden protrusions, sinking
   supports, mismatched pivots, floating parts, z-fighting, coplanar internal
   surfaces and unintended negative spaces.
4. **Use measured assistance:** optional
   `scripts/inspect_component_fit.py` on **explicit pairs of different
   mesh objects**. Configure `CHECKS` entries like:
   
   ```python
   CHECKS = [
       {"a": "ChairLeg_FL", "b": "Seat", "expectation": "surface_joint", "max_gap": 0.002},
       {"a": "Roof", "b": "Wall", "expectation": "no_penetration"},
       {"a": "Tenon", "b": "Beam", "expectation": "intentional_embed", "reason": "wood joinery"},
   ]
   ```

   `surface_joint`: a definite world-space AABB gap beyond `max_gap`
   is ISSUE; overlapping/nearby boxes are only REVIEW, not a verified seam.

   `no_penetration`: no positive AABB volume overlap is PASS for *that
   limited check*. An overlapping AABB gives REVIEW and optional BVH
   triangle-contact candidates—not proof of a genuine surface crossing.

   `intentional_embed`: always REVIEW with a required documented reason;
   never excuse an unexamined intersection automatically.

   The script is read-only; it checks evaluated object meshes and always
   leaves visual quality and collision-engine verification NOT VERIFIED.
   It cannot detect all penetration of fully contained objects, can
   flag correct face contacts for review, and **does not** analyze separate
   face islands inside one mesh object. For combined meshes, use face-island
   inspection, visualization, and further targeted analysis.
5. **Correct the actual cause:** adjust component dimensions/position to
   the mating surface, rebuild the receiving cavity, or use an explicit
   targeted Boolean/retopology operation on a safe copy when justified.
   Do not blindly merge meshes, disable collision warnings, hide defects
   behind materials, or delete internal geometry without confirming ownership.
6. **Retest after bevel/subdivision and export:** modifiers can change
   surface fit. Reinspect the final evaluated mesh and document
   intentional overlap; assess UVs/material seams, shading and intended
   engine collision separately.

## Acceptance and evidence

A joint passes artistic/structural review only when relevant real
images and measurable geometry establish that the pieces connect as
intended. Use a close-up and a wider scene view. For game-ready/rigged
assets, also validate pivots, movement clearances and collider behavior
in the destination where possible. If only AABB/BVH was run, status
is **REVIEW** or **NOT VERIFIED** for real joint quality, never an
unqualified PASS.

**Examples:**
- A chair leg that penetrates half the seat thickness without a designed
  socket is ISSUE; a correctly measured surface joint is acceptable.
- A wooden mortise-and-tenon with deliberate geometry is intentional
  embedding; document and inspect the depth.
- A narrow roof overhang over a wall can have overlapping bounding
  boxes without any actual penetration—do not auto-reject it.
- A wall-to-wall junction can use clean butt contact or an engineered
  overlap; what matters is actual visible/physical quality, not a universal
  ban on intersections.

**This is an agent-side QA aid, not a certified mesh Boolean intersection
solver.** Version-specific geometry behavior must be validated against
the actual Blender version and real viewport images.
