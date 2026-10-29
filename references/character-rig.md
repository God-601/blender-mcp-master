# Characters, Deformation, Rigging, and Animation

Use this guide for characters that will pose, deform, or animate. Character quality depends on form, topology, weights, pivots, and motion working together; a skeleton alone does not make a character production-ready.

## 1. Model and scale

- Define style, anatomy target, neutral pose, height/scale, orientation, and destination before modeling.
- Use a T-pose or A-pose when suitable for the target rig. Keep feet and root placement consistent with the chosen coordinate convention.
- Separate parts only when the material, pivot, deformation, or destination benefits from it.
- Use references/topology-retopology.md for deformation-aware edge flow and references/sculpting-highpoly.md if a high-poly source will be baked onto a low-poly character.

## 2. Rig structure

- Plan a hierarchy for root/hips, spine, chest, neck, head, arms, hands/fingers, legs, feet, and toes as required by the target.
- Name bones consistently and use .L/.R suffixes when Blender's symmetry tools are part of the workflow.
- Distinguish deform bones from control/IK bones; control bones usually should not deform the mesh.
- Build/edit bones in Edit Mode and verify parent relationships, connectivity, roll, and orientation before skinning.
- Do not assume a generic rig matches Roblox R15 or a specific game engine's retargeting conventions. Check the actual target specification.

## 3. Skinning and deformation checks

- Automatic weights are only a starting point. Inspect influences and weight distribution at shoulders, elbows, wrists, hips, knees, ankles, jaw, and other bending regions.
- Limit influences only when required by the target. Four influences per vertex is common in some realtime pipelines, but is not a universal rule for every renderer or deform system.
- Pose-test key joints through their expected range. Inspect candy-wrapper twisting, collapsed volume, pinching, sliding, self-intersections, and silhouette damage.
- Re-test after topology changes. Modifiers that change vertex order/count can invalidate weights and shape keys.

## 4. Animation checks

- Set frame rate, frame range, and intended motion before creating keys.
- Check timing, foot contact, interpolation, root motion, and looping where relevant.
- Inspect several frames rather than only the first and last pose.
- Do not claim an animation loops or deforms correctly unless the relevant frames and poses were inspected.

## 5. Delivery

- Check scale, orientation, root/pivot, armature hierarchy, mesh-to-bone relationships, weights, material compatibility, and export settings for the target.
- Preserve source meshes and rig data before destructive changes.
- State which poses, export formats, and destination-engine behavior were actually tested.
