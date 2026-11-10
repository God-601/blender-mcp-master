"""Recorded Codex A/B parameter-generation campaign, rendered by a trusted adapter.

This deliberately measures constrained geometry decisions, not freeform MCP use.
No provider-generated Python is executed. Run with ordinary Python; Blender uses
the same file with --build. All files are confined to the explicit output root.
"""
import argparse
import concurrent.futures
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

CASES = {
    "chair": {
        "brief": "Create a stylized wooden chair: seat width 0.5m, depth 0.5m, seat top 0.48m, total height 0.95m. Four square legs must touch z=0 and the seat underside; back has two posts and a broad backrest. Brown wood, readable supports, <=1200 triangles. All artistic choices are delegated.",
        "guide": "references/hard-surface.md",
        "params": {"seat_width": (.45, .55), "seat_depth": (.45, .55), "seat_height": (.43, .53), "seat_thickness": (.025, .07), "leg_width": (.035, .075), "leg_inset": (0, .04), "back_height": (.88, 1.02), "back_panel_height": (.18, .35), "support_height": (.12, .3), "bevel": (.001, .008)},
        "budget": 1200,
    },
    "sword": {
        "brief": "Create a stylized steel fantasy sword standing along +Z with pommel base z=0: total height 1.2m, blade around 0.85m and 0.10m wide tapering to a central point, thickness <=0.025m; centered guard around 0.25m wide, brown grip and metal pommel. Keep silhouette readable and all parts touching, <=1000 triangles. All artistic choices are delegated.",
        "guide": "references/hard-surface.md",
        "params": {"blade_length": (.75, .9), "blade_width": (.08, .13), "blade_thickness": (.008, .025), "tip_fraction": (.13, .3), "guard_width": (.2, .32), "guard_height": (.035, .07), "grip_length": (.19, .26), "grip_width": (.028, .05), "pommel_height": (.045, .075), "bevel": (.001, .004)},
        "budget": 1000,
    },
    "tree": {
        "brief": "Create a low-poly stylized spruce for a game: grounded trunk, total height 4m, maximum canopy diameter about 2.2m, 4-6 overlapping tapering green foliage tiers with brown trunk visible at the bottom. Coherent taper, <=1950 evaluated triangles, UVs and node materials, GLB destination. No image textures are supplied. All artistic choices are delegated.",
        "guide": "references/organic.md",
        "params": {"height": (3.8, 4.2), "trunk_radius": (.1, .2), "trunk_height": (2.6, 3.5), "canopy_radius": (.95, 1.2), "canopy_start": (.65, 1.0), "tiers": (4, 6), "segments": (8, 16), "overlap": (.25, .55), "taper": (.45, .7)},
        "integer": ["tiers", "segments"],
        "budget": 1950,
    },
    "modular_wall": {
        "brief": "Create a straight modular medieval wall assembly: three contiguous modules each 2m wide, 2.5m tall, 0.25m thick, total width 6m. Ground at z=0. Each module has a stone panel inside two timber posts and top/bottom beams. Timber/panel contacts must meet without gaps; module joints share a datum. Warm stone and dark brown timber, <=1500 triangles. All artistic choices are delegated.",
        "guide": "references/modular-modeling.md",
        "params": {"module_width": (1.9, 2.1), "height": (2.4, 2.6), "thickness": (.22, .28), "post_width": (.12, .22), "beam_height": (.12, .22), "panel_depth": (.16, .24), "bevel": (.001, .008)},
        "budget": 1500,
    },
    "retopology": {
        "brief": "Retopologize the supplied irregular open tube source fixture into a lower-density quad tube. Preserve source and sentinel exactly. Source has 32 vertices per ring, 25 ordered rings, z=0..2; boundary rings are open. Choose 8-16 vertices/ring and 5-10 rings, bridge explicit ordered rings, relax only interior vertices then project to source surface. Target <=300 triangles, two boundary loops, no non-manifold interior edges, max source-surface error <=0.05m. No rig or shape keys. UVs/node material and GLB. All artistic choices are delegated.",
        "guide": "references/advanced-retopology.md",
        "params": {"segments": (8, 16), "rings": (5, 10), "relax_iterations": (1, 5), "relax_factor": (.1, .5)},
        "integer": ["segments", "rings", "relax_iterations"],
        "budget": 300,
    },
}


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


def check_shared_fixture(path, spec):
    metadata = path.with_suffix('.input.json')
    expected = {'fixture_sha256': digest(spec), 'blend_sha256': digest(path.read_bytes())}
    if not metadata.is_file() or json.loads(metadata.read_text(encoding='utf-8')) != expected:
        raise ValueError('Shared fixture inputs changed or lack provenance; use a new evidence directory')


