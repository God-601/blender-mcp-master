"""Read-only, explicit-target Blender asset performance audit.

Measures *evaluated* triangles, material slots, shared mesh datablocks,
rough unique RGBA8 image footprint, and highlights budget exceedances.
It does not run a game, measure draw calls/FPS, rewrite meshes, optimize, or
prove shading/UV quality. Compatible with Blender's bpy runtime.
"""
import bpy
import json

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []  # Explicit mesh object names ONLY; never use selection/scene fallback.
MAX_EVALUATED_TRIS = 5000  # Project target, not an engine/platform hard limit.
MAX_MATERIAL_SLOTS = 2
MAX_TEXTURE_PX = 2048
MAX_TARGETS = 25
# ----------------------------------------------------------------------------

def _tris(mesh):
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def _textures(obj):
    """Return accessible image references without loading pixels."""
    found = {}
    for slot in obj.material_slots:
        mat = slot.material
        if mat is None or not mat.use_nodes or not mat.node_tree:
            continue
        for node in mat.node_tree.nodes:
            if node.type == "TEX_IMAGE" and node.image:
                image = node.image
                width, height = (int(v) for v in image.size)
                if width <= 0 or height <= 0:
                    continue
                ident = image.as_pointer()
                found[ident] = {
                    "name": image.name,
                    "width": width, "height": height,
                    # Only an illustrative uncompressed RGBA8 level-0 footprint.
                    "estimated_rgba8_bytes": width * height * 4,
                }
    return found


def _audit():
    report = {
        "status": "NOT VERIFIED",
        "assets": [],
        "errors": [],
        "total_evaluated_triangles": 0,
        "unique_base_mesh_datablocks": 0,
        "referenced_texture_count": 0,
        "estimated_unique_rgba8_bytes_without_mipmaps": 0,
        "fps_measurement": "NOT VERIFIED",
        "draw_calls": "NOT VERIFIED",
        "visual_quality": "NOT VERIFIED",
        "limits": [
            "Budgets are user/project targets, not verified engine hard limits.",
            "Evaluated triangle totals are per object; shared/instanced scene runtime cost differs.",
            "Material slots are not exact draw calls, and memory estimate is only RGBA8 level 0.",
            "No texture sampling cost, actual VRAM, performance timings or artistic quality were measured.",
        ],
    }
    if not isinstance(TARGETS, list) or not TARGETS or len(TARGETS) > MAX_TARGETS:
        report["errors"].append("Provide 1..25 explicit TARGETS; no selection fallback")
        return report
    if any(not isinstance(name, str) or not name.strip() for name in TARGETS):
        report["status"] = "INCOMPLETE"
        report["errors"].append("Every target must be a nonempty object name")
        return report
    if len(TARGETS) != len(set(TARGETS)):
        report["status"] = "INCOMPLETE"
        report["errors"].append("Duplicate names in TARGETS; refusing to inflate measured totals")
        return report
    if (not isinstance(MAX_EVALUATED_TRIS, int) or MAX_EVALUATED_TRIS <= 0
            or not isinstance(MAX_MATERIAL_SLOTS, int) or MAX_MATERIAL_SLOTS <= 0
            or not isinstance(MAX_TEXTURE_PX, int) or MAX_TEXTURE_PX <= 0):
        report["status"] = "INCOMPLETE"
        report["errors"].append("Budgets must be positive integers")
        return report
    graph = bpy.context.evaluated_depsgraph_get()
    unique_meshes = set()
    unique_images = {}
    for name in TARGETS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            report["errors"].append({"name": name, "issue": "missing target"})
            continue
        if obj.type != "MESH":
            report["errors"].append({"name": name, "issue": "object is not a mesh"})
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        if mesh is None:
            report["errors"].append({"name": name, "issue": "evaluated mesh unavailable"})
            continue
        try:
            base_tris = _tris(obj.data)
            final_tris = _tris(mesh)
            mats = len(obj.material_slots)
            textures = _textures(obj)
            unique_images.update(textures)
            shared = obj.data.users > 1
            unique_meshes.add(obj.data.as_pointer())
            warnings = []
            recommendations = []
            if final_tris > MAX_EVALUATED_TRIS:
                warnings.append("evaluated triangle target exceeded")
                recommendations.append(
                    "Try a copy-first Decimate/LOD prototype; inspect silhouette, topology and UVs before approval."
                )
            if mats > MAX_MATERIAL_SLOTS:
                warnings.append("material-slot target exceeded")
                recommendations.append(
                    "Review reusable materials/atlases; slots are only a draw-call risk indicator."
                )
            large = [t["name"] for t in textures.values()
                     if max(t["width"], t["height"]) > MAX_TEXTURE_PX]
            if large:
                warnings.append("texture dimension target exceeded: " + ", ".join(sorted(large)))
                recommendations.append(
                    "Consider smaller packed textures or atlas; compare texture quality at target viewing distance."
                )
            if shared:
                recommendations.append(
                    "Shared mesh data already saves source-data duplication; do not make unique without reason."
                )
            item = {
                "name": obj.name,
                "base_triangles": base_tris,
                "evaluated_triangles": final_tris,
                "material_slots": mats,
                "modifier_count": len(obj.modifiers),
                "shared_mesh_data": shared,
                "image_textures": sorted(textures.values(), key=lambda x: x["name"]),
                "budget_status": "ISSUE" if warnings else "PASS",
                "warnings": warnings,
                "recommendations": recommendations,
                "visual_quality": "NOT VERIFIED",
            }
            report["assets"].append(item)
            report["total_evaluated_triangles"] += final_tris
        except Exception as exc:
            report["errors"].append({"name": name, "issue": str(exc)})
        finally:
            evaluated.to_mesh_clear()
    report["unique_base_mesh_datablocks"] = len(unique_meshes)
    report["referenced_texture_count"] = len(unique_images)
    report["estimated_unique_rgba8_bytes_without_mipmaps"] = sum(
        item["estimated_rgba8_bytes"] for item in unique_images.values()
    )
    report["status"] = "INCOMPLETE" if report["errors"] else (
        "MEASURED" if report["assets"] else "NOT VERIFIED"
    )
    return report


def main():
    print("MCP_PERFORMANCE_AUDIT_BEGIN")
    print(json.dumps(_audit(), sort_keys=True, indent=2))
    print("MCP_PERFORMANCE_AUDIT_END")


if __name__ == "__main__":
    main()
