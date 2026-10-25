# Characters and rigging

## Model requirements for a rig-ready character
- Neutral pose: **T-pose or A-pose**, facing -Y (Blender front), feet on Z=0, centered on X.
- Symmetric base (Mirror), applied before skinning.
- Quads with edge loops around joints (shoulder, elbow, wrist, hip, knee, ankle, fingers, neck, jaw). 2 to 3 loops at bending joints.
- Apply scale and rotation (`apply_and_origin.py`). Origin at the feet center.
- Separate eyes, teeth, hair, clothes as their own objects (named), but one skeleton.
- Height in meters (about 1.7 to 1.8 for adult humans, stylized allowed, state it).

## Armature basics
- One armature, root bone at origin (ground), hips above it, spine chain, neck, head; arms (shoulder/clavicle, upper arm, forearm, hand, fingers); legs (thigh, shin, foot, toe).
- Bone naming: `Hips`, `Spine`, `Chest`, `Neck`, `Head`, `UpperArm.L`, `LowerArm.L`, `Hand.L`, `UpperLeg.L`, `LowerLeg.L`, `Foot.L`, `Toe.L` (mirror `.R`). Use `.L/.R` suffixes so Blender symmetrize works.
- Build bones in Edit Mode through the `armature.edit_bones` API (set head, tail, roll, parent, `use_connect`).
- Deform bones only for export: IK/control bones should have `use_deform=False`.

## Skinning
- Automatic weights: `bpy.ops.object.parent_set(type='ARMATURE_AUTO')` (needs selection: meshes then armature active, Object Mode). Then verify.
- Verify: `get_scene_info(fields=["weights"])` reports vertices with no deform bone and bones with no vertex group. Fix every orphan. Then pose test: rotate key bones in Pose Mode via script and `look(mode="angles")`; check for candy-wrapper twisting, collapsing elbows/knees, intersections.
- Limit to **4 bone influences per vertex** for game engines (`bpy.ops.object.vertex_group_limit_total(limit=4)`), normalize weights.

## Game engine targets
- Unity / Unreal: export FBX with armature, `Apply Scalings = FBX Units Scale`, forward `-Z`, up `Y` (Unity) or defaults for Unreal (see game-ready-export.md); only deform bones.
- Roblox: R15 / custom rigs need specific naming and attachments; tell the user the exact requirement is engine-side (Avatar Importer), export FBX with armature and meshes, one material per mesh where possible, keep under the triangle caps.

## Animation (if asked)
- Use keyframes via `obj.keyframe_insert` / `pose_bone.keyframe_insert`. Set fps (24/30/60) and frame range first. Verify with `look(mode="frames", frame_count=8)`.
- Loops (walk/idle): first and last pose identical; use linear or cyclic F-curve modifiers where useful.

## Do not
- Do not rig a mesh with non-manifold or overlapping shells without telling the user.
- Do not apply modifiers that change vertex order after skinning.
