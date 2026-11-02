import { readFileSync, readdirSync } from "node:fs";
import { resolve, dirname, basename } from "node:path";
import { fileURLToPath } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { excerptLines, markdownOutline } from "./resource-excerpts.js";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const PACKAGE_VERSION = JSON.parse(readFileSync(resolve(ROOT, "package.json"), "utf8")).version;
const SKILL_PATH = resolve(ROOT, "SKILL.md");
const REFERENCE_DIR = resolve(ROOT, "references");
const SCRIPT_DIR = resolve(ROOT, "scripts");
const references = readdirSync(REFERENCE_DIR).filter((name) => name.endsWith(".md")).sort();
const scripts = readdirSync(SCRIPT_DIR).filter((name) => name.endsWith(".py")).sort();

function readAllowedFile(directory, allowlist, requestedName) {
  const name = basename(requestedName ?? "");
  if (name !== requestedName || !allowlist.includes(name)) {
    throw new Error(`Unknown file '${requestedName}'. Use the list tool to see valid names.`);
  }
  return readFileSync(resolve(directory, name), "utf8");
}

const server = new McpServer({
  name: "blender-mcp-master",
  version: PACKAGE_VERSION
});

server.tool(
  "get_blender_skill",
  "Return the Blender MCP Master agent skill instructions (SKILL.md).",
  {},
  async () => ({
    content: [{ type: "text", text: readFileSync(SKILL_PATH, "utf8") }]
  })
);

server.tool(
  "list_blender_resources",
  "List the skill reference guides and reusable Blender Python scripts bundled with this package.",
  {},
  async () => ({
    content: [{
      type: "text",
      text: JSON.stringify({
        references,
        scripts,
        note: "Scripts use Blender's bpy API and must be run in Blender or through a Blender-control MCP server."
      }, null, 2)
    }]
  })
);

server.tool(
  "get_blender_reference",
  "Read one bundled modeling reference guide by exact filename.",
  { name: z.string().describe("Exact .md filename from list_blender_resources.references") },
  async ({ name }) => ({
    content: [{ type: "text", text: readAllowedFile(REFERENCE_DIR, references, name) }]
  })
);

server.tool(
  "get_blender_reference_outline",
  "List only section headings and their line numbers from one guide. Low-context alternative to reading the full document.",
  { name: z.string().describe("Exact .md guide filename") },
  async ({ name }) => {
    const outline = markdownOutline(readAllowedFile(REFERENCE_DIR, references, name));
    const lines = outline.headings.map(h => h.line + ": " + "#".repeat(h.level) + " " + h.title);
    return { content: [{ type: "text", text:
      "SOURCE references/" + name + " (" + outline.totalLines + " lines)\n" +
      lines.join("\n") + (outline.truncatedHeadings ? "\nMORE HEADINGS OMITTED" : "")
    }] };
  }
);

server.tool(
  "get_blender_reference_excerpt",
  "Read only a bounded line window from a reference. Returns continuation line; use before requesting full text.",
  {
    name: z.string().describe("Exact .md guide filename"),
    startLine: z.number().int().min(1).describe("One-based first line"),
    maxLines: z.number().int().min(1).max(80).optional().describe("Maximum returned lines; default 40")
  },
  async ({ name, startLine, maxLines }) => {
    const result = excerptLines(readAllowedFile(REFERENCE_DIR, references, name),
                                {startLine, maxLines: maxLines ?? 40});
    const heading = "SOURCE references/" + name + " lines " + result.startLine + "-" +
                    result.endLine + "/" + result.totalLines;
    const footer = "\nNEXT_LINE=" + (result.nextLine ?? "NONE") +
                   "\nTRUNCATED_CHARS=" + result.truncatedChars;
    return { content: [{ type: "text", text: heading + "\n" + result.text + footer }] };
  }
);

server.tool(
  "get_blender_script",
  "Return one reusable Blender Python script by exact filename. Review its configuration and safety notes before execution.",
  { name: z.string().describe("Exact .py filename from list_blender_resources.scripts") },
  async ({ name }) => ({
    content: [{ type: "text", text: readAllowedFile(SCRIPT_DIR, scripts, name) }]
  })
);

server.tool(
  "get_blender_mcp_setup",
  "Explain how this skill/resource server relates to a separate MCP server that controls a live Blender session.",
  {},
  async () => ({
    content: [{
      type: "text",
      text: [
        "blender-mcp-master provides the skill, reference guides, and bpy script templates over MCP.",
        "It does not itself connect to or control a live Blender process.",
        "To operate on a live scene, configure a separate Blender-control MCP server in the same AI client.",
        "Discover that server's actual tool names at runtime; do not assume all implementations expose the same tools.",
        "Review scripts before execution, and use a disposable or backed-up scene for destructive operations."
      ].join("\n")
    }]
  })
);

const transport = new StdioServerTransport();
await server.connect(transport);
