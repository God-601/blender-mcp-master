"""make_lods.py - create LOD copies of an object using Decimate (collapse) and report tri counts.
Original is untouched. Paste into execute_blender_code.
"""
import bpy

# ---- CONFIG ----------------------------------------------------------------
SOURCE = "MyAsset"                      # name of the LOD0 object
RATIOS = {"LOD1": 0.5, "LOD2": 0.25, "LOD3": 0.10}   # name suffix -> triangle ratio
PRESERVE_UV_BORDERS = True              # keep UV seams (use_collapse_triangulate off, symmetry off)
TRIANGULATE_FIRST = True                # decimate works best on triangulated meshes
# ----------------------------------------------------------------------------

src = bpy.data.objects.get(SOURCE)
if src is None or src.type != 'MESH':
    raise SystemExit(f"Source mesh '{SOURCE}' not found")

dg = bpy.context.evaluated_depsgraph_get()


def tris_of(ob):
    e = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = e.to_mesh()
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    e.to_mesh_clear()
    return n


base = tris_of(src)
print(f"{SOURCE}: {base} tris (LOD0)")
col = src.users_collection[0] if src.users_collection else bpy.context.scene.collection

for suffix, ratio in RATIOS.items():
    name = f"{SOURCE}_{suffix}"
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    lod = src.copy()
    lod.data = src.data.copy()
    lod.name = name
    lod.data.name = name
    col.objects.link(lod)

    if TRIANGULATE_FIRST:
        t = lod.modifiers.new("Tri", 'TRIANGULATE')
        t.quad_method = 'BEAUTY'
    d = lod.modifiers.new("Decimate", 'DECIMATE')
    d.decimate_type = 'COLLAPSE'
    d.ratio = ratio
    d.use_collapse_triangulate = True
    if PRESERVE_UV_BORDERS:
        d.use_symmetry = False   # symmetry collapse can disturb UV borders; keeps behavior predictable

    # apply modifiers through evaluated mesh (no operators needed)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = lod.evaluated_get(dg)
    new_me = bpy.data.meshes.new_from_object(ev)
    old_me = lod.data
    lod.modifiers.clear()
    lod.data = new_me
    new_me.name = name
    bpy.data.meshes.remove(old_me)

    # offset sideways so LODs are visible side by side
    lod.location.x = src.location.x + (list(RATIOS).index(suffix) + 1) * (src.dimensions.x * 1.3 + 0.1)
    n = tris_of(lod)
    print(f"{name}: {n} tris ({n / max(base, 1):.0%} of LOD0)")

print("Done. Compare with look(mode='angles', shading='wireframe'). Move LODs into engine-specific layout when exporting.")
