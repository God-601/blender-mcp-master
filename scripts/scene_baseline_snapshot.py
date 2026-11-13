"""Read-only baseline of explicitly protected Blender objects.

Run before editing and after editing or reopening a saved copy. Capture the JSON
between markers outside Blender and compare with scripts/compare_scene_baselines.py.
"""
from array import array
import hashlib
import json
import math
import sys

import bpy
from mathutils import Matrix

# ---- CONFIG: never scan or mutate an unnamed whole scene -------------------
TARGET_NAMES = []  # Example: ["USER_Keep_Mesh", "USER_Keep_Light", "Camera"]
MAX_TARGETS = 100
# ---------------------------------------------------------------------------
SCHEMA_VERSION = 2
SCOPE = "explicit_protected_objects_selected_properties"
PROTECTION_LIMITS = (
    "Only explicit TARGET_NAMES; scene globals and unnamed objects are outside this comparison.",
    "External asset bytes, evaluated geometry, simulation caches and render output are outside this comparison.",
    "Referenced datablocks are checked by identity unless captured explicitly; specialized nested node, modifier and datablock settings are only partially covered.",
    "Embedded image coverage is limited to readable single-buffer images of up to 67,108,864 pixel samples.",
)
MAX_IMAGE_SAMPLES = 67_108_864  # One 4096 × 4096 RGBA float buffer.


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


def numeric_digest(values):
    if sys.byteorder != "little":
        values.byteswap()
    return hashlib.sha256(values).hexdigest()


def collection_digest(collection, property_name, typecode, width=1):
    values = array(typecode, [0]) * (len(collection) * width)
    if values:
        try:
            collection.foreach_get(property_name, values)
        except (AttributeError, TypeError, RuntimeError, ValueError):
            if width == 1:
                values = array(typecode, (getattr(item, property_name) for item in collection))
            else:
                values = array(typecode, (value for item in collection
                                           for value in getattr(item, property_name)))
    return numeric_digest(values)


def id_reference(block):
    if block is None:
        return None
    return {
        "name": block.name_full,
        "type": block.bl_rna.identifier,
        "library": block.library.filepath if block.library else None,
    }


def custom_value(value):
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, bpy.types.ID):
        return id_reference(value)
    if hasattr(value, "keys"):
        return {key: custom_value(value[key]) for key in value.keys()}
    if isinstance(value, (list, tuple)) or hasattr(value, "to_list"):
        return [custom_value(item) for item in value]
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    raise ValueError("Unsupported custom property value: " + type(value).__name__)


def custom_properties(block):
    try:
        keys = block.keys()
    except (AttributeError, TypeError):
        # Some bpy_struct types do not support ID properties.
        return {}
    return {key: custom_value(block[key]) for key in keys}


def serialize_socket_value(value):
    if isinstance(value, (float, int, bool, str)):
        return finite_float(value) if isinstance(value, float) else value
    if isinstance(value, bpy.types.ID):
        return id_reference(value)
    try:
        return vec(value)
    except (TypeError, ValueError):
        return None


def scalar_properties(block):
    """Writable scalar RNA properties. Collections need explicit capture."""
    output = {}
    for prop in block.bl_rna.properties:
        if (prop.is_readonly or prop.identifier in {"tag", "dimensions"}
                or prop.type not in {"BOOLEAN", "INT", "FLOAT", "STRING", "ENUM"}):
            continue
        if (prop.identifier == "use_nodes" and isinstance(block, bpy.types.Material)
                and bpy.app.version >= (5, 0, 0)):
            continue
        value = getattr(block, prop.identifier)
        if isinstance(value, set):
            value = sorted(value)
        elif isinstance(value, Matrix):
            value = [vec(row) for row in value]
        elif getattr(prop, "is_array", False):
            value = list(value)
        output[prop.identifier] = value
    return output


def rna_signature(block):
    refs = {}
    for prop in block.bl_rna.properties:
        if prop.type == "POINTER" and not prop.is_readonly:
            value = getattr(block, prop.identifier)
            if isinstance(value, bpy.types.ID):
                refs[prop.identifier] = id_reference(value)
    return {"properties": scalar_properties(block), "references": refs,
            "custom_properties": custom_properties(block)}


def image_signature(image):
    packed_files = image.packed_files
    payload = {
        "id": id_reference(image), "filepath": image.filepath, "source": image.source,
        "colorspace": image.colorspace_settings.name, "alpha_mode": image.alpha_mode,
        "packed_sha256": [hashlib.sha256(file.packed_file.data).hexdigest() for file in packed_files],
    }
    if image.source != "GENERATED" and not packed_files and not image.is_dirty:
        return payload
    if image.source not in {"FILE", "GENERATED"} or image.is_multiview:
        raise ValueError("Unsupported embedded image source or multiple views: " + image.name)
    pixels = image.pixels
    count = len(pixels)
    if not count or count > MAX_IMAGE_SAMPLES:
        raise ValueError("Embedded image pixels unreadable or over the sample limit: " + image.name)
    values = array("f", [0]) * count
    pixels.foreach_get(values)
    payload["pixel_size"] = list(image.size)
    payload["pixels_sha256"] = numeric_digest(values)
    return payload


