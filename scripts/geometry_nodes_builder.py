"""geometry_nodes_builder.py — editable parametric cube/panel through Geometry Nodes.

Creates a new object and a reusable Geometry Nodes group with an exposed Dimensions
vector input. It does not edit existing objects or save the .blend automatically.
"""
import bpy

# ---- CONFIG ----------------------------------------------------------------
OBJECT_NAME = "MCP_Parametric_Panel"
NODE_GROUP_NAME = "MCP_Parametric_Panel_GN"
COLLECTION_NAME = "MCP_Parametric"
DIMENSIONS = (3.0, 0.3, 2.0)
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_geometry_nodes"
OWNER_VALUE = "parametric_panel_v1"


def get_collection():
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    elif col.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("collection collision: " + COLLECTION_NAME)
    return col


if min(float(v) for v in DIMENSIONS) <= 0:
    raise ValueError("all dimensions must be positive")
if OBJECT_NAME in bpy.data.objects:
    raise ValueError("object already exists; refusing overwrite: " + OBJECT_NAME)
if NODE_GROUP_NAME in bpy.data.node_groups:
    group = bpy.data.node_groups[NODE_GROUP_NAME]
    if group.get(OWNER_KEY) != OWNER_VALUE:
        raise ValueError("node group exists but is not owned by this generator")

group = bpy.data.node_groups.get(NODE_GROUP_NAME)
if group is None:
    group = bpy.data.node_groups.new(NODE_GROUP_NAME, "GeometryNodeTree")
    group[OWNER_KEY] = OWNER_VALUE
    if hasattr(group, "interface"):
        group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
        size_socket = group.interface.new_socket(name="Dimensions", in_out="INPUT", socket_type="NodeSocketVector")
    else:
        group.inputs.new("NodeSocketVector", "Dimensions")
        group.outputs.new("NodeSocketGeometry", "Geometry")
        size_socket = group.inputs.get("Dimensions")
    size_socket.default_value = tuple(float(v) for v in DIMENSIONS)
    nodes = group.nodes
    links = group.links
    nodes.clear()
    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-420, 0)
    cube = nodes.new("GeometryNodeMeshCube")
    cube.location = (-120, 0)
    output = nodes.new("NodeGroupOutput")
    output.location = (160, 0)
    links.new(group_input.outputs.get("Dimensions"), cube.inputs.get("Size"))
    links.new(cube.outputs.get("Mesh"), output.inputs.get("Geometry"))

collection = get_collection()
mesh = bpy.data.meshes.new(OBJECT_NAME + "_BaseMesh")
obj = bpy.data.objects.new(OBJECT_NAME, mesh)
collection.objects.link(obj)
obj[OWNER_KEY] = OWNER_VALUE
obj["parametric_dimensions"] = tuple(float(v) for v in DIMENSIONS)
modifier = obj.modifiers.new("Parametric_Geometry", "NODES")
modifier.node_group = group
print("PARAMETRIC OBJECT:", obj.name)
print("NODE GROUP:", group.name)
print("EDITABLE INPUT: Dimensions =", tuple(DIMENSIONS))
print("Change the Dimensions input on the Geometry Nodes modifier to regenerate the panel.")
