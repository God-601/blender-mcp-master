# Blender MCP Master 2.0 candidate

The stable distribution remains **1.4.0**. The default branch contains
unreleased 2.0 candidate source. Release acceptance is on hold pending the
[acceptance campaign](V2-ACCEPTANCE-CAMPAIGN.md) and
[milestone gates](V1.5-V2.0-MILESTONES.md).

## Engineering milestones in the candidate

| Milestone | Tooling available for candidate evaluation |
| --- | --- |
| 1.5 | UV overlap, texel density and gutters, PBR channel audit and actual bake fixtures |
| 1.6 | Evaluated game budgets, GLB/FBX/OBJ workflows, target receipts and Godot probes |
| 1.7 | Seven specialist modules, bounded planning, independent reviews and recovery |
| 1.8 | Matched A/B harness with timing, provider usage, geometry results and preserved failures |
| 1.9 | Isolated ZIP installation, source and artifact checks, release readiness gates |

Blender 3.1 uses its legacy vertex-color and glTF APIs. The curvature recipe
and animation fixture detect the available API before use.

The native host coordinates scoped protected-object fingerprints, one writer
per source path and a saved checkpoint. The
[evidence ledger](V2-EVIDENCE.md) records which behaviors were observed and
which still need acceptance evidence. Independently inspect real images before
accepting visual quality. The Godot animation probe reports sampled bone
motion in an imported clip. Static GLB inspection handles surfaces with optional
UV and index buffers absent. Roblox evidence applies to the particular assets
and Studio sessions recorded in the [campaign](V2-CAMPAIGN-2026-11-08.md).

## Review a preflight archive

1. Open the [Release readiness preflight (NO RELEASE)](https://github.com/God-601/blender-mcp-master/actions/workflows/release-readiness.yml)
   workflow run for the revision under review. Record the checked-out commit
   from the run. For pull requests, it may be a GitHub merge commit.
2. Download the artifact named `blender-mcp-master-preflight-<sha>`. Keep the
   inner ZIP, `SHA256SUMS.txt` and `clean-install-report.json` together.
   The candidate's package metadata can produce a ZIP named
   `blender-mcp-master-1.4.0-PREFLIGHT-NOT-A-RELEASE.zip`. The suffix and
   workflow SHA identify it as a preview. For stable 1.4.0, use the tagged
   [release ZIP](https://github.com/God-601/blender-mcp-master/releases/download/v1.4.0/blender-mcp-master-1.4.0.zip).
3. From a checkout of the tested revision, verify the checksum and rerun the
   isolated install smoke test. The example assumes the downloaded files
   are in `preflight/`:

   ```text
   python scripts/clean_install_smoke.py preflight/blender-mcp-master-1.4.0-PREFLIGHT-NOT-A-RELEASE.zip preflight/SHA256SUMS.txt --report preflight/local-clean-install-report.json
   ```

   A matching checksum and `result: PASS` confirm the isolated ZIP smoke
   checks. The report also records live agent discovery and MCP status.
   Test those separately on the actual client and Blender session.
4. Keep a copy of the installed 1.4.0 skill folder. Extract the inner
   `blender-mcp-master` folder and follow the [quickstart](QUICKSTART.md) to
   install it in a separate project or isolated skill directory. Verify
   the tools exposed by the client's configured Blender-control MCP before
   writes. Use a disposable or backed-up scene for preview testing.

## Recovery

To revert, restore the saved skill folder. Recover an interrupted scene from
its verified checkpoint and compare the protected-object snapshot before
resuming the task. See [scene recovery](../references/crash-recovery-and-baselines.md).

## Final release checks

Require green CI and independent acceptance evidence on the exact release
source. Record source and package hashes, real Blender-control MCP acceptance,
target-specific imports, Blender and client versions, benchmark coverage
and any unresolved failures. Confirm actual client discovery and clean
installation. In the authorized release change, align the package manifest,
lockfile, changelog and installation docs, then rebuild the versioned ZIP and
recheck the final source and artifacts. Publication requires the maintainer's
explicit authorization.
