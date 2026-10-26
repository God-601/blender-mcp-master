# Budgets and real-world sizes

Decide these BEFORE modeling and state the chosen numbers in your plan.

There are three kinds of number here, and they are not equally strict:
- **Platform limits** (for example the Roblox MeshPart cap of 21,844 triangles): hard. Never exceed them.
- **Project targets** (what this game, scene or client needs): set by the user or the destination. Ask or state an assumption; once chosen, stay within it.
- **Reference values in the tables below**: starting points. Adjust them for camera distance, how often the asset repeats, and how important it is. A hero prop may exceed a background default, and a distant plant should sit well under it.

## Triangle budgets (per single asset, rough guidance)

| Use | Hero / close-up | Mid-ground | Background / many copies |
|---|---|---|---|
| Mobile / Roblox | 1,500 to 5,000 | 300 to 1,500 | 50 to 300 |
| PC / console game | 10,000 to 60,000 | 2,000 to 10,000 | 200 to 2,000 |
| Playable character (PC/console) | 30,000 to 80,000 | - | - |
| Playable character (mobile/Roblox) | 3,000 to 10,000 | - | - |
| Offline render / film | no hard limit; keep subsurf-friendly quads | | |
| 3D print | watertight, wall >= 1 mm (FDM >= 1.2 mm) | | |

Roblox note: MeshPart limit is 21,844 triangles per mesh; keep far below it. Fewer, larger meshes with shared textures beat many small ones. Prefer 1 material per mesh.

## Texture budgets

| Use | Size per texture set |
|---|---|
| Small prop, mobile | 256 to 512 px |
| Standard prop | 1024 px |
| Hero prop / character | 2048 px |
| Terrain / hero close-up | 4096 px |

Always powers of two (256, 512, 1024, 2048, 4096). One texture atlas per asset family is better than many small textures. Use trim sheets and shared materials for environments.

## Material budget
- Props: 1 material (max 2).
- Characters: 1 to 3.
- Environments: reuse materials; target < 10 unique per scene section.

## Texel density (consistent resolution)
- Pick one density per project, e.g. 512 px/m (mobile) or 1024 px/m (PC), and keep UV islands proportional to world size across assets.

## Common real-world sizes (meters)

| Object | Size |
|---|---|
| Door | 0.9 x 2.05 |
| Standing human | 1.7 to 1.8 tall |
| Chair seat height | 0.45 |
| Table height | 0.75 |
| Kitchen counter | 0.9 |
| Bed (double) | 1.4 x 2.0 |
| Sofa seat height | 0.42, depth 0.9 |
| Stair step | 0.18 rise, 0.28 run |
| Car (sedan) | 4.5 x 1.8 x 1.45 |
| Coffee mug | 0.095 tall, 0.08 diameter |
| Smartphone | 0.15 x 0.07 x 0.008 |
| Street light | 5 to 8 tall |
| Tree (mature) | 8 to 20 tall |
| Room ceiling | 2.4 to 2.7 |

Roblox: 1 stud is about 0.28 m; a default avatar is about 5 studs (about 1.4 m) tall in R15 scale terms. When exporting for Roblox, confirm the user's scale convention and state it.

## Bevel size rule
Bevel width about 0.5 to 2 percent of the object's largest dimension (a 1 m object: 5 to 20 mm).
