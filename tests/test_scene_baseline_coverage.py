"""Real Blender probes for protected-object preservation and partial coverage."""
import unittest

from test_scene_baseline_runtime import bpy, compare_module, fake_baseline, run_snapshot


class ComparisonCoverageTests(unittest.TestCase):
    def test_legacy_match_is_explicitly_partial(self):
        original = fake_baseline()
        result = compare_module().compare(original, original)
        self.assertEqual(result["scope_status"], "PASS (escopo parcial)")
        self.assertTrue(result["limitations"])

    def test_different_fingerprint_schemas_are_not_comparable(self):
        original = fake_baseline()
        current = dict(original, schema_version=2)
        result = compare_module().compare(original, current)
        self.assertEqual(result["status"], "NOT VERIFIED")


@unittest.skipIf(bpy is None, "bpy unavailable")
class BaselineCoverageTests(unittest.TestCase):
    def cube(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add()
        return bpy.context.object

    def link(self, data):
        obj = bpy.data.objects.new("Protected", data)
        bpy.context.scene.collection.objects.link(obj)
        return obj

    def assert_mutation_detected(self, obj, mutate):
        bpy.context.view_layer.update()
        before = run_snapshot([obj.name])
        self.assertEqual(before["status"], "MEASURED", before["errors"])
        mutate()
        bpy.context.view_layer.update()
        after = run_snapshot([obj.name])
        self.assertEqual(after["status"], "MEASURED", after["errors"])
        result = compare_module().compare(before, after)
        self.assertEqual(result["status"], "ISSUE", result)
        self.assertEqual(result["changed"], [obj.name])

    def test_protected_mesh_and_object_edits(self):
        def group(obj):
            vertex_group = obj.vertex_groups.new(name="RigWeight")
            vertex_group.add([0], 0.25, "REPLACE")
            return vertex_group

        def shape(obj):
            obj.shape_key_add(name="Basis")
            return obj.shape_key_add(name="ProtectedShape")

        def crease(obj):
            edge = obj.data.edges[0]
            if hasattr(edge, "crease"):
                return lambda: setattr(edge, "crease", 0.5)
            layer = obj.data.attributes.new("crease_edge", "FLOAT", "EDGE")
            return lambda: setattr(layer.data[0], "value", 0.5)

        def vertex_color(obj):
            if hasattr(obj.data, "color_attributes"):
                layer = obj.data.color_attributes.new("Paint", "FLOAT_COLOR", "POINT")
            else:
                layer = obj.data.vertex_colors.new(name="Paint")
            return lambda: setattr(layer.data[0], "color", (0.1, 0.2, 0.3, 1.0))

        def split_normals(obj):
            mesh = obj.data
            for face in mesh.polygons:
                face.use_smooth = True
            if hasattr(mesh, "use_auto_smooth"):
                mesh.use_auto_smooth = True
            original = [(0.0, 0.0, 1.0)] * len(mesh.loops)
            mesh.normals_split_custom_set(original)
            changed = [(1.0, 0.0, 0.0)] + original[1:]
            return lambda: mesh.normals_split_custom_set(changed)

        def shared_mesh(obj):
            sibling = self.link(obj.data)
            return lambda: setattr(sibling.data.vertices[0].co, "x", 9.0)

        def material_color(obj):
            mat = bpy.data.materials.new("ProtectedMaterial")
            obj.data.materials.append(mat)
            return lambda: setattr(mat, "diffuse_color", (0.1, 0.2, 0.3, 1.0))

        def material_link(obj):
            obj.data.materials.append(bpy.data.materials.new("ProtectedMaterial"))
            return lambda: setattr(obj.material_slots[0], "link", "OBJECT")

        def image_node(obj, packed=False):
            mat = bpy.data.materials.new("ProtectedMaterial")
            mat.use_nodes = True
            obj.data.materials.append(mat)
            node = mat.node_tree.nodes.new("ShaderNodeTexImage")
            node.image = bpy.data.images.new("ProtectedTexture", 4, 4, float_buffer=True)
            if packed:
                node.image.pack()
            return node.image

        cases = {
            "object location": lambda o: lambda: setattr(o.location, "x", 9.0),
            "mesh vertex": lambda o: lambda: setattr(o.data.vertices[0].co, "x", 9.0),
            "shape key coordinate": lambda o: (lambda key: lambda: setattr(key.data[0].co, "x", 9.0))(shape(o)),
            "image colorspace": lambda o: (lambda img: lambda: setattr(img.colorspace_settings, "name", "Non-Color"))(image_node(o)),
            "material color": material_color,
            "material slot link": material_link,
            "shared mesh edit": shared_mesh,
            "smooth shading": lambda o: lambda: setattr(o.data.polygons[0], "use_smooth", True),
            "vertex group weight": lambda o: (lambda g: lambda: g.add([0], 0.75, "REPLACE"))(group(o)),
            "vertex group name": lambda o: (lambda g: lambda: setattr(g, "name", "Different"))(group(o)),
            "shape key value": lambda o: (lambda k: lambda: setattr(k, "value", 0.5))(shape(o)),
            "shape key mute": lambda o: (lambda k: lambda: setattr(k, "mute", True))(shape(o)),
            "shape key slider bounds": lambda o: (lambda k: lambda: setattr(k, "slider_max", 2.0))(shape(o)),
            "constraint addition": lambda o: lambda: o.constraints.new("COPY_LOCATION"),
            "keyframe addition": lambda o: lambda: o.keyframe_insert(data_path="location", frame=3),
            "packed image pixels": lambda o: (lambda img: lambda: img.pixels.__setitem__(0, 0.5))(image_node(o, packed=True)),
            "object custom property": lambda o: lambda: o.__setitem__("ProtectedProperty", {"values": [1, 2]}),
            "mesh custom property": lambda o: lambda: o.data.__setitem__("ProtectedProperty", 3),
            "edge seam": lambda o: lambda: setattr(o.data.edges[0], "use_seam", True),
            "edge sharp": lambda o: lambda: setattr(o.data.edges[0], "use_edge_sharp", True),
            "edge crease": crease,
            "vertex color": vertex_color,
            "new mesh attribute": lambda o: lambda: o.data.attributes.new("ProtectedAttribute", "FLOAT", "POINT"),
            "custom split normals": split_normals,
            "display type": lambda o: lambda: setattr(o, "display_type", "WIRE"),
            "pass index": lambda o: lambda: setattr(o, "pass_index", 4),
        }
        for label, setup in cases.items():
            with self.subTest(label=label):
                obj = self.cube()
                self.assert_mutation_detected(obj, setup(obj))

    def test_rest_bone_length_change(self):
        self.cube()
        armature = self.link(bpy.data.armatures.new("Rig"))
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode="EDIT")
        bone = armature.data.edit_bones.new("Bone")
        bone.tail.z = 1.0
        bpy.ops.object.mode_set(mode="OBJECT")

        def lengthen():
            bpy.ops.object.mode_set(mode="EDIT")
            armature.data.edit_bones["Bone"].tail.z = 2.0
            bpy.ops.object.mode_set(mode="OBJECT")

        self.assert_mutation_detected(armature, lengthen)

    def test_pose_bone_rotation_change(self):
        self.cube()
        bpy.ops.object.armature_add()
        armature = bpy.context.object
        bone = armature.pose.bones[0]
        bone.rotation_mode = "XYZ"
        self.assert_mutation_detected(armature, lambda: setattr(bone.rotation_euler, "z", 0.5))

    def test_curve_control_point_change(self):
        self.cube()
        curve = self.link(bpy.data.curves.new("ProtectedCurve", "CURVE"))
        spline = curve.data.splines.new("BEZIER")
        spline.bezier_points.add(1)
        self.assert_mutation_detected(curve, lambda: setattr(spline.bezier_points[0].co, "x", 9.0))

    def test_noop_controls_match_measured_properties(self):
        obj = self.cube()
        before = run_snapshot([obj.name])
        for mutate in (lambda: None, lambda: setattr(obj, "delta_location", tuple(obj.delta_location))):
            mutate()
            bpy.context.view_layer.update()
            result = compare_module().compare(before, run_snapshot([obj.name]))
            self.assertEqual(result["status"], "PASS (escopo parcial)", result)
            self.assertEqual(result["unchanged"], [obj.name])
            self.assertTrue(result["limitations"])

    def test_unmeasured_object_does_not_pass(self):
        self.cube()
        obj = self.link(bpy.data.metaballs.new("ProtectedMetaball"))
        snapshot = run_snapshot([obj.name])
        self.assertEqual(snapshot["status"], "NOT VERIFIED")
        self.assertTrue(snapshot["errors"])
        result = compare_module().compare(snapshot, snapshot)
        self.assertEqual(result["status"], "NOT VERIFIED")
        self.assertTrue(any(obj.name in reason for reason in result["reason"]))
