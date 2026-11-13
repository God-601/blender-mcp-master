import test from "node:test";
import assert from "node:assert/strict";
import { excerptLines, markdownOutline } from "../src/resource-excerpts.js";

const source = "# Main\nIntroduction\n## Basics\nOne\nTwo\nThree\n### Deeper\nSeven\nEight\n";

test("outline enumerates headings with exact one-based line numbers", () => {
  const result = markdownOutline(source);
  assert.deepEqual(result.headings.map(x => [x.line, x.title]),
                   [[1, "Main"], [3, "Basics"], [7, "Deeper"]]);
  assert.equal(result.totalLines, 10);
});

test("excerpt returns bounded lines with continuation and compact content", () => {
  const chunk = excerptLines(source, { startLine: 3, maxLines: 2, maxChars: 6000 });
  assert.equal(chunk.text, "## Basics\nOne");
  assert.equal(chunk.startLine, 3);
  assert.equal(chunk.endLine, 4);
  assert.equal(chunk.nextLine, 5);
  assert.ok(chunk.text.length < source.length);
});

test("requesting the final line gives no continuation", () => {
  const chunk = excerptLines(source, { startLine: 10, maxLines: 5, maxChars: 6000 });
  assert.equal(chunk.nextLine, null);
});

test("invalid line windows and sizes are rejected", () => {
  for (const args of [
    { startLine: 0, maxLines: 2 }, { startLine: 11, maxLines: 2 },
    { startLine: 1, maxLines: 100000 }, { startLine: 1, maxLines: 0 },
    { startLine: 1.5, maxLines: 2 }
  ]) assert.throws(() => excerptLines(source, args), /line|window|range/i);
});

test("even one excessively long line is capped and explicitly marked", () => {
  const chunk = excerptLines("x".repeat(20000), {startLine: 1, maxLines: 1, maxChars: 1200});
  assert.equal(chunk.text.length, 1200);
  assert.equal(chunk.truncatedChars, true);
  assert.equal(chunk.nextLine, null);
});

test("a character-limited excerpt resumes at the first omitted line", () => {
  const text = ["a".repeat(80), "b".repeat(50), "next guidance"].join("\n");
  const first = excerptLines(text, {maxLines: 3, maxChars: 100});
  assert.deepEqual([first.endLine, first.nextLine, first.truncatedChars], [1, 2, true]);
  assert.equal(first.text, "a".repeat(80));
  const rest = excerptLines(text, {startLine: first.nextLine, maxLines: 3, maxChars: 100});
  assert.equal(rest.text, "b".repeat(50) + "\nnext guidance");
});

test("outline caps headings without claiming full coverage", () => {
  const large = Array.from({ length: 90 }, (_, i) => "## Heading" + i).join("\n");
  const result = markdownOutline(large, { maxHeadings: 10 });
  assert.equal(result.headings.length, 10);
  assert.equal(result.truncatedHeadings, true);
});
