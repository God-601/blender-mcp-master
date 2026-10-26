#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const command = process.argv[2];

function usage() {
  process.stdout.write(`blender-mcp-master — Blender skill and MCP resource server

Usage:
  npx -y blender-mcp-master       Start the MCP server over stdio
  npx -y blender-mcp-master skill Print SKILL.md to stdout
  npx -y blender-mcp-master list  List bundled references and scripts
  npx -y blender-mcp-master help  Show this help

The MCP server exposes the skill, reference guides, and reusable bpy scripts.
It does not connect to or control a running Blender instance by itself; use it
alongside a Blender-control MCP server when you need live scene operations.
`);
}

if (command === "skill") {
  process.stdout.write(readFileSync(resolve(root, "SKILL.md"), "utf8"));
} else if (command === "list") {
  const { readdirSync } = await import("node:fs");
  process.stdout.write("References:\n");
  for (const name of readdirSync(resolve(root, "references")).filter((x) => x.endsWith(".md")).sort()) {
    process.stdout.write(`  ${name}\n`);
  }
  process.stdout.write("Scripts:\n");
  for (const name of readdirSync(resolve(root, "scripts")).filter((x) => x.endsWith(".py")).sort()) {
    process.stdout.write(`  ${name}\n`);
  }
} else if (command === "help" || command === "--help" || command === "-h") {
  usage();
} else if (command === "--version" || command === "-v") {
  const pkg = JSON.parse(readFileSync(resolve(root, "package.json"), "utf8"));
  process.stdout.write(pkg.version + "\n");
} else if (command === undefined) {
  await import("../src/server.js");
} else {
  process.stderr.write(`Unknown command: ${command}\n\n`);
  usage();
  process.exitCode = 2;
}
