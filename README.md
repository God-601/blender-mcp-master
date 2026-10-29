# Blender MCP Master

A cross-agent Blender skill for planning, creating, inspecting, refining, and validating 3D assets across hard-surface, organic, stylized, hand-painted, PBR, environment, character, and game-ready workflows.

- **Plan before modeling:** define purpose, style, constraints, deliverables, and acceptance criteria.
- **Specialized guidance:** load only the reference modules relevant to the task.
- **Quality loop:** inspect, block out, refine, validate, correct, and report.
- **Safety first:** protect existing scene content and disclose unverified results.

Works with compatible agents that can read Agent Skills and use a Blender-control MCP integration. MCP tool names vary; the agent must discover the tools actually available. This repository's skill does not replace the MCP server that controls a live Blender session.

## Quick start

1. Install or copy this repository's `SKILL.md` and relevant `references/` into the skills directory supported by your agent.
2. Configure a separate Blender-control MCP server and start Blender with its addon/extension enabled.
3. Ask the agent to create or modify an asset. It should inspect the scene, plan the workflow, and verify its changes.

Example request:

> Create a stylized, game-ready fantasy sword. Plan the modeling and texturing pipeline first, inspect the silhouette before detailing, validate the asset for the target engine, and report any remaining issues.

## Repository map

- `SKILL.md` — core workflow, module routing, safety, and delivery rules.
- `references/` — focused modeling, materials, environment, export, performance, and troubleshooting guides.
- `scripts/` — reusable Blender Python utilities and templates.
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

Start with `SKILL.md`, then load only the references relevant to the task. The detailed guides explain discipline-specific techniques and caveats.

## License

MIT

---

# Português

A Blender MCP Master é uma skill para agentes compatíveis que planejam, criam, inspecionam, refinam e validam assets 3D no Blender — de hard surface e modelagem orgânica a hand-painted, PBR, cenários, personagens e assets para jogos.

- **Planejamento antes da modelagem:** definir finalidade, estilo, limitações, entregáveis e critérios de aceitação.
- **Guias especializados:** consultar somente os módulos relevantes para a tarefa.
- **Ciclo de qualidade:** inspecionar, bloquear formas, refinar, validar, corrigir e relatar.
- **Segurança:** preservar o conteúdo existente da cena e informar resultados não verificados.

Funciona com agentes que suportam o formato Agent Skills e possuem acesso a uma integração MCP que controle o Blender. Os nomes e recursos das ferramentas MCP variam. A skill não substitui o servidor MCP necessário para controlar uma sessão do Blender.

## Início rápido

1. Instale ou copie o `SKILL.md` e a pasta `references/` para o diretório de skills reconhecido pelo agente.
2. Configure separadamente um servidor MCP de controle do Blender e inicie o Blender com o addon/extensão habilitado.
3. Peça ao agente para criar ou editar um asset. Ele deve inspecionar a cena, planejar o trabalho e verificar as alterações.

Exemplo:

> Crie uma espada fantasy estilizada e pronta para jogo. Planeje primeiro a modelagem e a texturização, confira a silhueta antes dos detalhes, valide o asset para a engine de destino e informe os problemas restantes.

## Estrutura

- `SKILL.md` — fluxo central, seleção de módulos, segurança e entrega.
- `references/` — guias especializados de modelagem, materiais, ambientes, exportação, desempenho e diagnóstico.
- `scripts/` — utilitários e modelos reutilizáveis em Python para Blender.
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
