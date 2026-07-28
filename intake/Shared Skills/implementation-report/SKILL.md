---
version: 1.0.0
name: implementation-report
description: >
  Produces a human-readable explanation of a change request (CR) — what was done, why, what
  was considered, and how the most critical changes work. Not a code review; an implementation
  narrative for developers, reviewers, and future maintainers. Output is written as
  implementation-report-<slug>.md.
---
# implementation-report

Explain a change request in narrative form: what changed, why, what tradeoffs were made,
and how the most important pieces of the implementation work.

## When to invoke

- User says "write an implementation report for CR <id>", "document this CR",
  "explain what we did in this change", "create an implementation report",
  or "document <branch/commit>"
- After completing a significant feature, fix, or refactor and before closing the CR
- When a change is complex enough that a future developer (or agent) would benefit from
  understanding the reasoning, not just the diff

## What you need to know before running

1. **CR scope** — one of:
   - A branch name (compare to `main`/`master`): `git diff main...<branch>`
   - A commit range: `git diff <sha1>..<sha2>`
   - "Current staged/unstaged changes": `git diff HEAD`
   - A specific commit: `git show <sha>`
   - If not specified, default to `git diff HEAD` (all uncommitted changes) and confirm with user
2. **Slug** — short identifier for the output filename (e.g., `cr-013`, `pagination-fix`,
   `bootstrap5-nav`). Ask if not provided.
3. **Ticket/issue number** — optional; include if provided (e.g., `FS-1950`)
4. **Output location** — default to the folder where the skill was invoked (or an existing
   project `docs/` folder, if one is already the project's convention). If the user's
   environment maintains a separate documentation/wiki location for this project, ask where
   to save the report instead of guessing.

---

## Instructions

### Step 1 — Gather the diff

```powershell
# For a branch vs main:
git --no-pager diff main...<branch> --stat
git --no-pager diff main...<branch>

# For current uncommitted changes:
git --no-pager diff HEAD --stat
git --no-pager diff HEAD

# For a specific commit:
git --no-pager show <sha> --stat
git --no-pager show <sha>
```

Also read the commit messages in scope for intent signals:
```powershell
git --no-pager log main...<branch> --oneline
# or: git --no-pager log <sha1>..<sha2> --oneline
```

### Step 2 — Read critical files in full

From the `--stat` output, identify the **most significant files** changed:
- Files with the most lines changed
- Files whose names suggest core logic (service, controller, domain, config)
- Files that are architecturally sensitive (security config, shared utilities, DB schema)

Read those files in full from the working tree to understand context beyond the diff.

### Step 3 — Read project context

If the project has a standing context document (e.g., `docs/agent-config.md`, `CONTRIBUTING.md`,
`README.md`, or an architecture guide), read it before writing. Use it to understand the
project's architecture, naming conventions, and known patterns — so the report uses correct
vocabulary and correctly identifies what is architecturally significant. If no such document
exists, infer conventions from the codebase structure itself.

### Step 4 — Compose the report

Populate each section below using the diff, commit messages, full file reads, and
project context. Write in **past tense, plain English**. This is a narrative for
humans — not a list of diffs.

---

## Output template

```markdown
# Implementation Report — <Title>

| Field | Value |
|-------|-------|
| **Ticket** | <ticket number, or "N/A"> |
| **CR Scope** | <branch name, commit range, or commit SHA> |
| **Date** | <YYYY-MM-DD> |
| **Author** | <git author from commits, if determinable> |

---

## Description

<2–4 sentences. What is this change? What problem does it solve or what feature does it add?
Write for someone who wasn't in the room — enough context to understand the change without
reading the code.>

---

## Implementation Considerations

<What shaped the implementation? These are the non-obvious constraints, existing patterns
that had to be respected, dependencies that influenced design, or technical realities that
drove decisions. Bullet list, 3–8 items. Examples:>

- The `FundingSelectionService` already handles optimistic locking; this change had to hook
  into that mechanism rather than introduce a second locking strategy.
- The Angular client is auto-generated from `swagger.json` — the DTO field names had to
  follow the existing naming convention or the client would need to be regenerated.
- H2 does not support the Oracle `ROWNUM` pseudocolumn used in the existing pagination query;
  the repository test required a different approach for the in-memory test database.

---

## Alternatives Considered

<What other approaches were evaluated and rejected? If only one approach was considered,
say so. Bullet list.>

- **Option A — <name>:** <brief description and why it was rejected>
- **Option B — <name>:** <brief description and why it was rejected>
- *(If no alternatives were considered: "No significant alternatives were evaluated; the
  approach was constrained by <reason>.")*

---

## Files Changed

<Grouped by logical area. Infer groupings from the file paths and the architecture described
in the project's context document, if one exists (e.g., Controller, Service, Repository, Domain, Frontend, Config, Tests).>

### <Layer / Area>
| File | Change Summary |
|------|---------------|
| `path/to/File.java` | Added `findByStatusAndDate()` query method |
| `path/to/FileTest.java` | New tests for the above |

### <Another Layer>
| File | Change Summary |
|------|---------------|
| `path/to/component.ts` | Wired new endpoint; added pagination state |

---

## Key Changes Explained

<For the 2–5 most important or non-obvious changes: a heading per change, a code snippet,
and a plain-English explanation of what it does and why it was done this way.
Skip trivial changes (renaming, formatting, adding a field to a DTO).>

### <Change title>

**File:** `path/to/File.java`

```java
// relevant snippet — keep to ~20 lines maximum
```

<2–4 sentences explaining what this code does, what problem it solves, and why this
approach was chosen over alternatives. Mention any gotchas or things a reviewer should
pay close attention to.>

### <Another change>

...

---

## Testing Notes

<How was this change tested? What test cases were added? Are there scenarios not covered
by automated tests that require manual verification? If test coverage is thin, say so.>

---

## Open Items

<Anything deliberately deferred, known limitations, or follow-up work this change creates.
If none, write "None.">

- [ ] ...
```

---

## Writing guidance

- **Description**: write for someone who wasn't in the room. What problem, what solution, what impact.
- **Implementation Considerations**: these are the *why* behind decisions — constraints, patterns,
  tradeoffs. Not a restatement of what the code does.
- **Alternatives Considered**: even "we only considered one approach" is useful information.
- **Files Changed**: group by architecture layer (Controller/Service/Repo/Domain/Frontend/Config/Test),
  not by directory. Use the project's context document to map paths to layer names if one exists.
- **Key Changes Explained**: pick changes that are *non-obvious* — where a reader looking at
  the diff would ask "why did they do it that way?" Trivial additions don't need explanation.
- **Code snippets**: keep them short and focused on the interesting part. Strip boilerplate.
  Use the language-appropriate fence (` ```java `, ` ```typescript `, ` ```sql `, etc.)

## Output location

Write the report to `implementation-report-<slug>.md` in the folder where the skill was
invoked (or the project's existing `docs/` folder, if that's already the convention).

Confirm the output path to the user after writing.

## Notes

- If the diff is very large (>500 lines), focus the Key Changes section on the top 3 most
  architecturally significant changes. Note in the report that it covers highlights, not every change.
- If no ticket number was provided and commit messages reference one (e.g., `FS-1950:`), extract it.
- If the branch/commit is ambiguous (e.g., no upstream configured), ask the user to confirm
  the diff scope before proceeding.
- This report is meant to be read by someone who may never look at the PR diff. Write accordingly.
