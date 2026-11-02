"""Read-only baseline of explicitly protected Blender objects.

Run once BEFORE model mutations and once AFTER (or after reopening a saved copy).
Capture the JSON between markers outside Blender. Compare with
scripts/compare_scene_baselines.py. These are *selected-property* fingerprints,
not a guarantee of byte-identical .blend files or all Blender settings.
"""
import bpy
import hashlib
import json
import math

# ---- CONFIG: never scan or mutate an unnamed whole scene -------------------
TARGET_NAMES = []  # Example: ["USER_Keep_Mesh", "USER_Keep_Light", "Camera"]
MAX_TARGETS = 100
# -----------------------------------------------------------------------------


def finite_float(value):
    x = float(value)
    if not math.isfinite(x):
        raise ValueError("non-finite protected property")
    return x


def vec(value):
    return [finite_float(x) for x in value]


def hash_payload(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                   allow_nan=False).encode("utf-8")).hexdigest()


def serialize_socket_value(value):
    if isinstance(value, (float, int, bool, str)):
        return finite_float(value) if isinstance(value, float) else value
    try:
        return vec(value)
    except (TypeError, ValueError):
        return None


def material_signature(mat):
    if mat is None:
        return None
    properties = {
        "name": mat.name, "library": mat.library.filepath if mat.library else None,
        "diffuse_color": vec(mat.diffuse_color),
        "use_nodes": bool(mat.use_nodes),
        "blend_method": str(mat.blend_method),
    }
    if mat.use_nodes and mat.node_tree:
        properties["nodes"] = sorted(
            [{"name": node.name, "type": node.bl_idname,
              "inputs": [{"name": sock.name, "value": serialize_socket_value(sock.default_value)}
                         for sock in node.inputs if hasattr(sock, "default_value")]}
             for node in mat.node_tree.nodes], key=lambda node: node["name"])
        properties["links"] = sorted(
            [[link.from_node.name, link.from_socket.name,
              link.to_node.name, link.to_socket.name]
             for link in mat.node_tree.links])
    # Partial material fingerprint: procedural image contents and some arbitrary
    # node properties are out of scope. Do not claim full .blend equality.
    return properties


def mesh_signature(mesh):
    return {
        "vertex_coordinates": [vec(vertex.co) for vertex in mesh.vertices],
        "edges": [list(edge.vertices) for edge in mesh.edges],
        "faces": [
            {"vertices": list(face.vertices), "material_index": int(face.material_index),
             "use_smooth": bool(face.use_smooth)}
            for face in mesh.polygons
        ],
        "uv_layers": [
            {"name": layer.name, "active": layer == mesh.uv_layers.active,
             "uv": [vec(loop.uv) for loop in layer.data]}
            for layer in mesh.uv_layers
        ],
        "shape_keys": (
            [{"name": key.name, "coordinates": [vec(v.co) for v in key.data]}
             for key in mesh.shape_keys.key_blocks]
            if mesh.shape_keys else []
        ),
    }


def capture_object(obj):
    props = {
        "name": obj.name, "type": obj.type,
        "collections": sorted(col.name for col in obj.users_collection),
        "parent": obj.parent.name if obj.parent else None,
        "matrix_world": [vec(row) for row in obj.matrix_world],
        "matrix_parent_inverse": [vec(row) for row in obj.matrix_parent_inverse],
        "location": vec(obj.location), "scale": vec(obj.scale),
        "rotation_mode": obj.rotation_mode,
        "rotation_euler": vec(obj.rotation_euler),
        "rotation_quaternion": vec(obj.rotation_quaternion),
        "hide_render": bool(obj.hide_render), "hide_viewport": bool(obj.hide_viewport),
        "hide_select": bool(obj.hide_select),
        "material_slots": [slot.material.name if slot.material else None
                           for slot in obj.material_slots],
        "materials": [material_signature(slot.material)
                      for slot in obj.material_slots],
        "modifiers": [{"name": mod.name, "type": mod.type,
                       "show_viewport": bool(mod.show_viewport),
                       "show_render": bool(mod.show_render)}
                      for mod in obj.modifiers],
    }
    if obj.type == "MESH":
        props["mesh_sha256"] = hash_payload(mesh_signature(obj.data))
    elif obj.type == "LIGHT":
        props["light"] = {"type": obj.data.type, "energy": finite_float(obj.data.energy),
                          "color": vec(obj.data.color),
                          "shadow_soft_size": finite_float(obj.data.shadow_soft_size)}
    elif obj.type == "CAMERA":
        props["camera"] = {"type": obj.data.type,
                           "lens": finite_float(obj.data.lens),
                           "clip_start": finite_float(obj.data.clip_start),
                           "clip_end": finite_float(obj.data.clip_end),
                           "shift_x": finite_float(obj.data.shift_x),
                           "shift_y": finite_float(obj.data.shift_y)}
    return {"name": obj.name, "type": obj.type,
            "fingerprint_sha256": hash_payload(props),
            "properties": props}


def main():
    output = {
        "schema_version": 1,
        "scope": "explicit_protected_objects_selected_properties",
        "blender_version": bpy.app.version_string,
        "source_blend_file": bpy.data.filepath or None,
        "scene": bpy.context.scene.name if bpy.context.scene else None,
        "status": "NOT VERIFIED",
        "objects": [],
        "missing_names": [],
        "errors": [],
        "limitations": [
            "Only explicit TARGET_NAMES; scene-global settings and unnamed objects are not audited.",
            "Material nodes and modifiers are partially represented; no complete .blend comparison.",
            "Printout must be archived outside Blender before risky operations or a crash.",
            "A before snapshot must be paired with an after snapshot of the same protected names.",
        ],
    }
    if (not isinstance(TARGET_NAMES, list) or not TARGET_NAMES
            or len(TARGET_NAMES) > MAX_TARGETS
            or any(not isinstance(name, str) or not name.strip() for name in TARGET_NAMES)
            or len(set(TARGET_NAMES)) != len(TARGET_NAMES)):
        output["errors"].append("Specify unique, nonempty explicit TARGET_NAMES (1..100)")
    else:
        for name in TARGET_NAMES:
            obj = bpy.data.objects.get(name)
            if obj is None:
                output["missing_names"].append(name)
                continue
            try:
                output["objects"].append(capture_object(obj))
            except Exception as exc:
                output["errors"].append(name + ": " + str(exc))
        if not output["missing_names"] and not output["errors"]:
            output["status"] = "MEASURED"
    print("MCP_SCENE_BASELINE_BEGIN")
    print(json.dumps(output, sort_keys=True, indent=2, ensure_ascii=False))
    print("MCP_SCENE_BASELINE_END")


if __name__ == "__main__":
    main()
