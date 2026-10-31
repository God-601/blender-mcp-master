"""Read-only asset diagnostics. Empty TARGETS validates selected meshes only."""
import bpy
import bmesh
import math

TARGETS = []  # Explicit object names; empty = selected mesh objects ONLY.
MAX_TRIS = 5000
MAX_MATERIALS = 2
MAX_TEX_SIZE = 2048
CHECK_SCALE = True
CHECK_UV = True
MISSING_TARGETS = []
INVALID_TARGETS = []


def tri_count(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def pick_objects():
    MISSING_TARGETS.clear()
    INVALID_TARGETS.clear()
    if TARGETS:
        result = []
        for name in TARGETS:
            obj = bpy.data.objects.get(name)
            if obj is None:
                MISSING_TARGETS.append(name)
            elif obj.type != "MESH":
                INVALID_TARGETS.append((name, obj.type))
            else:
                result.append(obj)
        return result
    result = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not result:
        print("INFO: TARGETS is empty and no mesh is selected. Scene-wide fallback is disabled.")
    else:
        print("INFO: validating selected mesh object(s): " + ", ".join(repr(obj.name) for obj in result))
    return result


def evaluated_mesh(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_obj = obj.evaluated_get(depsgraph)
    return evaluated_obj, evaluated_obj.to_mesh()


def check_object(obj):
    results = []
    base = obj.data
    results.append(("INFO", f"base mesh: {len(base.vertices)} verts, {len(base.edges)} edges, {len(base.polygons)} polygons, {tri_count(base)} triangles"))
    results.append(("INFO", f"mesh datablock users: {base.users}" + (" (shared data)" if base.users > 1 else "")))
    if base.shape_keys:
        results.append(("INFO", f"shape keys: {len(base.shape_keys.key_blocks)} (avoid topology-changing edits)"))

    evaluated_obj, mesh = evaluated_mesh(obj)
    try:
        tris = tri_count(mesh)
        results.append(("PASS" if tris <= MAX_TRIS else "WARN", f"evaluated triangles (modifiers included): {tris} / suggested budget {MAX_TRIS}"))
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            loose_verts = sum(1 for v in bm.verts if not v.link_edges)
            loose_edges = sum(1 for e in bm.edges if not e.link_faces)
            nonmanifold = sum(1 for e in bm.edges if len(e.link_faces) > 2)
            boundaries = sum(1 for e in bm.edges if len(e.link_faces) == 1)
            zero_area = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
            ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
            results.extend([
                ("PASS" if not loose_verts else "WARN", f"loose vertices: {loose_verts}"),
                ("PASS" if not loose_edges else "WARN", f"wire/loose edges: {loose_edges}"),
                ("PASS" if not zero_area else "WARN", f"near-zero-area faces: {zero_area}"),
                ("PASS" if not nonmanifold else "WARN", f"non-manifold edges with 3+ linked faces: {nonmanifold}"),
                ("INFO", f"boundary/open edges: {boundaries} (may be valid on cards/open surfaces)"),
                ("INFO", f"n-gons: {ngons} (review on curved/deforming surfaces)"),
                ("INFO", f"evaluated topology: {len(bm.verts)} verts, {len(bm.edges)} edges, {len(bm.faces)} faces"),
            ])
            duplicates = 0
            if bm.verts:
                from mathutils import kdtree
                tree = kdtree.KDTree(len(bm.verts))
                for i, v in enumerate(bm.verts):
                    tree.insert(v.co, i)
                tree.balance()
                for i, v in enumerate(bm.verts):
                    if any(other != i for _, other, _ in tree.find_range(v.co, 1e-5)):
                        duplicates += 1
            results.append(("INFO", f"vertices with nearby duplicates (1e-5 units): {duplicates} (hint, not proof)"))
        finally:
            bm.free()
    finally:
        evaluated_obj.to_mesh_clear()

    if CHECK_SCALE:
        scale = tuple(round(v, 4) for v in obj.scale)
        results.append(("PASS" if all(abs(v - 1.0) < 1e-4 for v in obj.scale) else "INFO",
                        f"scale: {scale} (apply only if required)"))
        rotation = obj.matrix_basis.to_euler()
        degrees = tuple(round(math.degrees(v), 2) for v in rotation)
        results.append(("PASS" if all(abs(v) < 1e-4 for v in rotation) else "INFO", f"rotation: {degrees} degrees"))

    d = obj.dimensions
    results.append(("INFO", f"dimensions in Blender units: {d.x:.3f} x {d.y:.3f} x {d.z:.3f}"))
    if CHECK_UV:
        layers = base.uv_layers
        results.append(("PASS" if len(layers) else "INFO", f"UV maps: {len(layers)} (optional for untextured assets)"))
        if layers.active and len(layers.active.data):
            uv = layers.active.data
            xs, ys = [loop.uv.x for loop in uv], [loop.uv.y for loop in uv]
            inside = min(xs) >= -0.001 and max(xs) <= 1.001 and min(ys) >= -0.001 and max(ys) <= 1.001
            results.append(("INFO", f"active UVs inside 0-1: {inside} (tiling/UDIM may exceed this)"))

    slots = [slot.material for slot in obj.material_slots]
    empty = sum(1 for mat in slots if mat is None)
    results.append(("PASS" if len(slots) <= MAX_MATERIALS else "WARN", f"material slots: {len(slots)} / suggested budget {MAX_MATERIALS}"))
    if empty:
        results.append(("WARN", f"empty material slots: {empty}"))
    prefixes = ("Cube", "Sphere", "Cylinder", "Plane", "Cone", "Torus", "Icosphere")
    bad_name = obj.name.split(".")[-1].isdigit() or " " in obj.name or obj.name.startswith(prefixes)
    results.append(("WARN" if bad_name else "PASS", f"name: {obj.name!r}"))
    if obj.modifiers:
        results.append(("INFO", "modifiers: " + ", ".join(f"{m.name}({m.type}, viewport={m.show_viewport})" for m in obj.modifiers)))
    return results


def check_images(objects):
    images = {}
    for obj in objects:
        for slot in obj.material_slots:
            mat = slot.material
            if mat and mat.node_tree:
                for node in mat.node_tree.nodes:
                    if node.type == "TEX_IMAGE" and node.image:
                        images[node.image.name] = node.image
    findings = []
    for image in images.values():
        if image.type in {"RENDER_RESULT", "COMPOSITING"}:
            continue
        w, h = image.size
        if w and h:
            too_large = max(w, h) > MAX_TEX_SIZE
            findings.append(("WARN" if too_large else "INFO",
                             f"image {image.name!r}: {w}x{h}" +
                             (f" exceeds suggested {MAX_TEX_SIZE}px maximum" if too_large else "")))
    return findings


objects = pick_objects()
print(f"=== validate_asset v2: {len(objects)} mesh object(s), Blender {bpy.app.version_string} ===")
counts = {"PASS": 0, "WARN": 0, "INFO": 0}
total_triangles = 0
for name in MISSING_TARGETS:
    counts["WARN"] += 1
    print(f"WARN: target object not found: {name!r}")
for name, kind in INVALID_TARGETS:
    counts["WARN"] += 1
    print(f"WARN: target object is not a mesh: {name!r} (type: {kind})")
if not objects:
    counts["WARN"] += 1
    print("WARN: no mesh targets. Set TARGETS or select intended meshes; no scene-wide fallback.")

for obj in objects:
    print(f"\n[{obj.name}]")
    for level, message in check_object(obj):
        counts[level] += 1
        print(f"  {level:4s} {message}")
    evaluated_obj, mesh = evaluated_mesh(obj)
    try:
        total_triangles += tri_count(mesh)
    finally:
        evaluated_obj.to_mesh_clear()

for level, message in check_images(objects):
    counts[level] += 1
    print(f"  {level:4s} {message}")

unique_materials = {slot.material for obj in objects for slot in obj.material_slots if slot.material}
print(f"\nTOTAL: {len(objects)} mesh objects, {len(unique_materials)} unique materials, {total_triangles} evaluated triangles")
print(f"SUMMARY: {counts['PASS']} pass, {counts['WARN']} warn, {counts['INFO']} info")
if not objects or MISSING_TARGETS or INVALID_TARGETS:
    result = "INCOMPLETE - CHECK TARGETS"
elif counts["WARN"]:
    result = "REVIEW WARNINGS"
else:
    result = "NO WARNINGS REPORTED"
print("RESULT:", result)
