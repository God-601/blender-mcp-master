# Roblox Studio real-world import inspection

An actual Studio MCP campaign is recorded in
[V2-CAMPAIGN-2026-11-08.md](../../docs/V2-CAMPAIGN-2026-11-08.md).
It found scalar shader-color loss on the tested Open Cloud path and a
constant-texture encoding issue. The isolated `constant_pbr_fixture.py`
example preserves the source and creates correctly encoded color/data maps
for that controlled case; it does not bake arbitrary node graphs.

The audit script is read-only. Run it from the Command Bar or a connected
Studio MCP; it does not import or upload files by itself. The manual recipe
below is a fallback when a compatible connector is unavailable.

1. Export a real Blender model (ideally GLB) with fixed units, UVs,
   mesh/object names and triangle counts. Save file SHA256 separately.
2. In Roblox Studio use **File > Import 3D** (or the 3D Importer available
   in your Studio version). Choose the GLB; inspect the importer preview
   and complete import.
3. In **Explorer**, select the resulting Model or MeshPart.
4. Open **View > Command Bar**, paste the full
   `integrations/roblox/studio_mesh_audit.lua` and run it once.
5. Save the three-line output from the Studio Output panel, beginning
   `BLENDER_MCP_STUDIO_MESH_AUDIT_BEGIN`. Compare reported MeshPart sizes,
   material/texture presence and collision settings with the Blender
   preflight report.
6. Manually inspect Studio front/side/3/4 screenshots, actual material
   appearance, orientation, pivot and physical collisions in a temporary
   test place. Re-export/reimport after any corrections.

The script is **read-only** and inspects selected instances only. It does
not upload assets, alter collisions, auto-test physics, infer Blender
SHA256, compare pixels, measure FPS or certify engine integration by
metadata alone. Actual user-saved Studio screenshots and original
Blender exports are required to support visual matching.

**Expected receipt:** source Blender file checksum; exported GLB checksum;
Studio version; selected MeshPart audit output; screenshot evidence from
Studio and Blender; notes on scale/UV/material/physical-collision results.
When evidence is missing use **NOT VERIFIED**.
