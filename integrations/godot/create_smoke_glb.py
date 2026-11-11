"""Generate a deterministic *test-only* glTF 2.0 GLB triangle for engine importer CI.

Not a substitute for Blender-exported assets. Only tests whether a real Godot
process can import a valid geometry+UV+material GLB through our probe.
No dependencies; refuses overwriting an existing destination.
"""
import argparse
import json
import struct
from pathlib import Path


def generate(path, *, bare=False):
    target = Path(path).resolve()
    if target.exists():
        raise FileExistsError("Refusing to overwrite existing fixture")
    if not target.parent.is_dir():
        raise ValueError("Destination directory does not exist")
    positions = struct.pack("<9f", 0., 0., 0., 1., 0., 0., 0., 1., 0.)
    uv = struct.pack("<6f", 0., 0., 1., 0., 0., 1.)
    indices = struct.pack("<3H", 0, 1, 2)
    # Accessor offsets are multiples of the component's required alignment.
    binary = positions + uv + indices + b"\x00\x00"
    assert len(binary) == 68
    document = {
        "asset": {"version": "2.0", "generator": "blender-mcp-master importer smoke fixture"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "TestTriangle"}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "TEXCOORD_0": 1},
                                     "indices": 2, "material": 0, "mode": 4}]}],
        "materials": [{"name": "TestMaterial", "pbrMetallicRoughness": {
            "baseColorFactor": [0.8, 0.4, 0.2, 1.0], "metallicFactor": 0.0,
            "roughnessFactor": 0.75}}],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(positions), "target": 34962},
                        {"buffer": 0, "byteOffset": 36, "byteLength": len(uv), "target": 34962},
                        {"buffer": 0, "byteOffset": 60, "byteLength": len(indices), "target": 34963}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3",
             "min": [0, 0, 0], "max": [1, 1, 0]},
            {"bufferView": 1, "componentType": 5126, "count": 3, "type": "VEC2"},
            {"bufferView": 2, "componentType": 5123, "count": 3, "type": "SCALAR"},
        ],
    }
    if bare:
        primitive = document['meshes'][0]['primitives'][0]
        primitive['attributes'].pop('TEXCOORD_0')
        primitive.pop('indices')
    json_blob = json.dumps(document, separators=(",", ":"), sort_keys=True).encode("utf-8")
    json_blob += b" " * (-len(json_blob) % 4)
    total_length = 12 + 8 + len(json_blob) + 8 + len(binary)
    glb = (struct.pack("<III", 0x46546C67, 2, total_length)
           + struct.pack("<I4s", len(json_blob), b"JSON") + json_blob
           + struct.pack("<I4s", len(binary), b"BIN\x00") + binary)
    with target.open("xb") as handle:
        handle.write(glb)
    return {"bytes": len(glb), "triangles": 1, "has_uv": not bare, "has_material": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("destination", help="Fresh absolute or relative .glb file path")
    parser.add_argument("--bare", action="store_true", help="Omit optional UV and index arrays")
    args = parser.parse_args()
    if Path(args.destination).suffix.lower() != ".glb":
        parser.error("Destination must have .glb extension")
    print(json.dumps(generate(args.destination, bare=args.bare), sort_keys=True))
