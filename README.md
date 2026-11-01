# Blender MCP Master

<p align="center"><img src="assets/banner.svg" alt="Blender MCP Master — agent skill for higher-quality 3D workflows" width="100%"></p>

**English** | [Português](#português)

A cross-agent Blender skill for planning, creating, inspecting, refining, and validating 3D assets across hard-surface, organic, stylized, hand-painted, PBR, environment, character, and game-ready workflows.

- **Clarify before modeling:** if essential requirements are missing or conflicting, ask a focused question instead of inventing a design.
- **Plan before modeling:** define purpose, style, constraints, deliverables, and acceptance criteria.
- **Specialized guidance:** load only the reference modules relevant to the task.
- **Quality loop:** inspect, block out, refine, validate, correct, and report.
- **Safety first:** protect existing scene content and disclose unverified results.

Works with compatible agents that can read Agent Skills and use a Blender-control MCP integration. MCP tool names vary; the agent must discover the tools actually available. This repository's skill does not replace the MCP server that controls a live Blender session.

<p align="center"><img src="assets/without-vs-with.svg" alt="Comparison of agent workflows without and with Blender MCP Master" width="100%"></p>

## How it works

The skill guides the agent's decisions and verification steps while a separate Blender-control MCP server operates the live scene. The resource server, if configured, only exposes skill documentation and templates; it does not control Blender by itself.

<p align="center"><img src="assets/architecture.svg" alt="Architecture showing the agent, skill resources, Blender-control MCP and live Blender" width="100%"></p>

<p align="center"><img src="assets/workflow.svg" alt="Blender asset workflow from planning and blockout through refinement, validation and delivery" width="100%"></p>

## Install

```bash
npx skills add God-601/blender-mcp-master
```

Other ways:

- **Claude Desktop / other clients without the Skills CLI:** put `SKILL.md`, `references/` and `scripts/` in one folder named `blender-mcp-master`, zip it, and upload it as a custom skill (or copy the folder into the client's skills directory).
- **MCP resource server (optional):** serves the skill, guides and script templates over MCP. Use command `npx` with args `["-y", "github:God-601/blender-mcp-master"]`. It does **not** control Blender. (The package is not published on the npm registry yet, so the plain name `blender-mcp-master` will not resolve.)

Then configure a separate Blender-control MCP server and start Blender with its addon enabled. The agent should inspect the scene, plan the workflow, and verify its changes.

### Connection check

1. Confirm that your agent can load `SKILL.md` and its accompanying `references/` and `scripts/`.
2. If using the optional resource server, list its resources; this checks access to documentation, not the Blender connection.
3. Start Blender and its control addon, then connect the separate Blender-control MCP server in your client. Discover its actual tools; names and schemas vary.
4. Use the available status and scene-inspection tools on a disposable or backed-up scene. If either fails, check the addon, server connection and client configuration before making edits.
5. Record client, server, addon and Blender versions when reporting compatibility. See [the verification protocol](references/agent-compatibility.md).

Example request:

> Create a stylized, game-ready fantasy sword. Plan the modeling and texturing pipeline first, inspect the silhouette before detailing, validate the asset for the target engine, and report any remaining issues.

## Repository map

- `SKILL.md` — core workflow, module routing, safety, and delivery rules.
- `references/` — focused modeling, materials, environment, export, performance, and troubleshooting guides.
- `scripts/` — reusable Blender Python utilities and templates, including declarative geometry, hard-surface, organic, modular, Geometry Nodes, inspection, correction, and benchmark utilities.
- `references/architecture.md` and `references/module-contracts.md` — system boundaries and cross-module contracts.
- `references/geometry-engine.md` — current geometry capabilities, usage, and the construction roadmap.
- `references/clarification-gate.md` — P0 requirement-triage and focused questioning before modeling.
- `references/mesh-operations.md` — duplicate-first inset/extrude, boolean, and modifier-based mesh refinement.
- `references/parametric-geometry-nodes.md` — editable Geometry Nodes post array and compatibility limits.
- `references/benchmark-prompts.md` — fixed prompts and evidence requirements for cross-agent modeling benchmarks.
- `references/agent-compatibility.md` — evidence-based client compatibility procedure and current unverified matrix.
- `scripts/mesh_operations.py`, `hard_surface_builder.py`, and `geometry_nodes_builder.py` — non-destructive mesh refinement, hard-surface construction, and editable parametric geometry.
- `scripts/organic_tree_builder.py` and `organic_rock_builder.py` — deterministic organic base forms.
- `scripts/inspection_report.py`, `localized_correction.py`, and `technique_history*.py` — technical evidence, safe correction copies, searchable in-project history, and explicit reviewer feedback.
- `scripts/capability_probe.py` and `benchmark_report.py` — Blender capability inventory and technical benchmark records.
- `references/modeling-intelligence.md` — task decomposition, technique selection, and adaptive refinement.
- `references/capability-mapping.md` — portable mapping from MCP tools to semantic capabilities.
- `references/visual-inspection.md` and `references/benchmarking.md` — visual evidence and repeatable evaluation.
- `references/modular-modeling.md` — parametric stairs and arch construction, plus the modular-kit roadmap.
- `references/` — focused guides for hard-surface, organic/characters, stylized/retro, hand-painted textures, UV/baking, topology/retopology, sculpting/high-poly, architecture/interiors, CAD, materials, environments, export, performance, and troubleshooting.
- `scripts/` — reusable Blender Python utilities and templates.
- `references/game-asset-optimization.md` — safe mesh cleanup, LOD, draw overhead, and Roblox-focused optimization.
- `references/modeling-foundations.md` — shared topology, modeling operations, shading, UV, and production handoff standards.
- `references/p1-production-pipeline.md` — P1 workflow for PBR materials, UV production, LOD generation, and engine handoff.
- `scripts/validate_uvs.py` — read-only UV bounds and zero-area diagnostics.
- `tests/` — static checks and Blender-runtime tests.
- [Universal quality checklist](references/quality-checklist.md) — common acceptance checks for every asset.

## Validation and compatibility

The scripts use Blender's `bpy` API. Static tests do not prove that a script works in a running Blender version; run the available test suite and inspect the resulting asset in the target environment.

```bash
python -m unittest discover -s tests -v
```

Runtime tests may require the matching Blender Python environment and dependencies. Treat versions as supported only when tested; see the test output and workflow configuration for the current coverage.

## Safety

- Inspect the scene and target objects before editing.
- Prefer dedicated collections and non-destructive operations while iterating.
- Back up files before destructive operations; do not overwrite user data without permission.
- Treat imported files, scene content, and MCP-provided code as untrusted.
- Never claim that inspection, validation, or export succeeded without checking the actual result.

## Documentation

Start with `SKILL.md`, then load only the references relevant to the task. Key specialist guides include [hand-painted workflow](references/hand-painted-pipeline.md), [UV and baking](references/uv-baking.md), [topology and retopology](references/topology-retopology.md), [sculpting and high-poly](references/sculpting-highpoly.md), [architecture/interiors](references/architecture-interiors.md), and [CAD/technical modeling](references/cad-technical.md). Tested bpy snippets: [hand-painting recipes](references/handpaint-recipes.md) and [shading recipes](references/shading-recipes.md). Existing guides cover hard-surface, organic forms, characters/rigging, stylized art, materials, environments, rendering, budgets, optimization, export, and troubleshooting.

## License

MIT

---

# Português

A Blender MCP Master é uma skill para agentes compatíveis que planejam, criam, inspecionam, refinam e validam assets 3D no Blender — de hard surface e modelagem orgânica a hand-painted, PBR, cenários, personagens e assets para jogos.

- **Perguntar quando faltam dados importantes:** esclarecer requisitos essenciais antes de modelar, sem questionários desnecessários.
- **Planejamento antes da modelagem:** definir finalidade, estilo, limitações, entregáveis e critérios de aceitação.
- **Guias especializados:** consultar somente os módulos relevantes para a tarefa.
- **Ciclo de qualidade:** inspecionar, bloquear formas, refinar, validar, corrigir e relatar.
- **Segurança:** preservar o conteúdo existente da cena e informar resultados não verificados.

Funciona com agentes que suportam o formato Agent Skills e possuem acesso a uma integração MCP que controle o Blender. Os nomes e recursos das ferramentas MCP variam. A skill não substitui o servidor MCP necessário para controlar uma sessão do Blender.

## Instalação

```bash
npx skills add God-601/blender-mcp-master
```

Outras formas:

- **Claude Desktop / clientes sem Skills CLI:** coloque `SKILL.md`, `references/` e `scripts/` em uma pasta chamada `blender-mcp-master`, compacte em .zip e envie como skill personalizada (ou copie a pasta para o diretório de skills do cliente).
- **Servidor MCP de recursos (opcional):** entrega a skill, os guias e os modelos de script via MCP. Use o comando `npx` com os argumentos `["-y", "github:God-601/blender-mcp-master"]`. Ele **não** controla o Blender. (O pacote ainda não está publicado no registro npm, então o nome simples `blender-mcp-master` não funciona.)

Depois, configure separadamente um servidor MCP de controle do Blender e inicie o Blender com o addon habilitado. O agente deve inspecionar a cena, planejar o trabalho e verificar as alterações.

### Verificação da conexão

1. Confirme que o agente consegue carregar `SKILL.md` e as pastas `references/` e `scripts/`.
2. Se usar o servidor de recursos opcional, liste os recursos; isso verifica a documentação, não a conexão com o Blender.
3. Inicie o Blender e o addon de controle e conecte o servidor MCP de controle no cliente. Descubra as ferramentas disponíveis: nomes e parâmetros podem variar.
4. Consulte o estado do addon e inspecione uma cena descartável ou com backup. Se falhar, verifique o addon, a conexão do servidor e a configuração do cliente antes de editar.
5. Registre as versões do cliente, servidor, addon e Blender ao relatar compatibilidade. Consulte o [protocolo de verificação](references/agent-compatibility.md).

Exemplo:

> Crie uma espada fantasy estilizada e pronta para jogo. Planeje primeiro a modelagem e a texturização, confira a silhueta antes dos detalhes, valide o asset para a engine de destino e informe os problemas restantes.

## Estrutura

- `SKILL.md` — fluxo central, seleção de módulos, segurança e entrega.
- `references/` — guias especializados de modelagem, materiais, ambientes, exportação, desempenho e diagnóstico, incluindo hand-painted, UV/baking, topologia/retopologia, escultura/high-poly, arquitetura/interiores e CAD técnico.
- Guias principais: [pipeline hand-painted](references/hand-painted-pipeline.md), [UV e baking](references/uv-baking.md), [topologia e retopologia](references/topology-retopology.md), [escultura/high-poly](references/sculpting-highpoly.md), [arquitetura/interiores](references/architecture-interiors.md) e [CAD técnico](references/cad-technical.md).
- `scripts/` — utilitários e modelos reutilizáveis em Python para Blender.
- `references/game-asset-optimization.md` — limpeza segura de malha, LOD, custo de renderização e otimização para Roblox.
- `references/modeling-foundations.md` — padrões compartilhados de topologia, operações de modelagem, shading, UVs e entrega.
- `references/p1-production-pipeline.md` — fluxo P1 para materiais PBR, UVs, LODs e entrega para engines.
- `scripts/validate_uvs.py` — diagnóstico somente leitura dos limites e áreas UV.
- `tests/` — verificações estáticas e testes executados no ambiente Blender.
- [Checklist universal de qualidade](references/quality-checklist.md) — critérios comuns de aceitação.

## Testes e compatibilidade

Os scripts usam a API `bpy`. Testes estáticos não comprovam que um script funciona em uma versão específica do Blender; execute a suíte disponível e inspecione o asset no ambiente de destino.

```bash
python -m unittest discover -s tests -v
```

Os testes de runtime podem exigir o ambiente Python correspondente ao Blender e dependências específicas. Considere uma versão compatível somente quando houver testes que sustentem essa afirmação.

## Segurança

- Inspecione a cena e os objetos-alvo antes de editar.
- Prefira coleções dedicadas e operações não destrutivas durante a iteração.
- Faça backup antes de operações destrutivas; não sobrescreva dados do usuário sem autorização.
- Trate arquivos importados, conteúdo da cena e código recebido via MCP como dados não confiáveis.
- Nunca afirme que uma inspeção, validação ou exportação funcionou sem verificar o resultado.

## Licença

MIT