def node_tree_signature(tree, seen=None, images=None):
    if tree is None:
        return None
    seen = set() if seen is None else seen
    images = {} if images is None else images
    pointer = tree.as_pointer()
    if pointer in seen:
        return {"recursive_group": id_reference(tree)}
    seen.add(pointer)
    try:
        nodes = []
        for node in sorted(tree.nodes, key=lambda node: node.name):
            image = getattr(node, "image", None)
            if image is not None and image.as_pointer() not in images:
                images[image.as_pointer()] = image_signature(image)
            nodes.append({
                "name": node.name, "type": node.bl_idname,
                "properties": rna_signature(node),
                "image": images[image.as_pointer()] if image is not None else None,
                "group": node_tree_signature(getattr(node, "node_tree", None), seen, images),
                "inputs": [{"id": sock.identifier, "name": sock.name,
                            "value": serialize_socket_value(sock.default_value)}
                           for sock in node.inputs if hasattr(sock, "default_value")],
            })
        return {
            "name": tree.name, "nodes": nodes,
            "custom_properties": custom_properties(tree),
            "animation": animation_signature(tree),
            "links": sorted([[link.from_node.name, link.from_socket.identifier,
                              link.to_node.name, link.to_socket.identifier, link.is_muted]
                             for link in tree.links]),
        }
    finally:
        seen.remove(pointer)


def material_signature(mat, images):
    if mat is None:
        return None
    tree = mat.node_tree if bpy.app.version >= (5, 0, 0) or mat.use_nodes else None
    return {
        "id": id_reference(mat), "properties": rna_signature(mat),
        "animation": animation_signature(mat),
        "node_tree": node_tree_signature(tree, images=images),
    }


def constraint_signature(constraint):
    return {
        "type": constraint.type,
        "state": rna_signature(constraint),
        "targets": [rna_signature(target) for target in getattr(constraint, "targets", ())],
    }


def fcurve_signature(curve):
    driver = curve.driver
    return {
        "state": rna_signature(curve),
        "group": curve.group.name if curve.group else None,
        "keyframes": [scalar_properties(point) for point in curve.keyframe_points],
        "samples_sha256": collection_digest(curve.sampled_points, "co", "f", 2),
        "modifiers": [{"type": mod.type, "state": rna_signature(mod),
                       "control_points": [scalar_properties(point)
                                          for point in getattr(mod, "control_points", ())]}
                      for mod in curve.modifiers],
        "driver": {
            "state": scalar_properties(driver),
            "variables": [{"state": scalar_properties(variable),
                           "targets": [rna_signature(target) for target in variable.targets]}
                          for variable in driver.variables],
        } if driver else None,
    }


def action_signature(action, cache):
    if action is None:
        return None
    pointer = action.as_pointer()
    if pointer in cache:
        return cache[pointer]
    state = {"id": id_reference(action), "state": rna_signature(action),
             "markers": [rna_signature(marker) for marker in action.pose_markers]}
    if getattr(action, "is_action_layered", False):
        state["slots"] = [{"handle": slot.handle, "identifier": slot.identifier,
                           "target_id_type": slot.target_id_type}
                          for slot in action.slots]
        state["layers"] = []
        for layer in action.layers:
            strips = []
            for strip in layer.strips:
                if strip.type != "KEYFRAME" or not hasattr(strip, "channelbags"):
                    raise ValueError("Unsupported layered action strip: " + action.name)
                strips.append({
                    "state": scalar_properties(strip),
                    "channels": [{"slot": bag.slot_handle,
                                  "groups": [rna_signature(group) for group in getattr(bag, "groups", ())],
                                  "curves": [fcurve_signature(curve) for curve in bag.fcurves]}
                                 for bag in strip.channelbags],
                })
            state["layers"].append({"state": scalar_properties(layer), "strips": strips})
    else:
        state["curves"] = [fcurve_signature(curve) for curve in action.fcurves]
        state["groups"] = [rna_signature(group) for group in action.groups]
    cache[pointer] = hash_payload(state)
    return cache[pointer]


def action_slot_identifier(owner):
    slot = getattr(owner, "action_slot", None)
    return slot.identifier if slot else None


