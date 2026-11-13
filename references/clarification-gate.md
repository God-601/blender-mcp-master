# Design interview — understand the model before creating it

**P0 new-project decision gate.** Before substantial geometry, exporting,
irreversible changes, or paid generation, determine what the user actually
wants the asset to look like and how it will be used. Read the complete
brief, references and already-answered constraints first. Read-only discovery
of Blender and the scene is allowed at any point. **Before any scene mutation**,
resolve material ambiguities. **Do not repeat answered requirements** from the
user's brief or prior discussion.

## GENERAL KICKOFF — resolve gaps in a new brief

Ask zero questions when the brief resolves every consequential choice or the
user delegates the remaining design decisions. Record any editable defaults
and proceed through scene protection and planning.

When the brief leaves a consequential gap, ask a specific question. If several
independent choices are open, group multiple specific questions in a short list. Typical ranges for
underspecified briefs are **2–3** for a simple prop, **4–6** for a moderately
complex asset and **5–8 across one or two rounds** for a character, building,
hero asset or multi-part scene. The actual gaps determine the number.

Choose the most important *unanswered* dimensions:
1. **Purpose and target:** gameplay/Roblox/other engine, animation, static
   prop, cinematic render, 3D print; camera distance, file deliverables.
2. **Visual style and references:** realistic, stylized, low-poly, exact
   game/franchise *style attributes*; ask for reference images or descriptions,
   and what elements to emulate, not copy protected assets.
3. **Silhouette and proportions:** overall shape, approximate dimensions,
   dominant masses, symmetry/asymmetry, distinctive parts or variant.
4. **Materials and colors:** wood/metal/fabric/weathering, texture resolution,
   hand-painted/PBR, intended palette, details and visual complexity.
5. **Construction and technical limits:** polygon budget, separate parts,
   UVs, rigging, LOD, pivot, scale, collision, constraints of a destination.
6. **Priority/tradeoffs:** accuracy vs performance, silhouette vs details,
   hero object vs background, must-have/must-avoid visual traits.

**No duplicate questions.** Remove any category already answered. Engine,
dimensions and triangle budget may be settled while color, material or
silhouette preferences still need input. Ask only about the remaining gaps
that would materially change the asset.

**Never ask "posso seguir?", "pode prosseguir?", "is that OK?" or equivalent
as a design question.** If the user says "you choose", make a coherent choice
and record it in the brief. Ask for approval only when an action separately
requires authorization.

Wait for answers to the initial meaningful questions before scene mutation.
Then update a compact **Design Brief**: known values, user choices, agent
editable assumptions, critical unknowns and acceptance evidence. Ask a
**second short round (1–3 questions) only when replies expose a consequential
new ambiguity**. For non-blocking omitted items, choose safe editable defaults
and state them; do not restart an interview just to fill every field.

**When you continue the existing project:** do NOT run the interview again for a
requested correction, export retry, post-crash recovery, or follow-up on
previously approved asset; reuse established decisions and ask only genuinely
new high-impact questions.

## How to tailor the conversation

| Missing requirement | Ask | Why |
| --- | --- | --- |
| Concept/subject unclear | "Que tipo de árvore é — pinheiro, carvalho ou algo fantástico? Qual referência visual devo seguir?" | Species changes silhouette and branching |
| Low-poly game prop, style missing | "Qual visual você prefere: blocado, facetas suaves ou pintado à mão? Tem uma referência?" | Topology and materials change |
| Realtime target, purpose unclear | "Vai aparecer de perto ou como cenário? Precisa de colisão ou animação?" | Determines scale/detail/pivots |
| Mechanical prop without dimensions | "Quais medidas e folgas precisam ser exatas?" | Prevents fictional fits |
| Character | "Qual anatomia/silhueta, roupa, expressão e pose? Vai animar?" | Shape + topology + rig |
| Finish unspecified | "O metal deve parecer novo, pintado ou envelhecido?" | Affects surface appearance |
| Delegation | No new question if meaningful choices explicitly delegated | Respect user autonomy |

### Example — low-poly Roblox tree

Already known: 2,000 evaluated triangles max, light PBR texture, Roblox.
A useful kickoff is:

> Para a árvore, me diga só algumas coisas sobre o visual:
> 1. Qual espécie ou formato de copa você imagina?
> 2. O tronco deve ser mais reto ou retorcido? Copa densa ou com espaços?
> 3. Prefere tons mais realistas ou um visual levemente estilizado?
> 4. Tem alguma imagem ou jogo de referência para eu seguir?

Notice that none of these repeats the triangle budget, engine or texture style.
Do not finish with "posso começar?" — take the answers into the plan.

### Example — high-detail sword

> 1. A espada deve parecer histórica, fantasia ou sci-fi?
> 2. Como você imagina a lâmina (reta, curva, larga, fina) e o comprimento?
> 3. Quais materiais/cores e nível de desgaste?
> 4. O detalhe mais importante é lâmina, guarda, cabo ou ornamentos?
> 5. Ela será vista de perto em jogo ou usada em render?

## Severity and permissions

| Class | Meaning | Action |
| --- | --- | --- |
| **BLOCKER** | Contradictory scope, required fit/tolerances, unknown export target that changes deliverable, paid cost or overwrite | Stop. Ask focused questions, record answers. |
| **QUALITY-RISK** | Missing reference, silhouette, material or priority that would produce materially different assets | Ask about it if the user has left the decision open. |
| **OPTIONAL** | Small decorative/bevel/camera details after core brief resolved | Use editable defaults and report them. |

Explicit approval is **still required for destructive edits, overwrites,
paid operations or replacing user-owned data**. That separate safety
authorization is never substituted by answered artistic questions.

## Acceptance

- An ambiguous brief elicits specific questions before mutation. A complete
  brief or explicit delegation elicits zero design questions.
- If the user has answered an element already, it does not reappear.
- Responses change a written design plan and modeling choices.
- Repeat instructions/follow-ups use the existing brief without resetting it.
- Missing real blockers stop edits; delegated minor details do not cause loops.
- Logs/snapshots/visual and engine validations still remain independent of
  whether the questions were answered.

See `references/modeling-quality-loop.md`, `references/p0-integrity.md`,
and `references/visual-inspection.md` for the downstream quality gates.
