# Blender MCP Master — roadmap após v1.0

**Planejamento proposto, não promessa de datas ou compatibilidade.** Cada versão
deverá ter escopo limitado, regressões reproduzíveis, evidências práticas e
release notes que diferenciem capacidades medidas de hipóteses.

## v1.0.1 — Estabilidade e correções rápidas

**Foco:** resolver bugs concretos observados pelos primeiros usuários da
versão estável sem introduzir novas APIs ou fluxos complexos.

- Receber issues com versões de Blender, agente e Blender-control MCP, arquivos
  mínimos e logs; priorizar regressões e falhas de instalação.
- Melhorar mensagens de erro para cenas não salvas e reconexão pós-crash,
  sem fingir preservação de objetos perdidos.
- Corrigir incompatibilidades reproduzíveis de arquivos, links, ferramentas
  e scripts, preservando o comportamento e testes já aprovados.
- Incluir testes que falhem antes de cada correção e passem depois.

**Critério:** smoke test do ZIP + CI verde + regressões cobertas.

## v1.1.0 — Encaixes e topologia de verdade

**Foco:** os problemas de qualidade geométrica vistos em T03, T06, T07 e
T09, sem atribuir precisão ao AABB que ele não fornece.

- Definir semântica explícita das juntas: `surface_joint`,
  `intentional_embed`, fresta, penetração indesejada, pino/soquete.
- Adicionar diagnósticos locais conservadores e cortes/vistas de inspeção
  para componentes próximos, com tolerâncias documentadas em unidades Blender.
- Exercitar T10 para distinguir quad editável, diagonal simples e
  quatro triângulos coplanares em X; não dissolver arestas automaticamente
  quando afetar shading, UV, deformation ou material.
- Melhorar a correção de cabo/guarda, pernas/travessas, aro/tampa e
  outros encaixes, validando uma cópia antes de aplicar.

**Critério:** cenários positivos/negativos reproduzidos no Blender, com
falsos positivos quantificados e provas de preservação da cena.

## v1.1.0 — Entregue (escopo medido)

A atualização v1.1.0 entrega diagnósticos conservadores de encaixes por
AABB, riscos de UV/material/shape keys em topologia X, comparação de
silhueta convexa antes/depois da otimização, hashing de capturas reais e
verificação do checkpoint salvo após reconexão. Testes automatizados são
executados com bpy 4.2–5.2, além de Python/Node.

**Não foi entregue:** detecção exata de interseções entre sólidos,
correção automática de topologia ou encaixes, avaliação artística de
pixels ou benchmark comprovado em outro agente/engine. Esses são
objetivos futuros, não resultados da versão 1.1.
Veja [evidências v1.1](RELEASE-1.1-EVIDENCE.md).

## v1.2.0 — Pipeline de assets para jogos e entrevista de design

Além do fluxo de exportação, a v1.2 introduz uma mudança no primeiro contato com o usuário: **várias perguntas específicas**, proporcionais à complexidade do modelo, sobre referência, forma, materiais e finalidade. O agente não deve simplesmente perguntar se pode começar. Reutiliza respostas já dadas e permite delegar escolhas criativas.

O escopo automatizado da fase inicial inclui auditoria read-only de UV gutter por ilha, preflight de assets estáticos para jogo e round-trip GLB no Blender. **Importação real no Roblox/Unity/Godot/Unreal continua NOT VERIFIED até haver execução naquele ambiente**, sem contar Blender reimport como aprovação de engine.

### Expansões que exigem testes externos

- Testar GLB/FBX em um destino real escolhido, preservando dados, imagens e pivôs.
- Exercitar LOD com casos reais, margens de câmera e normais/tangentes.
- Confirmar shader/PBR/baking em cada engine, com screenshots verificáveis.

### Plano original v1.2 (referência)


**Foco:** medir a qualidade do fluxo completo, não apenas o .blend.

- Testar GLB/FBX em um destino real escolhido (por exemplo Roblox Studio,
  Godot ou Unity), incluindo escala, pivô, normais, materiais e UVs.
- Acrescentar diagnóstico de padding UV/texel density por objetivo de
  produção e advertências de baking sem prometer certificação de textura.
- Otimização/LOD com orçamento de triângulos e tolerâncias de silhueta,
  curvatura, detalhes e encaixes; reduzir custo sem perder o visual exigido.
- Melhorar checagens de materiais/texturas presentes e riscos de importação.

**Critério:** projeto reproduzível de exportação e reimportação na engine,
com arquivos, capturas, critérios de PASS/ISSUE e limites documentados.

## v1.3.0 — Autonomia de agentes e eficiência mensurada

**Foco:** reduzir retrabalho e aumentar consistência, não apenas comprimir
o texto da skill.

- Executar o mesmo benchmark em agentes suportados e com cenas iniciais
  salvas e idênticas, registrando chamadas na mesma metodologia.
- Medir tokens **apenas se expostos pelo cliente**, sem deduzir economia
  a partir do número de ferramentas; reter crashes como falhas da amostra.
- Adaptar referências progressivas ao tipo de asset, preservar decisões
  anteriores e diminuir perguntas redundantes.
- Testar recuperação após erros do MCP, com checkpoint e limitação segura
  de ferramentas mutáveis.

**Critério:** múltiplas execuções com logs auditáveis, qualidade aferida
e ganhos somente declarados se forem estatisticamente/tecnicamente sustentados.

## v2.0.0 — Revisão visual e workflows avançados

**Hipótese de versão maior, condicionada a capacidade e evidência reais.**

- Loop de avaliação visual por múltiplos ângulos com imagens efetivamente
  inspecionadas, anotações de defeitos e correções localizadas.
- Workflows mais amplos de retopologia e modelagem orientada a deformação,
  rigs e animações — preservando fontes e com testes em poses.
- Planejamento modular de cenas maiores, verificações entre componentes e
  validação de resultados complexos; sem se declarar modelador infalível.
- Revisão de interfaces e estrutura da skill quando mudanças incompatíveis
  forem justificadas por uso real.

**Critério:** definição explícita de capacidades suportadas, limites,
migração entre versões e bateria de testes realistas antes da release.

## Priorização

1. P0: impedir perda de cena, sobrescrita indevida e resultados técnicos falsos.
2. P1: melhorar qualidade visual/topologia/encaixes comprovadamente.
3. P2: pipeline de jogos e redução de custo com qualidade controlada.
4. P3: integrações e expansão de escopo depois de estabilizar o núcleo.

A versão inicial v1.0 não afirma compatibilidade real em todos os agentes,
certificação Blender 3.x, importação em qualquer engine, economia de tokens
ou julgamento artístico automático. Cada uma dessas promessas exige
evidência adicional na versão que a introduzir.
