"""export_asset.py - export mesh objects as FBX / GLB / OBJ with engine-specific axis settings.
Paste into execute_blender_code.

Exports temporary evaluated copies (modifiers applied), so the scene's objects keep their data.
The scene state is always restored afterwards, even if the export fails: original object names,
selection, active object, Edit Mode, and the temporary copies/collection/meshes.

Not supported: rigged / animated characters (armatures, shape keys). Export those by hand.
Reports success only when the output file exists; otherwise it raises an error.
"""
import os
import tempfile
import bpy
import bmesh

# ---- CONFIG ----------------------------------------------------------------
OBJECTS = ["MyAsset"]                  # mesh objects to export (children are NOT auto-included)
PATH = "C:/Users/Public/Documents/MyAsset.fbx"   # output path; relative paths resolve against the .blend folder / cwd
FORMAT = "FBX"                         # "FBX", "GLB", "OBJ"
ENGINE = "GENERIC"                     # "UNITY", "UNREAL", "ROBLOX", "GODOT", "GENERIC"
TRIANGULATE = True                     # triangulate export copies
APPLY_MODIFIERS = True                 # bake modifier stack into the exported copy
OVERWRITE = False                      # refuse to replace an existing file unless explicitly enabled
# ----------------------------------------------------------------------------

if FORMAT not in ("FBX", "GLB", "OBJ"):
    raise ValueError(f"Unknown FORMAT {FORMAT!r}; use FBX, GLB or OBJ")

out_path = os.path.abspath(bpy.path.abspath(PATH))
os.makedirs(os.path.dirname(out_path), exist_ok=True)
if os.path.exists(out_path) and not OVERWRITE:
    raise FileExistsError(f"Refusing to overwrite existing export: {out_path}. Set OVERWRITE=True to replace it.")
extension = os.path.splitext(out_path)[1] or (".glb" if FORMAT == "GLB" else "." + FORMAT.lower())
fd, temp_path = tempfile.mkstemp(prefix="._blender_mcp_export_", suffix=extension, dir=os.path.dirname(out_path))
os.close(fd)
os.remove(temp_path)

view_layer = bpy.context.view_layer
saved_selection = [o.name for o in bpy.context.selected_objects]
saved_active = view_layer.objects.active.name if view_layer.objects.active else None
saved_mode = view_layer.objects.active.mode if view_layer.objects.active else 'OBJECT'

renamed = []          # (object, original name)
temps = []            # temporary export copies
temp_meshes = []      # meshes created for the copies
tmp_col = None
total_tris = 0

try:
    if saved_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    tmp_col = bpy.data.collections.new("_EXPORT_TMP")
    bpy.context.scene.collection.children.link(tmp_col)
    depsgraph = bpy.context.evaluated_depsgraph_get()

    for name in OBJECTS:
        ob = bpy.data.objects.get(name)
        if ob is None:
            print("missing:", name)
            continue
        if ob.type != 'MESH':
            print("skip non-mesh:", name)
            continue
        if any(m.type == 'ARMATURE' for m in ob.modifiers) or (ob.data.shape_keys and ob.data.shape_keys.key_blocks):
            print(f"WARNING: {name} has an armature modifier or shape keys; they are not exported by this script.")
        if APPLY_MODIFIERS:
            me = bpy.data.meshes.new_from_object(
                ob.evaluated_get(depsgraph), preserve_all_data_layers=True, depsgraph=depsgraph
            )
        else:
            me = ob.data.copy()
        temp_meshes.append(me)
        if TRIANGULATE:
            bm = bmesh.new()
            try:
                bm.from_mesh(me)
                bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
                bm.to_mesh(me)
            finally:
                bm.free()
        me.calc_loop_triangles()
        total_tris += len(me.loop_triangles)

        # Free the clean name for the copy, then restore it in `finally`.
        renamed.append((ob, ob.name))
        ob.name = ob.name + "__orig"
        dup = bpy.data.objects.new(name, me)
        dup.matrix_world = ob.matrix_world
        tmp_col.objects.link(dup)
        temps.append(dup)

    if not temps:
        raise RuntimeError("Nothing to export: no valid mesh objects found in OBJECTS.")

    bpy.ops.object.select_all(action='DESELECT')
    for t in temps:
        t.select_set(True)
    view_layer.objects.active = temps[0]

    if FORMAT == "FBX":
        kw = dict(filepath=temp_path, use_selection=True, object_types={'MESH'},
                  use_mesh_modifiers=False, mesh_smooth_type='FACE', add_leaf_bones=False,
                  bake_anim=False, path_mode='COPY', embed_textures=False)
        if ENGINE == "UNITY":
            kw.update(apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y', apply_unit_scale=True)
        elif ENGINE == "UNREAL":
            kw.update(apply_scale_options='FBX_SCALE_NONE', axis_forward='-Y', axis_up='Z', global_scale=1.0)
        elif ENGINE == "ROBLOX":
            kw.update(apply_scale_options='FBX_SCALE_NONE', axis_forward='-Z', axis_up='Y')
        export_result = bpy.ops.export_scene.fbx(**kw)
    elif FORMAT == "GLB":
        bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB', use_selection=True,
                                  export_apply=False, export_yup=True, export_materials='EXPORT')
    else:  # OBJ
        if hasattr(bpy.ops.wm, "obj_export"):                       # Blender 3.2+
            bpy.ops.wm.obj_export(filepath=out_path, export_selected_objects=True, export_materials=True,
                                  apply_modifiers=False, export_triangulated_mesh=False)
        else:                                                       # Blender 3.1 and older
            bpy.ops.export_scene.obj(filepath=out_path, use_selection=True, use_materials=True)

    if 'FINISHED' not in locals().get("export_result", set()):
        raise RuntimeError(f"Export operator did not finish successfully for {out_path}.")
    if not os.path.isfile(temp_path) or os.path.getsize(temp_path) == 0:
        raise RuntimeError(f"Export failed: no non-empty output was written for {out_path}.")
    os.replace(temp_path, out_path)
    print(f"Exported {len(temps)} object(s), {total_tris} tris -> {out_path} "
          f"({os.path.getsize(out_path) / 1024:.1f} KB), engine={ENGINE}")
finally:
    if os.path.exists(temp_path):
        try:
            os.remove(temp_path)
        except OSError:
            print(f"note: temporary export file could not be removed: {temp_path}")
    for t in temps:
        bpy.data.objects.remove(t, do_unlink=True)
    for me in temp_meshes:
        if me.users == 0:
            bpy.data.meshes.remove(me)
    if tmp_col is not None:
        bpy.data.collections.remove(tmp_col)
    for orig, orig_name in renamed:
        orig.name = orig_name
    # restore selection, active object and mode
    for o in bpy.context.selected_objects:
        o.select_set(False)
    for name in saved_selection:
        o = bpy.data.objects.get(name)
        if o is not None and o.name in view_layer.objects:
            o.select_set(True)
    active = bpy.data.objects.get(saved_active) if saved_active else None
    if active is not None and active.name in view_layer.objects:
        view_layer.objects.active = active
        if saved_mode != 'OBJECT':
            try:
                bpy.ops.object.mode_set(mode=saved_mode)
            except RuntimeError:
                print(f"note: could not return to {saved_mode} mode")
