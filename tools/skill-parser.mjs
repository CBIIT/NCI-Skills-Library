// Shared parsing helpers for the skill Markdown files in this repository.
// Zero dependencies: this repo intentionally has no package.json.

import { readdir, readFile } from "node:fs/promises";
import path from "node:path";

export const REPOSITORY = "CBIIT/NCI-Skills-Library";
export const SCAN_DIRS = ["framework", "intake"];
export const EXCLUDED_FILENAMES = new Set([
  "README.md",
  "skills__template.md",
  "TESTCASES.md",
]);

// Frontmatter keys and body sections mandated by intake/skills__template.md.
export const TEMPLATE_KEYS = [
  "name",
  "description",
  "author",
  "subject_matter_expert",
  "Language",
  "Framework",
];

export const TEMPLATE_SECTIONS = [
  "Purpose",
  "When to Use",
  "Inputs",
  "Output",
  "Workflow",
  "Quality Checklist",
  "Guardrails",
];

// Literal placeholder tokens copied from intake/skills__template.md. Matching
// on these rather than on any <angle-bracket> text avoids flagging legitimate
// values such as "implementation-report-<slug>.md".
export const TEMPLATE_PLACEHOLDERS = [
  "<skill-name-kebab-case>",
  "<author-name/DOC>",
  "<sme-name/DOC>",
  "<specific context>",
  "<target users>",
  "<outcome>",
  "<output type>",
];

function stripQuotes(value) {
  const trimmed = value.trim();
  if (trimmed.length >= 2) {
    const first = trimmed[0];
    const last = trimmed[trimmed.length - 1];
    if ((first === '"' && last === '"') || (first === "'" && last === "'")) {
      return trimmed.slice(1, -1);
    }
  }
  return trimmed;
}

/**
 * Minimal YAML frontmatter reader covering the shapes actually used in this
 * repo: scalars, quoted scalars, `>` / `|` blocks, `- ` lists, and `[a, b]`.
 */
export function parseFrontmatter(text) {
  if (!text.startsWith("---")) return null;
  const closing = text.indexOf("\n---", 3);
  if (closing === -1) return null;

  const firstNewline = text.indexOf("\n");
  const lines = text.slice(firstNewline + 1, closing).split("\n");
  const data = {};
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];
    if (!line.trim() || line.trimStart().startsWith("#")) {
      index += 1;
      continue;
    }

    const match = /^([A-Za-z0-9_-]+):[ \t]*(.*)$/.exec(line);
    if (!match) {
      index += 1;
      continue;
    }

    const key = match[1];
    const value = match[2].trim();

    if (["|", ">", "|-", ">-", "|+", ">+"].includes(value)) {
      const parts = [];
      index += 1;
      while (index < lines.length && (/^\s{2,}\S/.test(lines[index]) || !lines[index].trim())) {
        parts.push(lines[index].trim());
        index += 1;
      }
      data[key] = parts.join(" ").replace(/\s+/g, " ").trim();
      continue;
    }

    if (value === "") {
      const items = [];
      index += 1;
      while (index < lines.length && /^\s*-\s+/.test(lines[index])) {
        items.push(stripQuotes(lines[index].replace(/^\s*-\s+/, "")));
        index += 1;
      }
      data[key] = items.length > 0 ? items : "";
      continue;
    }

    if (value.startsWith("[") && value.endsWith("]")) {
      data[key] = value
        .slice(1, -1)
        .split(",")
        .map((entry) => stripQuotes(entry))
        .filter(Boolean);
      index += 1;
      continue;
    }

    data[key] = stripQuotes(value);
    index += 1;
  }

  return data;
}

export function stripFrontmatter(text) {
  if (!text.startsWith("---")) return text;
  const closing = text.indexOf("\n---", 3);
  if (closing === -1) return text;
  const afterMarker = text.indexOf("\n", closing + 1);
  return afterMarker === -1 ? "" : text.slice(afterMarker + 1);
}

/** Maps `## Heading` to its body text, ignoring headings inside fenced code. */
export function extractSections(body) {
  const sections = new Map();
  const order = [];
  let currentHeading = null;
  let buffer = [];
  let inFence = false;

  for (const line of body.split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) inFence = !inFence;

    const heading = inFence ? null : /^##\s+(.+?)\s*$/.exec(line);
    if (heading) {
      if (currentHeading) sections.set(currentHeading, buffer.join("\n").trim());
      currentHeading = heading[1];
      order.push(currentHeading);
      buffer = [];
      continue;
    }
    if (currentHeading) buffer.push(line);
  }

  if (currentHeading) sections.set(currentHeading, buffer.join("\n").trim());
  return { sections, order };
}

