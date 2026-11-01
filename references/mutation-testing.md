# Targeted mutation testing — 2026-11-01

## Verified outcome

**15/15 killed, 0 survived, 0 invalid** on `bpy 5.2.3` / Python 3.13 in the [GitHub Actions run](https://github.com/God-601/blender-mcp-master/actions/runs/41304279529). The unmodified baseline passed all 15 selected behavioral tests before mutations were injected. The ordinary runtime suite passed **174 tests** on each of the five bpy versions in that same run; Python static checks and Node 18/20/22 npm checks also passed.

**Important provenance:** The Claude audit of commit `6d2f83a` reported **nine surviving mutation classes out of fifteen**, and only those nine exact *classes* were available to reproduce. This campaign uses nine comparable perturbations (M01–M09) and **six explicitly new** safety mutations (M10–M15). It is not a claim to reconstruct the six unspecified original mutations, nor to have rerun the auditor's original harness byte for byte.

## Observed mutation matrix

| ID | Scope | Fault injected | Outcome |
|---|---|---|---|
| M01 | Prior-survivor class | Lathe end-cap winding reversed | KILLED |
| M02 | Prior-survivor class | Extruded-profile winding normalization disabled | KILLED |
| M03 | Prior-survivor class | Architectural arch end cap reversed | KILLED |
| M04 | Prior-survivor class | Wire edges ignored in inspection report | KILLED |
| M05 | Prior-survivor class | Local face-normal recalculation disabled | KILLED |
| M06 | Prior-survivor class | Optimizer ignores shared mesh safeguard | KILLED |
| M07 | Prior-survivor class | Normal map treated as sRGB instead of Non-Color | KILLED |
| M08 | Prior-survivor class | Tree branches disconnected from trunk | KILLED |
| M09 | Prior-survivor class | Boolean DIFFERENCE replaced with UNION | KILLED |
| M10 | Additional safety | Thin-mesh bevel width guard weakened | KILLED |
| M11 | Additional safety | Color texture alpha disconnected | KILLED |
| M12 | Additional safety | Inspector ignores mixed face winding | KILLED |
| M13 | Additional safety | Missing targets incorrectly considered verified | KILLED |
| M14 | Additional safety | In-place edit permission bypassed | KILLED |
| M15 | Additional safety | Cleanup implicitly operates on selected objects | KILLED |

The **first run** detected 14/15; M15 was masked because the test helper overwrote the mutated `TARGETS` configuration. We corrected the injection point to mutate the **runtime selection branch**, not the configurable default, and repeated the campaign. The second run detected M15, as well as the other fourteen. The first-run 14/15 result must not be represented as a source-code defect without this qualification.

## Reproduce

With a matching `bpy` installation in a disposable repository checkout:

```bash
python tests/run_all.py -v
python tests/run_mutation_campaign.py --strict --report mutation-results.json
```

Each mutant runs in a new temporary copy of `scripts/` and `tests/`, in its own Python/Blender subprocess. The source tree is never patched in place. A mutant is **KILLED** only when its selected behavioral test actually fails after a passing baseline. Missing anchors, syntax errors, failed imports, timeouts and other inconclusive runs are **INVALID**. The `--strict` flag fails CI if even one mutant survives or is invalid.

The JSON report is generated in the workflow's working directory; the [Actions logs](https://github.com/God-601/blender-mcp-master/actions/runs/41304279529) provide the complete observed summary. Use `tests/run_mutation_campaign.py` for the exact code mutations and selected test identities.

## What is NOT established

- Mutation coverage of every script or every potential regression; 15/15 is a **targeted**, deliberately small sample, not global code quality.
- The six unknown original Claude mutations or exact reproduction of his audit environment.
- Visual quality, proportions, precise physical contacts, deformation quality, rigging, Blender 3.1 live MCP control or real game-engine export quality.
- Future code remains protected without rerunning the campaign: tests must evolve with the code.

Next engineering work: [issue #18](https://github.com/God-601/blender-mcp-master/issues/18) for UV and export/engine validation, and [issue #19](https://github.com/God-601/blender-mcp-master/issues/19) for real agent-behavior tests.
