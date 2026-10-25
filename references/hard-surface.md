# Hard-surface modeling (furniture, tools, weapons, vehicles, machines)

## Workflow
1. **Blockout** with primitives (cubes, cylinders) at real dimensions. Name each part. `look(mode="angles")`.
2. **Primary forms**: refine each part so the silhouette is right. Use Mirror modifiers (axis X, `use_clip=True`, small merge threshold) for symmetric objects: model one half only.
3. **Secondary forms**: panel lines, inset details, holes. Prefer Boolean (non-destructive, `solver='EXACT'` for quality, `'FAST'` for speed) with cutter objects hidden from render (`display_type='WIRE'`, `hide_render=True`).
4. **Bevel**: Bevel modifier, `limit_method='ANGLE'`, `angle_limit=radians(30)`, `segments=2` or 3, `harden_normals=True`.
5. **Shading**: smooth shading + Weighted Normal modifier (keep_sharp, mode 'FACE_AREA') or Smooth by Angle. Placed AFTER Bevel in the stack.
6. **Cleanup / apply** only at the end (or per export needs).

## Modifier stack order (typical)
Mirror -> Array -> Boolean -> Solidify -> Bevel -> Weighted Normal (or Smooth by Angle) -> Triangulate (export only).
Subdivision Surface goes before Bevel only for deliberate rounded forms; for hard-surface prefer bevel + support loops.

## Rules
- Parts that move (doors, wheels, drawers, lids): separate objects with the **origin at the pivot**.
- Fasteners (screws, rivets, bolts): model one, instance (linked duplicates), unless close-up hero.
- Never boolean dense meshes against dense meshes; keep cutters simple (8 to 16 sides for circles when low-poly).
- Keep circles at sensible side counts: 8 to 12 (game bg), 16 to 24 (mid), 32 to 64 (hero/render).
- Avoid thin slivers and sub-millimeter gaps that vanish at game scale; exaggerate small details slightly.
- Wear: add subtle edge wear via bevels + material (edge/curvature mask), not extra geometry.
- Interior of closed objects (inside a drawer, hidden faces behind panels) should be deleted for games.

## Typical proportion checks
- Chair: seat 0.45 high, back top 0.9 to 1.0, legs inset slightly from seat edge.
- Table: top thickness 0.03 to 0.05, leg width 0.05 to 0.08.
- Sword: blade length about 3 to 4x handle; cross-guard about 0.2 wide; pommel gives balance.
- Car: wheel diameter about 0.65 to 0.75 m; wheelbase about 2.7 m.

## Verification
`look(shading="wireframe")`, `get_scene_info(fields=["topology"])`, run `validate_asset.py`. Check z-fighting (coplanar faces), shading pinches, and inverted normals (`shading="material"` from inside/behind).
