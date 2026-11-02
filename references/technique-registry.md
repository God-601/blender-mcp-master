# Cross-project technique registry (explicit opt-in)

`scripts/technique_registry.py` extends the existing Blender Text-based `technique_history.py`, `technique_feedback.py`, and `technique_history_query.py` workflow with a **local JSON file that can be reused across .blend projects**.

It does **not** train an AI model, discover all projects automatically, connect to external services or silently collect user data. Only records explicitly marked `REVIEWED_PASS`, with reviewer identity, a score (0–4), a real evidence reference, task, technique and Blender version, qualify for import. The existence of an evidence filename does not prove that someone inspected the image; the reviewer is responsible for checking it.

## Use in Blender

1. Run `technique_history.py` after a technique was executed; it creates a review-required record in the current project.
2. Verify the actual asset (geometry and screenshots); run `technique_feedback.py` with explicit reviewer feedback and pass/issue result.
3. Open `scripts/technique_registry.py` and set `REGISTRY_PATH` to a **user-controlled absolute path** within an existing directory, e.g. `C:/BlenderMCP/techniques.json`.
4. Leave `MODE = "preview"` and run in Blender. It prints how many verified candidates would be added without touching the registry file.
5. If the preview is correct, choose `MODE = "merge"` and set `EXPLICIT_APPROVAL = True`. A same-folder temporary file, an exclusive lock and a timestamped backup protect existing data during updates.
6. In another Blender project, set `MODE = "query"` and `QUERY = "panel"` to inspect approved matches. Choosing a past technique remains an agent judgment based on the new Blender version and current task.

### Constraints

- No default registry location, background sync or network.
- Concurrent writers must respect the lock; a leftover lock after a crash requires investigation before manual removal.
- The storage can contain task names, filenames and reviewer notes. Avoid recording secrets or sensitive project content. Backups are also local and not deleted automatically.
- Rejected and unreviewed entries are not carried into the reusable registry.
- Retrieval is deterministic text matching plus review score, not learned semantic similarity.
- The saved technique registry cannot by itself tell whether a generated model looks correct.

For per-project details, see `technique_history.py` and the [quality loop](modeling-quality-loop.md).
