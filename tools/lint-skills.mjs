#!/usr/bin/env node
// Reports how each skill file measures up against intake/skills__template.md.
//
// Report-only by default, because no skill in the repository conforms yet.
// Pass --strict once framework/ has been retrofitted to make curated skills
// blocking; pass --only <path> to gate a single file (used for new skills).

import path from "node:path";
import { fileURLToPath } from "node:url";
import { collectSkills } from "./skill-parser.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const strict = args.includes("--strict");
const onlyIndex = args.indexOf("--only");
const only = onlyIndex !== -1 ? args[onlyIndex + 1] : null;

const skills = await collectSkills(ROOT);

let conforming = 0;
let blocking = 0;
let warnings = 0;

for (const skill of skills) {
  if (skill.conformsToTemplate) {
    conforming += 1;
    console.log(`ok    ${skill.path}`);
    continue;
  }

  const isBlocking = only ? skill.path === only : strict && skill.tier === "framework";
  if (isBlocking) blocking += 1;
  else warnings += 1;

  console.log(`${isBlocking ? "FAIL" : "warn"}  ${skill.path}`);
  for (const issue of skill.templateIssues) {
    console.log(`        - ${issue}`);
  }
}

console.log(
  `\n${skills.length} skills checked: ${conforming} conforming, ` +
    `${blocking} blocking, ${warnings} warning(s).`,
);

if (only && !skills.some((skill) => skill.path === only)) {
  console.error(`\n--only path not found in the catalog: ${only}`);
  process.exit(1);
}

process.exit(blocking > 0 ? 1 : 0);
