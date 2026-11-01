"""Reproducible, source-level mutation campaign against real Blender outcome tests.

Run in an isolated checkout with a compatible bpy wheel:
    python tests/run_mutation_campaign.py --strict --report mutation-results.json

No repository source is edited. Each mutant runs in its own temporary copy
using a fresh Python/Blender process. KILLED means the selected behavioral
test failed; SURVIVED means it passed. This campaign contains the nine
historical survivors described in audit #22 plus six *new* safety checks:
the original audit's other six mutation definitions were not retained.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
MUTANTS = [
  {
    "id": "M01",
    "label": "lathe upper cap winding reversed",
    "kind": "claude-previous-survivor",
    "file": "scripts/geometry_builder.py",
    "old": "        faces.append(tuple(rings[-1]))",
    "new": "        faces.append(tuple(reversed(rings[-1])))",
    "tests": [
      "test_geometry_builder_runtime.GeometryBuilderRuntimeTests.test_lathe_reversed_profile_has_positive_solid_volume_and_consistent_caps"
    ]
  },
  {
    "id": "M02",
    "label": "extruded profile winding normalization disabled",
    "kind": "claude-previous-survivor",
    "file": "scripts/geometry_builder.py",
    "old": "    if area2 < 0:\n        profile.reverse()",
    "new": "    if area2 < 0:\n        pass  # MUTANT: skip normalization",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_reference_extrusion_winding_normalized_in_both_orders"
    ]
  },
  {
    "id": "M03",
    "label": "modular arch one end cap reversed",
    "kind": "claude-previous-survivor",
    "file": "scripts/modular_builder.py",
    "old": "    faces = [tuple(range(n)), tuple(reversed(range(n, 2 * n)))]",
    "new": "    faces = [tuple(reversed(range(n))), tuple(reversed(range(n, 2 * n)))]",
    "tests": [
      "test_modular_builder_runtime.ModularBuilderTests.test_arch_default_has_outward_winding_positive_volume"
    ]
  },
  {
    "id": "M04",
    "label": "inspection report ignores wire edges",
    "kind": "claude-previous-survivor",
    "file": "scripts/inspection_report.py",
    "old": "        wire = sum(1 for edge in bm.edges if edge.is_wire)",
    "new": "        wire = 0  # MUTANT ignores wire edges",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_inspection_report_does_not_ignore_wire_edges"
    ]
  },
  {
    "id": "M05",
    "label": "localized face normal correction disabled",
    "kind": "claude-previous-survivor",
    "file": "scripts/localized_correction.py",
    "old": "                bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])",
    "new": "                pass  # MUTANT: skip recalc",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_local_recalculate_normals_changes_duplicate_not_inverted_source"
    ]
  },
  {
    "id": "M06",
    "label": "optimizer shared-mesh safeguard disabled",
    "kind": "claude-previous-survivor",
    "file": "scripts/optimize_mesh.py",
    "old": "    if obj.data.users > 1:",
    "new": "    if False and obj.data.users > 1:  # MUTANT ignores sharing",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_optimizer_skips_shared_mesh_in_apply_mode"
    ]
  },
  {
    "id": "M07",
    "label": "normal texture routed as sRGB color",
    "kind": "claude-previous-survivor",
    "file": "scripts/pbr_material.py",
    "old": "n = add_tex(_loaded_images[\"normal\"], \"Normal\", True, -900, -600)",
    "new": "n = add_tex(_loaded_images[\"normal\"], \"Normal\", False, -900, -600)  # MUTANT",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_normal_map_is_noncolor_and_connected_to_principled"
    ]
  },
  {
    "id": "M08",
    "label": "tree branches detached from trunk",
    "kind": "claude-previous-survivor",
    "file": "scripts/organic_tree_builder.py",
    "old": "        start = Vector((0, 0, z))",
    "new": "        start = Vector((TRUNK_RADIUS * 4.0, 0, z))  # MUTANT",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_tree_branches_attach_near_trunk_centerline"
    ]
  },
  {
    "id": "M09",
    "label": "boolean difference turned into union",
    "kind": "claude-previous-survivor",
    "file": "scripts/mesh_operations.py",
    "old": "        mod.operation = \"DIFFERENCE\"",
    "new": "        mod.operation = \"UNION\"  # MUTANT",
    "tests": [
      "test_audit_regressions_runtime.ProfessionalMutationRegressionTests.test_boolean_difference_actually_removes_mesh_volume"
    ]
  },
  {
    "id": "M10",
    "label": "thin-panel bevel width guard weakened",
    "kind": "additional-safety-check",
    "file": "scripts/geometry_builder.py",
    "old": "        cap = 0.20 * min(dimensions)",
    "new": "        cap = 3.0 * min(dimensions)  # MUTANT excessive bevel",
    "tests": [
      "test_geometry_builder_runtime.GeometryBuilderRuntimeTests.test_extreme_bevel_request_is_clamped_before_modifier_evaluation"
    ]
  },
  {
    "id": "M11",
    "label": "color alpha connection removed",
    "kind": "additional-safety-check",
    "file": "scripts/pbr_material.py",
    "old": "                alpha_source = n.outputs['Alpha']",
    "new": "                alpha_source = None  # MUTANT ignores color texture alpha",
    "tests": [
      "test_p0_integrity_runtime.P0SafetyRuntimeTests.test_color_texture_alpha_is_connected_to_cutout"
    ]
  },
  {
    "id": "M12",
    "label": "winding continuity ignored by geometry inspector",
    "kind": "additional-safety-check",
    "file": "scripts/inspect_geometry.py",
    "old": "        inconsistent_winding = sum(edge.is_manifold and not edge.is_contiguous for edge in bm.edges)",
    "new": "        inconsistent_winding = 0  # MUTANT",
    "tests": [
      "test_p0_integrity_runtime.P0SafetyRuntimeTests.test_mixed_face_normals_are_detected_even_when_volume_is_positive"
    ]
  },
  {
    "id": "M13",
    "label": "missing target reported as PASS",
    "kind": "additional-safety-check",
    "file": "scripts/inspect_geometry.py",
    "old": "            \"NOT VERIFIED\" if missing or invalid or not statuses or \"NOT VERIFIED\" in statuses else",
    "new": "            \"PASS\" if missing or invalid or not statuses or \"NOT VERIFIED\" in statuses else  # MUTANT",
    "tests": [
      "test_professional_quality_runtime.ProfessionalGeometryRuntimeTests.test_missing_target_never_reports_pass"
    ]
  },
  {
    "id": "M14",
    "label": "unowned in-place bevel permission bypassed",
    "kind": "additional-safety-check",
    "file": "scripts/bevel_and_shade.py",
    "old": "    if EDIT_IN_PLACE and ob.get(OWNER_KEY) != OWNER_VALUE and not ALLOW_UNOWNED_INPLACE:",
    "new": "    if False and EDIT_IN_PLACE and ob.get(OWNER_KEY) != OWNER_VALUE and not ALLOW_UNOWNED_INPLACE:  # MUTANT",
    "tests": [
      "test_p0_final_edges_runtime.P0FinalEdgesTests.test_bevel_explicit_inplace_refuses_unowned_and_applied_modifiers"
    ]
  },
  {
    "id": "M15",
    "label": "cleanup falls back to selected objects implicitly",
    "kind": "additional-safety-check",
    "file": "scripts/cleanup_mesh.py",
    "old": "if not TARGETS:\n    print(\"RESULT: NO TARGETS; set explicit TARGETS, no selected-object fallback.\")\nelse:\n    col = None if EDIT_IN_PLACE else get_collection()",
    "new": "if not TARGETS:\n    TARGETS.extend(obj.name for obj in bpy.context.selected_objects if obj.type == \"MESH\")  # MUTANT\nif TARGETS:\n    col = None if EDIT_IN_PLACE else get_collection()",
    "tests": [
      "test_p0_transactional_runtime.P0TransactionalTests.test_cleanup_default_source_is_unchanged_and_no_selected_fallback"
    ]
  }
]


def verify_anchor(root: Path, mutant: dict) -> tuple[bool, str]:
    path = root / mutant["file"]
    source = path.read_text(encoding="utf-8")
    count = source.count(mutant["old"])
    if count != 1:
        return False, f"source replacement anchor count={count} (expected 1)"
    revised = source.replace(mutant["old"], mutant["new"], 1)
    try:
        compile(revised, str(path), "exec")
    except SyntaxError as exc:
        return False, f"syntactically invalid mutation: {exc}"
    path.write_text(revised, encoding="utf-8")
    return True, "valid"


def run_tests(root: Path, tests: list[str], timeout: int) -> dict:
    env = dict(os.environ)
    env["REQUIRE_BPY"] = "1"
    env["PYTHONPATH"] = os.pathsep.join([str(root / "tests"), str(root)])
    command = [sys.executable, "-u", str(root / "tests" / "run_mutation_subset.py"), *tests]
    try:
        process = subprocess.run(
            command, cwd=str(root), env=env, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=timeout, check=False)
        output = process.stdout or ""
        return {
            "exit_code": process.returncode,
            "ran_tests": "Ran " in output and " test" in output,
            "has_test_failure": "FAIL:" in output or "ERROR:" in output,
            "invalid_import": "_FailedTest" in output or "ModuleNotFoundError" in output,
            "tail": "\n".join(output.splitlines()[-36:]),
        }
    except subprocess.TimeoutExpired as exc:
        return {"exit_code": None, "ran_tests": False,
                "has_test_failure": False, "invalid_import": False,
                "tail": "TIMEOUT after %d seconds: %s" % (timeout, exc)}


def scratch_repo(source: Path, temp: Path) -> Path:
    root = temp / "repo"
    root.mkdir()
    shutil.copytree(source / "scripts", root / "scripts")
    shutil.copytree(source / "tests", root / "tests")
    return root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="fail when any mutant survives or is not verifiable")
    parser.add_argument("--report", default="mutation-results.json")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    ids = [item["id"] for item in MUTANTS]
    if len(ids) != 15 or len(set(ids)) != 15:
        raise RuntimeError("Expected exactly 15 unique mutation definitions")
    if args.timeout <= 0:
        raise ValueError("Timeout must be positive")

    tested = sorted({name for item in MUTANTS for name in item["tests"]})
    print("Mutation baseline: %d selected behavior tests" % len(tested), flush=True)
    baseline = run_tests(ROOT, tested, max(args.timeout, 180))
    if baseline["exit_code"] != 0 or not baseline["ran_tests"]:
        print("BASELINE ERROR: cannot certify mutation detection", flush=True)
        print(baseline["tail"], flush=True)
        return 2
    results = []
    for mutant in MUTANTS:
        start = time.monotonic()
        with tempfile.TemporaryDirectory(prefix="mcp-mutation-") as folder:
            root = scratch_repo(ROOT, Path(folder))
            valid, reason = verify_anchor(root, mutant)
            if not valid:
                outcome = "INVALID"
                details = reason
            else:
                run = run_tests(root, mutant["tests"], args.timeout)
                if run["exit_code"] == 0 and run["ran_tests"]:
                    outcome = "SURVIVED"
                elif run["exit_code"] == 1 and run["ran_tests"] and run["has_test_failure"] and not run["invalid_import"]:
                    outcome = "KILLED"
                else:
                    outcome = "INVALID"
                details = run["tail"]
        row = {key: mutant[key] for key in ("id", "label", "kind", "file", "tests")}
        row.update({"outcome": outcome, "seconds": round(time.monotonic() - start, 2),
                    "details": details})
        results.append(row)
        print("%s %s %s (%ss)" % (mutant["id"], outcome, mutant["label"], row["seconds"]), flush=True)
        if outcome != "KILLED":
            print(details, flush=True)
    summary = {status: sum(r["outcome"] == status for r in results)
               for status in ("KILLED", "SURVIVED", "INVALID")}
    report = {"baseline": {"pass": True, "selected_tests": tested},
              "matrix": "bpy wheel as installed in the runner (not live MCP)",
              "reference_commit": os.environ.get("GITHUB_SHA", "local"),
              "definitions": {"historical_survivors": 9, "additional_checks": 6},
              "summary": summary, "mutations": results}
    dest = Path(args.report)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("CAMPAIGN RESULT " + json.dumps(summary, sort_keys=True), flush=True)
    print("Report: " + str(dest.absolute()), flush=True)
    return 1 if args.strict and (summary["SURVIVED"] or summary["INVALID"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
