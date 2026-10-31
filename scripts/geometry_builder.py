"""geometry_builder.py — declarative, repeatable geometry construction for Blender MCP.

Paste this script into the active Blender-control MCP code executor.
It creates new objects only; it never edits or deletes pre-existing objects.

Supported component types:
  box, sphere, ico_sphere, cylinder, cone, torus, beam, extruded_profile, lathe

Set ASSET_NAME and COMPONENTS below. Coordinates and dimensions use Blender units.
The script is intentionally compatible with Blender 3.1+ and avoids context-sensitive
operators for mesh construction wherever practical.
"""
import bpy
import bmesh
import math
from mathutils import Vector

# ---- CONFIG ----------------------------------------------------------------
ASSET_NAME = "MCP_Asset"
COLLECTION_NAME = "MCP_Asset_Geometry"
REUSE_COLLECTION = True

# Every component has a stable name and a type-specific parameter set.
# Existing objects with the same name are never implicitly replaced.
COMPONENTS = [
    {"name": "Base", "type": "box", "location": (0, 0, 0.5),
     "dimensions": (2.0, 1.0, 1.0), "bevel": 0.04},
    {"name": "Post", "type": "beam", "start": (0, 0, 1.0),
     "end": (0, 0, 2.5), "radius": 0.08, "vertices": 12},
]
# ----------------------------------------------------------------------------

OWNER_KEY = "_blender_mcp_geometry_builder"
OWNER_VALUE = "geometry_builder_v1"


def _collection(name):
    col = bpy.data.collections.get(name) if REUSE_COLLECTION else None
    if col is None:
        col = bpy.data.collections.new(name)
        col[OWNER_KEY] = OWNER_VALUE
        bpy.context.scene.collection.children.link(col)
    else:
        if col.get(OWNER_KEY) != OWNER_VALUE:
            raise ValueError("Collection name already exists and is not owned by this builder: " + name)
        if col.name not in bpy.context.scene.collection.children:
            bpy.context.scene.collection.children.link(col)
    return col


def _existing_owned(name):
    obj = bpy.data.objects.get(name)
    if obj is None:
        return None
    if obj.get(OWNER_KEY) == OWNER_VALUE:
        return obj
    raise ValueError("Object name already exists and is not owned by this builder: " + name)


def _link_object(name, mesh, collection, location=(0, 0, 0)):
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = Vector(location)
    obj[OWNER_KEY] = OWNER_VALUE
    obj["mcp_asset_name"] = ASSET_NAME
    return obj


def _mesh_object(name, verts, faces, collection, location=(0, 0, 0)):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.validate(verbose=False, clean_customdata=False)
    mesh.update()
    if not mesh.polygons:
        bpy.data.meshes.remove(mesh)
        raise ValueError("Generated mesh contains no faces: " + name)
    return _link_object(name, mesh, collection, location)


def _primitive_mesh(name, kind, params, collection):
    location = params.get("location", (0, 0, 0))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        if kind == "box":
            dims = Vector(params.get("dimensions", (1, 1, 1)))
            if min(dims) <= 0:
                raise ValueError("box dimensions must be positive")
            bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, verts=bm.verts, vec=dims)
        elif kind in ("sphere", "ico_sphere"):
            radius = float(params.get("radius", 1.0))
            if radius <= 0:
                raise ValueError("sphere radius must be positive")
            if kind == "sphere":
                bmesh.ops.create_uvsphere(
                    bm, u_segments=max(8, int(params.get("segments", 32))),
                    v_segments=max(4, int(params.get("rings", 16))), radius=radius
                )
            else:
                bmesh.ops.create_icosphere(
                    bm, subdivisions=max(1, int(params.get("subdivisions", 2))), radius=radius
                )
        elif kind in ("cylinder", "cone"):
            radius1 = float(params.get("radius", 0.5))
            radius2 = float(params.get("radius_top", 0.0 if kind == "cone" else radius1))
            depth = float(params.get("depth", 1.0))
            segments = max(3, int(params.get("vertices", 24)))
            if radius1 <= 0 or radius2 < 0 or depth <= 0:
                raise ValueError("cylinder/cone radii and depth are invalid")
            bmesh.ops.create_cone(
                bm, cap_ends=True, cap_tris=False, segments=segments,
                radius1=radius1, radius2=radius2, depth=depth
            )
        elif kind == "torus":
            major = float(params.get("major_radius", 1.0))
            minor = float(params.get("minor_radius", 0.25))
            if major <= 0 or minor <= 0 or minor >= major:
                raise ValueError("torus radii are invalid")
            bmesh.ops.create_torus(
                bm, major_segments=max(3, int(params.get("major_segments", 48))),
                minor_segments=max(3, int(params.get("minor_segments", 12))),
                major_radius=major, minor_radius=minor
            )
        else:
            raise ValueError("Unsupported primitive type: " + kind)
        bm.to_mesh(mesh)
    except Exception:
        bm.free()
        bpy.data.meshes.remove(mesh)
        raise
    bm.free()
    mesh.update()
    return _link_object(name, mesh, collection, location)


