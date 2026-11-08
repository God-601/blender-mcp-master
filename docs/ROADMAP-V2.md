# Blender MCP Master 2.0 — Auditoria, arquitetura e plano de entrega

**Status:** proposta de engenharia, **não** release 2.0. O protocolo executável de testes por etapa está em [V2-ACCEPTANCE-CAMPAIGN.md](V2-ACCEPTANCE-CAMPAIGN.md); o script de comparação antes/depois de silhuetas exige evidência de preservação da cena e revisão independente, sem emitir aprovação artística automática. Não confundir documentação,
scripts no repositório, CI bpy ou um importador smoke com uma demonstração de
qualidade artística ou compatibilidade entre agentes.

> Os marcos detalhados **1.5, 1.6, 1.7, 1.8 e 1.9**, com ferramentas entregues e testes externos ainda pendentes, estão em [V1.5-V2.0-MILESTONES.md](V1.5-V2.0-MILESTONES.md). Não representam releases publicadas.

## 1. Objetivo do 2.0

Transformar a skill em um **sistema de produção 3D guiado por evidências**:
perguntar apenas o que muda o resultado, planejar por destino, modelar com
operações pequenas e reversíveis, reconhecer visualmente erros quando o
cliente oferece imagens, validar geometria e materiais e entregar assets com
prova externa apropriada. **Não** substituir Blender, seu addon ou o MCP
de controle. Não atribuir capacidade de visão a scripts que só medem metadados.

### Contrato do produto

- **Segurança acima de autonomia:** nenhum objeto não autorizado, arquivo do
  usuário, cena ou datablock compartilhado pode ser alterado silenciosamente.
- **Qualidade por destino:** projeto para render, Roblox, Godot, Unity, Unreal,
  arquitetura, rig/deformação e 3D print exigem critérios diferentes.
- **Execução orientada à tarefa:** selecionar 1 guia principal, especializar
  só quando necessário e pedir dados essenciais sem reentrevista.
- **Evidência verificável:** `PASS / ISSUE / N/A / NOT VERIFIED` por critério
  com artefatos e proveniência; nenhuma nota artística sem imagens realmente
  observadas; nenhuma aprovação de engine sem engine.
- **Custos medidos, não estimados:** tamanhos de texto, calls e tokens são
  indicadores diferentes. Proteger qualidade antes de reduzir custo.

## 2. Auditoria pré-v2.0 — descobertas

**Método/limite:** leitura dos principais scripts, entrypoint, Node/MCP, testes
Python/Blender e npm, workflows GitHub Actions, docs de distribuição, versão
do pacote e PRs existentes via GitHub. O checkout/clonagem local não pôde ser
feito neste ambiente (DNS indisponível), portanto isso **não** é uma auditoria
linha a linha de cada arquivo nem prova de ausência de falhas.

