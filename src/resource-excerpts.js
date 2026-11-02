/** Bounded pure helpers for reference browsing without loading full documents. */

export function excerptLines(source, {startLine = 1, maxLines = 40, maxChars = 6000} = {}) {
  if (typeof source !== "string") throw new TypeError("resource source must be text");
  const lines = source.split(/\r?\n/);
  const totalLines = lines.length;
  if (!Number.isInteger(startLine) || startLine < 1 || startLine > totalLines)
    throw new RangeError("start line outside document");
  if (!Number.isInteger(maxLines) || maxLines < 1 || maxLines > 80)
    throw new RangeError("line window must be between 1 and 80");
  if (!Number.isInteger(maxChars) || maxChars < 100 || maxChars > 6000)
    throw new RangeError("character window must be between 100 and 6000");
  const endLine = Math.min(totalLines, startLine + maxLines - 1);
  const original = lines.slice(startLine - 1, endLine).join("\n");
  return {
    startLine, endLine, totalLines,
    text: original.slice(0, maxChars),
    truncatedChars: original.length > maxChars,
    nextLine: endLine < totalLines ? endLine + 1 : null
  };
}

export function markdownOutline(source, {maxHeadings = 80} = {}) {
  if (typeof source !== "string") throw new TypeError("resource source must be text");
  if (!Number.isInteger(maxHeadings) || maxHeadings < 1 || maxHeadings > 100)
    throw new RangeError("outline headings must be between 1 and 100");
  const lines = source.split(/\r?\n/);
  const headings = [];
  let fenced = false;
  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trimStart();
    if (trimmed.startsWith(String.fromCharCode(96, 96, 96)) || trimmed.startsWith("~~~")) {
      fenced = !fenced;
      continue;
    }
    if (fenced) continue;
    const match = /^(#{1,6})\s+(.+?)\s*#*\s*$/.exec(lines[i]);
    if (match) headings.push({line: i + 1, level: match[1].length, title: match[2]});
  }
  return {totalLines: lines.length,
    headings: headings.slice(0, maxHeadings),
    truncatedHeadings: headings.length > maxHeadings};
}
