# Measured proportion examples — sword, table, vehicle

**Scope:** Editable Blender modeling *starting points*. Do not infer that these
numbers define all cars, swords or tables. Read the user's dimensions, purpose,
reference images and target engine first. If vital parameters are missing, apply
`references/clarification-gate.md`.

These examples revive numeric **art-blockout conventions** from
[`references/hard-surface.md` before PR #5](https://github.com/God-601/blender-mcp-master/blob/2bc6ab6841d28ea71aced74487481c5c5cce6ba5/references/hard-surface.md);
they were not verified as standards or universal dimensions. A direct dimension
specified by the user overrides every figure below.

| Example | Starting measurements | What to check |
|---|---|---|
| Stylized sedan | Wheel diameter 0.65–0.75 m, wheelbase about 2.70 m; demo body length 4.25 m and width 1.78 m | Wheel axle separation, tire radius, grounding, body silhouette, four independent wheel pivots, clearance |
| Decorative fantasy sword | Blade 3–4× grip length; guard about 0.20 m; demo 0.84 m blade / 0.24 m grip | Front/side silhouette, blade-handle alignment, guard size, thickness, end connections |
| Table / furniture | Top 0.03–0.05 m thick; leg width 0.05–0.08 m; demo height 0.75 m | Four ground contacts, legs meet underside, leg spacing, top dimensions and thickness |

## Vehicle: a measured blockout, not a finished car

Run `scripts/vehicle_proportion_example.py` via an available
`execute_blender_code` tool after inspecting Blender/scene capabilities.
Change `LENGTH`, `WIDTH`, `WHEELBASE`, `WHEEL_DIAMETER`,
`WHEEL_WIDTH` or `WHEEL_SEGMENTS` before executing. The script:
- makes a sealed body and sloping-cabin blockout;
- creates four independent 16-segment wheel meshes with origins at axle centers;
- uses **+X front, +Y left, +Z up**, in meters;
- preflights names/collection ownership and rolls back its own outputs after errors.

**Verify** center-to-center axle separation (wheelbase), wheel contact with
ground, overall length, roof silhouette and wheel-body relationship. A box body
above the tire tops is an *intentional simplified placeholder*, not a finished
wheel-well geometry, suspension or steering/rig. A 0.70 m wheel is NOT a
recommendation for trucks, toy cars or unusual designs.

For a game, check actual engine scale and constraints, moving wheel pivots,
collision and in-engine materials/exports. For manufacturing, Blender blockout
dimensions are NOT evidence of safe wheel fit or tolerances.

## Sword and table: two small measurable exercises

Run `scripts/prop_proportion_example.py` with `EXAMPLE="SWORD"` or
`EXAMPLE="TABLE"`. Both produce named separate components and keep unrelated
user objects untouched.

The sword's ratio is enforced only by **this demo**; a different weapon style
may need very different proportions. The demo is decorative geometry, not a
manufacturing, balancing, sharpness or structural specification.

The table uses four legs ending at the underside of the top and resting on
Z=0. A geometric joint/contact check does **not** prove load-bearing strength,
manufacturability or absence of close-up shading issues. Inspect the actual
asset and the brief.

## Production acceptance

Record `reference, scale convention, target_dimensions, measured_dimensions,
pivots, contact_checks, evaluated_triangles, visual_review, result`. Tests
verify the script geometry and repeatability, not professional artistic finish.
If viewport inspection or engine import was not run, report **NOT VERIFIED**
for those steps. Do not convert example numbers into rigid agent rules.
