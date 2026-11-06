-- Roblox Studio Command Bar: read-only MeshPart import inspection.
-- Select the imported Model/MeshPart in Explorer, then run. Does not mutate.
local Selection = game:GetService("Selection")
local HttpService = game:GetService("HttpService")
local selected = Selection:Get()
local results = {
    status = "NOT VERIFIED",
    importer = "Roblox Studio current DataModel (selection only)",
    studio_version = tostring(version()),
    selected_count = #selected,
    selected_meshes = {},
    actual_import_source_sha256 = "NOT VERIFIED",
    pixel_material_fidelity = "NOT VERIFIED",
    collisions_verified = "NOT VERIFIED",
    performance_verified = "NOT VERIFIED",
    source_blender_scene_preserved = "NOT VERIFIED",
    warnings = {},
}
if #selected == 0 then
    table.insert(results.warnings, "Select the imported Model or MeshPart in Explorer before running")
else
    local seen = {}
    for _, root in ipairs(selected) do
        local targets = {root}
        for _, child in ipairs(root:GetDescendants()) do
            table.insert(targets, child)
        end
        for _, obj in ipairs(targets) do
            if obj:IsA("MeshPart") and not seen[obj] then
                seen[obj] = true
                local size = obj.Size
                local validSize = size.X > 0 and size.Y > 0 and size.Z > 0
                local mesh = {
                    name = obj:GetFullName(),
                    size_studs = {size.X, size.Y, size.Z},
                    mesh_id_present = obj.MeshId ~= "",
                    texture_id_present = obj.TextureID ~= "",
                    material = tostring(obj.Material),
                    collision_fidelity = tostring(obj.CollisionFidelity),
                    can_collide_configured = obj.CanCollide,
                    anchored = obj.Anchored,
                    valid_nonzero_size = validSize,
                    visual_quality = "NOT VERIFIED",
                    live_collision_test = "NOT VERIFIED",
                }
                table.insert(results.selected_meshes, mesh)
                if not validSize or not mesh.mesh_id_present then
                    table.insert(results.warnings, "Missing geometry metadata or nonpositive size: " .. obj.Name)
                end
            end
        end
    end
end
if #results.selected_meshes > 0 then
    results.status = "MESHES_PRESENT_IN_STUDIO"
else
    table.insert(results.warnings, "No MeshPart was found in selected instances")
end
print("BLENDER_MCP_STUDIO_MESH_AUDIT_BEGIN")
print(HttpService:JSONEncode(results))
print("BLENDER_MCP_STUDIO_MESH_AUDIT_END")
