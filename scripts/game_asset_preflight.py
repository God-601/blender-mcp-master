"""Read-only Blender game-asset export preflight, not an engine certification.

Checks named static mesh objects for evaluated triangle budgets, world-space
size, origin, UV presence, material texture image dependencies, transforms
and asset organization. Does not create exports, alter user meshes, or claim
an actual Roblox/Unity/Godot/Unreal engine import succeeded.
"""
import bpy
import json
import math
import os

# ---- Explicit user/project configuration -----------------------------------
TARGETS = []  # Explicit mesh names; no selection/scene fallback.
ENGINE = "GENERIC"  # ROBLOX / UNITY / GODOT / UNREAL / GENERIC
MAX_EVALUATED_TRIANGLES = 5000   # project budget, NOT an engine hard cap
MAX_MATERIAL_SLOTS = 4          # project budget, not draw-call count
REQUIRE_UV = True
REQUIRE_IMAGE_FILES = False     # use for image-textured deliverables
MAX_TARGETS = 25
MAX_EVALUATED_VERTICES = 250000
# -----------------------------------------------------------------------------


def _images(obj):
    images = []
    missing = []
    seen = set()
    for slot in obj.material_slots:
        material = slot.material
        if not material or not material.use_nodes or not material.node_tree:
            continue
        for node in material.node_tree.nodes:
            if node.type != "TEX_IMAGE" or not node.image:
                continue
            img = node.image
            if img.as_pointer() in seen:
                continue
            seen.add(img.as_pointer())
            raw = str(img.filepath or "")
            packed = bool(img.packed_file)
            exists = False
            if raw:
                try:
                    exists = os.path.isfile(bpy.path.abspath(raw))
                except (OSError, ValueError):
                    exists = False
            if img.source != "FILE":
                availability = "NON_FILE_IMAGE_REVIEW"
            elif packed:
                availability = "PACKED"
            elif exists:
                availability = "EXISTS"
            else:
                availability = "MISSING_FILE"
                missing.append(img.name)
            images.append({
                "name": img.name, "source": img.source,
                "size": [int(x) for x in img.size],
                "availability": availability,
                "packed": packed,
            })
    return images, missing


def inspect(obj, depsgraph):
    report = {"name": obj.name, "status": "NOT VERIFIED",
              "in_engine_import": "NOT VERIFIED",
              "actual_draw_calls": "NOT VERIFIED",
              "actual_fps": "NOT VERIFIED",
              "rendered_material_fidelity": "NOT VERIFIED"}
    if obj.type != "MESH" or obj.mode != "OBJECT":
        report["reason"] = "Target must be a mesh in Object Mode"
        return report
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    if mesh is None:
        report["reason"] = "Evaluated mesh unavailable"
        return report
    try:
        if not 3 <= len(mesh.vertices) <= MAX_EVALUATED_VERTICES:
            report["reason"] = "Evaluated vertex count outside safe audit limits"
            return report
        mesh.calc_loop_triangles()
        verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        if not verts or any(not all(math.isfinite(float(v[i])) for i in range(3)) for v in verts):
            report["reason"] = "Nonfinite or missing evaluated vertices"
            return report
        bounds = [[min(float(v[i]) for v in verts), max(float(v[i]) for v in verts)] for i in range(3)]
        spans = [b[1] - b[0] for b in bounds]
        images, missing = _images(obj)
        tris = len(mesh.loop_triangles)
        uv_layers = len(mesh.uv_layers)
        materials = sum(slot.material is not None for slot in obj.material_slots)
        warnings = []
        issues = []
        if tris > MAX_EVALUATED_TRIANGLES:
            issues.append("evaluated triangle count exceeds project budget")
        if REQUIRE_UV and uv_layers == 0:
            issues.append("no evaluated UV map")
        if REQUIRE_IMAGE_FILES and missing:
            issues.append("missing source texture image file(s): " + ", ".join(sorted(missing)))
        elif missing:
            warnings.append("missing linked texture file(s), inspect before engine import")
        if materials > MAX_MATERIAL_SLOTS:
            warnings.append("material-slot budget exceeded (not exact draw-call count)")
        scale = [float(v) for v in obj.scale]
        if any(abs(value - 1.0) > 1e-5 for value in scale):
            warnings.append("object scale differs from unity; verify engine import scale/pivot")
        if any(dimension < 1e-8 for dimension in spans):
            warnings.append("degenerate world-space dimension; review intended flat geometry")
        report.update({
            "status": "ISSUE" if issues else "REVIEW" if warnings else "MEASURED",
            "scene_unit_scale_length": float(bpy.context.scene.unit_settings.scale_length),
            "evaluated_triangles": tris,
            "project_triangle_budget": MAX_EVALUATED_TRIANGLES,
            "evaluated_vertices": len(mesh.vertices),
            "world_aabb_xyz": [[round(v, 6) for v in pair] for pair in bounds],
            "world_extent_xyz": [round(v, 6) for v in spans],
            "origin_world": [round(float(v), 6) for v in obj.matrix_world.translation],
            "object_scale": [round(v, 6) for v in scale],
            "evaluated_uv_layers": uv_layers,
            "material_slots": len(obj.material_slots),
            "assigned_material_slots": materials,
            "texture_images": images,
            "warnings": warnings, "issues": issues,
        })
    finally:
        evaluated.to_mesh_clear()
    return report


