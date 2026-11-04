# Design interview — understand the model before creating it

**P0 new-project decision gate.** Before substantial geometry, exporting,
irreversible changes, or paid generation, determine what the user actually
wants the model to look like. The goal is a **useful multi-question design
conversation**, NOT a perfunctory "can I proceed?" permission request.
Read the complete user brief, references and already-answered constraints first.
Read-only discovery of Blender and existing scenes is allowed at any point. **Before any scene mutation**, collect the necessary answers. Always **do not repeat answered requirements** from the user's brief or prior discussion.

## GENERAL KICKOFF — several useful questions on every NEW project

For a genuinely NEW modeling assignment, summarize the known requirements in
two lines, then ask **multiple specific, independent design questions in a
conversational numbered or compact grouped format**. Default to **4–6**
questions for a moderately complex asset; **2–3** for a simple prop and
**5–8 across one or two rounds** for characters, architecture, hero assets
and multi-part scenes. Do not send 20 mechanical questions in a single wall
of text. Questions must improve the expected 3D result, not just fill a quota.

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

**No duplicate questions:** remove any category already answered. A brief
can be complete on engine, dimensions and triangle budget but still have
unanswered color, material and silhouette preferences. Ask the *remaining*
artistic questions rather than repeating specs. If truly every meaningful
choice is covered, or the user explicitly says "choose everything / surprise
me / no questions", make a brief editable plan and proceed. A new project
does not require pointless questions to satisfy a number.

**Never ask "posso seguir?", "pode prosseguir?", "is that OK?" or equivalent
as the sole design question.** The user's replies to the actual questions
are the design input, not an administrative approval ritual. If they say
"you choose", propose a coherent choice and move on. Do not repeatedly
ask for permission to start after the design details are known.

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
| Full brief, one visual choice missing | "O metal deve parecer novo, pintado ou envelhecido? Qual cor predomina?" | Genuine user preference |
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
| **QUALITY-RISK** | Missing reference, silhouette, material or priority that would produce materially different assets | Include in the multi-question design interview. |
| **OPTIONAL** | Small decorative/bevel/camera details after core brief resolved | Use editable defaults and report them. |

Explicit approval is **still required for destructive edits, overwrites,
paid operations or replacing user-owned data**. That separate safety
authorization is never substituted by answered artistic questions.

## Acceptance

- A new ambiguous 3D project elicits several specific, nonredundant design
  questions before mutation, rather than one generic permission question.
- If the user has answered an element already, it does not reappear.
- Responses change a written design plan and modeling choices.
- Repeat instructions/follow-ups use the existing brief without resetting it.
- Missing real blockers stop edits; delegated minor details do not cause loops.
- Logs/snapshots/visual and engine validations still remain independent of
  whether the questions were answered.

See `references/modeling-quality-loop.md`, `references/p0-integrity.md`,
and `references/visual-inspection.md` for the downstream quality gates.
