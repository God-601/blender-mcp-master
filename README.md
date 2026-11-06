# Blender MCP Master

Agent Skill for planning, building and checking 3D assets in Blender.

<p align="center"><img src="assets/banner.svg" width="100%" alt="Concept illustration showing the skill's plan, model and verify workflow; it is not a Blender render"></p>

Blender MCP Master gives an AI agent task-specific modeling guidance, inspection scripts and a way to report what it actually verified. It covers props, low-poly and organic assets, environments, characters, UVs, materials and game export. The agent reads [SKILL.md](SKILL.md) first, then opens only the references needed for the job.

**Connection required:** this skill does not operate Blender on its own. Live scene work requires Blender and a separately configured Blender-control MCP server and addon. The optional resource MCP server in this repository provides read-only documents and scripts; it cannot edit a scene.

## Install the skill

With the [Skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add God-601/blender-mcp-master -g
```

Or download the [v1.4.0 release ZIP](https://github.com/God-601/blender-mcp-master/releases/tag/v1.4.0) and its `SHA256SUMS.txt`, verify the checksum, then copy the extracted inner `blender-mcp-master` folder to your agent's skills directory. See the [Windows and agent setup guide](docs/QUICKSTART.md) for paths and commands.

Connect your Blender-control MCP separately, confirm its available tools and Blender version, and inspect the current scene before editing. Start with a scratch scene or a backed-up `.blend`.

## What the skill does

| Stage | Agent behavior | Evidence to keep |
| --- | --- | --- |
| Scope | Establish purpose, reference, proportions, destination and missing design choices. | Brief, constraints and scene baseline |
| Model | Build in an owned collection; check silhouette before detail. | Named objects and inspected views |
| Inspect | Check evaluated geometry, UVs, materials, fit and export budgets where relevant. | Measurements and actual viewport views |
| Deliver | Correct observed defects and distinguish verified results from open questions. | Output paths and `PASS / ISSUE / N/A / NOT VERIFIED` |

<p align="center"><img src="assets/workflow.svg" width="100%" alt="Workflow from clarification through modeling, inspection and correction"></p>

The [quality checklist](references/quality-checklist.md) defines the delivery checks. A Blender round trip or a numeric mesh check cannot establish visual quality, collision behavior or performance in every target engine. Report each of those separately.

## Use it with an agent

After installation and Blender-control setup, try:

> Use Blender MCP Master to inspect my current Blender scene. Create a low-poly wooden chair in a new collection without changing existing objects. Show front, side and three-quarter views, check geometry and UVs, and list what remains unverified.

The skill's [entrypoint](SKILL.md) routes the agent to a guide for the task. Useful starting points are [hard-surface modeling](references/hard-surface.md), [organic modeling](references/organic.md), [stylized low-poly](references/stylized-lowpoly.md), [UV and baking](references/uv-baking.md), and [game export](references/game-ready-export.md). The available operations depend on the connected Blender tools and installed Blender version.

<p align="center"><img src="assets/architecture.svg" width="100%" alt="Agent Skill, read-only resource server and separate Blender-control MCP roles"></p>

## Optional resource server

If you want your agent to browse this repository's references through MCP, run the source package as a stdio resource server:

```bash
npx -y github:God-601/blender-mcp-master
```

This command is separate from skill installation. It does not provide scene-control tools. The [quickstart](docs/QUICKSTART.md) explains the setup and the [resource catalog](references/resource-catalog.md) lists the guides and scripts.

## Project and verification

The current source is v1.4.0. The [release notes](docs/release-notes-1.4.md) describe its tested scope, including Blender runtime checks and a Godot GLB fixture import. Those checks are narrower than validation of an arbitrary asset in a game.

Run repository checks with `python -m unittest discover -s tests -v` and `npm test`. Some Python tests need a compatible `bpy` runtime. [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [MIT license](LICENSE)

---

<a id="portugues"></a>
# Português

Blender MCP Master é uma skill para orientar agentes na criação e verificação de modelos 3D no Blender. Ela fornece instruções, referências e scripts de inspeção. Para editar uma cena ao vivo, é preciso instalar o Blender e conectar separadamente um Blender-control MCP compatível.

- **Instale a skill:** `npx skills add God-601/blender-mcp-master -g` ou baixe o [ZIP da v1.4.0](https://github.com/God-601/blender-mcp-master/releases/tag/v1.4.0), confira o SHA-256 e copie a pasta interna para o diretório de skills do seu agente.
- **Configure o Blender:** conecte o MCP de controle, confira as ferramentas disponíveis e inspecione a cena antes de alterar objetos. Veja o [guia de instalação](docs/QUICKSTART.md).
- **Use com um agente:** informe a referência, o destino e as restrições do modelo. O agente deve planejar, modelar em uma coleção própria, inspecionar e relatar `PASS / ISSUE / N/A / NOT VERIFIED` conforme as evidências.
- **Servidor opcional:** `npx -y github:God-601/blender-mcp-master` oferece recursos de leitura via MCP; não controla o Blender.

Consulte [SKILL.md](SKILL.md), a [lista de verificação](references/quality-checklist.md) e as [notas da v1.4.0](docs/release-notes-1.4.md).
