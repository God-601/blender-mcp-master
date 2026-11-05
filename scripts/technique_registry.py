"""Opt-in local technique registry shared across Blender projects.

Pure-Python functions work without Blender. To import a tagged technique history
from the current .blend, run this script inside Blender after setting
REGISTRY_PATH and EXPLICIT_APPROVAL=True. Default mode only previews candidates.

No automatic scan, background sync, network access, or AI model training.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

# --- CONFIG -----------------------------------------------------------------
REGISTRY_PATH = ""            # User-owned absolute path, e.g. C:/BlenderMCP/techniques.json
MODE = "preview"              # preview | merge | query
QUERY = ""                    # For query mode
EXPLICIT_APPROVAL = False     # Must be True for any file write
TEXT_NAME = "MCP_Technique_History.json"
# -----------------------------------------------------------------------------
MAX_BYTES = 2_000_000
MAX_RECORDS = 10000


def _validate_path(path):
    p = Path(path)
    if not p.is_absolute():
        raise ValueError("registry path must be an explicit absolute path")
    if p.is_symlink():
        raise ValueError("registry file must not be a symbolic link")
    if not p.parent.is_dir():
        raise ValueError("registry parent folder does not exist")
    return p


def _approved(record):
    if not isinstance(record, dict):
        return False
    if record.get("status") != "REVIEWED_PASS":
        return False
    review = record.get("review", {})
    if not isinstance(review, dict) or review.get("result") != "pass":
        return False
    if not str(review.get("reviewer", "")).strip():
        return False
    score = review.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 4:
        return False
    for field in ("task", "technique", "blender_version"):
        if not isinstance(record.get(field), str) or not record[field].strip():
            return False
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
        return False
    if not isinstance(record.get("parameters", {}), dict):
        return False
    if record.get("kind", "technique") not in ("technique", "defect_resolution"):
        return False
    if record.get("kind") == "defect_resolution":
        for field in ("defect_id", "symptom", "root_cause", "correction"):
            if not isinstance(record.get(field), str) or not record[field].strip():
                return False
        affected = record.get("affected_objects")
        if not isinstance(affected, list) or not affected or any(
                not isinstance(name, str) or not name.strip() for name in affected):
            return False
        # A corrected issue needs evidence of both states and a human/agent
        # review record, not a spontaneous 'self-learning' claim.
        for field in ("before_evidence", "after_evidence"):
            refs = record.get(field)
            if not isinstance(refs, list) or not refs or any(
                    not isinstance(item, str) or not item.strip() for item in refs):
                return False
    try:
        json.dumps(record, ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError):
        return False
    return True


def _fingerprint(record):
    keys = ("task", "technique", "parameters", "blender_version", "evidence",
            "kind", "defect_id", "symptom", "root_cause", "correction", "affected_objects",
            "before_evidence", "after_evidence")
    stable = {k: record.get(k) for k in keys}
    raw = json.dumps(stable, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def merge_reviewed(existing, incoming):
    if not isinstance(existing, list) or not isinstance(incoming, list):
        raise ValueError("registry and history must be JSON arrays")
    by_id = {}
    for record in existing:
        if not _approved(record):
            raise ValueError("existing registry contains unreviewed/invalid records")
        ident = record.get("registry_id") or _fingerprint(record)
        if ident != _fingerprint(record):
            raise ValueError("existing registry has inconsistent record IDs")
        by_id[ident] = dict(record, registry_id=ident)
    rejected = added = 0
    for record in incoming:
        if not _approved(record):
            rejected += 1
            continue
        ident = _fingerprint(record)
        if ident not in by_id:
            by_id[ident] = dict(record, registry_id=ident)
            added += 1
    if len(by_id) > MAX_RECORDS:
        raise ValueError("registry record limit exceeded")
    return {
        "records": sorted(by_id.values(), key=lambda x: x["registry_id"]),
        "added": added,
        "rejected": rejected,
    }


def read_registry(path):
    p = _validate_path(path)
    if not p.exists():
        return []
    if p.stat().st_size > MAX_BYTES:
        raise ValueError("registry exceeds size limit")
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("cannot read registry; refusing to replace: " + str(exc)) from exc
    if not isinstance(data, list):
        raise ValueError("registry must contain a JSON array; refusing to overwrite")
    merge_reviewed(data, [])
    return data


def find_techniques(records, query, limit=10):
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    q = str(query).strip().lower()
    if not q:
        return []
    matches = [r for r in records if _approved(r) and
               (q in r["task"].lower() or q in r["technique"].lower())]
    matches.sort(key=lambda r: (r["review"]["score"], r.get("timestamp_utc", "")),
                 reverse=True)
    return matches[:max(1, int(limit))]


def persist_registry(path, incoming, allow_write=False):
    if allow_write is not True:
        raise ValueError("explicit approval required to write cross-project technique registry")
    p = _validate_path(path)
    lock = p.with_name(p.name + ".lock")
    if lock.exists() or lock.is_symlink():
        raise ValueError("registry lock exists; check other writers before retrying")
    # Exclusivity prevents concurrent writers from replacing each other's work.
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError("registry is already locked") from exc
    os.close(fd)
    staged = None
    try:
        existing = read_registry(p)
        merged = merge_reviewed(existing, incoming)
        output = json.dumps(merged["records"], ensure_ascii=False, sort_keys=True,
                            indent=2, allow_nan=False).encode("utf-8")
        if len(output) > MAX_BYTES:
            raise ValueError("resulting registry exceeds size limit")
        if not merged["added"]:
            return {"added": 0, "rejected": merged["rejected"], "count": len(existing),
                    "written": False}
        with tempfile.NamedTemporaryFile(prefix=p.name + ".tmp-", dir=str(p.parent),
                                         delete=False) as f:
            staged = Path(f.name)
            f.write(output)
            f.flush()
            os.fsync(f.fileno())
        if p.exists():
            backup = p.with_name(p.name + ".backup-" +
                                 datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") +
                                 "-" + uuid4().hex[:8])
            shutil.copy2(p, backup)
        os.replace(str(staged), str(p))
        staged = None
        return {"added": merged["added"], "rejected": merged["rejected"],
                "count": len(merged["records"]), "written": True}
    finally:
        if staged is not None and staged.exists():
            staged.unlink()
        lock.unlink(missing_ok=True)


def main():
    if MODE not in ("preview", "merge", "query"):
        raise ValueError("unsupported registry mode")
    if not REGISTRY_PATH:
        raise ValueError("set REGISTRY_PATH to an explicit absolute location")
    if MODE == "query":
        print(json.dumps(find_techniques(read_registry(REGISTRY_PATH), QUERY),
                         ensure_ascii=False, indent=2))
        return
    import bpy
    text = bpy.data.texts.get(TEXT_NAME)
    if text is None or text.get("_blender_mcp_technique_history") != "technique_history_v1":
        raise ValueError("tagged technique history not found in current .blend")
    source = json.loads(text.as_string() or "[]")
    existing = read_registry(REGISTRY_PATH)
    if MODE == "preview":
        result = merge_reviewed(existing, source)
        print("DRY RUN — approved entries:", result["added"],
              "rejected:", result["rejected"], "no files modified")
        return
    result = persist_registry(REGISTRY_PATH, source, allow_write=EXPLICIT_APPROVAL)
    print("TECHNIQUE REGISTRY", json.dumps(result, sort_keys=True))
    print("No automatic training or inference from unreviewed outcomes.")


if __name__ == "__main__":
    main()
