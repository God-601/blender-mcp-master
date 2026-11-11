extends SceneTree
## Opt-in actual imported animation check; no rendered skin-fidelity claim.

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() != 1 or not args[0].is_absolute_path() or not args[0].ends_with(".glb"):
        _finish({"status": "ISSUE", "error": "One absolute animated GLB path required"}, 1)
        return
    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var error := document.append_from_file(args[0], state)
    if error != OK:
        _finish({"status": "ISSUE", "error": "GLB import failed: " + str(error)}, 1)
        return
    var scene := document.generate_scene(state)
    if scene == null:
        _finish({"status": "ISSUE", "error": "No imported scene"}, 1)
        return
    root.add_child(scene)
    var skeletons: Array[Skeleton3D] = []
    var players: Array[AnimationPlayer] = []
    var pending: Array[Node] = [scene]
    while not pending.is_empty():
        var node: Node = pending.pop_back()
        if node is Skeleton3D:
            skeletons.append(node)
        if node is AnimationPlayer:
            players.append(node)
        for child in node.get_children():
            pending.append(child)
    var clips: Array[Dictionary] = []
    var changed := false
    for player in players:
        for name in player.get_animation_list():
            if name == "RESET":
                continue
            var animation := player.get_animation(name)
            if animation.length <= 0.0:
                continue
            player.play(name)
            player.seek(0.0, true)
            player.advance(0.0)
            var before := _poses(skeletons)
            var clip_changed := false
            for fraction in [0.25, 0.5, 0.75, 0.99]:
                player.seek(animation.length * fraction, true)
                player.advance(0.0)
                var after := _poses(skeletons)
                for i in range(before.size()):
                    if not before[i].is_equal_approx(after[i]):
                        clip_changed = true
            clips.append({"name": name, "seconds": animation.length,
                "tracks": animation.get_track_count(), "sampled_bone_motion": clip_changed})
            changed = changed or clip_changed
            player.stop()
    var bones := 0
    for skeleton in skeletons:
        bones += skeleton.get_bone_count()
    var passed := bones >= 2 and changed and not clips.is_empty()
    _finish({"status": "PASS" if passed else "ISSUE", "source": args[0],
        "godot_version": Engine.get_version_info().get("string", "unknown"),
        "skeletons": skeletons.size(), "bones": bones, "clips": clips,
        "limits": "Actual imported AnimationPlayer sampled in Godot. Bone motion does not prove rendered skin quality, collision, or arbitrary rigs."}, 0 if passed else 1)

func _poses(skeletons: Array[Skeleton3D]) -> Array[Transform3D]:
    var poses: Array[Transform3D] = []
    for skeleton in skeletons:
        for i in range(skeleton.get_bone_count()):
            poses.append(skeleton.get_bone_global_pose(i))
    return poses

func _finish(report: Dictionary, code: int) -> void:
    print("BLENDER_MCP_GODOT_ANIMATION_BEGIN")
    print(JSON.stringify(report))
    print("BLENDER_MCP_GODOT_ANIMATION_END")
    quit(code)
