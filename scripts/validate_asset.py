"""validate_asset.py - mesh/scene health report. Paste into execute_blender_code.

Config: set TARGETS to a list of object names, or leave empty to check the
selected objects (falls back to all visible mesh objects).
Prints PASS / WARN / FAIL per object and a summary. Read-only: changes nothing.
"""
import bpy
import bmesh
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []            # e.g. ["Chair_Body", "Chair_Leg"]; empty = selection / all visible
MAX_TRIS = 5000         # triangle budget per object (see references/budgets.md)
MAX_MATERIALS = 2       # materials per object
MAX_TEX_SIZE = 2048     # largest allowed image texture side
CHECK_SCALE = True      # require applied scale (1,1,1)
CHECK_UV = True         # require a UV map (disable for untextured/vertex-color assets)
# ----------------------------------------------------------------------------


def pick_objects():
    if TARGETS:
        return [bpy.data.objects[n] for n in TARGETS if n in bpy.data.objects]
    sel = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    if sel:
        return sel
    return [o for o in bpy.context.view_layer.objects if o.type == 'MESH' and o.visible_get()]


def tri_count(me):
    me.calc_loop_triangles()
    return len(me.loop_triangles)


def check_object(ob):
    res = []  # (level, message)
    dg = bpy.context.evaluated_depsgraph_get()
    eval_ob = ob.evaluated_get(dg)
    me = eval_ob.to_mesh()
    try:
        tris = tri_count(me)
        res.append(("PASS" if tris <= MAX_TRIS else "FAIL",
                    f"triangles (with modifiers): {tris} / budget {MAX_TRIS}"))

        bm = bmesh.new()
        bm.from_mesh(me)
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        loose_v = [v for v in bm.verts if not v.link_edges]
        loose_e = [e for e in bm.edges if not e.link_faces]
        nonman = [e for e in bm.edges if e.link_faces and not e.is_manifold]
        boundary = [e for e in bm.edges if e.is_boundary]
        zero_area = [f for f in bm.faces if f.calc_area() < 1e-10]
        ngons = [f for f in bm.faces if len(f.verts) > 4]
        tris_f = [f for f in bm.faces if len(f.verts) == 3]

        res.append(("PASS" if not loose_v else "FAIL", f"loose verts: {len(loose_v)}"))
        res.append(("PASS" if not loose_e else "WARN", f"wire/loose edges: {len(loose_e)}"))
        res.append(("PASS" if not zero_area else "FAIL", f"zero-area faces: {len(zero_area)}"))
        res.append(("PASS" if not nonman else "WARN", f"non-manifold edges: {len(nonman)}"))
        res.append(("INFO", f"boundary (open) edges: {len(boundary)} (fine for planes/cards, bad for solids)"))
        res.append(("PASS" if not ngons else "WARN", f"n-gons (5+ sides): {len(ngons)}"))
        res.append(("INFO", f"faces: {len(bm.faces)}, tris-faces: {len(tris_f)}, verts: {len(bm.verts)}"))

        # duplicate verts (within 1e-5)
        kd_dupes = 0
        from mathutils import kdtree
        kd = kdtree.KDTree(len(bm.verts))
        for i, v in enumerate(bm.verts):
            kd.insert(v.co, i)
        kd.balance()
        for i, v in enumerate(bm.verts):
            hits = kd.find_range(v.co, 1e-5)
            if len(hits) > 1:
                kd_dupes += 1
        res.append(("PASS" if kd_dupes == 0 else "WARN", f"overlapping vertices: {kd_dupes}"))

        # normals consistency (rough): faces whose normal points toward the object's centre
        if bm.faces and not boundary:
            from mathutils import Vector
            center = sum((v.co for v in bm.verts), Vector()) / len(bm.verts)
            inward = sum(1 for f in bm.faces if (f.calc_center_median() - center).dot(f.normal) < 0)
            ratio = inward / len(bm.faces)
            res.append(("PASS" if ratio < 0.15 else "WARN",
                        f"faces pointing inward: {ratio:.0%} (high value on a convex solid = flipped normals)"))
        bm.free()
    finally:
        eval_ob.to_mesh_clear()

    # scale / origin
    if CHECK_SCALE:
        s = ob.scale
        ok = all(abs(x - 1.0) < 1e-4 for x in s)
        res.append(("PASS" if ok else "FAIL", f"scale applied: {tuple(round(x, 4) for x in s)}"))
        r = ob.rotation_euler
        okr = all(abs(x) < 1e-4 for x in r) if ob.rotation_mode != 'QUATERNION' else True
        res.append(("PASS" if okr else "WARN", f"rotation zeroed: {tuple(round(math.degrees(x), 2) for x in r)} deg"))

    # dimensions
    d = ob.dimensions
    res.append(("INFO", f"dimensions (m): {d.x:.3f} x {d.y:.3f} x {d.z:.3f}"))

    # UV
    if CHECK_UV:
        uvs = ob.data.uv_layers
        res.append(("PASS" if len(uvs) > 0 else "FAIL", f"UV maps: {len(uvs)}"))
        if len(uvs) > 0:
            uv = uvs.active.data
            if len(uv):
                xs = [l.uv.x for l in uv]
                ys = [l.uv.y for l in uv]
                inside = min(xs) >= -0.001 and max(xs) <= 1.001 and min(ys) >= -0.001 and max(ys) <= 1.001
                res.append(("PASS" if inside else "WARN",
                            f"UVs inside 0-1: {inside} (range x {min(xs):.2f}..{max(xs):.2f}, y {min(ys):.2f}..{max(ys):.2f})"))

    # materials
    used = [s.material for s in ob.material_slots]
    empty = sum(1 for m in used if m is None)
    res.append(("PASS" if len(used) <= MAX_MATERIALS else "WARN", f"material slots: {len(used)} / {MAX_MATERIALS}"))
    if empty:
        res.append(("WARN", f"empty material slots: {empty}"))

    # naming
    bad_name = ob.name.split('.')[-1].isdigit() or ' ' in ob.name or ob.name.startswith(("Cube", "Sphere", "Cylinder", "Plane", "Cone", "Torus", "Icosphere"))
    res.append(("PASS" if not bad_name else "WARN", f"name: '{ob.name}' (avoid default names, spaces, .001 suffixes)"))

    # modifiers still live
    if ob.modifiers:
        res.append(("INFO", "modifiers: " + ", ".join(f"{m.name}({m.type})" for m in ob.modifiers)))
    return res