def main():
    result = {
        "blender_version": bpy.app.version_string,
        "target_engine": ENGINE,
        "overall": "NOT VERIFIED",
        "objects": [],
        "engine_test": "NOT VERIFIED",
        "in_engine_materials": "NOT VERIFIED",
        "collision_and_lod": "NOT VERIFIED",
        "source_scene_mutated": False,
        "limitations": [
            "Budgets are authored project goals, not official engine limits.",
            "An evaluated mesh / available texture file does not prove game-engine import.",
            "Only explicitly selected static meshes are measured; rigs and animation need another export workflow.",
            "For actual engine validity inspect the imported asset, pivot, scale, normals, UVs, materials, collision and LOD in the destination.",
        ],
    }
    if ENGINE not in {"ROBLOX", "UNITY", "GODOT", "UNREAL", "GENERIC"}:
        result["error"] = "Unsupported target engine"
    elif (not isinstance(TARGETS, list) or not 1 <= len(TARGETS) <= MAX_TARGETS or
          len(TARGETS) != len(set(TARGETS)) or
          any(not isinstance(x, str) or not x.strip() for x in TARGETS)):
        result["error"] = "Provide unique explicit TARGETS (1..25)"
    elif not isinstance(MAX_EVALUATED_TRIANGLES, int) or MAX_EVALUATED_TRIANGLES <= 0 or not isinstance(MAX_MATERIAL_SLOTS, int) or MAX_MATERIAL_SLOTS < 1:
        result["error"] = "Project budgets must be positive integers"
    else:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        for name in TARGETS:
            obj = bpy.data.objects.get(name)
            if obj is None:
                result["objects"].append({"name": name, "status": "NOT VERIFIED", "reason": "Missing target"})
            else:
                try:
                    result["objects"].append(inspect(obj, depsgraph))
                except Exception as exc:
                    result["objects"].append({"name": name, "status": "NOT VERIFIED", "reason": str(exc)})
        states = {x["status"] for x in result["objects"]}
        result["overall"] = ("NOT VERIFIED" if "NOT VERIFIED" in states else
                             "ISSUE" if "ISSUE" in states else
                             "REVIEW" if "REVIEW" in states else "MEASURED")
    print("MCP_GAME_PREFLIGHT_BEGIN")
    print(json.dumps(result, indent=2, sort_keys=True))
    print("MCP_GAME_PREFLIGHT_END")


if __name__ == "__main__":
    main()
