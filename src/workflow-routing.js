/** Pure advisory task router for the read-only MCP resource server. */
export const PRIMARY = Object.freeze({
  hard_surface: "hard-surface.md",
  organic: "organic.md",
  stylized: "stylized-lowpoly.md",
  architecture: "modular-modeling.md",
  character: "character-rig.md",
  materials: "materials.md",
  game_asset: "game-ready-export.md",
  retopology: "advanced-retopology.md"
});
export const OPTIONAL = Object.freeze({
  rigging: "topology-retopology.md",
  uv: "uv-baking.md",
  pbr: "materials.md",
  fit: "component-fit-and-joints.md",
  visual: "visual-inspection.md",
  optimization: "model-performance-strategy.md",
  export: "game-ready-export.md",
  measure: "measured-proportion-recipes.md"
});
export const TOPICS = Object.freeze(["reference", "silhouette", "materials", "purpose", "technical"]);
export const DESTINATIONS = Object.freeze(["render", "roblox", "unity", "godot", "unreal", "animation", "3d_print", "other"]);

export function planWorkflow({ category, destination = "other", needs = [], known = [], delegated = [], continuation = false }) {
  if (typeof category !== "string" || !Object.hasOwn(PRIMARY, category)) throw new TypeError("Unknown modeling category");
  if (!DESTINATIONS.includes(destination)) throw new TypeError("Unsupported destination");
  if (![needs, known, delegated].every(Array.isArray)) throw new TypeError("List arguments required");
  if (needs.some(k => typeof k !== "string" || !Object.hasOwn(OPTIONAL, k)) || new Set(needs).size !== needs.length)
    throw new TypeError("Invalid or repeated need");
  if ([...known, ...delegated].some(k => !TOPICS.includes(k))) throw new TypeError("Unknown brief topic");
  if (typeof continuation !== "boolean") throw new TypeError("continuation must be a boolean");
  const primary = PRIMARY[category];
  const secondary = [...new Set(needs.map(k => OPTIONAL[k]))].filter(name => name !== primary);
  const knownSet = new Set([...known, ...delegated]);
  return {
    category,
    destination,
    primary: `references/${primary}`,
    optional: secondary.map(name => `references/${name}`),
    questions_to_consider: continuation ? [] : TOPICS.filter(topic => !knownSet.has(topic)),
    questions_already_known_or_delegated: [...knownSet].sort(),
    read_only: true,
    note: "Advisory plan only. It does not read images, edit Blender or prove a model was constructed."
  };
}
