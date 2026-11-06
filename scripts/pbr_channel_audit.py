"""Read-only PBR image/node/UV audit for explicitly named mesh targets.

Technical hints only. A shader graph can be complex; this does not simulate
cycles, bake textures or certify color and appearance in a game engine.
"""
import bpy
import json
import math
import os

TARGETS = []
MAX_TARGETS = 25
MAX_NODES = 500
MAX_IMAGES = 100
EXPECTED_CHANNELS = ("base_color", "roughness", "metallic", "normal")
COLOR_SOCKET_MAP = {
    "Base Color": "base_color",
    "Roughness": "roughness",
    "Metallic": "metallic",
}
NORMAL_COLORSPACES = ("Non-Color", "Non-Colour", "Raw")


def _colorspace(image):
    try:
        return str(image.colorspace_settings.name)
    except (AttributeError, RuntimeError, ValueError):
        return "NOT VERIFIED"


def audit_material(material):
    result = {
        "material": material.name,
        "status": "NOT VERIFIED",
        "channels": {},
        "texture_images": [],
        "engine_rendering": "NOT VERIFIED",
        "bake_quality": "NOT VERIFIED",
        "warnings": [],
    }
    if not material.use_nodes or not material.node_tree:
        result["warnings"].append("Material has no inspectable node graph")
        return result
    nodes = material.node_tree.nodes
    if len(nodes) > MAX_NODES:
        result["warnings"].append("Node count exceeds read-only audit cap")
        return result
    bsdfs = [n for n in nodes if n.type == "BSDF_PRINCIPLED"]
    if len(bsdfs) != 1:
        result["warnings"].append("Expected exactly one Principled BSDF; ambiguous graph")
        return result
    bsdf = bsdfs[0]
    for socket in bsdf.inputs:
        name = COLOR_SOCKET_MAP.get(socket.name)
        if name is None and socket.name == "Normal":
            name = "normal"
        if name is None:
            continue
        connections = list(socket.links)
        report = {"linked": bool(connections), "colorspace": "NOT VERIFIED",
                  "source": "NOT VERIFIED", "status": "NOT VERIFIED"}
        if len(connections) == 1:
            upstream = connections[0].from_node
            if name == "normal" and upstream.type == "NORMAL_MAP":
                normal_links = list(upstream.inputs.get("Color").links) if upstream.inputs.get("Color") else []
                if len(normal_links) == 1:
                    upstream = normal_links[0].from_node
            if upstream.type == "TEX_IMAGE" and upstream.image:
                img = upstream.image
                space = _colorspace(img)
                path = bpy.path.abspath(img.filepath) if img.filepath else ""
                available = bool(img.packed_file) or (img.source == "FILE" and bool(path) and os.path.isfile(path))
                report.update({"source": img.name, "colorspace": space,
                               "packed": bool(img.packed_file),
                               "external_file_present": bool(available),
                               "status": "REVIEW" if available else "ISSUE"})
                expected_noncolor = name != "base_color"
                if expected_noncolor and space not in NORMAL_COLORSPACES:
                    report["status"] = "ISSUE"
                    result["warnings"].append(name + " image appears to use color/sRGB interpretation")
                if not expected_noncolor and space in NORMAL_COLORSPACES:
                    result["warnings"].append("Base color image marked as data/non-color")
                    report["status"] = "REVIEW"
                if len(result["texture_images"]) < MAX_IMAGES:
                    result["texture_images"].append({"name": img.name, "colorspace": space,
                                                       "packed": bool(img.packed_file),
                                                       "external_file_present": available,
                                                       "dimensions": list(img.size)})
            else:
                result["warnings"].append(name + " uses procedural/unsupported or absent texture")
        result["channels"][name] = report
    status_values = {v["status"] for v in result["channels"].values()}
    result["status"] = ("ISSUE" if "ISSUE" in status_values else
                        "REVIEW" if result["channels"] else "NOT VERIFIED")
    return result


def inspect_targets(names):
    output = {"status": "NOT VERIFIED", "targets": [], "actual_bake": "NOT VERIFIED",
              "in_engine_material_fidelity": "NOT VERIFIED", "source_scene_mutated": False,
              "limitations": ["Node paths can include groups/mixers not resolved by this lightweight audit.",
                              "Colorspace hints are not evidence of shader fidelity.",
                              "UV presence, files and shader links do not prove any texture bake succeeded."]}
    if (not isinstance(names, list) or not 1 <= len(names) <= MAX_TARGETS
            or any(not isinstance(n, str) or not n.strip() for n in names)
            or len(set(names)) != len(names)):
        output["error"] = "Provide 1..25 unique explicit mesh names"
        return output
    for name in names:
        target = bpy.data.objects.get(name)
        if target is None or target.type != "MESH":
            output["targets"].append({"name": name, "status": "NOT VERIFIED", "reason": "Mesh not found"})
            continue
        mats = [slot.material for slot in target.material_slots if slot.material]
        report = {"name": name, "uv_layers": len(target.data.uv_layers),
                  "materials": [audit_material(mat) for mat in mats],
                  "status": "NOT VERIFIED"}
        if report["uv_layers"] == 0:
            report["status"] = "ISSUE"
            report["reason"] = "Mesh has no UV layer"
        elif not mats:
            report["status"] = "NOT VERIFIED"
            report["reason"] = "No assigned material"
        elif any(m["status"] == "ISSUE" for m in report["materials"]):
            report["status"] = "ISSUE"
        elif all(m["status"] == "REVIEW" for m in report["materials"]):
            report["status"] = "REVIEW"
        output["targets"].append(report)
    if any(x["status"] == "ISSUE" for x in output["targets"]):
        output["status"] = "ISSUE"
    elif all(x["status"] == "REVIEW" for x in output["targets"]):
        output["status"] = "REVIEW"
    return output


if __name__ == "__main__":
    print("MCP_PBR_AUDIT_BEGIN")
    print(json.dumps(inspect_targets(TARGETS), indent=2, sort_keys=True))
    print("MCP_PBR_AUDIT_END")