def fixture(case):
    data = {"sentinel": {"name": "PROTECTED_SENTINEL", "location": [30, 30, 30], "size": [.321, .654, .987]}, "source": None}
    if case == "retopology":
        verts = []
        for j in range(25):
            z = j / 12
            for i in range(32):
                a = 2 * math.pi * i / 32
                r = .45 + .09 * math.sin(z * 3) + .035 * math.cos(3 * a + z)
                verts.append([r * math.cos(a), r * math.sin(a), z])
        faces = [[j*32+i, j*32+(i+1)%32, (j+1)*32+(i+1)%32, (j+1)*32+i] for j in range(24) for i in range(32)]
        data["source"] = {"name": "PROTECTED_SOURCE_TUBE", "vertices": verts, "faces": faces, "ring_size": 32, "rings": 25}
    return data


def schema(case):
    spec = CASES[case]
    props = {k: {"type": "integer" if k in spec.get("integer", []) else "number", "minimum": limits[0], "maximum": limits[1]} for k, limits in spec["params"].items()}
    return {"type": "object", "properties": {"parameters": {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}, "rationale": {"type": "string"}}, "required": ["parameters", "rationale"], "additionalProperties": False}


def validate(case, result):
    if not isinstance(result, dict) or set(result) != {"parameters", "rationale"} or not isinstance(result["rationale"], str):
        raise ValueError("invalid top-level generation")
    p, spec = result["parameters"], CASES[case]
    if not isinstance(p, dict) or set(p) != set(spec["params"]):
        raise ValueError("unexpected parameter keys")
    for key, (low, high) in spec["params"].items():
        v = p[key]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not low <= v <= high:
            raise ValueError("out-of-bounds parameter: " + key)
        if key in spec.get("integer", []) and not isinstance(v, int):
            raise ValueError("expected integer: " + key)
    return p


