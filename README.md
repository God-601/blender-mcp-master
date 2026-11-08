# Blender MCP Master

<p align="center">
  <strong>Model with intent. Verify with evidence.</strong><br>
  An open-source Agent Skill for Blender workflows.
</p>

<p align="center">
  <a href="https://github.com/God-601/blender-mcp-master/releases"><img alt="Latest release" src="https://img.shields.io/github/v/release/God-601/blender-mcp-master?include_prereleases&style=flat-square&label=release"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-21262d?style=flat-square"></a>
  <a href="https://github.com/God-601/blender-mcp-master/actions/workflows/static-checks.yml"><img alt="GitHub Actions" src="https://img.shields.io/badge/CI-GitHub_Actions-21262d?style=flat-square"></a>
</p>

<p align="center">
  <a href="#get-started">Get started</a> ·
  <a href="#workflow">Workflow</a> ·
  <a href="#documentation">Documentation</a> ·
  <a href="#portugues">Português</a>
</p>

---

<p align="center"><img src="assets/banner.svg" width="100%" alt="Concept illustration: isometric mesh study representing Blender MCP Master, not an actual generated Blender model"></p>

### Better decisions. Better meshes.

Blender MCP Master helps AI agents **plan, model, inspect, and validate** Blender assets using task-specific instructions, scripts, and evidence-based quality checks.

> **Important:** This skill does **not** control Blender by itself. Live editing needs a separate Blender-control MCP server and Blender addon. The optional MCP resource server here is *read-only*.

**2.0 engineering candidate:** seven reusable specialist modules, executable
host-adapter orchestration, independent QA handoffs, hashed evidence receipts
and default dry-run. A concrete Codex CLI worker handles read-only reviews;
the bundled native bpy host supplies checkpoints, scene probes, writer leases
and dispatch of explicitly inspected production callbacks.
[Execution contract](references/specialist-orchestration.md) ·
[Implementation and Agency Agents references](docs/V2-IMPLEMENTATION.md) ·
[Validation status and release blockers](docs/V2-EVIDENCE.md).
The stable package remains **1.4.0**; these capabilities do not certify
artistic quality, all engines, agent compatibility or token savings.

| Define | Build | Inspect | Deliver |
| :--- | :--- | :--- | :--- |
| Establish style, purpose, proportions, and constraints. | Block out primary forms, then refine in reversible stages. | Verify actual mesh data and visual references. | Disclose measured results and what remains unverified. |

## Get started

**1. Install the skill using the CLI**

```bash
npx skills add God-601/blender-mcp-master -g
```

**Or download the release ZIP**

