"""Two measured prop examples from historical hard-surface proportion recipes.

EXAMPLE="SWORD": decorative rigid fantasy prop, not a manufactured weapon.
EXAMPLE="TABLE": game/art furniture blockout, not an engineering-certified table.
Dimensions are editable *starting examples* in meters. Never overwrite scene data.
"""
import bpy
import math

# ---- PROJECT CONFIG --------------------------------------------------------
EXAMPLE = "SWORD"              # "SWORD" or "TABLE"
ASSET_PREFIX = "MCP_PropStudy"
COLLECTION_NAME = "MCP_PropStudy_Kit"
SWORD_HANDLE_LENGTH = 0.24
SWORD_BLADE_LENGTH = 0.84      # blade:handle = 3.5:1 (historical 3-4)
SWORD_GUARD_WIDTH = 0.20
TABLE_HEIGHT = 0.75
TABLE_WIDTH = 1.20
TABLE_DEPTH = 0.70
TABLE_TOP_THICKNESS = 0.04    # historical example 0.03-0.05
TABLE_LEG_WIDTH = 0.06       # historical example 0.05-0.08
TABLE_LEG_INSET = 0.04
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_prop_example"
OWNER_VALUE = "measured_proportions_v1"
BOX_FACES = ((0,3,2,1),(4,5,6,7),(0,1,5,4),
             (1,2,6,5),(2,3,7,6),(3,0,4,7))


def box_vertices(x_size, y_size, z_size):
    x,y,z=x_size/2,y_size/2,z_size/2
    return ((-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),
            (-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z))


if EXAMPLE not in ("SWORD", "TABLE"):
    raise ValueError("EXAMPLE must be SWORD or TABLE")
dims = (SWORD_HANDLE_LENGTH, SWORD_BLADE_LENGTH, SWORD_GUARD_WIDTH,
        TABLE_HEIGHT, TABLE_WIDTH, TABLE_DEPTH, TABLE_TOP_THICKNESS,
        TABLE_LEG_WIDTH, TABLE_LEG_INSET)
if any(not math.isfinite(v) or v <= 0 for v in dims):
    raise ValueError("All example dimensions must be positive finite values")
if TABLE_TOP_THICKNESS >= TABLE_HEIGHT or TABLE_LEG_WIDTH + 2*TABLE_LEG_INSET >= min(TABLE_WIDTH, TABLE_DEPTH):
    raise ValueError("Table support dimensions do not fit inside top")
if not 3 <= SWORD_BLADE_LENGTH / SWORD_HANDLE_LENGTH <= 4:
    raise ValueError("Example sword blade length must be 3–4 handle lengths")
roles = ("Blade", "Grip", "Guard", "Pommel") if EXAMPLE == "SWORD" else (
    "Top", "Leg_FL", "Leg_FR", "Leg_RL", "Leg_RR")
names = [ASSET_PREFIX + "_" + role for role in roles]
if any(name in bpy.data.objects for name in names):
    raise ValueError("Output object collision; existing scene untouched")
col = bpy.data.collections.get(COLLECTION_NAME)
if col and col.get(OWNER_KEY) != OWNER_VALUE:
    raise ValueError("Unowned collection collision: " + COLLECTION_NAME)


def make_part(name, dimensions, location, color, collection):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = None
    try:
        mesh.from_pydata(box_vertices(*dimensions), [], BOX_FACES)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        obj[OWNER_KEY] = OWNER_VALUE
        obj.location = location
        obj.color = color
        collection.objects.link(obj)
        return obj
    except Exception:
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
        raise


created_col = False
if col is None:
    col = bpy.data.collections.new(COLLECTION_NAME)
    col[OWNER_KEY] = OWNER_VALUE
    bpy.context.scene.collection.children.link(col)
    created_col = True
created = []
try:
    if EXAMPLE == "SWORD":
        created.append(make_part(names[0], (.09,.022,SWORD_BLADE_LENGTH),
                                 (0,0,SWORD_HANDLE_LENGTH+SWORD_BLADE_LENGTH/2),
                                 (.74,.81,.86,1),col))
        created.append(make_part(names[1], (.036,.042,SWORD_HANDLE_LENGTH),
                                 (0,0,SWORD_HANDLE_LENGTH/2),(.27,.20,.14,1),col))
        created.append(make_part(names[2], (SWORD_GUARD_WIDTH,.037,.028),
                                 (0,0,SWORD_HANDLE_LENGTH),(.43,.32,.14,1),col))
        created.append(make_part(names[3], (.075,.055,.045),(0,0,-.0225),
                                 (.48,.35,.17,1),col))
        print("PROPORTION EXAMPLE: SWORD",
              "blade_to_handle=",round(SWORD_BLADE_LENGTH/SWORD_HANDLE_LENGTH,3),
              "guard_m=",SWORD_GUARD_WIDTH)
    else:
        leg_height = TABLE_HEIGHT - TABLE_TOP_THICKNESS
        created.append(make_part(names[0], (TABLE_WIDTH,TABLE_DEPTH,TABLE_TOP_THICKNESS),
                                 (0,0,TABLE_HEIGHT-TABLE_TOP_THICKNESS/2),
                                 (.52,.35,.21,1),col))
        for index,(role,fx,fy) in enumerate((("Leg_FL",1,1),("Leg_FR",1,-1),
                                              ("Leg_RL",-1,1),("Leg_RR",-1,-1)),start=1):
            x = fx*(TABLE_WIDTH/2 - TABLE_LEG_INSET - TABLE_LEG_WIDTH/2)
            y = fy*(TABLE_DEPTH/2 - TABLE_LEG_INSET - TABLE_LEG_WIDTH/2)
            created.append(make_part(names[index], (TABLE_LEG_WIDTH,TABLE_LEG_WIDTH,leg_height),
                                     (x,y,leg_height/2),(.34,.23,.16,1),col))
        print("PROPORTION EXAMPLE: TABLE",
              "height_m=",TABLE_HEIGHT,"top_thickness_m=",TABLE_TOP_THICKNESS,
              "leg_width_m=",TABLE_LEG_WIDTH)
    print("RESULT: SUCCESS", [ob.name for ob in created])
    print("Only a static blockout. Validate silhouette, references, contact and destination.")
except Exception:
    for ob in reversed(created):
        mesh = ob.data
        bpy.data.objects.remove(ob, do_unlink=True)
        if mesh.users == 0:
            bpy.data.meshes.remove(mesh)
    if created_col and not col.objects:
        bpy.data.collections.remove(col)
    raise
