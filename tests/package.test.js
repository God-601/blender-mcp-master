import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const pkg = JSON.parse(readFileSync(resolve(root, "package.json"), "utf8"));

test("package manifest has the expected public name and npx binary", () => {
  assert.equal(pkg.name, "blender-mcp-master");
  assert.equal(pkg.bin["blender-mcp-master"], "./bin/blender-mcp-master.js");
  assert.ok(pkg.files.includes("SKILL.md"));
  assert.ok(pkg.files.includes("references/"));
  assert.ok(pkg.files.includes("scripts/"));
});

test("skill and resource directories are present and non-empty", () => {
  assert.ok(readFileSync(resolve(root, "SKILL.md"), "utf8").length > 100);
  assert.ok(readdirSync(resolve(root, "references")).some((name) => name.endsWith(".md")));
  assert.ok(readdirSync(resolve(root, "scripts")).some((name) => name.endsWith(".py")));
});

test("CLI prints skill without starting the MCP transport", () => {
  const result = spawnSync(process.execPath, [resolve(root, "bin/blender-mcp-master.js"), "skill"], {
    encoding: "utf8",
    timeout: 5000
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /# Blender MCP Master/);
});

test("CLI list command reports bundled references and scripts", () => {
  const result = spawnSync(process.execPath, [resolve(root, "bin/blender-mcp-master.js"), "list"], {
    encoding: "utf8",
    timeout: 5000
  });
  assert.equal(result.status, 0, result.stderr);
  assert.match(result.stdout, /References:/);
  assert.match(result.stdout, /Scripts:/);
  assert.match(result.stdout, /validate_asset\.py/);
});


test("MCP server starts over stdio and exposes the expected tools", async () => {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [resolve(root, "src/server.js")]
  });
  const client = new Client({ name: "blender-mcp-master-test", version: "0.0.0" });
  try {
    await client.connect(transport);
    const result = await client.listTools();
    const names = result.tools.map((tool) => tool.name);
    assert.deepEqual(names.sort(), [
      "get_blender_mcp_setup",
      "get_blender_reference",
      "get_blender_script",
      "get_blender_skill",
      "list_blender_resources"
    ].sort());
    const skill = await client.callTool({ name: "get_blender_skill", arguments: {} });
    assert.match(skill.content[0].text, /# Blender MCP Master/);
    const resources = await client.callTool({ name: "list_blender_resources", arguments: {} });
    assert.match(resources.content[0].text, /validate_asset\\.py/);
  } finally {
    await client.close();
  }
});
