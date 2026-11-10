"""Disposable two-bone Blender export for actual Godot animation verification."""
import argparse
import json
import math
from pathlib import Path
import sys


def generate(path):
    target = Path(path).resolve()
    if target.suffix != '.glb' or not target.parent.is_dir():
        raise ValueError('Require a GLB path in an existing directory')
    if target.exists():
        raise FileExistsError('Refusing to overwrite animation fixture')
    import bpy
    if not bpy.app.background:
        raise RuntimeError('Fixture requires a disposable background Blender')
    original = bpy.context.scene
    scene = bpy.data.scenes.new('GodotAnimationFixture')
    window = bpy.context.window
    window.scene = scene
    created = []
    try:
        vertices = [(x, y, z / 4) for z in range(9) for x, y in [(-.15, -.15), (.15, -.15), (.15, .15), (-.15, .15)]]
        faces = [(i * 4 + j, i * 4 + (j + 1) % 4, (i + 1) * 4 + (j + 1) % 4, (i + 1) * 4 + j) for i in range(8) for j in range(4)]
        faces += [(3, 2, 1, 0), (32, 33, 34, 35)]
        mesh = bpy.data.meshes.new('AnimationFixtureMesh')
        mesh.from_pydata(vertices, [], faces)
        obj = bpy.data.objects.new('AnimationFixtureMesh', mesh)
        scene.collection.objects.link(obj)
        created.append(obj)
        uv = mesh.uv_layers.new(name='UVMap')
        for polygon in mesh.polygons:
            for loop in polygon.loop_indices:
                vertex = mesh.vertices[mesh.loops[loop].vertex_index].co
                uv.data[loop].uv = ((vertex.x + .15) / .3, vertex.z / 2)
        material = bpy.data.materials.new('AnimationFixtureMaterial')
        material.use_nodes = True
        shader = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value = (.12, .45, .7, 1)
        mesh.materials.append(material)
        rig_data = bpy.data.armatures.new('AnimationFixtureRig')
        rig = bpy.data.objects.new('AnimationFixtureRig', rig_data)
        scene.collection.objects.link(rig)
        created.append(rig)
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        lower = rig_data.edit_bones.new('Lower')
        lower.head, lower.tail = (0, 0, 0), (0, 0, 1)
        upper = rig_data.edit_bones.new('Upper')
        upper.head, upper.tail, upper.parent, upper.use_connect = (0, 0, 1), (0, 0, 2), lower, True
        bpy.ops.object.mode_set(mode='OBJECT')
        groups = [obj.vertex_groups.new(name=name) for name in ('Lower', 'Upper')]
        for vertex in mesh.vertices:
            upper_weight = max(0, min(1, (vertex.co.z - .75) / .5))
            for group, weight in zip(groups, (1 - upper_weight, upper_weight)):
                if weight > 0:
                    group.add([vertex.index], weight, 'REPLACE')
        modifier = obj.modifiers.new('Deform', 'ARMATURE')
        modifier.object = rig
        bone = rig.pose.bones['Upper']
        bone.rotation_mode = 'XYZ'
        for frame, degrees in [(1, 0), (12, 45), (24, 0)]:
            bone.rotation_euler[1] = math.radians(degrees)
            bone.keyframe_insert(data_path='rotation_euler', frame=frame)
        rig.animation_data.action.name = 'Bend'
        scene.frame_start, scene.frame_end = 1, 24
        def evaluated():
            evaluated_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            return [v.co.copy() for v in evaluated_obj.data.vertices]
        scene.frame_set(1)
        before = evaluated()
        scene.frame_set(12)
        displacement = max((a - b).length for a, b in zip(before, evaluated()))
        weight_sums_one = all(abs(sum(group.weight for group in v.groups) - 1) < 1e-6 for v in mesh.vertices)
        assert displacement > .1 and weight_sums_one
        scene.frame_set(1)
        for item in bpy.context.view_layer.objects:
            item.select_set(item in (obj, rig))
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(filepath=str(target), export_format='GLB', use_selection=True, export_animations=True)
        assert target.is_file() and target.stat().st_size > 100
        return {'bones': len(rig_data.bones), 'maximum_vertex_displacement': displacement,
                'all_weight_sums_one': weight_sums_one, 'blender_version': bpy.app.version_string}
    finally:
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        window.scene = original
        for item in created:
            bpy.data.objects.remove(item, do_unlink=True)
        bpy.data.scenes.remove(scene)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else None)
    print(json.dumps(generate(args.destination)), flush=True)
