"""export_asset.py - export objects as FBX / GLB / OBJ with safe engine-specific settings.
Exports temporary evaluated duplicates (modifiers applied), so the user's scene is not modified.
Paste into execute_blender_code.
"""
import bpy
import os

# ---- CONFIG ----------------------------------------------------------------
OBJECTS = ["MyAsset"]                  # objects to export (children are NOT auto-included)
PATH = "C:/Users/Public/Documents/MyAsset.fbx"   # full output path (extension decides default format)
FORMAT = "FBX"                         # "FBX", "GLB", "OBJ"
ENGINE = "GENERIC"                     # "UNITY", "UNREAL", "ROBLOX", "GODOT", "GENERIC"
TRIANGULATE = True                     # triangulate export copies
APPLY_MODIFIERS = True                 # bake modifier stack into the exported copy
INCLUDE_ARMATURE = False               # also export the armature found on the objects (skinned characters)
# ----------------------------------------------------------------------------

os.makedirs(os.path.dirname(PATH), exist_ok=True)

if bpy.context.object and bpy.context.object.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

dg = bpy.context.evaluated_depsgraph_get()
temps = []
tmp_col = bpy.data.collections.new("_EXPORT_TMP")
bpy.context.scene.collection.children.link(tmp_col)

total_tris = 0
renamed = []
for name in OBJECTS:
    ob = bpy.data.objects.get(name)
    if ob is None:
        print("missing:", name)
        continue
    if ob.type != 'MESH':
        print("skip non-mesh:", name)
        continue
    if APPLY_MODIFIERS:
        ev = ob.evaluated_get(dg)
        me = bpy.data.meshes.new_from_object(ev)
    else:
        me = ob.data.copy()
    renamed.append((ob, ob.name))
    ob.name = ob.name + "__orig"              # free the clean name so the exported copy keeps it
    dup = bpy.data.objects.new(renamed[-1][1], me)
    dup.matrix_world = ob.matrix_world
    tmp_col.objects.link(dup)
    if INCLUDE_ARMATURE:
        for m in ob.modifiers:
            if m.type == 'ARMATURE' and m.object:
                am = dup.modifiers.new("Armature", 'ARMATURE')
                am.object = m.object
                for vg in ob.vertex_groups:
                    dup.vertex_groups.new(name=vg.name)
        dup.parent = ob.parent
    if TRIANGULATE:
        import bmesh
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        bm.to_mesh(me)
        bm.free()
    me.calc_loop_triangles()
    total_tris += len(me.loop_triangles)
    temps.append(dup)

bpy.ops.object.select_all(action='DESELECT')
for t in temps:
    t.select_set(True)
if temps:
    bpy.context.view_layer.objects.active = temps[0]

try:
    if FORMAT == "FBX":
        kw = dict(filepath=PATH, use_selection=True, object_types={'MESH', 'ARMATURE'} if INCLUDE_ARMATURE else {'MESH'},
                  use_mesh_modifiers=False, mesh_smooth_type='FACE', add_leaf_bones=False,
                  bake_anim=False, path_mode='COPY', embed_textures=False)
        if ENGINE == "UNITY":
            kw.update(apply_scale_options='FBX_SCALE_ALL', axis_forward='-Z', axis_up='Y', apply_unit_scale=True)
        elif ENGINE == "UNREAL":
            kw.update(apply_scale_options='FBX_SCALE_NONE', axis_forward='-Y', axis_up='Z', global_scale=1.0)
        elif ENGINE == "ROBLOX":
            kw.update(apply_scale_options='FBX_SCALE_NONE', axis_forward='-Z', axis_up='Y')
        bpy.ops.export_scene.fbx(**kw)
    elif FORMAT == "GLB":
        bpy.ops.export_scene.gltf(filepath=PATH, export_format='GLB', use_selection=True,
                                  export_apply=False, export_yup=True, export_materials='EXPORT')
    elif FORMAT == "OBJ":
        try:
            bpy.ops.wm.obj_export(filepath=PATH, export_selected_objects=True, export_materials=True,
                                  apply_modifiers=False, export_triangulated_mesh=False)
        except AttributeError:
            bpy.ops.export_scene.obj(filepath=PATH, use_selection=True, use_materials=True)
    else:
        print("Unknown FORMAT", FORMAT)
finally:
    for t in temps:
        me = t.data
        bpy.data.objects.remove(t, do_unlink=True)
        if me.users == 0:
            bpy.data.meshes.remove(me)
    bpy.data.collections.remove(tmp_col)
    for orig, orig_name in renamed:
        orig.name = orig_name                 # restore original names

if os.path.exists(PATH):
    print(f"Exported {len(temps)} object(s), {total_tris} tris -> {PATH} ({os.path.getsize(PATH) / 1024:.1f} KB), engine={ENGINE}")
else:
    print("Export failed: file not created. Check the path is writable and Blender has permission.")
