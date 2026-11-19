# Blender MCP Master 2.0 engineering roadmap

Version [2.0.0 shipped on 2026-11-13](release-notes-2.0.md). This roadmap records
the original engineering goals. The [evidence ledger](V2-EVIDENCE.md) tracks
which claims still need testing. Milestones 1.5–1.9 were integrated into 2.0.

| Phase | Goal | How to check it |
| --- | --- | --- |
| Stability | Protect user data and recover after interruptions | Restore a checkpoint and compare protected objects in the same scene. |
| Visual review | Find defects in proportion, shading and fit | Compare the same views before and after a correction, with independent review. |
| Geometry | Preserve topology and intentional contact during retopology and optimization | Exercise known positive and negative fixtures, including deforming poses. |
| Materials and export | Preserve units, pivots, UVs, textures and LODs | Inspect an identifiable export in each target editor. |
| Agents and cost | Select specialists as needed and bound context use | Compare repeated trials including failures, provider usage and asset quality. |
| Distribution | Install a reproducible package | Match the tagged source, archive hash and clean-install report. |

[Original detailed plan in Portuguese](ROADMAP-V2.pt-BR.md).
