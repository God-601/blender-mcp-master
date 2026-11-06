"""Disposable Blender-authored GLB fixture for *real* Godot import CI.

Requires bpy 4.5.x. Creates a new empty CI scene, a UV-mapped cube and one
simple PBR material; writes a fresh explicit path. Never touches user files.
"""
import argparse
import json
import os
import sys
from pathlib import Path


def generate(path):
    target = Path(path).resolve()
    if target.suffix.lower() != ".glb" or not target.parent.is_dir():
        raise ValueError("Require an absolute/relative .glb path in an existing directory")
    if target.exists():
        raise FileExistsError("Refusing to overwrite existing fixture")
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
    cube = bpy.context.object
    cube.name = "BlenderGodotCI_Cube"
    mesh = cube.data
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    layer = mesh.uv_layers.active
    for polygon in mesh.polygons:
        for loop_index in polygon.loop_indices:
            point = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            layer.data[loop_index].uv = ((point.x + 0.5), (point.y + 0.5))
    material = bpy.data.materials.new(name="CI_Material")
    material.use_nodes = True
    principled = material.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (0.3, 0.6, 0.9, 1.0)
    mesh.materials.append(material)
    bpy.ops.object.select_all(action="DESELECT")
    cube.select_set(True)
    bpy.context.view_layer.objects.active = cube
    bpy.ops.export_scene.gltf(filepath=str(target), export_format="GLB",
                              use_selection=True)
    if not target.is_file() or target.stat().st_size < 100:
        raise RuntimeError("Blender GLB exporter produced no valid file")
    return {"source": "bpy evaluated static mesh", "file": str(target),
            "bytes": target.stat().st_size, "blender": bpy.app.version_string}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination")
    args = parser.parse_args()
    result = generate(args.destination)
    print(json.dumps(result, sort_keys=True), flush=True)
    # Blender wheels on some CI versions crash during C-level interpreter exit
    # after glTF export. We have already synchronously verified and flushed the
    # completed file; bypass that teardown only for this disposable test process.
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(0)
