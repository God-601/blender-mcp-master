extends SceneTree
## Headless *real Godot* GLB importer probe. Needs Godot 4.4+ installed.
## Run from repository with:
## godot --headless --path integrations/godot --script res://gltf_import_probe.gd -- /absolute/asset.glb
## No filesystem writes or gameplay/physics claims.

func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() != 1:
        _fail("Provide exactly one absolute GLB filepath")
        return
    var source: String = args[0]
    if not source.to_lower().ends_with(".glb") or not source.is_absolute_path():
        _fail("Input must be an absolute .glb file path")
        return
    if not FileAccess.file_exists(source):
        _fail("GLB file not found")
        return

    var document := GLTFDocument.new()
    var state := GLTFState.new()
    var err := document.append_from_file(source, state)
    if err != OK:
        _fail("GLTFDocument.append_from_file failed: " + str(err))
        return
    var scene := document.generate_scene(state)
    if scene == null:
        _fail("GLTFDocument.generate_scene returned null")
        return

    var meshes := 0
    var surfaces := 0
    var triangles := 0
    var uv_surfaces := 0
    var material_surfaces := 0
    var pending: Array[Node] = [scene]
    while not pending.is_empty():
        var node: Node = pending.pop_back()
        var instance := node as MeshInstance3D
        if instance != null and instance.mesh != null:
            meshes += 1
            for i in range(instance.mesh.get_surface_count()):
                surfaces += 1
                var arrays := instance.mesh.surface_get_arrays(i)
                var uvs: Variant = arrays[Mesh.ARRAY_TEX_UV]
                if uvs is PackedVector2Array and not uvs.is_empty():
                    uv_surfaces += 1
                if instance.get_active_material(i) != null:
                    material_surfaces += 1
                if instance.mesh.surface_get_primitive_type(i) == Mesh.PRIMITIVE_TRIANGLES:
                    var indices: Variant = arrays[Mesh.ARRAY_INDEX]
                    if indices is PackedInt32Array and not indices.is_empty():
                        triangles += int(indices.size() / 3)
                    else:
                        triangles += int(arrays[Mesh.ARRAY_VERTEX].size() / 3)
        for child in node.get_children():
            pending.append(child)

    print("BLENDER_MCP_GODOT_IMPORT_BEGIN")
    print(JSON.stringify({
        "status": "IMPORTED_GEOMETRY" if meshes > 0 else "NOT VERIFIED",
        "godot_version": Engine.get_version_info().get("string", "unknown"),
        "source": source,
        "mesh_instances": meshes,
        "mesh_surfaces": surfaces,
        "triangle_primitives": triangles,
        "uv_surfaces": uv_surfaces,
        "material_surfaces": material_surfaces,
        "scene_provenance": "GLTFDocument.append_from_file + generate_scene in this Godot process",
        "rendered_fidelity": "NOT VERIFIED",
        "collision": "NOT VERIFIED",
        "visual_quality": "NOT VERIFIED",
        "limitations": "Does not prove texture shading, animations, rendering, physics or game FPS."
    }))
    print("BLENDER_MCP_GODOT_IMPORT_END")
    scene.free()
    quit(0 if meshes > 0 else 1)


func _fail(message: String) -> void:
    print("BLENDER_MCP_GODOT_IMPORT_BEGIN")
    print(JSON.stringify({"status": "NOT VERIFIED", "error": message}))
    print("BLENDER_MCP_GODOT_IMPORT_END")
    quit(1)
