# v1.2.0 — evidence ledger and unverified limits

| Feature | Automated evidence | Result / limitations |
| --- | --- | --- |
| New-model interview | Static policy checks and task examples | Several relevant nonredundant questions; no single permission prompt; actual live-agent conversational compliance **NOT VERIFIED** |
| Game asset preflight | `tests/test_game_asset_preflight_runtime.py` in bpy matrix | Read-only evaluated triangles, world bounds/pivot, UV presence, material and texture references; **not game-engine validation** |
| UV island gutter | `tests/test_uv_island_gutter_runtime.py` in bpy matrix | UV-continuous face-island grouping and AABB spacing lower bounds; baker and final mip texture look **NOT VERIFIED** |
| GLB roundtrip | `test_GLTF_roundtrip_preserves_static_asset_bounds_uv_and_material_presence` in bpy matrix | Blender→GLB→Blender static reimport check for geometry/origin/UV/material presence; **not Roblox/Unity/Godot/Unreal** |
| Safety + packaging | Python static and mutation checks; npm resource tests; isolated ZIP smoke | No automatic source edits from preflight; user scene preservation limited to tested properties; live installed-agent discovery **NOT VERIFIED** |

## Deliberately not claimed

- No certified real Roblox Studio, Unity, Unreal or Godot import.
- No verified FBX import in a target engine, rig animation, physics collision,
  GPU measurements, LOD switch behavior, normal-map bake quality or shader fidelity.
- Bounding-box UV gaps only provide a conservative distance lower bound;
  they cannot replace rasterized bake and actual texture filtering tests.
- Static design instructions and tests cannot guarantee that every LLM will
  ask ideal questions in a live conversation; that requires agent-client tests.
- Existing limitations in v1.1 for exact mesh intersection, optimized
  silhouette with holes and crash reconstruction remain.

## Gating for tagged 1.2 release

- Merge CI-green functional PR #39 into main.
- Verify final version manifest + lock + README + notes consistent at 1.2.0.
- Require completed successful Python/Blender matrix, npm checks and
  nonpublishing clean-install preflight on the exact main release commit.
- Build a fresh versioned ZIP + checksum + optional npm tarball, run clean
  install on that ZIP, then publish only the verified GitHub Release/tag.
- Optional npm publication requires separately configured authorization.
