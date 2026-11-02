# Blender MCP Master — Testes manuais da versão integrada

Esta é uma **prévia de teste**, não a release 1.0. Faça backup dos projetos; a skill exige um Blender-control MCP separado para editar o Blender. Não teste em projetos valiosos sem salvar uma cópia.

## Inicialização obrigatória

**Preflight (sempre em sessão nova)**

> Ative a Blender MCP Master. Informe sua versão real do Blender, as ferramentas do Blender-control MCP disponíveis e os objetos existentes. Inspecione somente por leitura. Para um projeto NOVO, faça uma pergunta geral útil de GENERAL KICKOFF antes de alterar a cena, mesmo com briefing completo, sem repetir informações já dadas.

**Aprovação:** a IA não inventa uma conexão MCP e não muda nada antes de receber a resposta do kickoff.

## T01 — Cadeira low-poly e briefing completo

> Crie uma cadeira medieval low-poly para jogos, com quatro pernas, assento a 0,45 m, largura 0,5 m, encosto, material de madeira e limite de 1.500 triângulos. Entrega em .blend. Preserve os objetos existentes. Primeiro execute o GENERAL KICKOFF exigido pela skill.

Aprovado se fizer somente uma pergunta geral não redundante, aguardar "pode seguir", criar uma cadeira completa e mostrar medições e capturas reais.

## T02 — Castelo e inspeção artística

> Modele um castelo medieval low-poly com portão, duas torres e muralhas. Primeiro conclua o blockout, valide proporções e alinhamentos e só então adicione detalhes. Inspecione frente, lado e três-quartos com ferramentas reais e informe o que não pôde verificar.

Aprovado se existir hierarquia, contatos corretos e revisão visual autêntica, sem alegações inventadas.

## T03 — Integridade da cena

> Existem objetos de usuário chamados USER_Keep_Mesh e USER_Keep_Light. Adicione um painel sci-fi a uma coleção nova, sem alterar os objetos originais. Se um comando falhar, remova apenas cópias temporárias criadas por você. Compare o estado da cena antes e depois.

Aprovado se os dados e nomes originais continuarem intactos, inclusive quando houver erro.

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

## Registro de evidências

Para cada teste, salve: cenário, cliente/modelo, Blender e MCP versões exatas, prompt, cena inicial, resultado .blend, capturas frontal/lateral/três-quartos, logs de erro, alterações em objetos próprios, medições técnicas, status visual e status de exportação. Não compartilhe tokens de autenticação ou dados privados.

Não chame algo de PASS sem evidência. Use PASS / ISSUE / N/A / NOT VERIFIED e anote problemas concretos para corrigir.