def check_images():
    out = []
    for img in bpy.data.images:
        if img.type in {'RENDER_RESULT', 'COMPOSITING'}:
            continue
        w, h = img.size
        if w == 0:
            continue
        pot = (w & (w - 1) == 0) and (h & (h - 1) == 0)
        lvl = "PASS"
        msg = f"image '{img.name}': {w}x{h}"
        if max(w, h) > MAX_TEX_SIZE:
            lvl, msg = "WARN", msg + f" exceeds {MAX_TEX_SIZE}"
        if not pot:
            lvl, msg = "WARN", msg + " not power of two"
        out.append((lvl, msg))
    return out


objs = pick_objects()
print(f"=== validate_asset: {len(objs)} object(s), Blender {bpy.app.version_string} ===")
counts = {"PASS": 0, "WARN": 0, "FAIL": 0}
total_tris = 0
for ob in objs:
    print(f"\n[{ob.name}]")
    for lvl, msg in check_object(ob):
        if lvl in counts:
            counts[lvl] += 1
        print(f"  {lvl:4s} {msg}")
    dg = bpy.context.evaluated_depsgraph_get()
    e = ob.evaluated_get(dg)
    m = e.to_mesh()
    total_tris += tri_count(m)
    e.to_mesh_clear()

imgs = check_images()
if imgs:
    print("\n[images]")
    for lvl, msg in imgs:
        if lvl in counts:
            counts[lvl] += 1
        print(f"  {lvl:4s} {msg}")

print(f"\nTOTAL triangles: {total_tris}")
print(f"SUMMARY: {counts['PASS']} pass, {counts['WARN']} warn, {counts['FAIL']} fail")
print("RESULT:", "FAIL - fix FAIL items and re-run" if counts["FAIL"] else ("OK with warnings" if counts["WARN"] else "OK"))
