# Organic Modeling

Use this guide for plants, creatures, rocks, terrain, food, skin, soft props, and organic forms. Add the sculpting guide when form development or high-poly detail is central, and the topology guide when the mesh must deform or become game-ready.

## 1. Plan the form

- Identify the silhouette, main masses, asymmetry, style, and target viewing distance.
- For anatomy or recognizable creatures, use reference images and separate structural features from surface detail.
- Decide whether the result is a procedural base, a sculpt source, a static render mesh, or a low-poly deformable asset.
- Set scale and a useful camera before detailing. Do not use noise to hide weak proportions.

## 2. Workflow

1. Build primary volumes from primitives, curves, metaballs, or a deliberately simple base mesh.
2. Inspect front, side, top, and three-quarter views and correct the silhouette.
3. Establish secondary forms such as limbs, branches, folds, muscle masses, petals, rocks planes, or food forms.
4. Add fine detail only after the larger forms read clearly.
5. Use sculpting, displacement, procedural texture, or manual geometry according to the target and available tools.
6. For realtime delivery, create or validate a low-poly target, UVs, maps, materials, and export dependencies.

## 3. Subject-specific guidance

### Rocks and terrain
- Start from a low-resolution ico-sphere, grid, or terrain base; use broad displacement or carefully controlled noise to establish large planes.
- Flatten contact areas where the object must sit on the ground.
- Use a few distinct mesh variants and seeded randomization for repeated rocks.
- Avoid uniform noise amplitude; erosion and fracture need a hierarchy of large and small forms.

### Plants and trees
- Use tapered curves/cylinders for trunks and branches; leaves may be cards, clusters, or actual meshes depending on camera distance.
- For game foliage, use an atlas and alpha clipping where supported. Test transparency sorting and overdraw in the target engine.
- Preserve a few recognizable leaf/branch masses instead of scattering tiny geometry uniformly.
- Keep randomization reproducible when the scene must be regenerated.

### Soft props and food
- Favor broad volume changes, small asymmetry, and material-specific roughness.
- Use displacement only at a scale that suits the mesh density and final output.
- Subsurface effects are renderer-dependent; verify them instead of assuming all target engines support them.

### Humans and faces
- Anatomical accuracy requires reference, iterative visual review, and expert judgment. A procedural script can create a base form but should not be labeled production-quality anatomy without inspection.
- If the requested realism exceeds the available modeling workflow, report what is a blockout and what needs manual sculpting or specialist tools.

## 4. Topology and baking

- Static background meshes may tolerate decimation when silhouette and shading remain acceptable.
- Hero or deforming assets need intentional edge flow and a suitable low-poly cage rather than relying on decimation alone.
- See references/topology-retopology.md for topology selection and references/uv-baking.md for high-to-low projection.
- Keep an untouched source or clearly named working copy before remeshing, decimation, or applying topology-changing modifiers.

## 5. Validation

- Inspect the silhouette and surface shading under neutral lighting.
- Investigate loose geometry, degenerates, unexpected intersections, flipped normals, and non-manifold edges where closed solids are expected.
- Check ground contact, scale, materials, texture dependencies, triangle count, and visible artifacts.
- Treat open surfaces, foliage cards, cloth shells, and intentional thin surfaces according to their actual purpose rather than a universal closed-mesh rule.
