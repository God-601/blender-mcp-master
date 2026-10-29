# Game-Ready Assets and Export

Use this guide for assets headed to Roblox, Unity, Unreal, Godot, or another realtime engine. Verify the target-specific requirements instead of assuming one export preset is correct for every project.

## 1. Set the target before modeling

Choose the required format, units, forward/up axes, triangle budget, material count, texture dimensions, collision policy, LODs, pivot/origin, and allowed shader features. Read references/budgets.md for target-aware budgets and references/uv-baking.md for texture and bake preparation.

## 2. Pre-export checklist

1. Confirm scale, orientation, object origins, pivots, and ground placement.
2. Decide which modifiers must be applied or can be exported. Check version-dependent modifier behavior.
3. Inspect geometry for loose elements, degenerate faces, unwanted interior surfaces, normals, intersections, and non-manifold edges where relevant.
4. Decide when triangulation occurs. If normal maps are baked, keep triangulation and normal/tangent conventions consistent with the target pipeline.
5. Confirm UV layout, overlaps, padding, and the target's texture-coordinate expectations.
6. Confirm material count, naming, texture maps, color spaces, and supported shader features.
7. Exclude hidden cutters, helpers, lights, cameras, and unrelated user objects from the exported set unless explicitly needed.
8. Check collision, LOD, naming, and import conventions only where the destination uses them.
9. Run scripts/validate_asset.py and investigate warnings in context.
10. Export to a new path unless the user explicitly requested overwriting; verify the file exists and, where possible, reopen or import it.

## 3. LOD and scene performance

- Build LOD levels from the silhouette and screen-space role of the asset, not from a ratio alone.
- A decimated LOD can lose thin elements, UV quality, shading, and defining facets; inspect every level.
- Small or cheap objects may not need LODs. Repeated hero assets, vegetation, and large environment props may benefit substantially.
- Use instances for repeated objects and simple collision meshes where the engine needs them.
- Measure final triangles after modifiers and export conversion; do not report only the editable base-mesh count.

## 4. Destination considerations

- **Unity/Unreal/Godot/Roblox:** verify current import settings, scale conversion, axes, material support, texture compression, and any platform-specific limits in the actual destination.
- **glTF/GLB:** useful for realtime PBR assets, but not all Blender nodes or modifiers are represented. Confirm exported materials and textures.
- **FBX:** common for skeletal meshes and game assets; verify axes, scale, smoothing, armature, and animation data in the importer.
- **OBJ/STL:** mesh interchange formats with limited material/scene information; do not assume they preserve rigs, procedural shaders, or full scene organization.

Do not rely on a remembered numeric platform limit when the limit may change or depends on asset category. Verify against current official documentation for the intended engine and report the checked value/source when it affects acceptance.

## 5. Export script and safety

For scripts/export_asset.py, inspect its configuration and select only intended objects. The script has its own supported formats and limitations; read it before use. Rigged or shape-keyed meshes may require a dedicated, carefully checked export path.

- Preserve the working .blend and export a copy.
- Never delete user objects to make a clean export set; isolate the intended objects or use safe temporary copies.
- Record file path, format, file size, triangle count, material/texture dependencies, and validation status when those values were actually measured.
- If the destination application was not available, say that export settings and file presence were checked but in-engine behavior was not verified.
