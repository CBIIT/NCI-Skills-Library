---
version: 1.0
name: code-review
description: Performs a thorough, structured code review of a codebase, branch, set of changes, or specific files. Use this skill whenever the user asks for a code review, PR review, diff review, or asks you to "review" any code — whether it's a full repo, a recent commit, a feature branch, or a single file. Produces a categorized, severity-tagged issue report covering correctness, security, performance, architecture, readability, error handling, testing, and documentation. Supports multi-language codebases with separate report sections per language. Always trigger this skill for review requests, even if the user's phrasing is casual ("can you look at this?", "what do you think of this code?").
---

# Code Review Skill

Performs a comprehensive code review and produces a structured, evidence-based issue report, categorized by language then domain, tagged by severity and confidence. Each finding carries a unique identifier for traceability.

---

## Finding Identifiers

Every finding must have a unique ID in the format **CR-###**, where ### is a zero-padded, auto-incrementing counter starting at CR-001, continuing sequentially across all sections and languages in the report. These IDs allow findings to be referenced in tickets, PR comments, and follow-up reviews.

---

## Local Standards — Highest Priority

**Before analyzing any code**, check for project-local standards files. Look for:

- `.github/` directory (especially `CONTRIBUTING.md`, `PULL_REQUEST_TEMPLATE.md`, `copilot-instructions.md`)
- `CONTRIBUTING.md` at the repo root
- `CODE_STYLE.md`, `STANDARDS.md`, `GUIDELINES.md`, or similarly named files
- `.editorconfig`, linter configs (`.eslintrc`, `checkstyle.xml`, `pylintrc`, `rubocop.yml`, etc.)
- `README.md` sections describing conventions

**Local standards take precedence over all general guidance in this skill.** When a local standard applies to a finding:
- Note it explicitly: `**Local Standard**: per CONTRIBUTING.md §3 — ...`
- If the code violates a local standard, escalate severity by one level compared to what general guidance would suggest
- If a local standard conflicts with a language best practice, apply the local standard and note the conflict inline

If no local standards files are found, note this briefly in the report summary.

---

## Language-Specific Guidance

Apply idiomatic best practices for each language present in the codebase. **Language-specific rules take precedence over the general domain checklists below**, unless local project standards override them or the user explicitly instructs otherwise.

When a language best practice conflicts with a general rule in this skill, apply the language-specific rule and note the conflict inline in the finding:
> `⚠️ Conflict: general guidance suggests X, but idiomatic [Language] convention prefers Y — applying language convention per skill policy.`

Examples of language-specific concerns to layer in (non-exhaustive):
- **Java**: checked vs. unchecked exceptions, JavaDoc on public APIs, use of Optional, stream vs. loop idioms, visibility modifiers, null safety
- **JSP / Java EE**: EL injection risks, scriptlet avoidance, JSTL usage, session attribute hygiene, encoding on output
- **Python**: type hints, context managers, list comprehensions vs. loops, `__all__`, package structure
- **JavaScript / TypeScript**: strict null checks, async/await vs. promise chains, module boundaries, type safety
- **Go**: error wrapping conventions, goroutine lifecycle management, interface sizing
- **SQL**: parameterized queries, index coverage, explain plan awareness

---

## Multi-Language Codebases

When a codebase contains multiple languages (e.g., Java + JSP, Python + JavaScript, Go + TypeScript):

1. Identify all languages present during the context-gathering step
2. **Produce a separate report section for each language**, with its own domain breakdown, CR-### IDs continuing sequentially from the previous language's last ID
3. Apply language-specific guidance independently per section
4. Note cross-language concerns (e.g., a Java API that a JSP page calls unsafely) in whichever section is the root cause, with a cross-reference to the other language's section

---

## Severity Levels

Every finding must carry one of four severity tags:

| Tag | Label | Meaning |
|-----|-------|---------|
| 🔴 | **Severe** | Security vulnerability, data loss/corruption, crash, or major outage risk. Must be fixed before merge/ship. |
| 🟠 | **Major** | Likely functional breakage, significant design flaw, or serious maintainability risk. Should be fixed before merge unless explicitly deferred. |
| 🟡 | **Minor** | Code smell, non-idiomatic patterns, weak error handling, gaps in test coverage, missing docs. Should be addressed soon. |
| 🔵 | **Suggestion** | Nits, style preferences, optional improvements, refactor ideas. Nice-to-have, no urgency. |

---

## Confidence Levels

Every finding must carry a confidence level. Prefer fewer high-confidence findings over many speculative ones.

| Level | Meaning |
|-------|---------|
| **High** | The issue is clearly present and the impact is well-understood. |
| **Medium** | The issue is likely but depends on context or runtime behavior not fully visible in the code. |
| **Low** | Possible concern worth flagging; insufficient evidence to be certain. Low-confidence findings belong in **Deferred / Uncertain Items**, not the main findings list. |

---

## Review Domains

Cover all applicable domains per language. Use this checklist as guidance, not rigid law — apply engineering judgment. Skip a domain only if it is genuinely not applicable to the scope.

