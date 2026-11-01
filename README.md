# Blender MCP Master

<p align="center">
  <img src="assets/banner.svg" width="100%" alt="Blender MCP Master — illustrated isometric modeling workspace and wireframe geometry">
</p>

<p align="center">
  <a href="#quick-start">English</a> · <a href="#português">Português</a> · <a href="SKILL.md">Skill</a> · <a href="references/quality-checklist.md">Quality checklist</a>
</p>

**Better decisions. Better meshes.** An open-source agent skill for Blender.

Plan the shape. Model in stages. Catch defects. Protect the scene. Explain what was actually verified.

<p align="center">
  <img src="assets/workflow.svg" width="100%" alt="Visual process: clarify, block out, refine, inspect, deliver; inspection loops back to corrections">
</p>

## Quick start

```bash
npx skills add God-601/blender-mcp-master
```

You also need a **separate Blender-control MCP** server and its Blender addon. This skill guides the agent; it does **not** connect to Blender by itself.

Without Skills CLI: copy `SKILL.md`, `references/`, and `scripts/` into your agent's skills folder.

**Optional documentation-only MCP:** `npx -y github:God-601/blender-mcp-master`. Not published to the npm registry; this command is **not** the Blender-control server.

## Under the hood

<p align="center">
  <img src="assets/architecture.svg" width="100%" alt="Agent reads this skill, calls a separate Blender-control MCP server and operates a live Blender scene">
</p>

| | What you get |
|---|---|
| **Ask first** | Clarifies missing requirements; doesn't interrogate a complete brief. |
| **Build deliberately** | Hard-surface, organic, stylized, architecture, UVs and game assets. |
| **Review the result** | Evaluated mesh checks, visual checkpoints and targeted corrections. |
| **Keep control** | Explicit targets, cautious edits and honest verification statuses. |

**Start here:** [SKILL.md](SKILL.md) · [Modeling standards](references/professional-modeling-standards.md) · [Clarification gate](references/clarification-gate.md) · [Examples](references/production-recipes.md) · [Compatibility](references/agent-compatibility.md)

## Test it

```bash
python -m unittest discover -s tests -v
```

Blender runtime tests need a compatible `bpy` installation. Passing tests does **not** prove artistic quality or live MCP compatibility. Verify models and exports in their target environments.

[MIT License](LICENSE) · [Issues](https://github.com/God-601/blender-mcp-master/issues)

---

# Português

**Modelagem com método, não no improviso.** Uma skill aberta para agentes que trabalham com Blender por MCP.

O agente pergunta quando falta informação, planeja, modela em etapas, inspeciona a geometria e informa o que realmente conseguiu verificar.

## Comece aqui

```bash
npx skills add God-601/blender-mcp-master
```

É necessário configurar **separadamente o Blender-control MCP** e o addon no Blender. A skill orienta o agente; ela não controla o Blender sozinha.

Sem Skills CLI: copie `SKILL.md`, `references/` e `scripts/` para a pasta de skills do seu agente.

**MCP opcional, apenas para documentação:** `npx -y github:God-601/blender-mcp-master`. Ainda não publicado no registro npm. Não substitui o MCP que controla o Blender.

## O que inclui

**Briefing inteligente** · **Modelagem orientada por referências** · **Inspeção técnica e visual** · **Correção controlada** · **Proteção da cena**

[Manual da skill](SKILL.md) · [Padrões profissionais](references/professional-modeling-standards.md) · [Quando perguntar](references/clarification-gate.md) · [Receitas de modelagem](references/production-recipes.md) · [Checklist de qualidade](references/quality-checklist.md)

**Testes:** `python -m unittest discover -s tests -v` — a execução com Blender exige `bpy` compatível. Testes técnicos não substituem uma revisão artística.

[Licença MIT](LICENSE)
