"""technique_history_query.py — retrieve matching records from the current .blend."""
import bpy
import json

TEXT_NAME = "MCP_Technique_History.json"
QUERY = "panel"
LIMIT = 10

text = bpy.data.texts.get(TEXT_NAME)
if text is None or text.get("_blender_mcp_technique_history") != "technique_history_v1":
    raise ValueError("tagged technique history was not found")
records = json.loads(text.as_string() or "[]")
query = str(QUERY).strip().lower()
matches = [
    record for record in records
    if query in str(record.get("task", "")).lower()
    or query in str(record.get("technique", "")).lower()
]
matches.sort(key=lambda record: record.get("timestamp_utc", ""), reverse=True)
print("TECHNIQUE HISTORY MATCHES")
print(json.dumps(matches[:max(1, int(LIMIT))], indent=2, sort_keys=True))
print("matches:", len(matches), "returned:", min(len(matches), max(1, int(LIMIT))))
print("Records are evidence, not an automatic guarantee of quality or compatibility.")