### 1. Correctness
- Logic errors, off-by-one errors, wrong conditions
- Incorrect algorithm or data structure choice
- Race conditions, concurrency bugs (shared state, missing locks, TOCTOU)
- Incorrect assumptions about input ranges, nullability, encoding
- Floating point precision issues; integer overflow / underflow risks
- Incorrect handling of edge cases (empty input, zero, max values, Unicode)
- Mutation of inputs the caller doesn't expect to be mutated
- Expected, boundary, and failure cases all handled

### 2. Security
- Injection vulnerabilities (SQL, shell, template, XSS, path traversal, command execution)
- Hardcoded secrets, credentials, API keys, tokens
- Insecure deserialization
- Missing or incorrect input validation / sanitization
- Authentication and authorization gaps (missing checks, privilege escalation)
- Insecure cryptography (weak algorithms, reused IVs, improper key handling)
- Sensitive data exposure (logging PII, leaking stack traces to clients)
- SSRF, open redirect, CSRF risks
- Dependency vulnerabilities (obviously outdated/flagged packages)
- Timing attacks on security-sensitive comparisons
- Insecure defaults

### 3. Performance
- N+1 query patterns or unnecessary repeated DB/network calls
- Missing indexes implied by query patterns
- Inefficient algorithms (O(n²) where O(n log n) or O(n) is straightforward)
- Unnecessary allocations in hot paths
- Blocking I/O on async/event-loop threads
- Missing caching where it's clearly beneficial and safe
- Large payload sizes, missing pagination
- Unbounded loops or recursion without depth limits

### 4. Error Handling & Reliability
- Silently swallowed errors (`catch {}`, `_ = err`) — must be justified if intentional
- Missing error propagation; errors leaking low-level internals across boundaries
- Missing retries or backoff for transient failures
- No timeouts on network/IO calls
- Panic/crash on recoverable conditions
- Incomplete rollback on partial failure (transactions, multi-step writes)
- Missing circuit breakers or rate limiting on external calls

### 5. Architecture & Design
- Violation of separation of concerns (business logic in handlers, DB calls in views, etc.)
- Tight coupling that makes testing or future changes hard
- Inappropriate use of global state
- Missing abstraction (duplicated logic that should be extracted — DRY)
- Over-abstraction (unnecessary indirection)
- High-level policies not separated from low-level details
- Violation of SOLID principles where relevant; LSP violations in inheritance
- Breaking changes to public APIs without versioning
- Circular dependencies; god objects / god functions
- **Hidden / temporal coupling** — files or modules that the change history shows *consistently change together* despite no explicit dependency between them. This is a latent maintenance hazard (a change in one silently requires a change in the other). If the diff under review touches one side of a known coupling pair without the other, flag it. (Tornhill, *Your Code as a Crime Scene* — change-coupling analysis.)

### 6. Code Quality & Readability
- Misleading or ambiguous names (variables, functions, classes, modules)
- Functions that are too large or do more than one thing
- Deeply nested logic that should be flattened (early returns, guard clauses)
- Magic numbers or strings without named constants
- Dead code, commented-out code, TODO bombs
- Inconsistent style (where not caught by a linter)
- Copy-paste duplication
- Boolean traps (bare `true`/`false` args with no context)
- Flag arguments and output parameters that obscure intent

### 7. Testing
- Missing tests for new logic paths
- Tests that don't assert the right thing
- Brittle tests (testing implementation details, fragile mocks)
- Missing edge case coverage (empty, null, boundary, error paths)
- Tests with side effects that bleed across test cases
- Missing or inadequate integration/end-to-end tests for critical flows
- Flaky tests (time-dependent, random, order-dependent)
- Regression coverage when fixing bugs

### 8. Documentation & Observability
- Missing or outdated docstrings/comments for public interfaces
- Comments explaining *what* instead of *why* (low-noise, intent-focused comments preferred)
- Stale, redundant, or commented-out comments
- Missing or misleading README updates for changed behavior
- Insufficient structured logging for production debugging
- Missing or incorrect metrics/tracing instrumentation
- Changelog or migration guide missing for breaking changes

---

## Review Process

### Step 1: Understand Scope

Read the user's request carefully:
- **Full codebase**: traverse the directory structure, read key files (entry points, core modules, config, tests)
- **Recent changes / branch / diff**: focus on changed files; use `git diff`, `git log`, or files the user provides
- **Specific files**: review only what's specified

If the scope is ambiguous, state your assumptions clearly at the top of the report rather than blocking on a question. Ask only if an assumption would fundamentally change what gets reviewed.

### Step 2: Gather Context

