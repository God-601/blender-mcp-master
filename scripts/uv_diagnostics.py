"""P1 UV diagnostics on explicitly named Blender meshes. READ ONLY.

Checks positive-area triangle overlap (not mere shared boundaries), UV bounds,
per-triangle texel density from world-space area, and incomplete evidence.

This is an approximation for static mesh base topology: it doesn't evaluate
Geometry Nodes/modifier UV changes, island padding, UV rasterization artifacts
or actual texture sampling. Those are explicitly NOT VERIFIED.
"""
import bpy
import json
import math

# ---- CONFIG ----------------------------------------------------------------
TARGETS = []                      # required; never fall back to selection
UV_LAYER_NAME = ""                # empty = active layer
TEXTURE_WIDTH = 1024              # intended map size (px), not read from shader
TEXTURE_HEIGHT = 1024
ALLOW_STACKING = False            # mirrored/staked layouts: explicit review
ALLOW_TILING = False              # UDIM/tiling may deliberately leave 0-1
DENSITY_REVIEW_RATIO = 2.0       # review large differences; not hard failure
MAX_PAIRWISE_TRIANGLES = 1200     # cap quadratic overlap checks
MAX_OVERLAP_EXAMPLES = 15
# ----------------------------------------------------------------------------

def signed_area(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])

def point_inside_strict(point, tri, eps=1e-10):
    d = [signed_area(tri[i], tri[(i+1)%3], point) for i in range(3)]
    return all(value > eps for value in d) or all(value < -eps for value in d)

def properly_cross(a, b, c, d, eps=1e-10):
    ab1, ab2 = signed_area(a,b,c), signed_area(a,b,d)
    cd1, cd2 = signed_area(c,d,a), signed_area(c,d,b)
    return ((ab1 > eps and ab2 < -eps or ab1 < -eps and ab2 > eps)
            and (cd1 > eps and cd2 < -eps or cd1 < -eps and cd2 > eps))

def positive_overlap(first, second):
    """Overlap of non-zero 2D area. Border contact alone is not an overlap."""
    x1=[p[0] for p in first]
    x2=[p[0] for p in second]
    y1=[p[1] for p in first]
    y2=[p[1] for p in second]
    eps=1e-10
    if min(max(x1),max(x2)) - max(min(x1),min(x2)) <= eps:
        return False
    if min(max(y1),max(y2)) - max(min(y1),min(y2)) <= eps:
        return False
    for i in range(3):
        a,b=first[i],first[(i+1)%3]
        for j in range(3):
            if properly_cross(a,b,second[j],second[(j+1)%3],eps):
                return True
    if any(point_inside_strict(v,second,eps) for v in first):
        return True
    if any(point_inside_strict(v,first,eps) for v in second):
        return True
    # Coincident/rotated triangles can share boundaries with no strictly
    # contained vertex: centroid interior test catches real area stacking.
    center1=(sum(v[0] for v in first)/3,sum(v[1] for v in first)/3)
    center2=(sum(v[0] for v in second)/3,sum(v[1] for v in second)/3)
    return point_inside_strict(center1,second,eps) or point_inside_strict(center2,first,eps)

