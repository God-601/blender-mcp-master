"""capability_probe.py — report Blender-side capabilities without modifying the scene."""
import bpy
import json

capabilities = {
    "blender_version": bpy.app.version_string,
    "python_version": __import__("sys").version.split()[0],
    "mesh": all(hasattr(bpy.data, attr) for attr in ("meshes", "objects", "collections")),
    "curves": hasattr(bpy.data, "curves"),
    "geometry_nodes": hasattr(bpy.data, "node_groups") and hasattr(bpy.types, "GeometryNodeTree"),
    "boolean_modifier": hasattr(bpy.types, "BooleanModifier"),
    "bevel_modifier": hasattr(bpy.types, "BevelModifier"),
    "bmesh": True,
    "visual_capture": False,
    "scene_save_available": hasattr(bpy.ops.wm, "save_as_mainfile"),
}
print("MCP_CAPABILITY_PROBE_BEGIN")
print(json.dumps(capabilities, indent=2, sort_keys=True))
print("MCP_CAPABILITY_PROBE_END")
print("visual_capture=false means use the active MCP visual inspection tool, if present.")
