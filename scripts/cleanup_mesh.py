"""P0 safe cleanup: work on independent mesh copies; commit in place only by opt-in.

Default never edits source meshes or arbitrary selections. Mutating operators run
on disposable mesh copies. A failed target leaves the source and sibling targets intact.
"""
import bpy
import bmesh
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                 # explicit existing object names; never use selected fallback
EDIT_IN_PLACE = False       # default: produce a new named object and independent mesh
OUTPUT_SUFFIX = "_Cleaned"
COLLECTION_NAME = "MCP_Cleanup"
MERGE_DISTANCE = 0.0001
REMOVE_LOOSE = True
REMOVE_DEGENERATE = True
RECALC_NORMALS = True
TRIANGULATE = False
TRIS_TO_QUADS = False
DISSOLVE_ANGLE_DEG = 0.0
ALLOW_SHARED_MESH_DATA = False  # deprecated: shared in-place data is NEVER modified
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_cleanup"
OWNER_VALUE = "cleanup_v2"


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("Refusing to reuse an unowned cleanup collection: " + COLLECTION_NAME)
    return col


def clean(mesh):
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        before = (len(bm.verts), len(bm.edges), len(bm.faces))
        bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=MERGE_DISTANCE)
        if REMOVE_DEGENERATE:
            bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges[:])
            bad = [f for f in bm.faces if f.calc_area() < 1e-10]
            if bad:
                bmesh.ops.delete(bm, geom=bad, context='FACES')
        if REMOVE_LOOSE:
            loose_e = [e for e in bm.edges if not e.link_faces]
            if loose_e:
                bmesh.ops.delete(bm, geom=loose_e, context='EDGES')
            loose_v = [v for v in bm.verts if not v.link_edges]
            if loose_v:
                bmesh.ops.delete(bm, geom=loose_v, context='VERTS')
        if DISSOLVE_ANGLE_DEG > 0:
            bmesh.ops.dissolve_limit(
                bm, angle_limit=math.radians(DISSOLVE_ANGLE_DEG),
                verts=bm.verts[:], edges=bm.edges[:])
        if RECALC_NORMALS:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        if TRIS_TO_QUADS:
            bmesh.ops.join_triangles(
                bm, faces=[f for f in bm.faces if len(f.verts) == 3],
                angle_face_threshold=math.radians(40),
                angle_shape_threshold=math.radians(40))
        if TRIANGULATE:
            bmesh.ops.triangulate(
                bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
        after = (len(bm.verts), len(bm.edges), len(bm.faces))
        bm.to_mesh(mesh)
        mesh.update()
        return before, after
    finally:
        bm.free()


if not math.isfinite(float(MERGE_DISTANCE)) or MERGE_DISTANCE <= 0:
    raise ValueError("MERGE_DISTANCE must be positive and finite")
if not math.isfinite(float(DISSOLVE_ANGLE_DEG)) or not 0 <= DISSOLVE_ANGLE_DEG < 180:
    raise ValueError("DISSOLVE_ANGLE_DEG must be in [0, 180)")
if not TARGETS:
    print("RESULT: NO TARGETS; set explicit TARGETS, no selected-object fallback.")
else:
    col = None if EDIT_IN_PLACE else get_collection()
    results, errors = [], []
    for name in dict.fromkeys(TARGETS):
        source = bpy.data.objects.get(name)
        if source is None:
            print("WARNING: target object not found:", name)
            errors.append((name, "missing"))
            continue
        if source.type != "MESH":
            print("SKIP: non-mesh target", name)
            errors.append((name, "non-mesh"))
            continue
        if source.mode != "OBJECT":
            print(f"[{name}] SKIP: object is in {source.mode} mode")
            errors.append((name, "edit mode"))
            continue
        if source.data.shape_keys and source.data.shape_keys.key_blocks:
            print(f"[{name}] SKIP: mesh has Shape Keys")
            errors.append((name, "shape keys"))
            continue
        if source.library or source.data.library:
            print(f"[{name}] SKIP: linked/library data")
            errors.append((name, "library"))
            continue
        if EDIT_IN_PLACE and source.data.users > 1:
            print(f"[{name}] SKIP: mesh data is shared; in-place edits are forbidden")
            errors.append((name, "shared"))
            continue
        output_name = source.name + OUTPUT_SUFFIX
        if not EDIT_IN_PLACE and output_name in bpy.data.objects:
            print("ERROR: refusing output name collision", output_name)
            errors.append((name, "name collision"))
            continue
        working_mesh = source.data.copy()
        working_obj = None
        try:
            before, after = clean(working_mesh)
            if EDIT_IN_PLACE:
                old = source.data
                source.data = working_mesh
                old.name = old.name + "_BeforeCleanup"
                old.use_fake_user = True  # recovery backup; user can delete manually
                results.append(source.name)
            else:
                working_obj = source.copy()
                working_obj.data = working_mesh
                working_obj.name = output_name
                working_obj[OWNER_KEY] = OWNER_VALUE
                working_obj["mcp_source"] = source.name
                col.objects.link(working_obj)
                results.append(working_obj.name)
            print(f"[{name}] verts {before[0]}->{after[0]}, edges {before[1]}->{after[1]}, faces {before[2]}->{after[2]}")
        except Exception as exc:
            errors.append((name, str(exc)))
            print("ERROR:", name, repr(exc))
            if working_obj is not None:
                bpy.data.objects.remove(working_obj, do_unlink=True)
            if working_mesh.users == 0:
                bpy.data.meshes.remove(working_mesh)
    print("CLEANUP RESULT:", "SUCCESS" if not errors else "PARTIAL",
          "outputs=", results, "errors=", errors)
    print("NOTE: run validate_asset.py and visually inspect results before export.")
