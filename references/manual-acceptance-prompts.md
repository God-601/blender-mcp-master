# Blender MCP Master — Testes manuais da versão integrada

Esta é uma **prévia de teste**, não a release 1.0. Faça backup dos projetos; a skill exige um Blender-control MCP separado para editar o Blender. Não teste em projetos valiosos sem salvar uma cópia.

## Inicialização obrigatória

**Preflight (sempre em sessão nova)**

> Ative a Blender MCP Master. Informe sua versão real do Blender, as ferramentas do Blender-control MCP disponíveis e os objetos existentes. Inspecione somente por leitura. Se o briefing deixar decisões importantes em aberto, esclareça essas decisões antes de alterar a cena.

**Aprovação:** a IA não inventa uma conexão MCP e não muda nada antes de receber as respostas às perguntas relevantes.

## T01 — Cadeira low-poly e briefing com decisões em aberto

> Crie uma cadeira medieval low-poly para jogos, com quatro pernas, assento a 0,45 m, largura 0,5 m, encosto, material de madeira e limite de 1.500 triângulos. Entrega em .blend. Preserve os objetos existentes.

Aprovado se esclarecer as decisões em aberto que mudam o resultado, como a forma do encosto ou o acabamento da madeira, e usar as respostas. Repita o teste com um briefing completo ou com essas decisões delegadas. A segunda variante deve avançar com zero perguntas de design.

## T02 — Castelo e inspeção artística

> Modele um castelo medieval low-poly com portão, duas torres e muralhas. Primeiro conclua o blockout, valide proporções e alinhamentos e só então adicione detalhes. Inspecione frente, lado e três-quartos com ferramentas reais e informe o que não pôde verificar.

Aprovado se existir hierarquia, contatos corretos e revisão visual autêntica, sem alegações inventadas.

## T03 — Integridade da cena

> Existem objetos de usuário chamados USER_Keep_Mesh e USER_Keep_Light. Adicione um painel sci-fi a uma coleção nova, sem alterar os objetos originais. Se um comando falhar, remova apenas cópias temporárias criadas por você. Compare o estado da cena antes e depois.

Aprovado se os dados e nomes originais continuarem intactos, inclusive quando houver erro.

**Pré-condição do T03:** confirme por leitura que USER_Keep_Mesh e USER_Keep_Light existem na mesma instância/sessão do Blender-control MCP. Se não existirem, o teste fica NOT VERIFIED: abra o arquivo correto ou crie e salve os dois objetos antes de pedir a modelagem; o agente deve parar antes de qualquer mutação.

**Encaixe do painel:** solicite que parafusos, placas e suportes encontrem a superfície pretendida em vez de atravessar material sem um recorte intencional. Para pares nomeados, use `references/component-fit-and-joints.md` e análise read-only; faça revisão visual das juntas antes da conclusão.

## T04 — Retopologia guiada

> Construa uma malha descartável com dois loops quadrangulares de borda. Inspecione índices reais e execute a união usando scripts/retopology_advanced.py em uma cópia. Verifique quads, normais e preservação da fonte. Em seguida, experimente índices inválidos: o script deve recusar a operação sem deixar um objeto de saída falhado.

Aprovado se a fonte permanecer intacta e não houver falsas alegações de retopologia automática para personagens.

## T05 — UV

> Compare uma malha com duas ilhas UV separadas a uma variante com as ilhas sobrepostas. Use scripts/uv_diagnostics.py com TARGETS explícitos para checar overlap e texel density. Informe PASS, REVIEW, ISSUE e NOT VERIFIED conforme as evidências. Não modifique UVs durante a auditoria.

Aprovado se separar contato de borda de sobreposição verdadeira e não inventar padding, baking ou exportação.

## T06 — Otimização de assets

