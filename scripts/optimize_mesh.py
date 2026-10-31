"""Conservative, backup-first mesh optimizer. Paste into Blender's execute_blender_code.

Configure TARGETS and inspect a dry run first. APPLY defaults to False.
This script never guesses which faces are internal and never applies Decimate.
"""
import bpy
import bmesh

# ---------------------------- CONFIGURATION ----------------------------
TARGETS = []  # Explicit object names. Empty = selected mesh objects only.
APPLY = False  # Review dry-run report, then deliberately set True.
MODE = "conservative"  # "conservative" or "balanced"
MERGE_DISTANCE = 0.00001  # Blender units; set 0 to disable.
USE_LIMITED_DISSOLVE = False  # Balanced-only; inspect UVs and shading afterwards.
BACKUP_COLLECTION = "_MCP_OPTIMIZATION_BACKUPS"
ADD_DECIMATE_MODIFIER = False  # Non-destructive preview only.
DECIMATE_RATIO = 0.5  # Used only when ADD_DECIMATE_MODIFIER=True; 0 < ratio <= 1.
# -----------------------------------------------------------------------

if MODE not in {"conservative", "balanced"}:
    raise ValueError("MODE must be 'conservative' or 'balanced'")
if not 0.0 < DECIMATE_RATIO <= 1.0:
    raise ValueError("DECIMATE_RATIO must be in (0, 1]")
if MERGE_DISTANCE < 0:
    raise ValueError("MERGE_DISTANCE cannot be negative")


def tri_count(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def evaluated_tri_count(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        return tri_count(mesh)
    finally:
        evaluated.to_mesh_clear()


def targets():
    if TARGETS:
        result = []
        for name in TARGETS:
            obj = bpy.data.objects.get(name)
            if obj is None:
                print("SKIP: missing target:", name)
            elif obj.type != "MESH":
                print("SKIP: not a mesh:", name, obj.type)
            else:
                result.append(obj)
        return result
    selected = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not selected:
        print("No targets. Set TARGETS or select mesh objects; scene-wide fallback is disabled.")
    return selected


def skip_reason(obj):
    if obj.library or obj.data.library:
        return "linked/library data"
    if obj.data.users > 1:
        return f"shared mesh datablock ({obj.data.users} users)"
    if obj.data.shape_keys:
        return "shape keys present"
    if any(mod.type in {"ARMATURE", "HOOK", "LATTICE", "MESH_DEFORM", "SURFACE_DEFORM"}
           for mod in obj.modifiers):
        return "deformation-dependent modifier present"
    if obj.mode != "OBJECT":
        return f"object is in {obj.mode} mode"
    return None


def backup_object(obj, collection):
    backup = obj.copy()
    backup.data = obj.data  # Preserve exact original mesh datablock.
    backup.name = obj.name + "_OPT_BACKUP"
    collection.objects.link(backup)
    backup.hide_viewport = True
    backup.hide_render = True
    backup.hide_set(True)
    # Give the working object its own mesh so the backup retains the original.
    obj.data = obj.data.copy()
    return backup


def optimize_mesh(obj):
    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        before = (len(bm.verts), len(bm.edges), len(bm.faces))
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_edges],
                         context="VERTS")
        bmesh.ops.delete(bm, geom=[e for e in bm.edges if not e.link_faces],
                         context="EDGES")
        bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-12)
        if MERGE_DISTANCE > 0:
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=MERGE_DISTANCE)
        if MODE == "balanced" and USE_LIMITED_DISSOLVE:
            bmesh.ops.dissolve_limit(
                bm, angle_limit=0.01, use_dissolve_boundaries=False,
                verts=list(bm.verts), edges=list(bm.edges), delimit={"MATERIAL"}
            )
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        after = (len(bm.verts), len(bm.edges), len(bm.faces))
        bm.to_mesh(obj.data)
        obj.data.update()
        return before, after
    finally:
        bm.free()


objects = targets()
print(f"=== optimize_mesh | Blender {bpy.app.version_string} | APPLY={APPLY} | MODE={MODE} ===")
if not objects:
    print("RESULT: NO TARGETS")
else:
    backup_collection = bpy.data.collections.get(BACKUP_COLLECTION)
    if APPLY and backup_collection is None:
        backup_collection = bpy.data.collections.new(BACKUP_COLLECTION)
        bpy.context.scene.collection.children.link(backup_collection)
        backup_collection.hide_viewport = True
        backup_collection.hide_render = True

    total_before = 0
    total_after = 0
    changed = 0
    for obj in objects:
        reason = skip_reason(obj)
        if reason:
            print(f"SKIP: {obj.name!r}: {reason}")
            continue
        tris_before = evaluated_tri_count(obj)
        total_before += tris_before
        print(f"TARGET: {obj.name!r} | base verts/edges/faces="
              f"{len(obj.data.vertices)}/{len(obj.data.edges)}/{len(obj.data.polygons)}"
              f" | evaluated tris={tris_before}")
        if not APPLY:
            print("DRY RUN: no changes made.")
            total_after += tris_before
            continue

        backup = backup_object(obj, backup_collection)
        before, after = optimize_mesh(obj)
        if ADD_DECIMATE_MODIFIER and DECIMATE_RATIO < 1.0:
            modifier = obj.modifiers.new("MCP_Decimate_PREVIEW", "DECIMATE")
            modifier.ratio = DECIMATE_RATIO
            modifier.show_viewport = True
            modifier.show_render = True
        tris_after = evaluated_tri_count(obj)
        total_after += tris_after
        changed += 1
        print(f"BACKUP: {backup.name!r}")
        print(f"BASE MESH: {before[0]}/{before[1]}/{before[2]} -> "
              f"{after[0]}/{after[1]}/{after[2]} (verts/edges/faces)")
        print(f"EVALUATED TRIANGLES: {tris_before} -> {tris_after}")
        if tris_before:
            print(f"TRIANGLE CHANGE: {(tris_after - tris_before) / tris_before * 100:.2f}%")
        print("NOTE: inspect silhouette, UVs, material borders, normals and modifiers.")
    if not APPLY:
        print(f"DRY RUN TOTAL: {total_before} evaluated triangles; no edits or backups created.")
    else:
        print(f"APPLIED TO {changed} object(s).")
        print(f"TOTAL EVALUATED TRIANGLES: {total_before} -> {total_after}")
        if total_before:
            print(f"TOTAL CHANGE: {(total_after - total_before) / total_before * 100:.2f}%")
        print("Faces classified as internal were NOT automatically deleted.")