| ID | Gravidade | Descoberta | Ação |
| --- | --- | --- | --- |
| A01 | P1 | `package.json` e lock declaram Node >=18.18, porém dependência transitiva `@hono/node-server` exige >=20 | Corrigido para Node >=20, com teste |
| A02 | P1 | ZIP de release-readiness copia docs/scripts, mas omite `integrations/` recém-criada | Corrigido com verificação de Godot dentro do ZIP |
| A03 | P1 | Decoder PNG limita `decompress`, mas invoca `zlib.flush()` sem limite de saída | Saída limitada e regressão para PNG com deflate exagerado |
| A04 | P1 | Teste Godot anterior usa só GLB sintético; não prova exportação do Blender nem fidelidade visual | Adicionado fluxo bpy → GLB → Godot 4 real em CI; só é PASS depois de rodar no exato commit |
| A05 | P2 | Pré-release chamava o artefato de `1.2-PREFLIGHT` embora manifest atual fosse 1.3.0 | Corrigido: nome dinâmico a partir do `package.json`, sem alterar release histórica e sem publicar |
| A06 | P0 | Cliente real Codex/Claude + Blender-control MCP e custo/tokens efetivos continuam sem trials comparáveis | [#54](https://github.com/God-601/blender-mcp-master/issues/54), [#51](https://github.com/God-601/blender-mcp-master/issues/51) |
| A07 | P1 | BVH e paridade detectam candidatos mas não demonstram interseção universal; análise visual de máscara não avalia estética | [#55](https://github.com/God-601/blender-mcp-master/issues/55), [#56](https://github.com/God-601/blender-mcp-master/issues/56) |
| A08 | P1 | Godot fixture não significa Roblox/Unity/Unreal; UV, materiais e rig podem variar | [#57](https://github.com/God-601/blender-mcp-master/issues/57) |
| A09 | P2 | Workflows de releases históricas e documentação misturam versões, sem release v1.4 completa | [#58](https://github.com/God-601/blender-mcp-master/issues/58) |

**Pontos preservados**: `SKILL.md` curta (~6.2KB), recursos sob demanda,
MCP de referências somente leitura, entrevista não redundante, protected-object
baseline, export com alvos explícitos, script de importação Godot, scorecard e
registro opt-in de correções. Evitar implementar esses recursos duas vezes.

## 3. Arquitetura alvo

```text
Brief do usuário + referência(s)
  -> Clarification Gate (decisões ainda desconhecidas)
  -> Capability Probe (Blender/MCP/cliente, sem nomes assumidos)
  -> Workflow Director (modelo, destino, restrições, guias sob demanda)
  -> Scene Safety + Checkpoint (source SHA + ownership)
  -> Plan / Blockout (componentes e medidas)
  -> Specialist Executors (geom / topo / UV / materials / rig / export)
  -> Technical QA (bpy avaliado, UV, joints, preservação, orçamento)
  -> Visual QA (imagens reais, proporções, defect loop)
  -> Destination QA (importador do target real)
  -> Delivery Receipt + Benchmark Evidence
```

**Contratos**: `asset_id`, `scene_id`, `owned_object_ids`,
`checkpoint_ref`, `stage`, `tool_capabilities`, `measurements`,
`warnings`, `defects`, `artifact_refs`, `statuses`, `rollback_info`.
Schemas versionados, idempotência para operações repetidas, e ferramentas
sem acesso nunca retornam sucesso falso.

## 4. Execução por fases

### Fase 0 — Estabilizar base v1.4 e provar integração externa

- CI Python/bpy 4.2, 4.5, 5.0, 5.1, 5.2 e Node/npx limpo.
- Godot 4 CLI importa fixture sintética **e** arquivo exportado realmente pelo Blender.
- Testar guardas de escrita: não sobrescrever source, ZIP sem traversal e sem
  recurso ausente, noções de permissão/ownership preservadas.
- Rodar sessão real de agente Blender MCP com cadeira/espada/árvore e
  referência; registrar falhas.
- **Saída:** release v1.4 somente se aceita por evidência, ou manter
  versão candidata sem publicidade excessiva.

### Fase 1 — Visual intelligence e defect loop ([#55](https://github.com/God-601/blender-mcp-master/issues/55))

- Comparação imagem da referência/captura real por agente com visão;
  distinguir camera mismatch, geometria, shader e iluminação.
- Captura dos mesmos 3 pontos de vista e landmarks rastreados.
- Correção limitada no owner copy, rechecagem da cena e revisores
  independentes; logs dos defeitos e falsos alarmes.
- Critério: ao menos 4 tipos de assets, cada um com casos de defeitos
  injetados positivos e negativos, review real, sem auto-PASS de IoU.

### Fase 2 — Geometry intelligence e retopologia ([#56](https://github.com/God-601/blender-mcp-master/issues/56))

- Inspeção topológica medida com malhas avaliadas, BVH conservador,
  classes de contato/penetração e malha aberta/contenção.
- Retopo guiada avançada (quads, loops, bevel, hard-surface, deformação),
  preservar UV/material/shape keys por padrão; copies e rollback.
- Otimização para jogos: triângulos após modificadores, LOD,
  pivot, colisões, partes não visíveis, objetos sobrepostos.
- Critério: fixtures negativas e positivas em versões suportadas,
  invariantes de preservação, evidências visuais para juntas reais.

### Fase 3 — Materials and production delivery ([#57](https://github.com/God-601/blender-mcp-master/issues/57))

- PBR correto por finalidade; UV seam/padding/texel density, atlas,
  trim sheets e baking (normal/AO etc.) com texturas realmente gravadas.
- Export GLB/FBX/OBJ no destino aplicável com caminho específico para
  rig/animation, validação de cor/canais e units/transforms.
- Testes externos com Godot, Roblox Studio e pelo menos outra engine
  quando disponível. Não certificar plataforma não testada.
- Critério: preview e asset importados visualmente examinados,
  dimensões e shading conferidos no editor alvo.

### Fase 4 — Agent orchestration and context budget ([#54](https://github.com/God-601/blender-mcp-master/issues/54), [#58](https://github.com/God-601/blender-mcp-master/issues/58))

- Papéis especializados: planejador, modelador, UV/material, QA geom,
  QA visual, QA export. Delegação sob demanda, não swarm obrigatório.
- Estado mínimo para reuso: brief, cena, propriedade, último checkpoint,
  evidência verificada, decisões e próximo passo.
- Logs concisos/JSON; scripts fixados e inspecionados antes da execução,
  chamadas somente se schema disponível; reconexões invalidam cache.
- Bench A/B sem skill/com skill, 3 tentativas por pelo menos 5 cenários
  com mesmas fixtures, incluindo crashes, tempos, uso do provider
  quando disponível e revisão cega quando viável.
- **Meta**: economizar consumo sem sacrificar qualidade. **Não definir
  economia percentual sem valores medidos**.

### Fase 5 — v2.0 release-quality

- Documentação bilíngue e exemplos curtos, guias especializados separados
  e uma especificação única de contratos/limites.
- Distribuição npm (se autorizada), GitHub ZIP com SHA256, licença e
  assets íntegros; instalação limpa em agentes reais; rollback.
- Atualizar versões de manifest/lock/changelog juntos, gerar nomes de
  arquivo pelo manifest, descontinuar fluxos legados com cuidado.
- Evidências no commit/tag exatos, histórico das tentativas, release
  só depois de completar todas as gates relevantes.

## 5. Checklist de aceitação v2.0

- [ ] Nenhum dano silencioso a objetos não pertencentes ao agente em
  testes de criação, edição, export e crash/reconnect.
- [ ] Um cliente agente/MCP realmente demonstrado end-to-end;
  outros somente se testados.
- [ ] Critérios visuais de modelos avaliados a partir de imagens reais;
  falsos positivos/negativos documentados.
- [ ] Caminho game-ready inclui testes reais de importação no(s)
  editor(es) declarados, não apenas blender→blender.
- [ ] Retopologia, juntas, UV/PBR e materiais demonstrados com
  fixtures variadas e revisões.
- [ ] Bench com/sem skill de custo+qualidade, sem filtragem dos erros.
- [ ] CI na SHA final: Python, bpy, Node, Godot, archive e instalação limpa.
- [ ] Relatório PASS/ISSUE/N/A/NOT VERIFIED rastreável por artefato.
- [ ] Release tags, ZIP e npm **não publicados** antes da aprovação.

## 6. Priorização

**P0**: [#54](https://github.com/God-601/blender-mcp-master/issues/54)
trials reais, segurança e custo.

**P1**: [#55](https://github.com/God-601/blender-mcp-master/issues/55)
revisão visual, [#56](https://github.com/God-601/blender-mcp-master/issues/56)
geometria/retopo, [#57](https://github.com/God-601/blender-mcp-master/issues/57)
materiais/engine.

**P2**: [#58](https://github.com/God-601/blender-mcp-master/issues/58)
arquitetura e distribuição.

Concluir uma etapa não implica que o produto 2.0 esteja completo. Cada
release intermediária deve dizer exatamente o que foi medido e os
bloqueios que permanecem.