def self_check():
    for case in CASES:
        params = {k: int((a+b)//2) if k in CASES[case].get("integer", []) else (a+b)/2 for k, (a, b) in CASES[case]["params"].items()}
        assert validate(case, {"parameters": params, "rationale": "test"}) == params
        first = next(iter(params))
        bad = dict(params, **{first: float("nan")})
        try:
            validate(case, {"parameters": bad, "rationale": "test"})
        except ValueError:
            pass
        else:
            raise AssertionError("nonfinite generation accepted")
    assert fixture("retopology")["source"]["vertices"] != fixture("chair")["source"]
    print("SELF_CHECK_PASS", flush=True)


def provider_command(cli, out, model=None, effort=None):
    command = [cli, 'exec', '--ignore-user-config', '--ephemeral', '--json', '--sandbox', 'read-only', '--skip-git-repo-check', '--cd', str(out), '--output-schema', str(out / 'schema.json'), '--output-last-message', str(out / 'generation.json')]
    if model:
        command.extend(['--model', model])
    if effort:
        command.extend(['--config', 'model_reasoning_effort=' + json.dumps(effort)])
    return command + ['-']


def generation_matches(previous, record):
    return bool(previous and record.get('actual_prompt_sha256') and
                all(previous.get(key) == record.get(key) for key in
                    ('actual_prompt_sha256', 'model_requested', 'effort_requested')) and
                previous.get('thread_id') and previous.get('provider_usage'))


def run_campaign(args):
    self_check()
    repo = Path(__file__).resolve().parents[2]
    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if args.workers not in (1, 2, 3):
        raise ValueError("workers must be 1..3")
    cli = shutil.which("codex")
    if not cli or not Path(args.blender).is_file():
        raise RuntimeError("Codex CLI or Blender unavailable")
    guides = {c: ["SKILL.md", CASES[c]["guide"]] for c in CASES}
    manifest = {"campaign_version": 1, "scope": "Constrained declarative parameter generation using real Codex CLI; trusted fixed Blender adapter, not freeform live MCP or full skill capability certification.", "cli": cli, "model_override": None, "model_identity": None, "model_identity_status": "NOT VERIFIED unless emitted by provider events", "cases": CASES, "guide_sources": {}, "adapter_sha256": digest(Path(__file__).read_bytes()), "limitations": ["No reference images or blind artistic scoring.", "Adapter guarantees components, UV creation, and export; these are not evidence of agent tool execution.", "Simple node materials only, no image-based PBR maps, rig, or deformation certification.", "Retopology is source-backed tube ring bridging/relaxation/projection, not arbitrary character retopology."]}
    manifest.update(model_requested=args.model, effort_requested=args.effort)
    for rel in sorted({p for paths in guides.values() for p in paths}):
        src = repo / rel
        text = src.read_text(encoding="utf-8")
        copied = root / "source_guides" / rel
        copied.parent.mkdir(parents=True, exist_ok=True)
        copied.write_text(text, encoding="utf-8")
        manifest["guide_sources"][rel] = {"sha256": digest(text.encode()), "bytes": len(text.encode())}
    write_json(root / "manifest.json", manifest)

    def trial(case, arm, number):
        out = root / (case + "-" + arm + "-" + str(number))
        out.mkdir(exist_ok=True)
        receipt = out / "receipt.json"
        previous = None
        adapter_sha = digest(Path(__file__).read_bytes())
        if receipt.exists():
            previous = json.loads(receipt.read_text(encoding="utf-8"))
            archive = root / 'attempts' / (out.name + '-' + str(uuid.uuid4()))
            shutil.copytree(out, archive)
        scene = fixture(case)
        write_json(out / "fixture.json", scene)
        shape = schema(case)
        write_json(out / "schema.json", shape)
        task = "Controlled geometry parameter task v1.\n" + CASES[case]["brief"] + "\nUse the provided fixed adapter contract. Return only the schema JSON, no tools, files, commands, questions, or claimed visual inspection. The adapter constructs components and creates UV/materials. All source objects are protected. Choose values that satisfy brief proportions and budget.\nSchema:\n" + json.dumps(shape, sort_keys=True)
        if case == "retopology":
            task += "\nActual source fixture, with vertices and ordered faces:\n" + json.dumps(scene["source"], separators=(",", ":"))
        task += "\nAdapter geometry: " + {"chair": "Seat top=seat_height. Leg centers at +/- (seat size/2-leg_width/2-leg_inset), run from ground to seat underside. Back posts share rear leg XY, run from seat to back_height. Broad panel fits between posts. Support beams link legs at support_height. Bevel one segment.", "sword": "Pommel box z=0..pommel_height, grip above, guard above, blade above guard. Blade is an extruded six-point symmetrical tapered polygon. Bevel applies to boxes, not blade.", "tree": "Trunk cylinder at ground. Tiers: base_z=canopy_start+i*step, step=(height-canopy_start)/(tiers-1+1+overlap). tier_height=step*(1+overlap); radius=canopy_radius*(1-taper*i/(tiers-1)). Last apex is exactly height.", "modular_wall": "3 module origins at 0,width,2*width. Each occupies [origin,origin+width]. Posts are inset half their width; beams fit between posts. Stone panel fills between posts and beams, centered Y. Actual max panel depth must not exceed thickness. Bevel one segment.", "retopology": "Interpolate ordered source rings at evenly spaced z and angular samples. Construct each ring edges then bridge adjacent ordered equal-size loops with bmesh bridge_loops. Relax non-boundary vertices for requested iterations then project all vertices to nearest real source surface using BVH. Preserve source unchanged; two uncapped boundaries."}[case]
        (out / "common_task.txt").write_text(task, encoding="utf-8")
        prompt = task
        if arm == "with_skill":
            prompt += "\nRelevant repository skill and task guide follow. Apply applicable guidance within this constrained parameter-only task. User has delegated all remaining artistic choices.\n"
            for rel in guides[case]:
                prompt += "\n--- " + rel + " ---\n" + (repo / rel).read_text(encoding="utf-8")
        (out / "prompt.txt").write_text(prompt, encoding="utf-8")
        command = provider_command(cli, out, args.model, args.effort)
        record = {"case_id": case, "arm": arm, "trial": number, "common_task_sha256": digest(task.encode()), "actual_prompt_sha256": digest(prompt.encode()), "scene_fixture_sha256": digest((out / "fixture.json").read_bytes()), "schema_sha256": digest((out / "schema.json").read_bytes()), "command": command, "thread_id": None, "provider_usage": None, "model_identity": None, "status": "started", "guide_sources": guides[case] if arm == "with_skill" else [], "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        record['adapter_sha256'] = adapter_sha
        record.update(model_requested=args.model, effort_requested=args.effort)
        write_json(receipt, record)
        start = time.monotonic()
        try:
            reuse = generation_matches(previous, record) and (out / 'generation.json').is_file()
            if reuse:
                validate(case, json.loads((out / 'generation.json').read_text(encoding='utf-8')))
                completed = subprocess.CompletedProcess(command, 0)
                record['provider_generation_reused'] = True
                record['prior_attempt_path'] = str(archive.relative_to(root))
            else:
                with (out / "provider.jsonl").open("w", encoding="utf-8") as stdout, (out / "provider.stderr.txt").open("w", encoding="utf-8") as stderr:
                    completed = subprocess.run(command, input=prompt, text=True, encoding="utf-8", stdout=stdout, stderr=stderr, timeout=args.timeout)
            record["cli_exit_code"] = completed.returncode
            events = []
            for line in (out / "provider.jsonl").read_text(encoding="utf-8").splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                events.append(event)
                if event.get("type") == "thread.started":
                    record["thread_id"] = event.get("thread_id")
                if event.get("type") == "turn.completed":
                    record["provider_usage"] = event.get("usage")
                if event.get("model"):
                    record["model_identity"] = event["model"]
            record["provider_event_count"] = len(events)
            if reuse:
                origins = [json.loads(p.read_text(encoding='utf-8')) for p in (root / 'attempts').glob('*/receipt.json')]
                origin = next((r for r in origins if r.get('thread_id') == record['thread_id'] and not r.get('provider_generation_reused')), {})
                record['cli_seconds'] = origin.get('cli_seconds')
            else:
                record["cli_seconds"] = round(time.monotonic() - start, 3)
            if completed.returncode != 0:
                raise RuntimeError("provider exit " + str(completed.returncode))
            if not record["thread_id"] or not record["provider_usage"]:
                raise RuntimeError("missing actual thread/turn.completed usage receipt")
            generation = json.loads((out / "generation.json").read_text(encoding="utf-8"))
            validate(case, generation)
            write_json(out / "build_input.json", {"case": case, "generation": generation, "fixture": scene, "budget": CASES[case]["budget"]})
            blender_command = [args.blender, "--background", "--factory-startup", "--threads", "2", "--python-exit-code", "1", "--python", str(Path(__file__).resolve()), "--", "--build", str(out)]
            record["blender_command"] = blender_command
            with (out / "blender.log").open("w", encoding="utf-8") as log:
                built = subprocess.run(blender_command, stdout=log, stderr=subprocess.STDOUT, timeout=240)
            record["blender_exit_code"] = built.returncode
            if built.returncode != 0 or not (out / "geometry.json").is_file():
                raise RuntimeError("Blender build failed: " + str(built.returncode))
            record["geometry"] = json.loads((out / "geometry.json").read_text(encoding="utf-8"))
            record["artifact_hashes"] = {p.name: digest(p.read_bytes()) for p in out.iterdir() if p.suffix in (".blend", ".glb", ".png")}
            record["status"] = "completed"
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = type(exc).__name__ + ": " + str(exc)
        record["elapsed_seconds"] = round(time.monotonic() - start, 3)
        write_json(receipt, record)
        print(json.dumps({k: record.get(k) for k in ("case_id", "arm", "trial", "status", "elapsed_seconds", "error")}), flush=True)
        return record

    jobs = [(case, arm, n) for n in range(1, 4) for case in CASES for arm in ("baseline", "with_skill")]
    records = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(trial, *job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
            write_json(root / "running_summary.json", records)
    totals = {}
    for arm in ("baseline", "with_skill"):
        chosen = [r for r in records if r["arm"] == arm]
        usage = [r["provider_usage"] for r in chosen if isinstance(r.get("provider_usage"), dict)]
        totals[arm] = {"attempts": len(chosen), "completed": sum(r["status"] == "completed" for r in chosen), "failures": sum(r["status"] == "failed" for r in chosen), "usage_receipts": len(usage), "input_tokens": sum(u.get("input_tokens", 0) for u in usage), "cached_input_tokens": sum(u.get("cached_input_tokens", 0) for u in usage), "output_tokens": sum(u.get("output_tokens", 0) for u in usage), "geometry_issues": sum(bool(r.get("geometry", {}).get("issues")) for r in chosen)}
    summary = {"scope": manifest["scope"], "arms": totals, "records": sorted(records, key=lambda r: (r["case_id"], r["trial"], r["arm"])), "limitations": manifest["limitations"], "model_identity": "NOT VERIFIED" if any(not r.get("model_identity") for r in records) else sorted({r["model_identity"] for r in records}), "artistic_quality": "NOT VERIFIED", "mcp_agent_control": "NOT VERIFIED — trusted local Blender adapter used", "engine_import": "NOT VERIFIED by this campaign"}
    if all(totals[a]["usage_receipts"] == 15 for a in totals):
        b = totals["baseline"]["input_tokens"] + totals["baseline"]["output_tokens"]
        c = totals["with_skill"]["input_tokens"] + totals["with_skill"]["output_tokens"]
        summary["observed_token_delta"] = {"baseline": b, "with_skill": c, "delta": c-b, "percent": round(100*(c-b)/b, 3) if b else None, "caveat": "Observed provider receipts; model identity and full MCP equivalence remain unverified. No billing cost inference."}
    archived = [json.loads(p.read_text(encoding='utf-8')) for p in (root / 'attempts').glob('*/receipt.json')]
    unique_usage = {r['thread_id']: r['provider_usage'] for r in archived + records if r.get('thread_id') and r.get('provider_usage')}
    summary.update({'counts_scope': 'latest attempt per logical trial', 'archived_attempts': len(archived),
        'archived_failed_attempts': sum(r.get('status') == 'failed' for r in archived),
        'distinct_provider_usage_receipts': len(unique_usage),
        'distinct_provider_input_tokens': sum(u.get('input_tokens', 0) for u in unique_usage.values()),
        'distinct_provider_output_tokens': sum(u.get('output_tokens', 0) for u in unique_usage.values())})
    write_json(root / "summary.json", summary)
    print("CAMPAIGN_DONE " + str(root / "summary.json"), flush=True)


def build(out):
    import bpy
    import bmesh
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from blender_native_host import acquire_writer
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    out = Path(out).resolve()
    data = json.loads((out / "build_input.json").read_text(encoding="utf-8"))
    case = data["case"]
    p = validate(case, data["generation"])
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    def load_materials():
        loaded = {}
        for name, color, metallic, roughness in [("wood", (.16,.065,.025,1),0,.65), ("steel", (.5,.57,.62,1),.8,.3), ("green", (.035,.2,.065,1),0,.8), ("stone", (.45,.38,.26,1),0,.85)]:
            m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
            m.use_fake_user = True
            m.diffuse_color = color
            m.use_nodes = True
            bs = next(n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            bs.inputs["Base Color"].default_value = color
            bs.inputs["Metallic"].default_value = metallic
            bs.inputs["Roughness"].default_value = roughness
            loaded[name] = m
        return loaded
    materials = load_materials()
    owned = []

    def finish(obj, name, material, is_owned=True):
        obj.name = name
        obj.data.materials.append(materials[material])
        if is_owned:
            owned.append(obj)
        return obj

    def box(name, size, location, mat="wood", bevel=0, own=True):
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        o = bpy.context.object
        o.dimensions = size
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        finish(o, name, mat, own)
        if bevel:
            mod = o.modifiers.new("OwnedBevel", "BEVEL")
            mod.width, mod.segments = bevel, 1
            bpy.ops.object.modifier_apply(modifier=mod.name)
        return o

    def mesh(name, vertices, faces, mat="wood", own=True):
        me = bpy.data.meshes.new(name+"_Mesh")
        me.from_pydata(vertices, [], faces)
        me.update()
        o = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(o)
        finish(o, name, mat, own)
        return o

    f = data["fixture"]
    sent = box(f["sentinel"]["name"], f["sentinel"]["size"], f["sentinel"]["location"], own=False)
    protected = [sent]
    source = None
    if f["source"]:
        s = f["source"]
        source = mesh(s["name"], s["vertices"], s["faces"], "stone", False)
        protected.append(source)

    def snapshot(obj):
        return {"vertices": [list(v.co) for v in obj.data.vertices], "faces": [list(poly.vertices) for poly in obj.data.polygons], "matrix": [list(row) for row in obj.matrix_world], "materials": [m.name for m in obj.data.materials], "modifiers": [(m.name, m.type) for m in obj.modifiers], "hide_render": obj.hide_render, "hide_viewport": obj.hide_get()}
    shared = out.parent / "shared_fixtures"
    shared.mkdir(exist_ok=True)
    canonical = shared / (case + ".blend")
    lock = shared / (case + ".lock")
    deadline = time.monotonic() + 90
    while True:
        try:
            fixture_lease = acquire_writer(lock)
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise RuntimeError("shared fixture creation lock timed out")
            time.sleep(.1)
    try:
        if not canonical.exists():
            bpy.ops.wm.save_as_mainfile(filepath=str(canonical))
            write_json(canonical.with_suffix('.input.json'), {'fixture_sha256': digest(f), 'blend_sha256': digest(canonical.read_bytes())})
        check_shared_fixture(canonical, f)
    finally:
        fixture_lease.close()
    # Every trial reopens identical saved .blend bytes, including the first one.
    bpy.ops.wm.open_mainfile(filepath=str(canonical))
    materials = load_materials()
    protected = [bpy.data.objects[f["sentinel"]["name"]]]
    if f["source"]:
        source = bpy.data.objects[f["source"]["name"]]
        protected.append(source)
    initial_blend_sha256 = digest(canonical.read_bytes())
    shutil.copyfile(canonical, out / "scene_fixture.blend")
    before = {o.name: snapshot(o) for o in protected}
    write_json(out / "protected_before.json", before)
    measurements = {}
    if case == "chair":
        w,d,h,t,l = (p[k] for k in ("seat_width","seat_depth","seat_height","seat_thickness","leg_width"))
        box("Seat", (w,d,t), (0,0,h-t/2), bevel=p["bevel"])
        x,y = w/2-l/2-p["leg_inset"], d/2-l/2-p["leg_inset"]
        for i, xx in enumerate((-x,x)):
            for j, yy in enumerate((-y,y)):
                box("Leg_%d%d"%(i,j), (l,l,h-t), (xx,yy,(h-t)/2), bevel=p["bevel"])
            box("BackPost_"+str(i), (l,l,p["back_height"]-h), (xx,y,(h+p["back_height"])/2))
            box("SideSupport_"+str(i), (l,2*y-l,l), (xx,0,p["support_height"]))
        box("Backrest", (2*x-l,l,p["back_panel_height"]), (0,y,p["back_height"]-p["back_panel_height"]/2))
        measurements.update(leg_count=4, ground_z=0, seat_top=h, total_height=p["back_height"], seat_width=w, seat_depth=d, contact_formula="legs terminate at seat underside; back posts begin at seat top")
    elif case == "sword":
        ph,gh,gl = p["pommel_height"],p["guard_height"],p["grip_length"]
        box("Pommel", (p["grip_width"]*1.6,p["grip_width"]*1.3,ph), (0,0,ph/2), "steel", p["bevel"])
        box("Grip", (p["grip_width"],p["grip_width"],gl), (0,0,ph+gl/2), bevel=p["bevel"])
        box("Guard", (p["guard_width"],p["blade_thickness"]*2.5,gh), (0,0,ph+gl+gh/2), "steel", p["bevel"])
        z,le,wi,th = ph+gl+gh,p["blade_length"],p["blade_width"],p["blade_thickness"]
        profile = [(-wi/2,0), (wi/2,0), (wi*.42,le*(1-p["tip_fraction"])), (0,le), (-wi*.42,le*(1-p["tip_fraction"]))]
        verts = [(x,yy,zz+z) for yy in (-th/2,th/2) for x,zz in profile]
        n=len(profile)
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        mesh("Blade", verts, faces, "steel")
        measurements.update(total_height=z+le, blade_width=wi, blade_thickness=th, guard_center_x=0)
    elif case == "tree":
        bpy.ops.mesh.primitive_cylinder_add(vertices=p["segments"], radius=p["trunk_radius"], depth=p["trunk_height"], location=(0,0,p["trunk_height"]/2))
        finish(bpy.context.object, "Trunk", "wood")
        step=(p["height"]-p["canopy_start"])/(p["tiers"]+p["overlap"])
        for i in range(p["tiers"]):
            base=p["canopy_start"]+i*step
            depth=step*(1+p["overlap"])
            radius=p["canopy_radius"]*(1-p["taper"]*i/(p["tiers"]-1))
            bpy.ops.mesh.primitive_cone_add(vertices=p["segments"], radius1=radius, radius2=0, depth=depth, location=(0,0,base+depth/2))
            finish(bpy.context.object,"Foliage_"+str(i),"green")
        measurements.update(total_height=p["height"], canopy_diameter=2*p["canopy_radius"], tiers=p["tiers"], trunk_base=0)
    elif case == "modular_wall":
        w,h,d,pw,bh=(p[k] for k in ("module_width","height","thickness","post_width","beam_height"))
        for i in range(3):
            x=i*w
            for j,xx in enumerate((x+pw/2,x+w-pw/2)):
                box("Module%d_Post%d"%(i,j),(pw,d,h),(xx,0,h/2),bevel=p["bevel"])
            for j,zz in enumerate((bh/2,h-bh/2)):
                box("Module%d_Beam%d"%(i,j),(w-2*pw,d,bh),(x+w/2,0,zz),bevel=p["bevel"])
            box("Module%d_Panel"%i,(w-2*pw,p["panel_depth"],h-2*bh),(x+w/2,0,h/2),"stone")
        measurements.update(total_width=3*w,total_height=h,thickness=d,panel_depth=p["panel_depth"], module_joint_gap=0, joint_formula="modules contiguous on width grid; panel and beam dimensions fill post interiors")
    else:
        n,rings=p["segments"],p["rings"]
        sv=f["source"]["vertices"]
        verts=[]
        for j in range(rings):
            sj=j*24/(rings-1)
            j0=min(23,int(sj)); fj=sj-j0
            for i in range(n):
                si=i*32/n; i0=int(si); fi=si-i0
                low=Vector(sv[j0*32+i0]).lerp(Vector(sv[j0*32+(i0+1)%32]),fi)
                high=Vector(sv[(j0+1)*32+i0]).lerp(Vector(sv[(j0+1)*32+(i0+1)%32]),fi)
                verts.append(low.lerp(high,fj))
        target=mesh("Retopo_Tube",verts,[],"stone")
        bm=bmesh.new(); bm.from_mesh(target.data); bm.verts.ensure_lookup_table()
        ring_edges=[]
        for j in range(rings):
            ring_edges.append([bm.edges.new((bm.verts[j*n+i],bm.verts[j*n+(i+1)%n])) for i in range(n)])
        for j in range(rings-1):
            bmesh.ops.bridge_loops(bm,edges=ring_edges[j]+ring_edges[j+1],use_pairs=False,use_cyclic=False)
        interior=[v for v in bm.verts if not v.is_boundary]
        for unused in range(p["relax_iterations"]):
            bmesh.ops.smooth_vert(bm,verts=interior,factor=p["relax_factor"],use_axis_x=True,use_axis_y=True,use_axis_z=True)
        source_bm=bmesh.new(); source_bm.from_mesh(source.data)
        bvh=BVHTree.FromBMesh(source_bm)
        for v in bm.verts:
            nearest=bvh.find_nearest(v.co)
            if nearest[0] is not None:
                v.co=nearest[0]
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(target.data); bm.free()
        errors=[bvh.find_nearest(v.co)[3] for v in target.data.vertices]
        target.data.calc_loop_triangles()
        sampled_errors = []
        for triangle in target.data.loop_triangles:
            a,b,c = [target.data.vertices[i].co for i in triangle.vertices]
            for i in range(5):
                for j in range(5-i):
                    point = a*(1-(i+j)/4) + b*(i/4) + c*(j/4)
                    sampled_errors.append(bvh.find_nearest(point)[3])
        source_bm.free()
        measurements.update(source_vertices=len(source.data.vertices),source_faces=len(source.data.polygons),target_rings=rings,target_segments=n,max_vertex_projection_error=max(errors),max_sampled_surface_error=max(sampled_errors),surface_sample_count=len(sampled_errors),continuous_surface_error_bound='NOT VERIFIED',operations=["ordered_source_resample","bridge_loops","interior_relax","nearest_source_projection"])
    for o in owned:
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.uv.smart_project(island_margin=.03)
        bpy.ops.object.mode_set(mode="OBJECT")
    after={o.name:snapshot(o) for o in protected}
    write_json(out / "protected_after.json",after)
    geometry=[]
    for o in owned:
        o.data.calc_loop_triangles()
        bm=bmesh.new(); bm.from_mesh(o.data)
        geometry.append({"name":o.name,"vertices":len(o.data.vertices),"faces":len(o.data.polygons),"triangles":len(o.data.loop_triangles),"quads":sum(len(f.vertices)==4 for f in o.data.polygons),"boundary_edges":sum(e.is_boundary for e in bm.edges),"nonmanifold_nonboundary_edges":sum(not e.is_manifold and not e.is_boundary for e in bm.edges),"degenerate_faces":sum(f.calc_area()<1e-10 for f in bm.faces),"uv_layers":len(o.data.uv_layers),"materials":len(o.data.materials),"dimensions":list(o.dimensions)})
        bm.free()
    triangles=sum(g["triangles"] for g in geometry)
    issues=[]
    if before != after: issues.append("protected_object_changed")
    if triangles>data["budget"]: issues.append("triangle_budget_exceeded")
    if any(g["nonmanifold_nonboundary_edges"] or g["degenerate_faces"] for g in geometry): issues.append("nonmanifold_or_degenerate")
    if case != "retopology" and any(g["boundary_edges"] for g in geometry): issues.append("unexpected_open_boundary")
    if any(not g["uv_layers"] or not g["materials"] for g in geometry): issues.append("missing_uv_or_material")
    if case=="chair" and (abs(measurements["seat_top"]-.48)>.015 or abs(measurements["total_height"]-.95)>.025): issues.append("chair_proportions_outside_target_tolerance")
    if case=="sword" and abs(measurements["total_height"]-1.2)>.03: issues.append("sword_height_outside_target_tolerance")
    if case=="modular_wall" and (abs(measurements["total_width"]-6)>.03 or abs(measurements["total_height"]-2.5)>.02 or p["panel_depth"]>p["thickness"]): issues.append("wall_dimensions_outside_target_tolerance")
    if case=="tree" and abs(measurements["total_height"]-4)>.1: issues.append("tree_height_outside_target_tolerance")
    if case=="retopology" and (measurements["max_sampled_surface_error"]>.05 or geometry[0]["boundary_edges"]!=2*p["segments"] or geometry[0]["quads"]!=p["segments"]*(p["rings"]-1)): issues.append("retopology_topology_or_sampled_surface_failure")
    visibility = [(o, o.hide_render, o.hide_get()) for o in protected]
    for o in protected:
        o.hide_render=True
        o.hide_set(True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in owned:o.select_set(True)
    bpy.context.view_layer.objects.active=owned[0]
    bpy.ops.export_scene.gltf(filepath=str(out / "asset.glb"),export_format="GLB",use_selection=True,export_yup=True)
    scene=bpy.context.scene
    scene.render.engine="BLENDER_WORKBENCH"
    scene.display.shading.light="STUDIO"; scene.display.shading.color_type="MATERIAL"
    scene.display.shading.show_shadows=True; scene.display.shading.show_cavity=True
    scene.render.resolution_x=384; scene.render.resolution_y=384;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format="PNG";scene.render.film_transparent=True
    bounds=[o.matrix_world@Vector(corner) for o in owned for corner in o.bound_box]
    low=Vector([min(v[i] for v in bounds) for i in range(3)])
    high=Vector([max(v[i] for v in bounds) for i in range(3)])
    center=(low+high)/2; extent=max(high-low)
    bpy.ops.object.camera_add()
    cam=bpy.context.object;cam.name="CampaignCamera";scene.camera=cam
    cam.data.type="ORTHO";cam.data.ortho_scale=extent*1.55
    cameras={}
    for name,direction in [("front",(0,-1,0)),("side",(1,0,0)),("three_quarter",(1,-1,.7))]:
        cam.location=center+Vector(direction).normalized()*extent*3
        cam.rotation_euler=(center-cam.location).to_track_quat("-Z","Y").to_euler()
        scene.render.filepath=str(out/(name+".png"))
        bpy.ops.render.render(write_still=True)
        cameras[name]={"location":list(cam.location),"rotation":list(cam.rotation_euler),"ortho_scale":cam.data.ortho_scale}
    for obj, hide_render, hide_viewport in visibility:
        obj.hide_render = hide_render
        obj.hide_set(hide_viewport)
    after = {o.name: snapshot(o) for o in protected}
    assert before == after, 'Protected final scene properties changed'
    write_json(out / 'protected_after.json', after)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"asset.blend"))
    report={"blender_version":bpy.app.version_string,"initial_blend_sha256":initial_blend_sha256,"source_preserved":before==after,"protected_before_sha256":digest(before),"protected_after_sha256":digest(after),"triangles":triangles,"budget":data["budget"],"objects":geometry,"measurements":measurements,"issues":issues,"technical_status":"ISSUE" if issues else "PASS","visual_status":"NOT VERIFIED","cameras":cameras,"limits":"Fixed adapter creates mandatory parts/materials/UVs; no autonomous agent correction loop or arbitrary freeform topology; touching formulas do not prove visible joint quality."}
    write_json(out/"geometry.json",report)
    print("BUILD_DONE "+case,flush=True)


if __name__ == "__main__":
    if "--build" in sys.argv:
        build(sys.argv[sys.argv.index("--build")+1])
    else:
        parser=argparse.ArgumentParser(description=__doc__)
        parser.add_argument("--output",required=True)
        parser.add_argument("--blender",default="C:/Program Files/Blender Foundation/Blender 3.1/blender.exe")
        parser.add_argument("--workers",type=int,default=2)
        parser.add_argument("--timeout",type=int,default=600)
        parser.add_argument("--model", help="Explicit public model ID for both arms; provider backend identity is recorded separately")
        parser.add_argument("--effort", choices=['low', 'medium', 'high', 'xhigh', 'max', 'ultra'])
        parser.add_argument("--self-check",action="store_true")
        args=parser.parse_args()
        self_check() if args.self_check else run_campaign(args)
