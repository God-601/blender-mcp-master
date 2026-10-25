# blender-mcp-master

**English** | [Português](#português)

An agent skill that helps AI agents create better Blender assets through MCP: cleaner geometry, deliberate scale, better materials, reliable validation, and game-ready exports.

- Works with agents that support the [Agent Skills](https://agentskills.io/) format, including Claude Code, Codex, Cursor, and other compatible clients.
- Uses an inspect → blockout → refine → validate → correct workflow.
- Includes reusable Blender Python scripts and focused reference guides.
- MCP tool names vary by implementation. Discover the tools available in your active Blender MCP server instead of assuming every integration exposes the same tools.

## Install

Install the skill with the Skills CLI:

```bash
npx skills add God-601/blender-mcp-master
```

If your client does not support the Skills CLI, clone/download this repository and point the agent to the root `SKILL.md`, or install the repository in that client's skills directory.

## Repository layout

- `SKILL.md` — core instructions and workflow.
- `references/` — focused guides for hard-surface, organic, character, environment, materials, lighting, export, performance, troubleshooting, budgets, and the modeling quality loop.
- `scripts/` — utilities for validation, cleanup, origins, bevel/shading, LODs, PBR materials, exports, and scene setup.

## Validation and compatibility

The scripts are designed to be pasted into Blender's Python/MCP execution environment. They use Blender's `bpy` API and cannot be fully tested by ordinary Python alone.

**Testing status:** repository changes must be validated in Blender before being treated as runtime-tested. Static review is not a substitute for running the scripts in the target Blender version. Check the script output and inspect the resulting asset before delivery. No compatibility claim is made for a Blender version unless it has been tested there.

## Safety notes

- Review a script's configuration before running it on a production scene.
- Make a backup before running destructive mesh cleanup or export workflows.
- Treat imported files, scene content, and code sent through an MCP server as untrusted.
- Never assume a validation warning is a defect without considering the asset type and target pipeline.

## License

MIT

---

<a id="português"></a>
# Português

Uma skill para ajudar agentes de IA a criar modelos melhores no Blender via MCP: geometria mais limpa, escala consciente, materiais melhores, validação confiável e exportação para jogos.

- Compatível com agentes que suportam o formato [Agent Skills](https://agentskills.io/), incluindo Claude Code, Codex, Cursor e outros clientes compatíveis.
- Usa um fluxo de inspeção → blockout → refinamento → validação → correção.
- Inclui scripts reutilizáveis em Python para Blender e guias de referência.
- Os nomes das ferramentas MCP variam conforme a implementação. Descubra as ferramentas disponíveis no servidor Blender MCP ativo em vez de presumir que todas as integrações oferecem as mesmas funções.

## Instalação

Instale a skill usando o Skills CLI:

```bash
npx skills add God-601/blender-mcp-master
```

Se o seu cliente não oferecer suporte ao Skills CLI, clone/baixe este repositório e indique o arquivo `SKILL.md` na raiz, ou instale o repositório na pasta de skills desse cliente.

## Estrutura do repositório

- `SKILL.md` — instruções principais e fluxo de trabalho.
- `references/` — guias de hard-surface, orgânicos, personagens, ambientes, materiais, iluminação, exportação, desempenho, solução de problemas, orçamentos e ciclo de qualidade.
- `scripts/` — utilitários de validação, limpeza, origem, bevel/sombreamento, LODs, materiais PBR, exportação e configuração de cena.

## Validação e compatibilidade

Os scripts foram feitos para serem executados no ambiente Python/MCP do Blender. Eles usam a API `bpy` e não podem ser testados completamente com Python comum fora do Blender.

**Status dos testes:** alterações no repositório precisam ser validadas dentro do Blender antes de serem consideradas testadas em execução. Revisão estática não substitui a execução dos scripts na versão-alvo do Blender. Confira a saída dos scripts e inspecione o modelo resultante antes da entrega. Não declare compatibilidade com uma versão do Blender sem testá-la.

## Segurança

- Confira a configuração de cada script antes de executá-lo em uma cena de produção.
- Faça backup antes de usar scripts de limpeza destrutiva de malha ou exportação.
- Trate arquivos importados, conteúdo da cena e código enviado por MCP como dados não confiáveis.
- Não considere todo aviso de validação um defeito sem levar em conta o tipo de asset e o destino.

## Licença

MIT