def _beam(name, params, collection):
    start = Vector(params["start"])
    end = Vector(params["end"])
    delta = end - start
    length = delta.length
    if length <= 1e-8:
        raise ValueError("beam start and end must differ")
    radius = float(params.get("radius", 0.05))
    if radius <= 0:
        raise ValueError("beam radius must be positive")
    segments = max(3, int(params.get("vertices", 12)))
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_cone(
            bm, cap_ends=True, cap_tris=False, segments=segments,
            radius1=radius, radius2=radius, depth=length
        )
        bm.to_mesh(mesh)
    except Exception:
        bm.free()
        bpy.data.meshes.remove(mesh)
        raise
    bm.free()
    mesh.update()
    obj = _link_object(name, mesh, collection, (start + end) * 0.5)
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = delta.to_track_quat("Z", "Y")
    return obj


def _extruded_profile(name, params, collection):
    """Extrude a simple, non-self-intersecting 2D XY polygon along Z."""
    profile = [Vector((float(p[0]), float(p[1]))) for p in params["profile"]]
    height = float(params.get("height", 1.0))
    if len(profile) < 3 or height <= 0:
        raise ValueError("extruded_profile needs >=3 points and positive height")
    for i, point in enumerate(profile):
        if (point - profile[(i + 1) % len(profile)]).length <= 1e-8:
            raise ValueError("profile contains repeated consecutive points")
    area2 = sum(profile[i].x * profile[(i + 1) % len(profile)].y -
                profile[(i + 1) % len(profile)].x * profile[i].y
                for i in range(len(profile)))
    if abs(area2) <= 1e-8:
        raise ValueError("profile has zero area")
    if area2 < 0:
        profile.reverse()
    n = len(profile)
    verts = [(p.x, p.y, 0.0) for p in profile] + [(p.x, p.y, height) for p in profile]
    faces = [tuple(reversed(range(n))), tuple(range(n, 2 * n))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, j + n, i + n))
    return _mesh_object(name, verts, faces, collection, params.get("location", (0, 0, 0)))


def _lathe(name, params, collection):
    """Revolve a radius/Z profile around the local Z axis."""
    profile = [(float(p[0]), float(p[1])) for p in params["profile"]]
    segments = max(3, int(params.get("segments", 32)))
    if len(profile) < 2 or any(r < 0 for r, _z in profile):
        raise ValueError("lathe profile needs >=2 points with non-negative radii")
    verts = []
    for radius, z in profile:
        for i in range(segments):
            angle = (2.0 * math.pi * i) / segments
            verts.append((radius * math.cos(angle), radius * math.sin(angle), z))
    faces = []
    for ring in range(len(profile) - 1):
        for i in range(segments):
            a = ring * segments + i
            b = ring * segments + (i + 1) % segments
            c = (ring + 1) * segments + (i + 1) % segments
            d = (ring + 1) * segments + i
            faces.append((a, b, c, d))
    if profile[0][0] > 0:
        faces.append(tuple(reversed(range(segments))))
    if profile[-1][0] > 0:
        base = (len(profile) - 1) * segments
        faces.append(tuple(base + i for i in range(segments)))
    return _mesh_object(name, verts, faces, collection, params.get("location", (0, 0, 0)))


def build_component(spec, collection):
    name = str(spec["name"])
    kind = str(spec["type"])
    if not name or name in {"Cube", "Object"}:
        raise ValueError("component needs a meaningful explicit name")
    if _existing_owned(name) is not None:
        raise ValueError("component already exists; no implicit overwrite: " + name)
    if kind in {"box", "sphere", "ico_sphere", "cylinder", "cone", "torus"}:
        return _primitive_mesh(name, kind, spec, collection)
    if kind == "beam":
        return _beam(name, spec, collection)
    if kind == "extruded_profile":
        return _extruded_profile(name, spec, collection)
    if kind == "lathe":
        return _lathe(name, spec, collection)
    raise ValueError("Unknown component type: " + kind)


def _add_optional_bevel(obj, spec):
    width = float(spec.get("bevel", 0.0))
    if width <= 0:
        return
    segments = max(1, int(spec.get("bevel_segments", 2)))
    modifier = obj.modifiers.new("MCP_Bevel", "BEVEL")
    modifier.width = width
    modifier.segments = segments
    modifier.limit_method = "ANGLE"
    modifier.angle_limit = math.radians(float(spec.get("bevel_angle", 30.0)))


print("Blender:", bpy.app.version_string)
print("Asset:", ASSET_NAME)
collection = _collection(COLLECTION_NAME)
created = []
errors = []
for component in COMPONENTS:
    try:
        obj = build_component(component, collection)
        _add_optional_bevel(obj, component)
        created.append(obj)
        print("CREATED:", obj.name, "type=", component["type"],
              "vertices=", len(obj.data.vertices), "faces=", len(obj.data.polygons))
    except Exception as exc:
        errors.append((component.get("name", "<unnamed>"), str(exc)))
        print("ERROR:", component.get("name", "<unnamed>"), repr(exc))

print("GEOMETRY BUILD REPORT")
print("created:", len(created), "errors:", len(errors))
print("objects:", [obj.name for obj in created])
print("result:", "SUCCESS" if not errors else "PARTIAL")
