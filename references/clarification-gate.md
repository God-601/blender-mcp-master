# Clarification gate — ask before modeling when information is insufficient

**Priority: P0 (pre-production decision gate).** A professional agent should not invent major requirements. Resolve critical ambiguity before constructing geometry, applying irreversible edits, commissioning paid generation, or exporting to a target platform. Apply this protocol after reading the request and any already-supplied context; scene inspection and capability discovery may be performed read-only if useful.

## 1. Assess the brief, not merely its length

Extract:
- **Asset/subject and scope:** what to build, which components/variants, whether it is a prop, scene, character or technical part.
- **Intended use and deliverables:** game/engine, animation, still render, 3D printing, CAD, or concept; file types.
- **Visual direction:** style, key references, silhouette, theme, expected detail/quality, important colors/materials.
- **Constraints:** dimensions/units, geometry budget, UVs/LOD, rigging/deformation, pivots, exact fit, target Blender/version if relevant.
- **Authority:** references and decisions from the current task, previous instructions and existing scene; user-specified values override defaults.

A request may be short but sufficient (e.g. "low-poly pine tree for a still render, around 3 m, choose a palette"). A request may be long but contradictory. Do **not** ask about facts the user already supplied.

## 2. Classify missing information

| Level | Signals | Action before modeling |
|---|---|---|
| **BLOCKER** | Subject/scope unclear; conflicting requirements; essential mechanical dimensions, fits, rig/engine compatibility or irreversible operation undecided; cost or overwrite needs approval | **Stop and ask** the smallest focused question that resolves the blocker. Do not silently assume. |
| **QUALITY-RISK** | Complex/hero asset with no visual style/reference, key proportions or intended use, where alternatives would create materially different models | **Prefer a brief question** before substantial work. If the request explicitly delegates creative direction, select and state an art direction rather than questioning. |
| **OPTIONAL** | Minor palette, bevel thickness, camera angle, decorative details, modest budgets for exploratory assets | Choose a safe editable default, disclose it, proceed; offer refinement later. |

A reference image can answer style/proportion questions. When available, inspect it first and ask only about what is still unresolved. Reference retrieval is not a reason to ignore user-provided constraints.

## 3. Ask better questions

- **Ask before building** when critical information is missing; do not complete a speculative asset first.
- Default to **one focused question** addressing the highest-impact uncertainty. If several *independent, essential* choices are missing, ask a short grouped set (usually 2–3), allowing partial answers. Never send a long questionnaire for a simple request.
- Present concrete, non-leading options or a recommended default when that helps the user decide; allow "choose for me".
- Explain the impact in a short clause (for example, game-ready topology differs from a cinematic render).
- Avoid asking the user to specify implementation details the agent should know (exact modifier settings, loop counts, normal workflow) unless the user demands them.
- Never ask the same question twice if it has already been answered in the request or connected project context.
- **After the answer**, update the production brief and acceptance gates; do not restart the interview. If no reply exists, do not claim the scene was built.

## 4. Example prompts

**Too vague:** "Make a realistic car."

Ask: "Is this car for a real-time game or a close-up render? That changes polygon density, UV work and detail." If the use is clear but the design isn't: "Do you have a model/reference or should I create an original design?"

**Character:** "Make a character."

Ask: "Will this character need to be animated, and what style should it follow (realistic, stylized or low-poly)?" For a stylized static bust request with style specified, proceed without extra questions.

**Technically constrained:** "Model this mechanical mount for 3D printing."

Ask for dimensioned drawing or critical mounting dimensions/tolerances **before** building a production part; never invent load-bearing fits.

**Sufficient:** "Create a 3 m low-poly pine tree for a game; green palette; 800 triangles max; Blender file."

Proceed directly. Optional leaf layout, branch count and bevel sizes are agent decisions; validate evaluated triangles.

**Delegated choices:** "Surprise me with a detailed fantasy house and choose the art style."

Proceed with a declared design direction, inspect silhouette and follow the professional quality loop.

## 5. Expected agent response format

When blocked, ask conversationally:

```text
To model this for [use/goal], I need [one decision]:
[focused question, optionally with examples / choose-for-me]
```

When proceeding with assumptions, include one concise sentence:

```text
I'll use [stated assumptions] for [reason]; they remain editable.
```

This gate is separate from **visual verification**. Even with an excellent brief, a successful tool call does not make visual quality PASS. See `references/professional-modeling-standards.md` and `references/modeling-quality-loop.md`.
