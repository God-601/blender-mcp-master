"""Disposable *real Blender Cycles* texture bake acceptance fixture.

Bakes an emission material on a freshly created UV cube into a 64x64 PNG.
Checks actual pixel values, texture map variation, object geometry integrity,
and file path; never accesses user project scenes. Requires bpy with Cycles.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def run(directory):
    target = Path(directory).resolve()
    if not target.is_dir():
        raise ValueError("Existing output directory required")
    image_path = target / "cycles-emission-bake.png"
    if image_path.exists():
        raise FileExistsError("Will not overwrite prior texture bake evidence")
    import bpy
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 8
    scene.render.bake.margin = 2
    bpy.ops.mesh.primitive_plane_add(size=2)
    ob = bpy.context.object
    ob.name = "DisposableBakePlane"
    if not ob.data.uv_layers:
        raise AssertionError("Plane created without a UV map")
    geometry_before = [tuple(v.co) for v in ob.data.vertices]
    material = bpy.data.materials.new("DisposableBakeMaterial")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    nodes.clear()
    out = nodes.new("ShaderNodeOutputMaterial")
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (0.15, 0.65, 0.25, 1.0)
    emission.inputs["Strength"].default_value = 1.0
    material.node_tree.links.new(emission.outputs["Emission"], out.inputs["Surface"])
    target_node = nodes.new("ShaderNodeTexImage")
    texture = bpy.data.images.new("DisposableBakedTexture", width=64, height=64, alpha=False)
    target_node.image = texture
    nodes.active = target_node
    ob.data.materials.clear()
    ob.data.materials.append(material)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    result = bpy.ops.object.bake(type="EMIT", margin=2, use_clear=True)
    if "FINISHED" not in result:
        raise AssertionError("Cycles bake did not report FINISHED")
    pixels = list(texture.pixels)
    if len(pixels) != 64 * 64 * 4:
        raise AssertionError("Baked texture has invalid dimensions")
    center = pixels[4 * (32 * 64 + 32):4 * (32 * 64 + 32) + 3]
    if not (center[1] > 0.20 and center[1] > center[0] and center[1] > center[2]):
        raise AssertionError("Actual baked center pixel does not reflect green emission")
    if geometry_before != [tuple(v.co) for v in ob.data.vertices]:
        raise AssertionError("Bake mutated original geometry")
    texture.filepath_raw = str(image_path)
    texture.file_format = "PNG"
    texture.save()
    if not image_path.is_file() or image_path.stat().st_size < 100:
        raise AssertionError("Bake PNG was not saved")
    return {
        "status": "BAKED_TEXTURE_MEASURED", "engine": "Cycles",
        "blender_version": bpy.app.version_string,
        "png": str(image_path),
        "png_sha256": hashlib.sha256(image_path.read_bytes()).hexdigest(),
        "resolution": [64, 64], "sample_rgb": [round(x, 5) for x in center],
        "scene_geometry_preserved": True,
        "visual_artistic_quality": "NOT VERIFIED",
        "actual_game_engine_shader": "NOT VERIFIED",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    record = run(args.directory)
    print("MCP_CYCLES_BAKE_BEGIN", flush=True)
    print(json.dumps(record, sort_keys=True), flush=True)
    print("MCP_CYCLES_BAKE_END", flush=True)
    sys.stdout.flush()
    sys.stderr.flush()
    # Isolated disposable CI process: avoid known bpy glTF teardown issues.
    os._exit(0)