Before reading code, orient yourself:
- Project type, language(s), framework(s) — identify **all** languages present
- **Local standards files** — read these first (see Local Standards section above)
- Entry points and core modules
- Test structure
- Config / dependency files (`package.json`, `pyproject.toml`, `go.mod`, `pom.xml`, etc.)
- Existing linting/formatting config (to avoid flagging issues already enforced by tools)
- **Change history of the files in scope** — for a full-codebase or branch review, mine version control to direct attention. The most-churned, defect-prone files deserve the deepest scrutiny; stable, rarely-touched code needs less. (Forensic approach from Adam Tornhill, *Your Code as a Crime Scene*.)

  ```bash
  # Churn ranking — where change and risk concentrate
  git log --format=format: --name-only --since="12 months ago" \
    | grep -v '^$' | sort | uniq -c | sort -rn | head -20

  # Past defect density — files that recur in bug/fix commits are the riskiest
  git log --since="12 months ago" --grep -iE 'fix|bug|patch|hotfix' \
    --format=format: --name-only | grep -v '^$' | sort | uniq -c | sort -rn | head -20
  ```
  A file that is both high-churn *and* historically bug-prone is a **hotspot** — weight its findings accordingly and review it first.

### Step 3: Read and Analyze

Work through the code systematically in this order:
1. **Architecture and design** — overall structure, separation of concerns, abstraction levels
2. **Implementation** — correctness, readability, maintainability, language idioms
3. **Security and error handling** — injection risks, auth/authz, silent failures, input validation
4. **Tests and testability** — coverage quality, regression safety, developer workflow

Apply every domain checklist to each file or change, layering in language-specific guidance. Take notes as you go — don't produce the report from memory.

For large codebases, prioritize:
1. Security and correctness issues everywhere
2. **Hotspots first** — the high-churn / bug-prone files surfaced in Step 2; that's where review effort has the highest return
3. Deep review of core business logic, auth, data access layers
4. Lighter pass over boilerplate, generated code, and pure UI

Only report issues supported by evidence from the code. Do not speculate. If something is uncertain, it belongs in Deferred / Uncertain Items.

### Step 4: Write the Report

Structure the report as follows. For single-language codebases, omit the per-language wrapper. For multi-language codebases, repeat the domain sections under each language heading.

```
# Code Review: <scope description>

## Summary
<2–4 sentence overall assessment: quality signal, main themes, key risks>

**Local Standards**: [Files found and applied, or "None found — general guidance applied"]
**Scope Assumptions**: [State any assumptions made about scope, or "None"]

## Issue Count
🔴 Severe: N  |  🟠 Major: N  |  🟡 Minor: N  |  🔵 Suggestion: N

---

## [Language: e.g., Java]  *(omit wrapper for single-language)*

### [Domain Name]

#### CR-001 · [SHORT-TITLE] · 🔴 Severe · Confidence: High
**File**: `path/to/file.ext`, line N (or line range N–M)
**Issue**: Concise problem statement.
**Why it matters**: Risk or impact if left unaddressed.
**Evidence**: Specific code reference and reasoning that supports the finding.
**Local Standard**: *(if applicable)* Per CONTRIBUTING.md §N — ...
**Recommendation**: Concrete fix or approach. Include a corrected code snippet when it makes the fix clearer.

#### CR-002 · [SHORT-TITLE] · 🟠 Major · Confidence: Medium
...

---

## [Language: e.g., JSP]

### [Domain Name]

#### CR-003 · [SHORT-TITLE] · 🔴 Severe · Confidence: High
...

---

## Deferred / Uncertain Items

Items noticed but not included in findings due to insufficient evidence, incomplete visibility, or dependency on runtime context. Worth investigating but not reportable with confidence.

| # | Area | Observation | Why deferred |
|---|------|-------------|--------------|
| D-001 | Security | Possible SSRF in `fetchUrl()` — couldn't verify if URL is user-controlled | Need to trace call sites |

*(Omit this section if there are no deferred items.)*

---

## What's Working Well
<Genuine callout of strong patterns, clean abstractions, good test coverage, etc. Skip if nothing stands out — do not add boilerplate praise.>
```

**Formatting rules:**
- CR-### IDs are assigned sequentially across the entire report, never reset per language or domain
- Group issues by language → domain → severity (Severe first, Suggestion last)
- Every finding must have: CR-### ID, title, severity tag, confidence level, file + line reference, issue, why it matters, evidence, and recommendation
- Include a corrected code snippet for 🔴 Severe and 🟠 Major findings whenever the fix isn't obvious
- Note local standard applicability and language/general-rule conflicts inline per finding
- Low-confidence observations go in Deferred / Uncertain Items, not the main findings list
- Do not pad the report — only include real, evidence-backed issues

### Step 5: Save the Report

Save the report to the project root as `code-review-YYYYMMDD.md`. Get today's date with:

```bash
date +%Y%m%d
```

Write the full report to `code-review-$(date +%Y%m%d).md` and confirm the path to the user.

---

## Tone and Calibration

- Be direct and specific. Vague feedback ("this could be better") is not useful.
- Severity must be honest. Don't inflate Minor issues to Major to seem thorough.
- If a domain has no issues, omit it — don't write "No issues found in Security."
- Suggestions should feel like a senior peer's thoughtful input, not a style lecture.
- Acknowledge trade-offs where they exist — not every imperfect decision is a bug.
- When local standards or language conventions override general guidance, say so clearly — don't silently apply a different rule.
- Never report a finding you can't back with evidence from the code.
