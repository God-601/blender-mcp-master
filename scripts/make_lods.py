"""make_lods.py - create LOD copies of an object using Decimate (collapse) and report tri counts.
Paste into execute_blender_code.

Safety: the source is never modified. If any LOD output name already exists the script stops
before creating anything, and existing scene objects are never deleted automatically. If a
LOD fails midway, the LOD objects created by this run are removed again.

Notes: modifiers on the source are baked into the LODs. Rigged or shape-keyed meshes are
not supported (a warning is printed). Decimate may distort UVs on heavy reductions: inspect
the result before using it.
"""
import bpy

# ---- CONFIG ----------------------------------------------------------------
SOURCE = "MyAsset"                      # name of the LOD0 object
RATIOS = {"LOD1": 0.5, "LOD2": 0.25, "LOD3": 0.10}   # name suffix -> triangle ratio (0 to 1)
TRIANGULATE_FIRST = True                # decimate works best on triangulated meshes
DISABLE_SYMMETRY = True                 # keep Decimate symmetry off so results are predictable
# ----------------------------------------------------------------------------


def tris_of(ob):
    e = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    me = e.to_mesh()
    try:
        me.calc_loop_triangles()
        return len(me.loop_triangles)
    finally:
        e.to_mesh_clear()


src = bpy.data.objects.get(SOURCE)
if src is None or src.type != 'MESH':
    raise RuntimeError(f"Source mesh '{SOURCE}' not found")

for suffix, ratio in RATIOS.items():
    if not 0.0 < ratio <= 1.0:
        raise ValueError(f"Ratio for {suffix} must be in (0, 1], got {ratio}")
existing = [f"{SOURCE}_{s}" for s in RATIOS if f"{SOURCE}_{s}" in bpy.data.objects]
if existing:
    raise RuntimeError(
        f"LOD output(s) already exist: {existing}. Rename or remove them manually, "
        "then rerun; existing scene objects are never deleted automatically."
    )
if any(m.type == 'ARMATURE' for m in src.modifiers) or (src.data.shape_keys and src.data.shape_keys.key_blocks):
    print("WARNING: source has an Armature modifier or shape keys; LODs will not keep them.")

base = tris_of(src)
print(f"{SOURCE}: {base} tris (LOD0)")
col = src.users_collection[0] if src.users_collection else bpy.context.scene.collection
created = []

try:
    for index, (suffix, ratio) in enumerate(RATIOS.items(), start=1):
        name = f"{SOURCE}_{suffix}"
        lod = src.copy()
        lod.data = src.data.copy()
        lod.name = name
        lod.data.name = name
        col.objects.link(lod)
        created.append(lod)

        if TRIANGULATE_FIRST:
            t = lod.modifiers.new("Tri", 'TRIANGULATE')
            t.quad_method = 'BEAUTY'
        d = lod.modifiers.new("Decimate", 'DECIMATE')
        d.decimate_type = 'COLLAPSE'
        d.ratio = ratio
        d.use_collapse_triangulate = True
        if DISABLE_SYMMETRY:
            d.use_symmetry = False

        # apply modifiers through the evaluated mesh (no operators needed)
        ev = lod.evaluated_get(bpy.context.evaluated_depsgraph_get())
        new_me = bpy.data.meshes.new_from_object(
            ev, preserve_all_data_layers=True,
            depsgraph=bpy.context.evaluated_depsgraph_get()
        )
        old_me = lod.data
        # Remove modifiers one by one: older Blender versions have no modifiers.clear().
        for modifier in list(lod.modifiers):
            lod.modifiers.remove(modifier)
        lod.data = new_me
        new_me.name = name
        if old_me.users == 0:
            bpy.data.meshes.remove(old_me)

        # offset sideways so LODs are visible side by side
        lod.location.x = src.location.x + index * (src.dimensions.x * 1.3 + 0.1)
        n = tris_of(lod)
        print(f"{name}: {n} tris ({n / max(base, 1):.0%} of LOD0)")
except Exception:
    for lod in created:               # only objects created by this run
        mesh = lod.data
        bpy.data.objects.remove(lod, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    print("LOD generation failed; LOD objects created by this run were removed.")
    raise

print("Done. Compare with look(mode='angles', shading='wireframe'). Move LODs into engine-specific layout when exporting.")
