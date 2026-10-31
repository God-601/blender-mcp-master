"""geometry_nodes_builder.py — editable repeated post array through Geometry Nodes.

Creates a new object and node group exposing Count, Spacing, Height, and Radius inputs.
It does not edit existing objects or save the .blend automatically.
"""
import bpy

# ---- CONFIG ----------------------------------------------------------------
OBJECT_NAME = "MCP_Parametric_Posts"
NODE_GROUP_NAME = "MCP_Parametric_Posts_GN"
COLLECTION_NAME = "MCP_Parametric"
COUNT = 5
SPACING = 1.5
HEIGHT = 2.0
RADIUS = 0.12
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_geometry_nodes"
OWNER_VALUE = "parametric_posts_v1"


def add_interface_socket(group, name, direction, socket_type, default_value):
    if hasattr(group, "interface"):
        socket = group.interface.new_socket(
            name=name, in_out=direction, socket_type=socket_type
        )
    else:
        sockets = group.inputs if direction == "INPUT" else group.outputs
        socket = sockets.new(socket_type, name)
    if direction == "INPUT":
        socket.default_value = default_value
    return socket


if COUNT < 1 or SPACING <= 0 or HEIGHT <= 0 or RADIUS <= 0:
    raise ValueError("parametric post array parameters must be positive")
if OBJECT_NAME in bpy.data.objects:
    raise ValueError("object already exists; refusing overwrite: " + OBJECT_NAME)
if NODE_GROUP_NAME in bpy.data.node_groups:
    existing = bpy.data.node_groups[NODE_GROUP_NAME]
    if existing.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("node group exists but is not owned by this generator")

collection = bpy.data.collections.get(COLLECTION_NAME)
if collection is None:
    collection = bpy.data.collections.new(COLLECTION_NAME)
    collection[OWNER_KEY] = OWNER_VALUE
    bpy.context.scene.collection.children.link(collection)
elif collection.get(OWNER_KEY) != OWNER_VALUE:
    raise ValueError("collection collision: " + COLLECTION_NAME)

group = bpy.data.node_groups.get(NODE_GROUP_NAME)
if group is None:
    group = bpy.data.node_groups.new(NODE_GROUP_NAME, "GeometryNodeTree")
    group[OWNER_KEY] = OWNER_VALUE
    add_interface_socket(group, "Geometry", "OUTPUT", "NodeSocketGeometry", None)
    add_interface_socket(group, "Count", "INPUT", "NodeSocketInt", int(COUNT))
    add_interface_socket(group, "Spacing", "INPUT", "NodeSocketFloat", float(SPACING))
    add_interface_socket(group, "Height", "INPUT", "NodeSocketFloat", float(HEIGHT))
    add_interface_socket(group, "Radius", "INPUT", "NodeSocketFloat", float(RADIUS))

    nodes = group.nodes
    links = group.links
    nodes.clear()
    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-720, 0)

    line = nodes.new("GeometryNodeMeshLine")
    line.location = (-420, 160)
    line.mode = "OFFSET"
    combine = nodes.new("ShaderNodeCombineXYZ")
    combine.location = (-650, -180)
    links.new(group_input.outputs.get("Spacing"), combine.inputs.get("X"))
    links.new(combine.outputs.get("Vector"), line.inputs.get("Offset"))
    links.new(group_input.outputs.get("Count"), line.inputs.get("Count"))

    cylinder = nodes.new("GeometryNodeMeshCylinder")
    cylinder.location = (-420, -260)
    links.new(group_input.outputs.get("Radius"), cylinder.inputs.get("Radius"))
    links.new(group_input.outputs.get("Height"), cylinder.inputs.get("Depth"))

    instance = nodes.new("GeometryNodeInstanceOnPoints")
    instance.location = (-120, 100)
    links.new(line.outputs.get("Mesh"), instance.inputs.get("Points"))
    links.new(cylinder.outputs.get("Mesh"), instance.inputs.get("Instance"))

    realize = nodes.new("GeometryNodeRealizeInstances")
    realize.location = (120, 100)
    links.new(instance.outputs.get("Instances"), realize.inputs.get("Geometry"))

    output = nodes.new("NodeGroupOutput")
    output.location = (380, 100)
    links.new(realize.outputs.get("Geometry"), output.inputs.get("Geometry"))

mesh = bpy.data.meshes.new(OBJECT_NAME + "_BaseMesh")
obj = bpy.data.objects.new(OBJECT_NAME, mesh)
collection.objects.link(obj)
obj[OWNER_KEY] = OWNER_VALUE
obj["parametric_count"] = int(COUNT)
obj["parametric_spacing"] = float(SPACING)
obj["parametric_height"] = float(HEIGHT)
obj["parametric_radius"] = float(RADIUS)
modifier = obj.modifiers.new("Parametric_Post_Array", "NODES")
modifier.node_group = group
print("PARAMETRIC OBJECT:", obj.name)
print("NODE GROUP:", group.name)
print("EDITABLE INPUTS:", {"Count": COUNT, "Spacing": SPACING, "Height": HEIGHT, "Radius": RADIUS})
print("Edit the Geometry Nodes modifier inputs to regenerate the repeated post assembly.")
