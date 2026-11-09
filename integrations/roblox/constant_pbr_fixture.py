"""Opt-in constant-factor PBR fixture conversion in an isolated background Blender.

This creates image maps for untextured constant shaders; it does not bake arbitrary
shaders. Base-color PNG bytes are sRGB encoded; data maps remain linear.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def linear_to_srgb(value):
    if not 0 <= value <= 1:
        raise ValueError('Expected normalized linear channel')
    return 12.92 * value if value <= .0031308 else 1.055 * value ** (1 / 2.4) - .055


def prepare(source, output):
    import bpy
    if not bpy.app.background:
        raise ValueError('Use an isolated background Blender process, never the interactive scene')
    source, output = Path(source).resolve(), Path(output).resolve()
    if source == output or output.exists():
        raise ValueError('Output must be new and distinct from source')
    original = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    maps = []
    for index, material in enumerate(bpy.data.materials):
        if not material.use_nodes:
            raise ValueError('Fixture requires node materials')
        shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        if any(shader.inputs[s].is_linked for s in ('Base Color', 'Roughness', 'Metallic', 'Normal')):
            raise ValueError('Only constant untextured inputs are supported')
        color = tuple(shader.inputs['Base Color'].default_value)
        encoded = tuple(linear_to_srgb(v) if i < 3 else v for i, v in enumerate(color))
        rough = float(shader.inputs['Roughness'].default_value)
        metal = float(shader.inputs['Metallic'].default_value)
        channels = [('base', encoded, 'sRGB', 'Base Color'),
                    ('roughness', (rough, rough, rough, 1), 'Non-Color', 'Roughness'),
                    ('metallic', (metal, metal, metal, 1), 'Non-Color', 'Metallic'),
                    ('normal', (.5, .5, 1, 1), 'Non-Color', None)]
        for name, values, colorspace, socket in channels:
            path = output.with_name(output.stem + '-%s-%s.png' % (index, name))
            if path.exists():
                raise ValueError('Refusing to overwrite texture: ' + str(path))
            image = bpy.data.images.new(material.name + '_' + name, width=16, height=16)
            image.colorspace_settings.name = colorspace
            image.pixels = list(values) * 256
            image.filepath_raw = str(path)
            image.file_format = 'PNG'
            image.save()
            maps.append(path.name)
            node = material.node_tree.nodes.new('ShaderNodeTexImage')
            node.image = image
            if socket:
                material.node_tree.links.new(node.outputs['Color'], shader.inputs[socket])
            else:
                normal = material.node_tree.nodes.new('ShaderNodeNormalMap')
                material.node_tree.links.new(node.outputs['Color'], normal.inputs['Color'])
                material.node_tree.links.new(normal.outputs['Normal'], shader.inputs['Normal'])
        shader.inputs['Base Color'].default_value = (1, 1, 1, 1)
        shader.inputs['Roughness'].default_value = 1
        shader.inputs['Metallic'].default_value = 1
    bpy.ops.export_scene.gltf(filepath=str(output), export_format='GLB')
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original
    return {'source_sha256': original, 'output_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
            'source_preserved': True, 'maps': maps,
            'scope': 'constant-color controlled fixture; not a general bake or engine certification'}


if __name__ == '__main__':
    assert abs(linear_to_srgb(.5) - .7353569830524495) < 1e-12
    assert linear_to_srgb(0) == 0 and abs(linear_to_srgb(1) - 1) < 1e-12
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    print(json.dumps(prepare(args.source, args.output), indent=2))
