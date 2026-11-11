# Real Godot 4 GLB import check

This optional integration runs **inside a real Godot executable**, unlike the
Blender-to-Blender GLB roundtrip. Godot 4.4+ is recommended. It deliberately
does not load/render a game world, write files or claim collision/material
fidelity, animation, FPS or visual quality.

## Run

1. Export your static asset to an absolute `.glb` path from Blender.
2. Install Godot 4 and run in a terminal (adjust the executable name):

```sh
godot --headless --path integrations/godot --script res://gltf_import_probe.gd -- /absolute/path/model.glb
```

For Windows PowerShell:

```powershell
& "C:\\Path\\To\\Godot_v4.exe" --headless --path integrations/godot --script res://gltf_import_probe.gd -- "C:\\Assets\\model.glb"
```

3. Save the console output. A successful run emits
`BLENDER_MCP_GODOT_IMPORT_BEGIN` and `BLENDER_MCP_GODOT_IMPORT_END`
with `status=IMPORTED_GEOMETRY`, an actual Godot version, and mesh/surface,
triangle, UV and material presence counts. A nonzero exit indicates failure.

4. Record actual exported file SHA256, Blender version, reference images and
independently inspected Godot screenshots if the claim needs visual fidelity.

This is a **real importer smoke test**, not a certificate that the model
looks identical to Blender, is game-ready, has correct collision or meets
frame-rate targets. Unity, Roblox Studio and Unreal still require their own
import tests; never substitute this Godot result for another engine.

Reference:
[Godot 4 GLTFDocument](https://docs.godotengine.org/en/4.5/classes/class_gltfdocument.html).

## Animated fixture

Export a weighted two-bone sample in disposable Blender and measure imported
pose motion in Godot:

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python integrations/godot/blender_animation_fixture.py -- /absolute/path/animated.glb
godot --headless --path integrations/godot --script res://animation_probe.gd -- /absolute/path/animated.glb
```

The probe reports imported skeleton and clip counts and sampled bone motion.
Rendered skin deformation and physics require their own destination tests.
