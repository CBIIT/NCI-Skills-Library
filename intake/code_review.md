---
name: code-review
description: Guide for performing code reviews. Use this when asked to review an application, branch, pull request, or change set.
---

## Purpose

Perform a structured code review and produce an actionable report.

## Precedence

1. If repository-specific standards exist (e.g., `github-instructions.md`, `CONTRIBUTING.md`, or other agent guidance), those rules take priority over this document.
2. If this guide conflicts with language/framework conventions, follow the language/framework conventions and note the rationale in the report.

## Scope Discovery

1. Determine review scope from user request:
   - Entire repository, or
   - Specific branch / PR / commit range / files.
2. If scope is unclear, state assumptions clearly in the report before listing findings.

## Output Requirements

1. Save results to `code-review-YYYYMMDD.md` using local system date in `YYYYMMDD` format.
2. Report must include:
   - Scope reviewed
   - Standards used (repo-specific + this guide)
   - Summary by severity
   - Detailed findings
   - Positive observations
   - Deferred / uncertain items (if any)

## Finding Format (Required)

For each finding, include:

- **ID:** `CR-###`
- **Severity:** Critical | High | Medium | Low
- **Confidence:** High | Medium | Low
- **Category:** Design | Correctness | Security | Performance | Maintainability | Testing | Documentation
- **Location:** file path + line(s)
- **Issue:** concise problem statement
- **Why it matters:** risk / impact
- **Recommendation:** specific fix
- **Evidence:** code reference and reasoning

Only report issues supported by evidence. Avoid speculative claims.

## Review Workflow

1. Identify applicable standards and conventions.
2. Review architecture and design fit for the requested scope.
3. Review implementation details (correctness, readability, maintainability).
4. Review security and error handling.
5. Review tests and testability.
6. Produce prioritized findings and concrete recommendations.

## Review Checklist

Use this checklist as guidance, not rigid law. Apply engineering judgment.

### Architecture and General Design

- **Duplication (DRY):** Is logic duplicated and suitable for extraction?
- **Abstraction levels:** Are high-level policies separated from low-level details?
- **Correct behavior:** Are expected, boundary, and failure cases handled?
- **Dead code:** Are there unused functions/variables or unreachable branches?

### Classes and Modules

- **Single responsibility:** Does each module/class have a focused purpose?
- **Encapsulation:** Are internals hidden and interfaces minimal?
- **Size/complexity:** Is the unit too large or doing too much?
- **Inheritance/substitution:** If inheritance exists, does it satisfy “is-a” and LSP?

### Functions and Routines

- **Single purpose:** Does each function do one coherent task?
- **Arguments:** Are parameter counts reasonable for readability and correctness?
- **Flags/output params:** Avoid when they obscure intent; justify if used.
- **Naming:** Do names accurately describe behavior?

### Variables and Data

- **Clarity:** Are names explicit and unambiguous?
- **Initialization/lifetime:** Are variables initialized and scoped appropriately?
- **Magic values:** Are unexplained literals replaced with named constants/config?

### Control Flow

- **Condition clarity:** Is the common path obvious and readable?
- **Branch correctness:** Are `if/else/switch` branches correct and complete?
- **Defaults:** Are default/error branches defensive and meaningful?

### Error Handling and Security

- **Error model:** Use idiomatic language approach (exceptions/results/error codes).
- **Abstraction of errors:** Avoid leaking low-level internals across boundaries.
- **No silent failures:** Empty catches/ignored errors must be justified.
- **Input validation:** Validate and sanitize external input.
- **Security checks:** Look for injection risks, auth/authz flaws, secret exposure, unsafe deserialization, path traversal, command execution risks, and insecure defaults.

### Comments and Formatting

- **Intent-focused comments:** Explain why, not obvious how.
- **No commented-out code:** Remove dead commented code.
- **Low-noise docs:** Remove stale or redundant comments.

### Testing and Environment

- **Coverage quality:** Are critical paths and edge cases tested?
- **Regression safety:** Are nearby risk areas tested when bugs are fixed?
- **Developer workflow:** Can build/test run with simple documented commands?

## Prioritization Guidance

- **Critical:** Security vulnerability, data loss/corruption, or major outage risk.
- **High:** Likely functional breakage or serious maintainability risk.
- **Medium:** Important quality issue with moderate impact.
- **Low:** Minor improvement or style-level concern.

Prefer fewer high-confidence findings over many low-confidence observations.
