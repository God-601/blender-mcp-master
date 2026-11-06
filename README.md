# Blender MCP Master

Agent Skill for planning, modeling and checking 3D assets in Blender.

![Concept illustration of the plan, model and verify workflow; not a Blender render](assets/banner.svg)

The skill provides instructions, task-specific references and inspection scripts. Live editing requires Blender and a **separate Blender-control MCP** with its addon. The optional resource server only reads project guidance.

## Install

```bash
npx skills add God-601/blender-mcp-master -g
```

Or download the [v1.4.0 ZIP](https://github.com/God-601/blender-mcp-master/releases/tag/v1.4.0), verify it with `SHA256SUMS.txt` and install its inner `blender-mcp-master` folder in your agent's skills directory. See the [setup guide](docs/QUICKSTART.md).

Connect your Blender-control MCP, check the available tools and inspect the scene before editing.

## Use

> Use Blender MCP Master to create a low-poly chair in a new collection. Preserve existing objects, show front and side views, check geometry and UVs, and report what remains unverified.

The agent starts with [SKILL.md](SKILL.md) and loads only the references needed for the task. It plans the asset, models in an owned collection, inspects the result and reports evidence. Use the [quality checklist](references/quality-checklist.md) for delivery. A Blender check does not prove appearance or performance in a game engine.

## Optional resource server

```bash
npx -y github:God-601/blender-mcp-master
```

This serves references over MCP. It does not control Blender.

## Português

Skill para orientar agentes na modelagem e verificação de assets 3D no Blender. Instale com `npx skills add God-601/blender-mcp-master -g` ou pelo [ZIP da v1.4.0](https://github.com/God-601/blender-mcp-master/releases/tag/v1.4.0). Para editar a cena, conecte separadamente um MCP de controle do Blender. Veja o [guia de instalação](docs/QUICKSTART.md).

O servidor opcional `npx -y github:God-601/blender-mcp-master` fornece referências somente para leitura. Comece por [SKILL.md](SKILL.md) e entregue os resultados com evidências conforme a [lista de verificação](references/quality-checklist.md).

[Licença MIT](LICENSE) · [Notas da v1.4.0](docs/release-notes-1.4.md)
