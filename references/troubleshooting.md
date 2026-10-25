# Troubleshooting (symptom -> cause -> fix)

| Symptom | Likely cause | Fix |
|---|---|---|
| `RuntimeError: Operator bpy.ops.X.poll() failed, context is incorrect` | Wrong mode/active object/area | Switch to Object Mode, set `view_layer.objects.active`, select the object, or use `bpy.context.temp_override(...)`; prefer bmesh/data API |
| `AttributeError: 'Mesh' object has no attribute 'use_auto_smooth'` | Blender 4.1+ removed auto smooth | Use `shade_auto_smooth` operator / "Smooth by Angle" modifier, or sharp edges by angle in bmesh |
| `KeyError: 'Specular'` / `'Emission'` on Principled | Renamed in 4.0 | Use `Specular IOR Level`, `Emission Color`; set via try/fallback helper |
| Object appears dark / black faces | Flipped normals | `bpy.ops.mesh.normals_make_consistent(inside=False)` in Edit Mode, or bmesh `recalc_face_normals` |
| Strange shading streaks on flat surfaces | Smooth shading on ngons/tris with uneven topology | Smooth by angle (30 deg), add edge loops or Weighted Normal; mark sharps |
| Z-fighting flicker | Coplanar faces | Offset or delete duplicate faces; decals 1 to 2 mm above |
| Model looks tiny or huge | Wrong scale/unit | Check `scene.unit_settings`, apply scale, rescale to real size (`target_size` on import) |
| Pieces are floating | Origin/ground mismatch | `get_scene_info(fields=["ground"])`; move to Z so bbox min Z = 0 |
| Mirror leaves a seam | Merge/clip off, verts not on axis | Enable `use_clip`, `use_mirror_merge`, snap center verts to X=0 |
| Boolean produces holes/garbage | Non-manifold or overlapping geometry | Use `solver='EXACT'`, clean both meshes first, make cutter a closed manifold |
| Bevel looks uneven | Non-uniform scale | Apply scale; use `limit_method='ANGLE'`, adjust width |
| Textures stretched | UV not scaled to world size / scale not applied | Apply scale, re-unwrap, check checker texture |
| Export in engine is rotated or scaled wrong | Axis/unit settings | See game-ready-export.md axis table; apply transforms |
| Armature deforms badly | Bad weights / bone roll / overlapping parts | Check weights report, redo automatic weights after fixing mesh, limit influences to 4 |
| Viewport lags | Heavy modifiers, high-res textures, many unique objects | See performance.md |
| Script timed out | Single huge call | Split in steps, use bmesh bulk ops |
| Objects duplicated after re-running | Non-idempotent script | Clear own collection first, or `.get(name)` before creating |
| `look` shows nothing / wrong object | Target typo, object hidden, camera missing | List names via `get_scene_info(query=...)`, unhide, try `mode="angles"` |
| Imported asset huge/odd | Library scale arbitrary | Use `target_size`, ground it, apply scale |
| Material missing after save | Material has 0 users | Use fake user or assign it; never leave created-but-unused materials |
| generate_3d result messy | AI meshes are dense/uneven | Decimate, remesh, cleanup, rebuild UVs, fix scale; warn user it's a base |

## Debug routine
1. Print the exact exception (`traceback.print_exc()` inside try/except).
2. Print object state (`mode`, `active`, `selected`, type, mesh stats).
3. Reduce to the smallest failing statement; test it alone.
4. Check version-specific API (`bpy.app.version`).
5. If still failing after two different approaches, tell the user what failed and propose an alternative instead of retrying blindly.
