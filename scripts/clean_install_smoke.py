"""Validate a standalone Agent Skill ZIP through a real fresh-directory install.

This does not launch Codex/Claude, connect to Blender, or claim that an agent
recognized the skill. It verifies archive integrity, installs into an isolated
agent-like home, checks routing/resources and runs a safe Python helper there.

Usage:
  python scripts/clean_install_smoke.py dist/blender-mcp-master-1.0-PREFLIGHT-NOT-A-RELEASE.zip dist/SHA256SUMS.txt --report dist/clean-install-report.json
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import re
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SKILL_NAME = "blender-mcp-master"
PREFIX = SKILL_NAME + "/"
REQUIRED = (
    "SKILL.md", "README.md", "LICENSE", "CHANGELOG.md",
    "references/clarification-gate.md",
    "references/p0-integrity.md",
    "references/quality-checklist.md",
    "references/crash-recovery-and-baselines.md",
    "scripts/inspect_geometry.py",
    "scripts/uv_diagnostics.py",
    "scripts/scene_baseline_snapshot.py",
    "scripts/compare_scene_baselines.py",
    "scripts/specialist_plan.py",
    "scripts/specialist_orchestrator.py",
    "references/specialist-modules.json",
    "integrations/agents/codex_reviewer.py",
    "integrations/agents/run_specialists.py",
    "docs/QUICKSTART.md",
)
MAX_ENTRIES = 2500
MAX_UNCOMPRESSED = 64 * 1024 * 1024


def checked_hash(archive, checksums):
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    entries = []
    for line in checksums.read_text(encoding="utf-8").splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            raise ValueError("Invalid SHA256SUMS.txt entry")
        digest, filename = parts
        filename = filename.lstrip("*").strip()
        if filename == archive.name:
            entries.append(digest.lower())
    if len(entries) != 1 or not re.fullmatch(r"[0-9a-f]{64}", entries[0]):
        raise ValueError("Missing or ambiguous ZIP hash entry")
    if actual != entries[0]:
        raise ValueError("ZIP SHA256 mismatch")
    return actual


def validate_members(zf):
    members = zf.infolist()
    if not members or len(members) > MAX_ENTRIES:
        raise ValueError("Unexpected number of archive entries")
    names = [info.filename for info in members]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate ZIP paths")
    if sum(info.file_size for info in members) > MAX_UNCOMPRESSED:
        raise ValueError("ZIP uncompressed payload too large")
    for info in members:
        name = info.filename
        parts = name.rstrip("/").split("/")
        if (not name.startswith(PREFIX) or name.startswith("/") or
                "\\" in name or any(x in ("", ".", "..") for x in parts)):
            raise ValueError("Unsafe ZIP member: " + name)
        if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
            raise ValueError("Symlink ZIP member rejected: " + name)
    for required in REQUIRED:
        if PREFIX + required not in names:
            raise ValueError("Missing skill file: " + required)
    if zf.testzip() is not None:
        raise ValueError("Corrupt ZIP entry")


def smoke(archive_path, checksums_path):
    archive = Path(archive_path).resolve()
    checksums = Path(checksums_path).resolve()
    checksum = checked_hash(archive, checksums)
    with tempfile.TemporaryDirectory(prefix="blender-master-clean-home-") as temp:
        home = Path(temp)
        skills_dir = home / ".agents" / "skills"
        if skills_dir.exists():
            raise ValueError("Clean-home fixture was not empty")
        skills_dir.mkdir(parents=True)
        with zipfile.ZipFile(archive) as zf:
            validate_members(zf)
            zf.extractall(skills_dir)
        installed = skills_dir / SKILL_NAME
        if sorted(p.name for p in skills_dir.iterdir()) != [SKILL_NAME]:
            raise ValueError("Unexpected installed skill folders")
        skill_file = installed / "SKILL.md"
        skill = skill_file.read_text(encoding="utf-8")
        front = re.match(r"\A---\n(.*?)\n---\n", skill, re.S)
        if front is None or not re.search(r"(?m)^name:\s*blender-mcp-master\s*$", front.group(1)):
            raise ValueError("Skill frontmatter missing declared name")
        if "GENERAL KICKOFF" not in skill or "references/p0-integrity.md" not in skill:
            raise ValueError("Installed skill lost safety routing")
        for resource in re.findall(r"(?:references/[\w-]+\.md|scripts/[\w-]+\.py)", skill):
            if not (installed / resource).is_file():
                raise ValueError("Broken installed skill resource: " + resource)
        readme = (installed / "README.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)]+)\)", readme)
        links += re.findall(r'(?:href|src)="([^"]+)"', readme)
        local = [link.split("#", 1)[0] for link in links if not link.startswith(
            ("http://", "https://", "#", "mailto:", "data:"))]
        missing = [link for link in local if link and not (installed / link).is_file()]
        if missing:
            raise ValueError("Broken installed README links: " + repr(missing))
        scripts = sorted((installed / "scripts").glob("*.py"))
        for script in scripts:
            ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
        helper = installed / "scripts" / "compare_scene_baselines.py"
        spec = importlib.util.spec_from_file_location("installed_scene_baseline_compare", helper)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        record = {
            "schema_version": 1,
            "scope": "explicit_protected_objects_selected_properties",
            "status": "MEASURED", "missing_names": [], "errors": [],
            "objects": [{"name": "USER_Keep_Mesh", "fingerprint_sha256": "a" * 64}],
        }
        if mod.compare(record, record)["status"] != "PASS":
            raise ValueError("Installed helper failed unchanged-scene smoke check")
        changed = dict(record)
        changed["objects"] = [{"name": "USER_Keep_Mesh", "fingerprint_sha256": "b" * 64}]
        if mod.compare(record, changed)["status"] != "ISSUE":
            raise ValueError("Installed helper failed scene-change smoke check")
        brief = home / 'brief.json'
        brief.write_text(json.dumps({'category': 'game_asset', 'needs': ['export', 'uv', 'pbr']}), encoding='utf-8')
        planned = subprocess.run([sys.executable, str(installed / 'scripts/specialist_plan.py'), str(brief)],
                                 capture_output=True, text=True, encoding='utf-8', timeout=10, check=True)
        plan = json.loads(planned.stdout)
        if plan['steps'][-2]['module'] != 'export' or plan['mode'] != 'delegated':
            raise ValueError('Installed specialist planner failed')
        return {
            "result": "PASS", "scope": "isolated agent-style skill ZIP installation",
            "sha256": checksum, "archive_name": archive.name,
            "installed_relative_path": ".agents/skills/blender-mcp-master/SKILL.md",
            "python_scripts_parsed": len(scripts),
            "readme_links_checked": len(local),
            "skill_routing": "PASS",
            "protected_object_helper": "PASS",
            "specialist_planning": "PASS",
            "actual_agent_discovery": "NOT VERIFIED",
            "live_blender_mcp_connection": "NOT VERIFIED",
            "target_engine_import": "NOT VERIFIED",
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive")
    parser.add_argument("checksums")
    parser.add_argument("--report", default=None)
    args = parser.parse_args()
    try:
        report = smoke(args.archive, args.checksums)
    except (OSError, ValueError, zipfile.BadZipFile, SyntaxError) as error:
        report = {"result": "ISSUE", "reason": str(error)}
    print(json.dumps(report, indent=2, sort_keys=True))
    if args.report:
        Path(args.report).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    # Return a boolean to callers without terminating a host process.
    return report["result"] == "PASS"


if __name__ == "__main__":
    if not main():
        raise RuntimeError("Isolated clean-install smoke failed")