**[Download v1.4.0 · Installable ZIP](https://github.com/God-601/blender-mcp-master/releases/download/v1.4.0/blender-mcp-master-1.4.0.zip)**

Get [SHA256SUMS.txt](https://github.com/God-601/blender-mcp-master/releases/download/v1.4.0/SHA256SUMS.txt) from the same release, verify the hash, extract the ZIP and copy its inner `blender-mcp-master` folder to your agent's skills directory. Full [Windows and agent setup instructions](docs/QUICKSTART.md).

**2. Set up Blender control separately**

Connect a compatible Blender-control MCP and its addon; discover the actual tool names and Blender version. Start in a scratch or backed-up scene. The skill supplies guidance, **not** a live Blender connection.

<details>
<summary><strong>Optional: read-only MCP resource server</strong></summary>

The optional read-only MCP resource server is available from the GitHub source (the v1.4.0 package has not been published to the npm registry):

```bash
npx -y github:God-601/blender-mcp-master
```

Neither command provides Blender scene-control tools.
</details>

<p align="center"><img src="assets/workflow.svg" width="100%" alt="Clarify, plan, build, inspect and correct workflow diagram"></p>

**v1.4.0 stable:** The skill adapts its design questions to the brief, plans
modeling by task, and checks evaluated geometry, scene preservation, UVs,
materials and game-asset budgets. The quality toolkit includes conservative
component-fit and containment diagnostics, PNG silhouette measurements,
PBR channel inspection, and evidence-backed specialist review reports.

**Verified in CI:** Blender bpy regression suites, a real Cycles texture-bake
fixture, and Blender-authored GLB import in Godot 4.4.1. **User-reported
Roblox Studio acceptance:** Sofa V3 LOD meshes and PBR maps were inspected
and the user approved the visible result. This does *not* certify universal
Roblox/Unity compatibility or artistic quality.

See the [v1.4.0 release notes](docs/release-notes-1.4.md),
[game export guidance](references/game-ready-export.md), and the
[v1.5–1.9 milestone plan](docs/V1.5-V2.0-MILESTONES.md).

## Workflow

```text
USER BRIEF + REFERENCE
          |
          v
  BLENDER MCP MASTER  [Agent Skill]
  Clarify -> Plan -> Blockout -> Refine -> Verify
          |                              ^
          v                              |
  BLENDER-CONTROL MCP ------------------+
          |
       Blender scene
```

The agent must **inspect before it claims success**. Geometry checks, screenshots, and target-format checks answer different questions; missing evidence is **NOT VERIFIED**, not a pass.

| Focus | What changes |
| :--- | :--- |
| **Scene safety** | Explicit targets, owned collections, backup-first changes |
| **Modeling quality** | Proportion checks before unnecessary micro-detail |
| **Technical validity** | Evaluated topology, modifiers, UVs, materials, and budgets |
| **Visual validation** | Real viewport views before judging appearance |
| **Delivery** | `PASS / ISSUE / N/A / NOT VERIFIED` plus known limitations |

Supported workflows include hard-surface props, organic modeling, stylized and low-poly assets, architecture, environments, characters, UV/baking, materials, and game-ready exports. Available features depend on the actual Blender installation and connected MCP tools.

<p align="center"><img src="assets/architecture.svg" width="100%" alt="Skill and separate Blender-control MCP architecture"></p>

## Documentation

| Resource | Purpose |
| :--- | :--- |
| [Quickstart](docs/QUICKSTART.md) | Installation, Windows paths, checksums, and MCP setup |
| [SKILL.md](SKILL.md) | Main instruction entrypoint for agents |
| [Official Blender documentation](references/official-blender-documentation.md) | Curated modeling, modifiers, UV, Geometry Nodes, Python API, export references |
| [Evidence-first workflow](references/evidence-first-workflow.md) | Stage gates, independent review, defect diagnosis, and stop conditions |
| [Modeling standards](references/professional-modeling-standards.md) | Production requirements and quality evidence |
| [Production recipes](references/production-recipes.md) | Concrete modeling examples |
| [Skill comparisons](docs/ECOSYSTEM-COMPARISON.md) | Reference patterns, including Superpowers |
| [Roadmap v2.0](docs/ROADMAP-V2.md) | Production architecture, staged acceptance gates and remaining validation |
| [v1.5–v1.9 milestones](docs/V1.5-V2.0-MILESTONES.md) | Planned upgrades and the boundaries of experimental foundations |
| [Roblox Studio inspection](integrations/roblox/README.md) | Read-only MeshPart/PBR/LOD inspection procedure |
| [Godot GLB import](integrations/godot/README.md) | Executable import probe, scope and limitations |
| [Agent efficiency](references/token-efficient-agent-execution.md) | Tool-first, bounded reads and progressive context loading |
| [3D model optimization](references/model-performance-strategy.md) | Evaluated triangle, material, texture and Geometry Nodes guidance |
| [Paired token benchmark](docs/EFFICIENCY-BENCHMARK.md) | Reproducible with/without skill comparison protocol |

<details>
<summary><strong>Tests and contribution</strong></summary>

```bash
python -m unittest discover -s tests -v
```

Some tests require a compatible `bpy` runtime. Passing tests is not proof of artistic quality or live MCP and downstream export compatibility.

[Milestones v1.5–1.9](docs/V1.5-V2.0-MILESTONES.md) · [Roadmap v2.0 and pre-release audit](docs/ROADMAP-V2.md) · [Quality checklist](references/quality-checklist.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)
</details>

---

<a id="portugues"></a>
# Português

**Uma skill para agentes de IA modelarem no Blender com método e evidências.** Ajuda a planejar, modelar, verificar topologia, UVs, materiais PBR e preparar assets para jogos. Ela orienta o agente; não instala nem substitui o Blender-control MCP.

- **Instalar:** `npx skills add God-601/blender-mcp-master -g` ou [baixar o ZIP da Release](https://github.com/God-601/blender-mcp-master/releases/download/v1.4.0/blender-mcp-master-1.4.0.zip).
- **Alternativa sem npm:** `npx -y github:God-601/blender-mcp-master` inicia o servidor de recursos somente leitura.
- **CLI:** `npx skills add God-601/blender-mcp-master -g` instala a skill.
- **Configurar:** conectar separadamente um Blender-control MCP. Veja o [guia para Windows e agentes](docs/QUICKSTART.md).
- **Fluxo:** esclarecer → planejar → modelar → inspecionar → corrigir → relatar o que foi verificado.
- **Aprofundar:** [documentação oficial](references/official-blender-documentation.md) · [verificação e recuperação](references/evidence-first-workflow.md) · [padrões profissionais](references/professional-modeling-standards.md).

**Versão estável v1.4.0.** Inclui verificações técnicas e exemplos reais de baking e importação no Godot. Um sofá com três LODs e mapas PBR também foi aprovado pelo usuário no Roblox Studio. Os testes não garantem qualidade artística universal, redução real de tokens ou compatibilidade com todas as engines.

**Candidata de engenharia 2.0:** módulos especializados, executor por adaptador
do cliente, um escritor por vez, QA independente e recibos com SHA256.
Tarefas simples ficam com o coordenador. O adaptador deve fornecer as
ferramentas reais do Blender; a ponte de revisão Codex é somente leitura.
[Contrato e uso](references/specialist-orchestration.md) ·
[Evidências e pendências](docs/V2-EVIDENCE.md). A 2.0 não foi publicada.

[Notas da v1.4.0](docs/release-notes-1.4.md) · [Roadmap 2.0](docs/ROADMAP-V2.md) · [Guia Roblox Studio](integrations/roblox/README.md)

<p align="center">
  <a href="LICENSE">MIT License</a> ·
  <a href="https://github.com/God-601/blender-mcp-master/issues">Feedback</a> ·
  <a href="https://github.com/God-601/blender-mcp-master/releases">Releases</a>
</p>
