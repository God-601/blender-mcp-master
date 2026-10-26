"""Read-only mesh health report. Paste into execute_blender_code.

Configure TARGETS, MAX_TRIS, MAX_MATERIALS, MAX_TEX_SIZE and CHECK_UV below.
Diagnostics are heuristics: interpret findings according to the intended asset.
"""
import bpy
import bmesh
import math

TARGETS = []  # empty = selected meshes, then visible meshes
MAX_TRIS = 5000
MAX_MATERIALS = 2
MAX_TEX_SIZE = 2048
CHECK_SCALE = True
CHECK_UV = True
MISSING_TARGETS = []


def pick_objects():
    if TARGETS:
        missing = [name for name in TARGETS if name not in bpy.data.objects]
        MISSING_TARGETS.extend(missing)
        return [bpy.data.objects[name] for name in TARGETS if name in bpy.data.objects]
    selected = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if selected:
        return selected
    return [obj for obj in bpy.context.view_layer.objects
            if obj.type == "MESH" and obj.visible_get()]


def tri_count(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def check_object(obj):
    results = []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated_obj = obj.evaluated_get(depsgraph)
    mesh = evaluated_obj.to_mesh()
    try:
        tris = tri_count(mesh)
        results.append(("PASS" if tris <= MAX_TRIS else "WARN",
                        f"triangles with modifiers: {tris} / suggested budget {MAX_TRIS}"))
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            loose_verts = sum(1 for vert in bm.verts if not vert.link_edges)
            loose_edges = sum(1 for edge in bm.edges if not edge.link_faces)
            # BMEdge.is_manifold is False for boundary edges too, so count real non-manifold
            # edges (3+ faces) separately from boundary (open) edges.
            nonmanifold = sum(1 for edge in bm.edges if len(edge.link_faces) > 2)
            boundaries = sum(1 for edge in bm.edges if len(edge.link_faces) == 1)
            zero_area = sum(1 for face in bm.faces if face.calc_area() < 1e-10)
            ngons = sum(1 for face in bm.faces if len(face.verts) > 4)
            results.extend([
                ("PASS" if not loose_verts else "WARN", f"loose vertices: {loose_verts}"),
                ("PASS" if not loose_edges else "WARN", f"wire/loose edges: {loose_edges}"),
                ("PASS" if not zero_area else "WARN", f"near-zero-area faces: {zero_area}"),
                ("PASS" if not nonmanifold else "WARN", f"non-manifold edges (3+ faces): {nonmanifold}"),
                ("INFO", f"boundary/open edges: {boundaries} (may be expected on cards/open surfaces)"),
                ("INFO", f"n-gons: {ngons} (review on curved/deforming surfaces; not automatically wrong)"),
                ("INFO", f"vertices: {len(bm.verts)}, edges: {len(bm.edges)}, faces: {len(bm.faces)}"),
            ])
            # Coincident vertices are a hint, not proof of bad topology.
            duplicates = 0
            if bm.verts:
                from mathutils import kdtree
                tree = kdtree.KDTree(len(bm.verts))
                for index, vert in enumerate(bm.verts):
                    tree.insert(vert.co, index)
                tree.balance()
                for index, vert in enumerate(bm.verts):
                    if any(other_index != index for _, other_index, _ in tree.find_range(vert.co, 1e-5)):
                        duplicates += 1
            results.append(("INFO", f"vertices with nearby duplicates (1e-5 units): {duplicates}"))
            results.append(("INFO", "check face orientation with Blender's face-orientation overlay and shading"))
        finally:
            bm.free()
    finally:
        evaluated_obj.to_mesh_clear()

    if CHECK_SCALE:
        scale = obj.scale
        scale_ok = all(abs(value - 1.0) < 1e-4 for value in scale)
        results.append(("PASS" if scale_ok else "INFO",
                        f"scale: {tuple(round(value, 4) for value in scale)} (apply only if required)"))
        # rotation_euler is stale when the object uses quaternion/axis-angle rotation.
        rotation = obj.matrix_basis.to_euler()
        rotation_ok = all(abs(value) < 1e-4 for value in rotation)
        results.append(("PASS" if rotation_ok else "INFO",
                        f"rotation: {tuple(round(math.degrees(value), 2) for value in rotation)} degrees"))

    dimensions = obj.dimensions
    results.append(("INFO", f"dimensions in Blender units: {dimensions.x:.3f} x {dimensions.y:.3f} x {dimensions.z:.3f}"))

    if CHECK_UV:
        uv_layers = obj.data.uv_layers
        results.append(("PASS" if len(uv_layers) else "INFO",
                        f"UV maps: {len(uv_layers)} (optional for untextured assets)"))
        if uv_layers.active and len(uv_layers.active.data):
            uv_data = uv_layers.active.data
            xs = [loop.uv.x for loop in uv_data]
            ys = [loop.uv.y for loop in uv_data]
            inside = min(xs) >= -0.001 and max(xs) <= 1.001 and min(ys) >= -0.001 and max(ys) <= 1.001
            results.append(("INFO", f"active UVs inside 0-1: {inside} (tiling/UDIM may exceed this)"))

    slots = [slot.material for slot in obj.material_slots]
    empty_slots = sum(1 for material in slots if material is None)
    results.append(("PASS" if len(slots) <= MAX_MATERIALS else "WARN",
                    f"material slots: {len(slots)} / suggested budget {MAX_MATERIALS}"))
    if empty_slots:
        results.append(("WARN", f"empty material slots: {empty_slots}"))

    default_prefixes = ("Cube", "Sphere", "Cylinder", "Plane", "Cone", "Torus", "Icosphere")
    bad_name = obj.name.split(".")[-1].isdigit() or " " in obj.name or obj.name.startswith(default_prefixes)
    results.append(("WARN" if bad_name else "PASS", f"name: {obj.name!r}"))
    if obj.modifiers:
        results.append(("INFO", "modifiers: " + ", ".join(f"{mod.name}({mod.type})" for mod in obj.modifiers)))
    return results


def check_images():
    findings = []
    for image in bpy.data.images:
        if image.type in {"RENDER_RESULT", "COMPOSITING"}:
            continue
        width, height = image.size
        if width and height:
            message = f"image {image.name!r}: {width}x{height}"
            if max(width, height) > MAX_TEX_SIZE:
                message += f" exceeds suggested {MAX_TEX_SIZE}px maximum"
                findings.append(("WARN", message))
            else:
                findings.append(("INFO", message))
    return findings


objects = pick_objects()
print(f"=== validate_asset: {len(objects)} mesh object(s), Blender {bpy.app.version_string} ===")
counts = {"PASS": 0, "WARN": 0, "INFO": 0}
total_triangles = 0
for missing_name in MISSING_TARGETS:
    counts["WARN"] += 1
    print(f"WARN: target object not found: {missing_name!r}")
if not objects:
    counts["WARN"] += 1
    print("WARN: no mesh objects found; set TARGETS or select/unhide the intended meshes.")

for obj in objects:
    print(f"\n[{obj.name}]")
    for level, message in check_object(obj):
        counts[level] = counts.get(level, 0) + 1
        print(f"  {level:4s} {message}")
    evaluated_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated_mesh = evaluated_obj.to_mesh()
    try:
        total_triangles += tri_count(evaluated_mesh)
    finally:
        evaluated_obj.to_mesh_clear()

for level, message in check_images():
    counts[level] = counts.get(level, 0) + 1
    print(f"  {level:4s} {message}")

print(f"\nTOTAL triangles with modifiers: {total_triangles}")
print(f"SUMMARY: {counts['PASS']} pass, {counts['WARN']} warn, {counts['INFO']} info")
if not objects or MISSING_TARGETS:
    result = "INCOMPLETE - CHECK TARGETS"
elif counts["WARN"]:
    result = "REVIEW WARNINGS"
else:
    result = "NO WARNINGS REPORTED"
print("RESULT:", result)
