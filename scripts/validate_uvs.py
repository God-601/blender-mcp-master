"""Read-only UV diagnostics for explicitly named or selected mesh objects.

Paste into Blender MCP execute_blender_code. No mesh or UV data is modified.
"""
import bpy

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []          # Explicit object names; empty = selected mesh objects ONLY.
UV_LAYER_NAME = ""    # Empty = active UV layer; otherwise inspect this named layer.
ZERO_AREA_EPSILON = 1e-12
OUT_OF_TILE_TOLERANCE = 1e-4
# ----------------------------------------------------------------------------

missing = []
invalid = []
warnings = []
incomplete = []


def resolve_targets():
    if TARGETS:
        result = []
        for name in TARGETS:
            obj = bpy.data.objects.get(name)
            if obj is None:
                missing.append(name)
            elif obj.type != "MESH":
                invalid.append((name, obj.type))
            else:
                result.append(obj)
        return result
    selected = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
    if not selected:
        print("INFO: TARGETS empty and no mesh selected; scene-wide fallback is disabled.")
    return selected


objects = resolve_targets()
print(f"=== UV VALIDATION | Blender {bpy.app.version_string} | {len(objects)} target(s) ===")
for name in missing:
    print(f"WARN: missing target {name!r}")
for name, kind in invalid:
    print(f"WARN: target {name!r} is {kind}, not MESH")
if not objects:
    incomplete.append("no mesh targets")
if missing or invalid:
    incomplete.append("invalid or missing targets")
    
for obj in objects:
    mesh = obj.data
    layer = mesh.uv_layers.get(UV_LAYER_NAME) if UV_LAYER_NAME else mesh.uv_layers.active
    print(f"\n[{obj.name}]")
    if layer is None:
        print("WARN: requested UV layer not found" if UV_LAYER_NAME else "INFO: no active UV layer")
        incomplete.append(obj.name + ": UV layer unavailable")
        continue
    uv_data = layer.data
    if len(uv_data) != len(mesh.loops):
        print(f"WARN: UV loop count {len(uv_data)} does not match mesh loop count {len(mesh.loops)}")
        incomplete.append(obj.name + ": UV loop count mismatch")
        continue

    coords = [item.uv.copy() for item in uv_data]
    if not coords:
        print("WARN: UV layer is empty")
        incomplete.append(obj.name + ": empty UV layer")
        continue
    min_u, max_u = min(v.x for v in coords), max(v.x for v in coords)
    min_v, max_v = min(v.y for v in coords), max(v.y for v in coords)
    outside = sum(
        1 for v in coords
        if v.x < -OUT_OF_TILE_TOLERANCE or v.x > 1 + OUT_OF_TILE_TOLERANCE
        or v.y < -OUT_OF_TILE_TOLERANCE or v.y > 1 + OUT_OF_TILE_TOLERANCE
    )
    zero_area = 0
    for poly in mesh.polygons:
        if len(poly.loop_indices) < 3:
            continue
        points = [coords[i] for i in poly.loop_indices]
        area = abs(sum(points[i].x * points[(i + 1) % len(points)].y -
                       points[(i + 1) % len(points)].x * points[i].y
                       for i in range(len(points)))) * 0.5
        if area <= ZERO_AREA_EPSILON:
            zero_area += 1

    print(f"INFO: UV layer={layer.name!r}, loops={len(coords)}, polygons={len(mesh.polygons)}")
    print(f"INFO: UV bounds U[{min_u:.5f}, {max_u:.5f}] V[{min_v:.5f}, {max_v:.5f}]")
    print(f"{'WARN' if outside else 'PASS'}: coordinates outside 0-1 tile: {outside}")
    print(f"{'WARN' if zero_area else 'PASS'}: polygons with zero/negligible UV area: {zero_area}")
    if outside or zero_area:
        warnings.append(obj.name)
    print("INFO: UV overlap and texel density are not measured by this script; inspect a checker/material view.")
    print("INFO: UDIM or intentional tiling can legitimately extend beyond 0-1.")

print("\nUV validation complete. Read-only: no UVs, objects, or materials were changed.")
print("RESULT:", "INCOMPLETE - CHECK TARGETS OR UV LAYERS" if incomplete else
      "REVIEW WARNINGS" if warnings else "NO WARNINGS REPORTED")
