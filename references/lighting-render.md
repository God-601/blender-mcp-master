# Lighting, camera and render

## Engine choice
- **Workbench**: instant, for topology/proportion checks.
- **EEVEE**: fast previews and stylized finals. Enable soft shadows, AO and bloom/screen-space reflections only if needed (names vary by version: EEVEE Next in 4.2+).
- **Cycles**: final photoreal renders. Use Denoise (OpenImageDenoise), 64 to 256 samples for finals, 16 to 32 for tests, adaptive sampling on, light-path bounces about 4 to 8. Use GPU if available (check `bpy.context.preferences.addons['cycles'].preferences`).

## Lighting recipes
- **Quick studio (3-point)**: Key area light about 45 degrees to the side and above (power 500 to 1500 W at 3 m), Fill 25 to 40 percent of key on the other side, Rim/back light behind to separate silhouette. Soft shadows = larger light size (1 to 3 m area lights).
- **Outdoor**: Sun (strength 2 to 5) + HDRI (`search_assets(source="polyhaven", asset_type="hdris")`, `import_asset(asset_type="hdris")`); HDRI strength about 1.
- **Interior**: portal-style area lights at windows (or sun through windows with Cycles), warm practical lights (2700 to 3500 K) vs cool daylight (5500 to 6500 K). Use Filmic/AgX view transform to avoid blown highlights.
- **Product shot**: large soft top light, gradient background, reflective floor or shadow catcher, neutral gray backdrop.
- **Stylized**: one strong directional light + ambient fill, simple color grading.

## Color management
- View Transform: **AgX** (4.x default) or Filmic; Look: Medium High Contrast for punch. `Standard` only for flat/unlit comparisons.
- Exposure: adjust until midtones read (histogram not clipped).

## Camera
- Focal length: 35 mm (environment/wide), 50 mm (neutral), 85 mm (product/portrait), 24 mm only for interiors.
- Frame the subject with the rule of thirds; keep horizon level; sensor fit consistent.
- Add subtle depth of field for products (`dof.use_dof`, focus on the object, f-stop 2.8 to 5.6).
- Resolution: 1920x1080 (preview), 2560x1440 or 4K (final); `resolution_percentage` 50 for quick tests.

## Turntable
- Empty at asset center, parent camera to empty, rotate empty 0 to 360 degrees over N frames (120 frames at 30 fps = 4 s loop), linear interpolation, camera slightly above looking down about 10 to 15 degrees.

## Checking results
- `look(mode="camera", shading="rendered", max_size=768)` for EEVEE/Workbench views. For Cycles final frames, render via script (`bpy.ops.render.render(write_still=True)`) to a file path, then `look(image="Render Result")` or the file path.
- Don't spend final-render time before blockout and materials are approved.
