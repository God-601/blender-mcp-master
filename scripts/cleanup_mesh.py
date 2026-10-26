"""cleanup_mesh.py - fix common mesh problems with bmesh (no operators, no mode switching).
Paste into execute_blender_code. Prints before/after counts.

Safety: objects in Edit Mode are skipped, and meshes shared by several objects are skipped
unless ALLOW_SHARED_MESH_DATA is True.
"""
import bpy
import bmesh
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                 # object names; empty = selected mesh objects
MERGE_DISTANCE = 0.0001      # remove doubles threshold (Blender units)
REMOVE_LOOSE = True          # delete loose verts / wire edges
REMOVE_DEGENERATE = True     # dissolve zero-area faces / zero-length edges
RECALC_NORMALS = True        # make normals consistent (outward)
TRIANGULATE = False          # triangulate faces (game export); prefer doing it last
TRIS_TO_QUADS = False        # join triangles into quads (cleaner topology for subsurf)
DISSOLVE_ANGLE_DEG = 0.0     # >0 = limited dissolve of near-flat edges (e.g. 1.0) to cut useless geometry
ALLOW_SHARED_MESH_DATA = False  # set True only if editing every linked instance is intentional
# ----------------------------------------------------------------------------


def real_users(mesh):
    """Object users of the mesh data; a fake user does not make the mesh shared."""
    return mesh.users - (1 if mesh.use_fake_user else 0)


def clean(me, bm):
    bm.from_mesh(me)
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
        bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(DISSOLVE_ANGLE_DEG),
                                 verts=bm.verts[:], edges=bm.edges[:])

    if RECALC_NORMALS:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    if TRIS_TO_QUADS:
        bmesh.ops.join_triangles(bm, faces=[f for f in bm.faces if len(f.verts) == 3],
                                 angle_face_threshold=math.radians(40),
                                 angle_shape_threshold=math.radians(40))

    if TRIANGULATE:
        bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')

    after = (len(bm.verts), len(bm.edges), len(bm.faces))
    bm.to_mesh(me)
    me.update()
    return before, after


for name in TARGETS:
    if name not in bpy.data.objects:
        print(f"WARNING: target object not found: {name!r}")

objs = [bpy.data.objects[n] for n in TARGETS if n in bpy.data.objects] if TARGETS else \
       [o for o in bpy.context.selected_objects if o.type == 'MESH']

if not objs:
    print("No target mesh objects. Select objects or set TARGETS.")

for ob in objs:
    if ob.type != 'MESH':
        continue
    if ob.mode != 'OBJECT':
        print(f"[{ob.name}] SKIP: object is in {ob.mode} mode; switch to Object Mode so edits are not lost.")
        continue
    users = real_users(ob.data)
    if users > 1 and not ALLOW_SHARED_MESH_DATA:
        print(f"[{ob.name}] SKIP: mesh data is shared by {users} users. "
              "Make the mesh single-user or set ALLOW_SHARED_MESH_DATA=True intentionally.")
        continue
    if users > 1:
        print(f"[{ob.name}] WARNING: editing shared mesh data used by {users} objects")
    bm = bmesh.new()
    try:
        before, after = clean(ob.data, bm)
    finally:
        bm.free()
    print(f"[{ob.name}] verts {before[0]}->{after[0]}, edges {before[1]}->{after[1]}, faces {before[2]}->{after[2]}")

print("Done. Run validate_asset.py to confirm.")
