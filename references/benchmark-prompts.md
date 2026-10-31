# Standardized modeling benchmark prompts

Use the same prompt text, reference image, starting scene, Blender version, and camera framing across agents. Do not modify prompts mid-comparison; increment the prompt version when changing them.

## B01 — Stylized chair

Create a complete stylized low-poly chair. Include seat, backrest, four legs, and any structural supports needed. Prioritize readable silhouette, believable proportions, aligned parts, clean intersections, and a coherent material palette. Do not add decorative details until the blockout passes front, side, and three-quarter inspection.

## B02 — Fantasy sword

Create a stylized fantasy sword with a distinct blade silhouette, guard, grip, and pommel. The blade must read clearly from front and side. Keep the guard centered, grip aligned to the blade axis, and components joined or intentionally separated. Use bevels only where they improve light readability.

## B03 — Organic rock

Create an irregular stylized rock with a stable grounded base, varied planes, asymmetrical silhouette, and no obvious primitive-sphere appearance. Use controlled deformation rather than arbitrary noise. Inspect front, side, top, and three-quarter views.

## B04 — Low-poly house

Create a compact low-poly house with walls, roof, door, windows, and a readable entrance. Keep roof overhangs consistent, openings aligned, and the structure grounded. Use modular construction where repetition helps.

## B05 — Stylized creature

Create a simple stylized creature with a clear primary body mass, head, limbs or appendages appropriate to the concept, and readable front/side silhouettes. Prioritize proportions and attachment points over surface detail.

## Required run record

- benchmark ID and prompt version
- agent/client and model, only when known
- MCP server/version and discovered capabilities
- Blender version
- exact task prompt and reference identifiers
- execution time and any tool errors
- target object names and technical report
- front, side, and three-quarter captures (plus detail/wireframe when relevant)
- visual rubric scores 0–4 with evidence and reviewer notes
- known issues and NOT VERIFIED checks

A benchmark report script can collect technical metrics, but visual scores must be supplied by an actual reviewer or a documented vision-capable inspection step. Never infer visual quality from polygon counts.