def nla_strip_signature(strip, actions):
    return {
        "state": rna_signature(strip),
        "action": action_signature(strip.action, actions),
        "action_slot": action_slot_identifier(strip),
        "strips": [nla_strip_signature(child, actions) for child in strip.strips],
        "curves": [fcurve_signature(curve) for curve in strip.fcurves],
        "modifiers": [{"type": mod.type, "state": rna_signature(mod)} for mod in strip.modifiers],
    }


def animation_signature(block):
    animation = getattr(block, "animation_data", None)
    if animation is None:
        return None
    actions = {}
    return hash_payload({
        "state": rna_signature(animation),
        "action": action_signature(animation.action, actions),
        "action_slot": action_slot_identifier(animation),
        "drivers": [fcurve_signature(curve) for curve in animation.drivers],
        "nla_tracks": [{"state": rna_signature(track),
                        "strips": [nla_strip_signature(strip, actions) for strip in track.strips]}
                       for track in animation.nla_tracks],
    })


def shape_key_signature(keys):
    if keys is None:
        return None
    return {
        "state": rna_signature(keys), "animation": animation_signature(keys),
        "blocks": [{"state": rna_signature(key),
                    "relative_key": key.relative_key.name if key.relative_key else None,
                    "coordinates_sha256": collection_digest(key.data, "co", "f", 3),
                    "curve_points_sha256": {
                        prop.identifier: collection_digest(key.data, prop.identifier, "f",
                                                           prop.array_length if prop.is_array else 1)
                        for prop in key.data[0].bl_rna.properties
                        if prop.type == "FLOAT" and prop.identifier != "co"
                    } if len(key.data) else {}}
                   for key in keys.key_blocks],
    }


ATTRIBUTE_STORAGE = {
    "BOOLEAN": ("value", "b", 1),
    "INT8": ("value", "b", 1),
    "INT": ("value", "i", 1),
    "INT16_2D": ("value", "i", 2),
    "INT32_2D": ("value", "i", 2),
    "FLOAT": ("value", "f", 1),
    "FLOAT2": ("vector", "f", 2),
    "FLOAT_VECTOR": ("vector", "f", 3),
    "FLOAT_COLOR": ("color", "f", 4),
    "BYTE_COLOR": ("color_srgb", "f", 4),
    "QUATERNION": ("value", "f", 4),
    "FLOAT4X4": ("value", "f", 16),
}


def attribute_signature(attribute):
    if attribute.data_type == "STRING":
        digest = hash_payload([custom_value(item.value) for item in attribute.data])
    elif attribute.data_type in ATTRIBUTE_STORAGE:
        prop, typecode, width = ATTRIBUTE_STORAGE[attribute.data_type]
        if attribute.data_type == "BYTE_COLOR" and len(attribute.data) and not hasattr(attribute.data[0], prop):
            prop = "color"
        if attribute.data_type == "FLOAT4X4":
            digest = hash_payload([[vec(row) for row in item.value] for item in attribute.data])
        else:
            digest = collection_digest(attribute.data, prop, typecode, width)
    else:
        raise ValueError("Unsupported mesh attribute type: " + attribute.data_type)
    return {"name": attribute.name, "type": attribute.data_type, "domain": attribute.domain,
            "count": len(attribute.data), "data_sha256": digest}


def mesh_signature(mesh):
    properties = {
        "vertex_count": len(mesh.vertices),
        "vertex_coordinates_sha256": collection_digest(mesh.vertices, "co", "f", 3),
        "edges_sha256": collection_digest(mesh.edges, "vertices", "i", 2),
        "edge_flags": {prop: collection_digest(mesh.edges, prop, code)
                       for prop, code in (("use_seam", "b"), ("use_edge_sharp", "b"),
                                          ("crease", "f"), ("bevel_weight", "f"),
                                          ("use_freestyle_mark", "b"))
                       if len(mesh.edges) and hasattr(mesh.edges[0], prop)},
        "face_vertices_sha256": collection_digest(mesh.loops, "vertex_index", "i"),
        "face_sizes_sha256": collection_digest(mesh.polygons, "loop_total", "i"),
        "face_materials_sha256": collection_digest(mesh.polygons, "material_index", "i"),
        "face_smooth_sha256": collection_digest(mesh.polygons, "use_smooth", "b"),
        "uv_layers": [
            {"name": layer.name, "active": layer == mesh.uv_layers.active,
             "active_render": layer.active_render, "active_clone": layer.active_clone,
             "uv_sha256": collection_digest(layer.data, "uv", "f", 2)}
            for layer in mesh.uv_layers
        ],
        "attributes": [attribute_signature(attribute) for attribute in mesh.attributes
                       if attribute.name not in {"position", ".edge_verts", ".corner_vert", ".corner_edge",
                                                 "material_index", "sharp_face", "sharp_edge", ".uv_seam"}],
        "shape_keys": shape_key_signature(mesh.shape_keys),
        "has_custom_normals": mesh.has_custom_normals,
    }
    if not hasattr(mesh, "color_attributes"):
        properties["vertex_colors"] = [
            {"name": layer.name, "active": layer == mesh.vertex_colors.active,
             "active_render": layer.active_render,
             "data_sha256": collection_digest(layer.data, "color", "f", 4)}
            for layer in mesh.vertex_colors
        ]
    if mesh.has_custom_normals:
        if hasattr(mesh, "corner_normals"):
            normals, prop = mesh.corner_normals, "vector"
        else:
            # Blender 3.x exposes split normals through the derived loop cache.
            mesh.calc_normals_split()
            normals, prop = mesh.loops, "normal"
        properties["split_normals_sha256"] = collection_digest(normals, prop, "f", 3)
    return properties


