# Roblox Studio real-world import inspection

This is an operator-driven test, **not** a claim that ChatGPT has
remote control of an open Roblox Studio window.

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