/** Splits a "When to Use" section into positive triggers and near-misses. */
export function extractTriggers(whenToUse) {
  const triggers = [];
  const antiTriggers = [];
  if (!whenToUse) return { triggers, antiTriggers };

  let target = triggers;
  for (const line of whenToUse.split("\n")) {
    if (/do\s+not\s+use/i.test(line)) {
      target = antiTriggers;
      continue;
    }
    if (/use\s+this\s+skill\s+when/i.test(line)) {
      target = triggers;
      continue;
    }
    const bullet = /^\s*[-*]\s+(.*\S)\s*$/.exec(line);
    if (bullet) target.push(bullet[1]);
  }

  return { triggers, antiTriggers };
}

function firstHeading(body) {
  const match = /^#\s+(.+?)\s*$/m.exec(body);
  return match ? match[1] : null;
}

function toTitleFromName(name) {
  return name
    .split(/[-_]/)
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
}

function hasUnfilledPlaceholder(value) {
  if (typeof value !== "string") return false;
  return TEMPLATE_PLACEHOLDERS.some((token) => value.includes(token));
}

export function checkConformance(data, sectionOrder, sections) {
  const issues = [];

  for (const key of TEMPLATE_KEYS) {
    if (!(key in data)) issues.push(`missing frontmatter key: ${key}`);
  }

  for (const section of TEMPLATE_SECTIONS) {
    if (!sections.has(section)) issues.push(`missing section: ## ${section}`);
  }

  if (typeof data.name === "string" && data.name && !/^[a-z0-9]+(-[a-z0-9]+)*$/.test(data.name)) {
    issues.push(`name is not kebab-case: ${data.name}`);
  }

  for (const key of ["name", "description", "author", "subject_matter_expert"]) {
    if (hasUnfilledPlaceholder(data[key])) {
      issues.push(`unfilled template placeholder in: ${key}`);
    }
  }

  // Template sections that are present must appear in the template's order.
  const present = sectionOrder.filter((heading) => TEMPLATE_SECTIONS.includes(heading));
  const expected = TEMPLATE_SECTIONS.filter((heading) => present.includes(heading));
  if (present.join("|") !== expected.join("|")) {
    issues.push(`template sections are out of order: ${present.join(" -> ")}`);
  }

  return issues;
}

async function walk(directory) {
  const found = [];
  let entries;
  try {
    entries = await readdir(directory, { withFileTypes: true });
  } catch {
    return found;
  }
  for (const entry of entries) {
    const full = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      found.push(...(await walk(full)));
    } else if (entry.isFile() && entry.name.endsWith(".md")) {
      found.push(full);
    }
  }
  return found;
}

export function encodePath(relativePath) {
  return relativePath.split("/").map(encodeURIComponent).join("/");
}

export async function collectSkills(root, ref = "main") {
  const files = [];
  for (const dir of SCAN_DIRS) {
    files.push(...(await walk(path.join(root, dir))));
  }

  const skills = [];
  for (const file of files.sort()) {
    const relativePath = path.relative(root, file).split(path.sep).join("/");
    if (EXCLUDED_FILENAMES.has(path.basename(relativePath))) continue;

    const text = await readFile(file, "utf8");
    const frontmatter = parseFrontmatter(text);
    const body = stripFrontmatter(text);
    const { sections, order } = extractSections(body);
    const data = frontmatter ?? {};
    const { triggers, antiTriggers } = extractTriggers(sections.get("When to Use"));

    const segments = relativePath.split("/");
    const name =
      typeof data.name === "string" && data.name.trim()
        ? data.name.trim()
        : path.basename(relativePath, ".md");

    const issues = checkConformance(data, order, sections);
    if (!frontmatter) issues.unshift("no YAML frontmatter");

    skills.push({
      name,
      title: firstHeading(body) ?? toTitleFromName(name),
      path: relativePath,
      tier: segments[0] === "framework" ? "framework" : "intake",
      category: segments.length > 2 ? segments[1] : segments[0],
      description: typeof data.description === "string" ? data.description : "",
      author: typeof data.author === "string" ? data.author : "",
      subjectMatterExpert:
        typeof data.subject_matter_expert === "string" ? data.subject_matter_expert : "",
      language: typeof data.Language === "string" ? data.Language : "",
      framework: typeof data.Framework === "string" ? data.Framework : "",
      requires: Array.isArray(data.requires) ? data.requires : [],
      triggers,
      antiTriggers,
      rawUrl: `https://raw.githubusercontent.com/${REPOSITORY}/${ref}/${encodePath(relativePath)}`,
      apiUrl: `https://api.github.com/repos/${REPOSITORY}/contents/${encodePath(relativePath)}?ref=${ref}`,
      conformsToTemplate: issues.length === 0,
      templateIssues: issues,
    });
  }

  return skills.sort((a, b) => {
    if (a.tier !== b.tier) return a.tier === "framework" ? -1 : 1;
    return a.path.localeCompare(b.path);
  });
}