def vertex_groups_signature(obj):
    groups = obj.vertex_groups
    return {
        "groups": [scalar_properties(group) for group in groups],
        "active_index": groups.active_index,
        "weights_sha256": hash_payload([
            [vertex.index, [[entry.group, entry.weight] for entry in vertex.groups]]
            for vertex in obj.data.vertices if len(vertex.groups)
        ]) if groups and obj.type == "MESH" else None,
    }


def curve_signature(curve):
    return {
        "splines": [{"state": scalar_properties(spline),
                     "points": [scalar_properties(point) for point in spline.points],
                     "bezier_points": [scalar_properties(point) for point in spline.bezier_points]}
                    for spline in curve.splines],
        "shape_keys": shape_key_signature(curve.shape_keys),
    }


def armature_signature(obj):
    return {
        "bones": [
            {"state": rna_signature(bone), "parent": bone.parent.name if bone.parent else None,
             "head": vec(bone.head_local), "tail": vec(bone.tail_local),
             "matrix": [vec(row) for row in bone.matrix_local]}
            for bone in obj.data.bones
        ],
        "pose": [
            {"state": rna_signature(bone),
             "constraints": [constraint_signature(constraint) for constraint in bone.constraints]}
            for bone in obj.pose.bones
        ],
    }


def capture_object(obj):
    if obj.type not in {"ARMATURE", "CAMERA", "CURVE", "EMPTY", "FONT", "LIGHT", "MESH", "SURFACE"}:
        raise ValueError("Unsupported protected object type: " + obj.type)
    if obj.mode == "EDIT":
        raise ValueError("Protected object must leave Edit Mode before capture")
    images = {}
    props = {
        "name": obj.name, "type": obj.type, "state": rna_signature(obj),
        "collections": sorted(col.name for col in obj.users_collection),
        "parent": id_reference(obj.parent),
        "matrix_world": [vec(row) for row in obj.matrix_world],
        "matrix_parent_inverse": [vec(row) for row in obj.matrix_parent_inverse],
        "material_slots": [{"link": slot.link, "material": id_reference(slot.material)}
                           for slot in obj.material_slots],
        "materials": [material_signature(slot.material, images) for slot in obj.material_slots],
        "modifiers": [{"type": mod.type, "state": rna_signature(mod),
                       "node_tree": node_tree_signature(getattr(mod, "node_group", None), images=images)}
                      for mod in obj.modifiers],
        "constraints": [constraint_signature(constraint) for constraint in obj.constraints],
        "animation": animation_signature(obj),
    }
    if obj.data is not None:
        props["data"] = {"id": id_reference(obj.data), "state": rna_signature(obj.data),
                         "animation": animation_signature(obj.data)}
    if obj.type == "MESH":
        props["mesh_sha256"] = hash_payload(mesh_signature(obj.data))
        props["vertex_groups"] = vertex_groups_signature(obj)
    elif obj.type in {"CURVE", "FONT", "SURFACE"}:
        props["curve_sha256"] = hash_payload(curve_signature(obj.data))
    elif obj.type == "ARMATURE":
        props["armature_sha256"] = hash_payload(armature_signature(obj))
    elif obj.type == "EMPTY" and isinstance(obj.data, bpy.types.Image):
        props["image"] = image_signature(obj.data)
    elif obj.type == "LIGHT":
        props["node_tree"] = node_tree_signature(getattr(obj.data, "node_tree", None), images=images)
    return {"name": obj.name, "type": obj.type,
            "fingerprint_sha256": hash_payload(props), "properties": props}


def main():
    output = {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "blender_version": bpy.app.version_string,
        "source_blend_file": bpy.data.filepath or None,
        "scene": bpy.context.scene.name if bpy.context.scene else None,
        "status": "NOT VERIFIED",
        "objects": [],
        "missing_names": [],
        "errors": [],
        "limitations": list(PROTECTION_LIMITS),
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