> Crie um cubo e uma variante com Subdivision ativo. Use scripts/asset_performance_audit.py em objetos explicitamente nomeados; compare triângulos base/avaliados, materiais e texturas. Se sugerir otimização, faça em uma cópia. Não alegue medição de FPS, draw calls ou VRAM real.

Aprovado se os dados reais incluírem modificadores e a cena original ficar intacta.

## T07 — Exportação

> Modele uma espada estilizada com materiais e UVs; exporte GLB ou FBX e reimporte em cena de teste. Verifique escala, pivô, topologia e materiais. Se não houver acesso à engine de destino, registre compatibilidade com a engine como NOT VERIFIED.

Aprovado se o arquivo existir e houver uma reimportação real.

## T08 — Comparação de tokens

> Execute o mesmo cenário T01 duas vezes, uma sem a skill e outra com ela, em cenas idênticas com mesmo agente/modelo/MCP. Registre chamadas Bash/MCP e contagem de tokens APENAS quando disponível. Compare com scripts/agent_efficiency_compare.py e docs/EFFICIENCY-BENCHMARK.md, sem inventar redução.

Aprovado com entradas reproduzíveis e análise de qualidade junto de custo.

## T09 — Encaixes estruturais, sem atravessamento arbitrário

> Use a skill Blender MCP Master para construir uma cadeira low-poly de teste com assento, quatro pernas e duas travessas. Projete explicitamente o plano de contato entre topo das pernas e parte inferior do assento e entre ponta das travessas e faces dos postes. Não deixe peças atravessarem outras somente para esconder a junção. Se usar encaixe embutido, desenhe/documente a cavidade e a profundidade. Inspecione cada junta em vista frontal, lateral, inferior e três-quartos, antes e depois do chanfro. Use scripts/inspect_component_fit.py somente em pares de objetos separados para encontrar candidatos, e indique seus limites; se você consolidar tudo em um mesh, avalie visualmente as ilhas internas. Corrija encaixes ruins em cópias próprias, sem alterar objetos preexistentes.

**Esperado:** o agente descreve as superfícies de apoio e distingue contato intencional de interseção problemática. Exibir imagens reais de juntas em close-up, geometria/transformações nomeadas e sem declarar PASS só por AABB/BVH. Registrar se houve correção e evidência antes/depois. Para comparação, produza um exemplo descartável de uma viga atravessando uma parede para demonstrar que o agente **sinaliza REVIEW/ISSUE**, em vez de aprovar automaticamente. A auditoria deve ser não destrutiva.

## T10 — Excessive editable face triangulation / X across flat panels

> Use Blender MCP Master. Create three separate named editable mesh tests: A one completely planar quad face; B two planar triangles sharing one diagonal that make the same quad; C one planar quad-shaped patch split by a center vertex into four triangles making an X. Run `scripts/topology_face_diagnostics.py` with explicit `TARGETS` for all three. Report native Blender face count and render triangle count separately. Demonstrate that A and B have two render triangles, C has four; C should yield a REVIEW candidate while B is not an X fan. Inspect the C patch in Edit Mode, and on an owned COPY only, remove the redundant center vertex/edges if UVs, normals and shape remain safe. Validate before/after UV and shading. Do not edit the original or treat every triangulation/glTF vertex split as a defect.

**Esperado:** A one quad/two render tris, B two triangular faces/two render tris, C four triangular faces/four render tris. Analyzer marks C REVIEW but never auto-modifies. Correction on a copy is visually and technically verified, or stays NOT VERIFIED with a reason. Check Blender version before executing the new script.

## Registro de evidências

Para cada teste, salve: cenário, cliente/modelo, Blender e MCP versões exatas, prompt, cena inicial, resultado .blend, capturas frontal/lateral/três-quartos, logs de erro, alterações em objetos próprios, medições técnicas, status visual e status de exportação. Não compartilhe tokens de autenticação ou dados privados.

Não chame algo de PASS sem evidência. Use PASS / ISSUE / N/A / NOT VERIFIED e anote problemas concretos para corrigir.
