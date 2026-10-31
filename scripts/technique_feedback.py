"""technique_feedback.py — attach explicit reviewer feedback to one history record."""
import bpy
import json

TEXT_NAME = "MCP_Technique_History.json"
RECORD_INDEX = -1
FEEDBACK = {
    "reviewer": "user",
    "result": "pass",
    "score": 3,
    "notes": "Visual inspection completed; proportions acceptable.",
}

text = bpy.data.texts.get(TEXT_NAME)
if text is None or text.get("_blender_mcp_technique_history") != "technique_history_v1":
    raise ValueError("tagged technique history was not found")
records = json.loads(text.as_string() or "[]")
if not records:
    raise ValueError("technique history is empty")
index = int(RECORD_INDEX)
if index < 0:
    index += len(records)
if index < 0 or index >= len(records):
    raise IndexError("record index is outside the history")
feedback = dict(FEEDBACK)
if feedback.get("result") not in ("pass", "issue", "not_reviewed"):
    raise ValueError("feedback result must be pass, issue, or not_reviewed")
if "score" in feedback and not 0 <= int(feedback["score"]) <= 4:
    raise ValueError("feedback score must be between 0 and 4")
records[index]["review"] = feedback
records[index]["status"] = {
    "pass": "REVIEWED_PASS",
    "issue": "REVIEWED_ISSUE",
    "not_reviewed": "USER_REVIEW_REQUIRED",
}[feedback["result"]]
text.clear()
text.write(json.dumps(records, indent=2, sort_keys=True))
print("FEEDBACK STORED:", index, records[index].get("technique"))
print("This records explicit feedback; it does not train or modify an AI model.")
