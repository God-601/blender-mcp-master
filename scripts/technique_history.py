"""technique_history.py — append a verified execution record to the current .blend.

Records live in a tagged Blender Text datablock and are saved with the project when the
user saves it. This script does not save the .blend automatically.
"""
import bpy
import json
from datetime import datetime, timezone

# ---- CONFIG ----------------------------------------------------------------
RECORD = {
    "task": "stylized hard-surface panel",
    "technique": "parametric_panel_boolean",
    "parameters": {"bevel_width": 0.035, "pocket_depth": 0.12},
    "result": "created",
    "evidence": ["MCP_HS_Panel", "MCP_HS_Panel_Pocket_Cutter"],
    "limitations": ["visual review must be completed separately"],
}
TEXT_NAME = "MCP_Technique_History.json"
# ----------------------------------------------------------------------------
OWNER_KEY = "_blender_mcp_technique_history"
OWNER_VALUE = "technique_history_v1"

text = bpy.data.texts.get(TEXT_NAME)
if text is None:
    text = bpy.data.texts.new(TEXT_NAME)
    text[OWNER_KEY] = OWNER_VALUE
elif text.get(OWNER_KEY) != OWNER_VALUE:
    raise ValueError("Text datablock exists but is not owned by technique history")
records = []
raw = text.as_string().strip()
if raw:
    try:
        records = json.loads(raw)
        if not isinstance(records, list):
            raise ValueError("history root must be a list")
    except Exception as exc:
        raise ValueError("existing history is not valid JSON; refusing to overwrite: " + str(exc))
entry = dict(RECORD)
entry["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
entry["blender_version"] = bpy.app.version_string
entry["status"] = "USER_REVIEW_REQUIRED"
records.append(entry)
text.clear()
text.write(json.dumps(records, indent=2, sort_keys=True))
print("TECHNIQUE HISTORY:", TEXT_NAME, "records=", len(records))
print("The record is stored in the .blend datablock; save the project to persist it.")
