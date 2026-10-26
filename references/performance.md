# Performance (Blender, scripts and model)

## Make scripts fast
- **Bulk geometry via bmesh / from_pydata**, never create thousands of objects with `bpy.ops.mesh.primitive_*`. One mesh built by `bmesh` with thousands of faces takes milliseconds; thousands of objects take seconds to minutes.
- Large arrays: `mesh.vertices.foreach_set("co", flat_list)` / `foreach_get` + numpy when available.
- Avoid `bpy.ops` inside loops. Avoid `bpy.context.view_layer.update()` per iteration (call once after the loop).
- Disable undo / redraw side effects by not switching modes repeatedly; do edits in Object Mode with bmesh (`bmesh.new()`, `bm.from_mesh`, `bm.to_mesh`, `bm.free()`).
- Always `bm.free()`. Do not run a global `bpy.data.orphans_purge(do_recursive=True)` as routine cleanup: it can remove unrelated orphan datablocks from the user's file. Only purge after inspecting the affected datablocks and getting explicit approval.
- Time heavy steps (`time.perf_counter()`) and print the result; split anything longer than about 10 seconds into several calls so the MCP request doesn't time out.

### Pattern: voxel surface extraction (visible-face culling)
```python
import bmesh, bpy
def voxels_to_mesh(cells, size=0.1, name="Voxels"):
    S = set(cells)                       # {(x,y,z), ...} integer coords
    bm = bmesh.new()
    dirs = [((1,0,0),[(1,0,0),(1,1,0),(1,1,1),(1,0,1)]),
            ((-1,0,0),[(0,0,0),(0,0,1),(0,1,1),(0,1,0)]),
            ((0,1,0),[(0,1,0),(0,1,1),(1,1,1),(1,1,0)]),
            ((0,-1,0),[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]),
            ((0,0,1),[(0,0,1),(1,0,1),(1,1,1),(0,1,1)]),
            ((0,0,-1),[(0,0,0),(0,1,0),(1,1,0),(1,0,0)])]
    cache = {}
    def v(p):
        if p not in cache: cache[p] = bm.verts.new((p[0]*size, p[1]*size, p[2]*size))
        return cache[p]
    for (x,y,z) in S:
        for (dx,dy,dz), quad in dirs:
            if (x+dx,y+dy,z+dz) in S: continue
            bm.faces.new([v((x+a,y+b,z+c)) for a,b,c in quad])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    return ob
```
This only creates visible faces and shares vertices (no interior faces, no doubles).

## Make the viewport fast
- Set heavy modifiers `show_viewport=False` during iteration; keep `show_render=True`.
- Use `display_type='BOUNDS'` or `'WIRE'` for far or heavy objects while working.
- Instances (`ob.copy()` with the same `ob.data`) cost memory once.
- Reduce Subdivision viewport levels (1) and keep render at 2 to 3.
- Hide collections not being edited (`layer_collection.hide_viewport = True`).
- EEVEE: lower shadow cube size, disable SSR/bloom while modeling; Workbench for checks.
- Avoid very high-res image textures in the viewport (use 1k previews).

## Make the model fast (runtime in a game)
- Triangle budget per `budgets.md`. Remove invisible faces (bottom, inside, behind walls).
- Fewer materials / draw calls: atlas, shared materials, merged static meshes.
- Texture sizes to budget, power of two, compressed in the engine.
- Use instancing for repeated parts; LODs for large repeats.
- Avoid transparency where possible (alpha clip over alpha blend), avoid overdraw (stacked leaf cards).
- Avoid thin, long triangles; avoid very small details that alias.
- Prefer one skin/skeleton per character; <= 4 bone influences per vertex; reasonable bone count (mobile under about 60).

## Make the agent fast (tokens and round trips)
- First call: `get_addon_status`; then scene info only for the fields needed.
- Combine related edits (create + name + material) into one script; verify with one print.
- Use `look` with `max_size=384 to 512` for iteration, a larger size only to read fine detail.
- Don't print mesh data dumps; print counts, bounding boxes, and warnings.
- Reuse earlier results; don't re-inspect unchanged objects.
- If a call fails, read the exception, fix the specific line, retry once; if it fails twice, change the approach (simpler API or smaller step) instead of looping.