def analyze(obj):
    mesh=obj.data
    layer=mesh.uv_layers.get(UV_LAYER_NAME) if UV_LAYER_NAME else mesh.uv_layers.active
    report={"name":obj.name, "mesh":mesh.name, "base_mesh":True,
            "texture_size_px":[TEXTURE_WIDTH,TEXTURE_HEIGHT],
            "world_unit_scale_length":float(bpy.context.scene.unit_settings.scale_length),
            "world_unit_system":bpy.context.scene.unit_settings.system,
            "status":"NOT VERIFIED"}
    if layer is None:
        report["reason"]="Requested UV layer unavailable"
        return report
    if len(layer.data)!=len(mesh.loops):
        report["reason"]="UV loop count mismatch"
        return report
    mesh.calc_loop_triangles()
    triangles=[]
    degenerates=0
    world_area_total=0.0
    uv_area_total=0.0
    densities=[]
    invalid_uv=False
    outside_tile=0
    for tri in mesh.loop_triangles:
        uv=[tuple(float(x) for x in layer.data[i].uv) for i in tri.loops]
        if any(not math.isfinite(value) for pt in uv for value in pt):
            invalid_uv=True
            continue
        if any(x < -1e-5 or x > 1.00001 or y < -1e-5 or y > 1.00001
               for x,y in uv):
            outside_tile+=1
        ua=abs(signed_area(*uv))*0.5
        world=[obj.matrix_world @ mesh.vertices[i].co for i in tri.vertices]
        wa=(world[1]-world[0]).cross(world[2]-world[0]).length*0.5
        if ua<=1e-12 or wa<=1e-12:
            degenerates+=1
            continue
        world_area_total+=wa
        uv_area_total+=ua
        densities.append(math.sqrt(ua*TEXTURE_WIDTH*TEXTURE_HEIGHT/wa))
        triangles.append({"polygon":int(tri.polygon_index),"uv":uv})
    report["uv_layer"]=layer.name
    report["triangles_measured"]=len(triangles)
    report["degenerate_uv_or_world_triangles"]=degenerates
    report["triangles_outside_0_1"]=outside_tile
    report["has_nonfinite_uv"]=invalid_uv
    report["measured_world_area_units2"]=round(world_area_total,8)
    report["measured_uv_area"]=round(uv_area_total,8)
    report["density_units"]="pixels_per_scene_length_unit"
    report["density_min"]=round(min(densities),5) if densities else None
    report["density_max"]=round(max(densities),5) if densities else None
    ratio=(max(densities)/min(densities)) if densities and min(densities)>0 else None
    report["density_max_to_min_ratio"]=round(ratio,5) if ratio is not None else None
    report["density_review_ratio"]=DENSITY_REVIEW_RATIO
    report["density_status"]="NOT VERIFIED" if not densities else (
        "REVIEW" if ratio > DENSITY_REVIEW_RATIO else "MEASURED")
    report["overlap_policy"]="ALLOWED_REVIEW" if ALLOW_STACKING else "UNIQUE_UV"
    report["uv_bounds_status"]="REVIEW" if outside_tile and ALLOW_TILING else (
        "ISSUE" if outside_tile else "PASS")
    report["overlap_examples"]=[]
    report["overlap_pairs"]=None
    if len(triangles)>MAX_PAIRWISE_TRIANGLES:
        report["overlap_status"]="NOT VERIFIED"
        report["overlap_reason"]="Triangle count exceeds pairwise comparison cap"
    elif not triangles:
        report["overlap_status"]="NOT VERIFIED"
        report["overlap_reason"]="No valid measurable UV triangles"
    else:
        pairs=0
        for i in range(len(triangles)):
            for j in range(i+1,len(triangles)):
                a,b=triangles[i],triangles[j]
                if a["polygon"]==b["polygon"]:
                    continue  # triangles tessellating the same n-gon/quad
                if positive_overlap(a["uv"],b["uv"]):
                    pairs+=1
                    if len(report["overlap_examples"]) < MAX_OVERLAP_EXAMPLES:
                        report["overlap_examples"].append([a["polygon"],b["polygon"]])
        report["overlap_pairs"]=pairs
        report["overlap_status"]=("REVIEW" if ALLOW_STACKING else "ISSUE") if pairs else "PASS"
    report["island_padding_status"]="NOT VERIFIED"
    report["modifier_uv_status"]="NOT VERIFIED"
    report["target_engine_status"]="NOT VERIFIED"
    if invalid_uv or degenerates:
        report["status"]="ISSUE"
    elif report["overlap_status"]=="ISSUE" or report["uv_bounds_status"]=="ISSUE":
        report["status"]="ISSUE"
    elif report["overlap_status"]=="NOT VERIFIED" or not densities:
        report["status"]="NOT VERIFIED"
    elif report["overlap_status"]=="REVIEW" or report["uv_bounds_status"]=="REVIEW" or report["density_status"]=="REVIEW":
        report["status"]="REVIEW"
    else:
        report["status"]="MEASURED"  # not artistic/game readiness approval
    return report

if not isinstance(TARGETS,list) or not TARGETS:
    raise ValueError("Specify explicit TARGETS. Selection/scene-wide fallback is forbidden")
if not all(isinstance(v,int) and v>0 for v in (TEXTURE_WIDTH,TEXTURE_HEIGHT)):
    raise ValueError("TEXTURE_WIDTH/HEIGHT must be positive integers")
if not math.isfinite(DENSITY_REVIEW_RATIO) or DENSITY_REVIEW_RATIO<=1:
    raise ValueError("DENSITY_REVIEW_RATIO must be finite and > 1")
if not isinstance(MAX_PAIRWISE_TRIANGLES,int) or MAX_PAIRWISE_TRIANGLES<1:
    raise ValueError("MAX_PAIRWISE_TRIANGLES must be positive")

reports=[]
for name in dict.fromkeys(TARGETS):
    ob=bpy.data.objects.get(name)
    if ob is None or ob.type!="MESH":
        reports.append({"name":name,"status":"NOT VERIFIED",
                        "reason":"Object missing or not a mesh"})
        continue
    if ob.mode!="OBJECT":
        reports.append({"name":name,"status":"NOT VERIFIED",
                        "reason":"Object not in Object Mode"})
        continue
    reports.append(analyze(ob))
summary="ISSUE" if any(item["status"]=="ISSUE" for item in reports) else (
    "NOT VERIFIED" if any(item["status"]=="NOT VERIFIED" for item in reports)
    else "REVIEW" if any(item["status"]=="REVIEW" for item in reports)
    else "MEASURED")
result={"blender_version":bpy.app.version_string,"summary":summary,
        "reports":reports,"scope":"BASE_MESH_UVS_ONLY",
        "limitation":"Does not certify padding, post-modifier UVs, baking, export or engine look."}
print("MCP_UV_DIAGNOSTICS_BEGIN")
print(json.dumps(result,sort_keys=True,indent=2))
print("MCP_UV_DIAGNOSTICS_END")
