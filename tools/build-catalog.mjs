#!/usr/bin/env node
// Regenerates framework/catalog.json from the skill Markdown files in this repo.
// Output is deterministic so CI only commits when a skill actually changes.

import { writeFile, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { REPOSITORY, collectSkills } from "./skill-parser.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUTPUT = path.join(ROOT, "framework", "catalog.json");
const REF = process.env.CATALOG_REF ?? "main";
const CHECK_ONLY = process.argv.includes("--check");

const skills = await collectSkills(ROOT, REF);

const catalog = {
  catalogVersion: 1,
  repository: REPOSITORY,
  ref: REF,
  skillCount: skills.length,
  curatedCount: skills.filter((skill) => skill.tier === "framework").length,
  notes:
    "Skills under intake/ are submitted but not yet reviewed. Treat them as drafts and say so when recommending them.",
  skills,
};

const serialised = `${JSON.stringify(catalog, null, 2)}\n`;

if (CHECK_ONLY) {
  const existing = await readFile(OUTPUT, "utf8").catch(() => null);
  if (existing !== serialised) {
    console.error("catalog.json is out of date. Run: node tools/build-catalog.mjs");
    process.exit(1);
  }
  console.log(`catalog.json is up to date (${skills.length} skills).`);
} else {
  await writeFile(OUTPUT, serialised, "utf8");
  console.log(`Wrote ${path.relative(ROOT, OUTPUT)} with ${skills.length} skills.`);
}
