# Specialist orchestration

`specialist-modules.json` maps modeling, materials, UV, retopology,
optimization, export and validation to existing resources and acceptance
criteria. `scripts/specialist_plan.py` resolves a workflow-router JSON brief
without reading the guides or editing the scene. The optional resource MCP's
`list_blender_resources` returns the same registry as `specialist_modules`.

Simple work stays with the coordinator. Plans with three or more production
disciplines request delegation; unavailable agent tools must be reported as
NOT VERIFIED. Never manufacture specialist identities to satisfy a gate.

Before any execution, discover the actual host's tools and scene identity,
name owned/protected objects and bind a verified checkpoint. One writer at a
time; reviewers inspect artifacts without editing the shared Blender scene.
The coordinator owns the final result and recovery decision. A checkpoint
reference alone does not prove recovery, and a JSON PASS does not establish
artistic quality, physical collision or target-engine compatibility.

## Execute through a host

```sh
python scripts/specialist_plan.py brief.json
python integrations/agents/run_specialists.py brief.json
python integrations/agents/run_specialists.py brief.json --context context.json --evidence-root ./evidence --adapter-config ./trusted-host.json --execute
```

The first two commands only plan. `--execute` is intentional host invocation;
without a host the result is NOT VERIFIED. `trusted-host.json` is operator
configuration: `{"command":["python","/absolute/path/to/my_host.py"],"timeout_seconds":60}`.
It must not come from a model, downloaded asset or task brief. No shell is
used. The standalone CLI exits nonzero on ISSUE/NOT VERIFIED.

Context contains `asset_id`, `scene_id`, exact source `commit_sha`, nonempty
`owned_objects`, disjoint `protected_objects`, and relative `checkpoint_ref`.
The checkpoint must already exist under the evidence root. The host creates
it using a compatible Blender save/copy operation; this runner never treats
a random file as a validated/recoverable .blend. Before using it, the native
host must verify save, reopen/recovery and source ownership.

`CommandHost` sends one JSON object to stdin and expects one JSON object on
stdout. Diagnostics go to stderr. Operations:

- `probe`: payload is context. Return actual `scene_id`, live connection
  `session_id`, `checkpoint_ref`, `protected` mapping of every protected name
  to its SHA256 selected-property fingerprint, available `modules`, and
  boolean `write`/`delegation` capabilities. Use the existing scoped Blender
  baseline logic; never substitute static metadata for a live probe.
- `dispatch`: payload includes fresh `request_id`, full original `task`,
  destination, context, selected module/acceptance/resources, previous
  hashed results and checkpoint digest. Invoke the actual named specialist
  with only this stage's resources. Honor read/write scope. In single mode
  all production and validation stages use the coordinator; independence
  remains NOT VERIFIED. In delegated mode choose suitable specialists and
  final QA must use a different actual identity from every producer.
  Return `request_id`, actual `agent_id`/unique `run_id`, `status`
  (PASS/ISSUE/NOT VERIFIED), relative `evidence` files, `errors`, `metrics`,
  and a relative JSON `receipt`.

`write_receipt(root, request, result)` creates a new exclusive receipt binding
request/run/agent/module/asset/scene/source SHA/status to artifact SHA256s.
The runner rehashes it and its evidence, rejects stale bindings and passes
compact receipts onward. Host assertions remain a trust boundary: hashes
prove bytes and correlation, not engineering/visual truth or agent honesty.

Execution is serial, including reads, so this coordinator never has competing
scene writers. Different coordinator processes are **not** a global lock:
the native host must hold the session writer lease. It must also restrict
shared datablocks/global edits and terminate descendant agents on timeout.
Any stage failure stops dependent work. No mutation retries or automatic
rollback occur; reconnect/protected/checkpoint drift requires recovery review.
Rerunning an executed plan is a new run and may repeat writes; inspect the
previous receipt and scene before explicitly restarting.

## Concrete Codex review worker

`integrations/agents/codex_reviewer.py` provides
`CodexReviewer(evidence_root).dispatch(request)` for a native host's **read-only**
steps. It actually launches Codex CLI, uses structured output, disables user
configuration loading, selects its read-only sandbox, obtains agent/run
identity from CLI events and writes the bound receipt in the coordinator.
Write requests are rejected before launch. Installed/authenticated Codex CLI
and its normal provider access are required; no model or token savings are
assumed. Tool configuration, production writers and live scene probes stay
with the embedding host. This is not a universal MCP-to-agent bridge.

Unit tests exercise real JSON subprocess transport and timeout plus simulated
scene failures. Those fixtures are not live Blender or LLM production trials.

## Native Blender host

`integrations/agents/blender_native_host.py` now supplies a concrete bpy host:

```python
with BlenderNativeHost(evidence_root, asset_id=asset_id,
        owned_objects=owned_names, protected_objects=protected_names,
        commit_sha=source_sha, actor_id=actual_client_agent_id,
        callbacks=inspected_callbacks, reviewer=independent_reviewer) as host:
    result = run(task, host.context, evidence_root, host, dry_run=False)
```

Run this inside Blender after inspecting the scene. Callbacks keyed by module
receive the bounded request and return explicit status/evidence/metrics/errors;
they are trusted code inspected by the calling agent, not Python from an
untrusted brief. The host creates real saved-copy checkpoints and stage files,
leaving the original filepath intact. It requires every existing unowned object
to be protected and rejects shared mesh data and shader/image dependencies
between owned and unowned objects. A per-process, per-scene exclusive file lease
prevents concurrent native hosts. A crashed process can leave a stale lock;
verify its PID/scene before removing it. Different Blender processes are separate
scene sessions; this lease does not lock their common source file on disk.

The host checks selected geometry/RNA/material/world properties before and
after callbacks; read stages also compare owned-object properties. These are
damage-detection checks with documented limits, not a complete .blend equality
proof or Python sandbox. Image pixels, arbitrary collection/custom properties,
some rig/deformation data and external files are not fully fingerprinted.
Callbacks must bound synchronous work and terminate descendants they launch.
On failure inspect the retained checkpoint; recovery never silently replaces
the current scene. Save/reopen is exercised in a separate scratch Blender test.

The Codex worker accepts actual text bytes and up to three explicitly selected
hashed upstream PNGs, pins input hashes across the review, restricts evidence
responses to actual input paths, retains parsed response/usage receipts, and
keeps scoped notes distinct from errors. This allows independent inspection
without granting shell access. A provider usage receipt is a measurement of that
run, not proof of savings or a matched A/B benchmark.
