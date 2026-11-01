# P0 — Blender scene and file integrity

The default workflow is **copy first, verify, then approve**. A script reporting
PARTIAL is not a safe final result. Test user data in a separate scratch Blender
project first, and inspect the resulting .blend in the actual MCP session.

## Mutator protocol
1. Discover Blender version, scene, and object/data ownership. Review the object
   names and export destination before any tool call that changes state.
2. Scope targets explicitly. Do not use global selection, run cleanup across all
   objects, rename user objects, or change workspace settings as defaults.
3. Run `cleanup_mesh.py`, `apply_and_origin.py` and `bevel_and_shade.py`
   in their **copy-first** modes. Compare the output to the original, run
   `inspect_geometry.py`, and obtain a viewport view when possible.
4. Only commit in-place when the user explicitly authorizes the objects,
   purpose and potential loss. Set the opt-in flags only in that case.
5. For PBR changes, only update owned materials. Reject shared or unexpected
   material users and do not silently overwrite another project's node graphs.
   Material updates use a staged copy and rollback of mesh material slots.
6. For `setup_scene.py`, changing units, render engine, active collection and
   viewport clipping is optional; preserve user cameras/lights and rollback on errors.
7. `export_asset.py` must receive a destination and explicit mesh targets.
   Existing FBX/GLB/OBJ files require `OVERWRITE=True`. OBJ and companion MTL
   are committed together with rollback, not as separate best-effort writes.
   Static exports must reject unsupported armature/shape key targets.
8. Record the actual result: SUCCESS, PARTIAL, ERROR, NOT VERIFIED. Do not label
   an untested export or a visually uninspected mesh production-ready.

## Limitations
- These guards reduce accidental edits; they are not a full Blender undo journal.
  Direct manual script edits or MCP tool commands outside these templates may
  still alter or delete user objects.
- In-place changes create recovery mesh datablocks in the Blender project when
  supported; they are **not** a saved backup file. Save a separate .blend
  before destructive work.
- No cross-process crash/power-loss guarantee, and filesystem commits are only
  atomic within the filesystem where their temporary files are staged.
- Complex rigs, animation, UV bakes, physical fits and engine-specific material
  round trips require specialized validation. Technical tests cannot certify art.

## Regression evidence
Tests `test_p0_integrity_runtime.py`, `test_p0_transactional_runtime.py`,
`test_p0_material_setup_runtime.py`, and `test_p0_final_edges_runtime.py`
include deliberate failure injection and source-preservation assertions.
Run the full Blender matrix and npm checks in GitHub Actions before merge.
