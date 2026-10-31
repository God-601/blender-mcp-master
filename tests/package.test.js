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
    assert.ok(resources.content[0].text.includes("validate_asset.py"));
  } finally {
    await client.close();
  }
});

async function withClient(run) {
  const transport = new StdioClientTransport({
    command: process.execPath,
    args: [resolve(root, "src/server.js")]
  });
  const client = new Client({ name: "blender-mcp-master-test", version: "0.0.0" });
  try {
    await client.connect(transport);
    return await run(client);
  } finally {
    await client.close();
  }
}

test("MCP server reports the package.json version", async () => {
  await withClient(async (client) => {
    assert.equal(client.getServerVersion().version, pkg.version);
  });
});

test("every listed reference and script can be read through the MCP tools", async () => {
  await withClient(async (client) => {
    const listed = await client.callTool({ name: "list_blender_resources", arguments: {} });
    const { references, scripts } = JSON.parse(listed.content[0].text);
    assert.ok(references.length > 0 && scripts.length > 0);
    for (const name of references) {
      const result = await client.callTool({ name: "get_blender_reference", arguments: { name } });
      assert.ok(!result.isError, `${name}: ${JSON.stringify(result.content)}`);
      assert.ok(result.content[0].text.length > 50, name);
    }
    for (const name of scripts) {
      const result = await client.callTool({ name: "get_blender_script", arguments: { name } });
      assert.ok(!result.isError, `${name}: ${JSON.stringify(result.content)}`);
      assert.match(result.content[0].text, /import bpy/);
    }
  });
});

test("file tools reject unknown names, path traversal and files from the other directory", async () => {
  const skillText = readFileSync(resolve(root, "SKILL.md"), "utf8");
  await withClient(async (client) => {
    const attempts = [
      ["get_blender_reference", "../SKILL.md"],
      ["get_blender_reference", "..\\SKILL.md"],
      ["get_blender_reference", "/etc/passwd"],
      ["get_blender_reference", "validate_asset.py"],
      ["get_blender_reference", "does-not-exist.md"],
      ["get_blender_reference", ""],
      ["get_blender_script", "../package.json"],
      ["get_blender_script", "budgets.md"],
      ["get_blender_script", "scripts/validate_asset.py"]
    ];
    for (const [tool, name] of attempts) {
      const result = await client.callTool({ name: tool, arguments: { name } });
      assert.equal(result.isError, true, `${tool}(${JSON.stringify(name)}) should be rejected`);
      const text = result.content.map((part) => part.text ?? "").join("\n");
      assert.ok(!text.includes(skillText.slice(0, 80)), "error must not leak file contents");
    }
  });
});

test("npm pack contains the skill content and excludes tests and dependencies", () => {
  const result = spawnSync("npm", ["pack", "--dry-run", "--json", "--ignore-scripts"], {
    cwd: root,
    encoding: "utf8",
    timeout: 60000
  });
  assert.equal(result.status, 0, result.stderr);
  const files = JSON.parse(result.stdout)[0].files.map((file) => file.path);
  for (const required of ["SKILL.md", "README.md", "LICENSE", "package.json", "bin/blender-mcp-master.js", "src/server.js", "scripts/validate_asset.py", "references/modeling-quality-loop.md"]) {
    assert.ok(files.includes(required), `missing from package: ${required}`);
  }
  assert.ok(!files.some((path) => path.startsWith("tests/") || path.startsWith("node_modules/") || path.startsWith(".github/")), "package must not ship tests, deps or CI files");
});
