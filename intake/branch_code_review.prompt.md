---
name: branch-code-review
description: "Review the current branch as if it were a production pull request."
agent: agent
model: Claude Opus 4.6 (copilot)
---

Review the current branch as if this were a production pull request.

Compare the current branch against `origin/develop` and review the changed code only, but inspect surrounding code, call paths, tests, configuration, and related files as needed to understand the impact of the changes.

This is a **review, planning, and prompt-creation task only**. Do not modify application code, tests, configuration, database scripts, or documentation other than the required review/remediation planning documents.

## Goal

Find actionable issues in the current branch that a strong GitHub Copilot PR review, senior engineer review, or quality gate should catch. Then create:

1. A detailed PR review findings document.
2. A detailed remediation plan for any issues found.
3. A separate execution prompt that can be used later to implement the remediation.

The execution prompt must be based on the actual findings from this review. Do not create a generic execution prompt.

Prioritize correctness, regressions, security, performance, data integrity, test coverage, maintainability, backward compatibility, and deployment safety.

Do not summarize every file. Do not provide generic praise. Focus on specific risks and actionable review comments.

## Required Comparison

Use the current branch diff against `origin/develop`.

Start by identifying the changed files with commands such as:

```bash
git diff --name-status origin/develop...HEAD
git diff --stat origin/develop...HEAD
git diff origin/develop...HEAD
```

If `origin/develop` is not the correct base branch, identify the likely base branch from the repository context and clearly state the assumption.

Review only changes introduced by this branch, but consider adjacent unchanged code when needed to understand whether a changed line is safe.

## Required Unique Output Naming

Do **not** write the review artifacts to shared fixed paths such as:

```text
docs/pr-review-findings.md
docs/pr-review-remediation-plan.md
docs/pr-review-remediation-execution-prompt.md
```

Those fixed file names create merge conflicts when multiple reviews or branches create the same files.

Instead, create a unique review output directory and unique artifact names for this review.

Use this format:

```text
docs/pr-reviews/<review-id>/
```

Where `<review-id>` should be derived from the current branch name, short commit SHA, and timestamp.

Recommended format:

```text
<branch-slug>-<short-sha>-<yyyymmdd-hhmmss>
```

Example:

```text
docs/pr-reviews/feature-ctro-1234-dashboard-fix-a1b2c3d-20260702-143015/
```

Use commands similar to the following to determine the values:

```bash
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
BRANCH_SLUG="$(echo "$CURRENT_BRANCH" | tr '/[:space:]' '-' | tr -cd '[:alnum:]._-' | tr '[:upper:]' '[:lower:]')"
SHORT_SHA="$(git rev-parse --short HEAD)"
RUN_TS="$(date +%Y%m%d-%H%M%S)"
REVIEW_ID="${BRANCH_SLUG}-${SHORT_SHA}-${RUN_TS}"
REVIEW_DIR="docs/pr-reviews/${REVIEW_ID}"
mkdir -p "$REVIEW_DIR"
```

If shell command execution is not available, manually create a unique review ID using:

```text
<branch-name-sanitized>-<short-sha>-<date-time>
```

All generated review artifacts must be created inside that unique directory.

Required artifact paths:

```text
docs/pr-reviews/<review-id>/pr-review-findings-<review-id>.md
docs/pr-reviews/<review-id>/pr-review-remediation-plan-<review-id>.md
docs/pr-reviews/<review-id>/pr-review-remediation-execution-prompt-<review-id>.md
```

The remediation execution prompt must reference the unique findings and remediation plan paths created for this review.

Do not overwrite a prior review directory or prior review files. If a path already exists, create a new review ID by adding a later timestamp or numeric suffix.

## Required Sequencing

Follow this sequence exactly:

1. Determine the unique review ID and review output directory.
2. Review the branch as a pull request.
3. Identify confirmed issues, risks, test gaps, and open questions.
4. Create the PR review findings document in the unique review directory.
5. Create a remediation plan based on those findings in the unique review directory.
6. Create a separate execution prompt based specifically on the remediation plan in the unique review directory.
7. Do not implement the remediation in this task.

The execution prompt must reference the completed remediation plan and include concrete repository-specific findings, files, classes, methods, tests, and commands where known.

Do not leave placeholders where repository-specific details are known.

## Review Method

Perform the review in multiple passes.

### Pass 1: Understand the Intent and Scope

Determine:

- what feature, bug fix, refactor, configuration change, migration, or test change this branch appears to implement,
- which workflows are affected,
- which APIs, UI screens, services, repositories, queries, jobs, or configuration files are affected,
- whether the diff contains unrelated changes,
- whether the implementation matches the apparent intent,
- whether the branch appears incomplete.

### Pass 2: Correctness and Regression Review

Look for:

- logic errors,
- incomplete branches or missing conditions,
- incorrect null/empty handling,
- incorrect default values,
- off-by-one or boundary issues,
- broken create/update/delete flows,
- mismatched request/response fields,
- DTO/entity/mapper inconsistencies,
- validation gaps,
- incorrect error handling,
- swallowed exceptions,
- incorrect status codes,
- incorrect redirects or navigation behavior,
- broken backward compatibility,
- changed behavior that is not covered by tests,
- deleted code that still appears to be needed,
- inconsistent behavior across similar code paths,
- failure to preserve existing business behavior.

### Pass 3: Security Review

Look for:

- reflected user input in responses or logs,
- XSS risks,
- SQL/HQL/JPQL injection risks,
- unsafe string concatenation in queries,
- missing authorization checks,
- privilege escalation risks,
- insecure direct object reference risks,
- missing ownership or tenant checks,
- sensitive data exposure,
- passwords, tokens, secrets, or PII being logged or returned,
- CSRF/session/authentication regressions,
- unsafe deserialization,
- path traversal or file upload risks,
- overly broad CORS or security configuration changes,
- insufficient input validation,
- insecure defaults.

### Pass 4: Performance and Scalability Review

Look for:

- N+1 query patterns,
- repeated repository or API calls inside loops,
- missing pagination,
- loading full entities where projections would be sufficient,
- large result sets returned to the UI,
- expensive queries introduced or made worse,
- inefficient joins, counts, sorts, grouping, or `DISTINCT`,
- missing or suspicious indexes for new queries,
- unnecessary eager loading,
- lazy loading during serialization,
- repeated calculations that should be batched,
- synchronous work that may cause timeouts,
- memory-heavy operations,
- blocking external calls without timeouts,
- excessive response payloads.

### Pass 5: Data, Database, and Migration Review

Look for:

- schema changes without corresponding entity/model changes,
- entity/model changes without corresponding migrations,
- unsafe migrations,
- nullable/non-nullable mismatches,
- missing defaults,
- data loss risks,
- backward-incompatible column changes,
- indexes missing for new lookup patterns,
- migration ordering problems,
- seed/reference data inconsistencies,
- changed enum/status values that may break existing data,
- rollback risks,
- SQL view or query changes that may affect performance or correctness.

### Pass 6: API and Contract Review

Look for:

- request/response contract changes,
- changed field names,
- changed JSON serialization behavior,
- missing compatibility handling,
- clients that may break due to the change,
- missing API validation,
- incorrect HTTP status codes,
- inconsistent error response shapes,
- OpenAPI/API documentation mismatches, if applicable,
- changes that require frontend, QA, or consumer coordination.

### Pass 7: Frontend/UI Review, if applicable

Look for:

- UI state not updating after actions,
- loading states that never clear,
- missing error states,
- missing empty states,
- broken form validation,
- incorrect disabled/enabled behavior,
- accessibility regressions,
- brittle selectors,
- broken routing,
- stale state after navigation,
- excessive API calls,
- missing debounce/throttle for search,
- table pagination/sorting/filtering regressions,
- tests that only verify page load instead of functionality.

### Pass 8: Test Coverage Review

Review existing and changed tests.

Identify:

- missing unit tests,
- missing integration tests,
- missing end-to-end tests,
- missing regression tests for bug fixes,
- tests that only verify page load,
- tests with weak assertions,
- tests that do not validate the changed behavior,
- tests that need new edge cases,
- tests that rely on brittle data or selectors,
- snapshots updated without clear reason,
- deleted tests that should not have been removed,
- tests that are now stale because behavior changed.

For each issue, state whether a test should be added or updated and what the test should verify.

### Pass 9: Maintainability and Code Quality Review

Look for:

- duplicated logic,
- overly broad changes,
- unnecessary refactoring,
- inconsistent patterns compared to surrounding code,
- unclear names,
- excessive complexity,
- dead code,
- unused imports or dependencies,
- inconsistent error handling,
- magic values,
- missing comments where logic is non-obvious,
- comments that no longer match code,
- violations of project conventions.

## Important Review Rules

- Be specific and evidence-based.
- Do not invent issues that are not supported by the diff or surrounding code.
- Do not comment on unchanged code unless the branch change makes that code relevant.
- Do not report style-only issues unless they affect maintainability or violate an established project convention.
- Do not stop after finding the first few issues; review the whole diff.
- Prefer fewer high-quality findings over many vague findings.
- Include potential issues even if confidence is medium, but label them clearly as requiring verification.
- Distinguish confirmed defects from risks, questions, and suggested improvements.
- If a finding depends on runtime behavior, state what should be tested or measured.
- If no significant issues are found, say so and identify the highest-risk areas reviewed.

## Required Deliverable 1: PR Review Findings Document

Create a markdown document at this unique path:

```text
docs/pr-reviews/<review-id>/pr-review-findings-<review-id>.md
```

The document must include the following sections.

### 1. Pull Request Review Summary

Include:

- review ID,
- review artifact directory,
- base branch used,
- current branch,
- current short commit SHA,
- review timestamp,
- number of files changed,
- high-level change intent,
- highest-risk changed areas,
- overall risk level: High, Medium, or Low,
- whether remediation is required before merge.

### 2. Changed File Inventory

Use this table:

| File | Change Type | Area | Review Notes | Risk Level |
| ---- | ----------- | ---- | ------------ | ---------- |

### 3. Blocking Issues

List issues that should be fixed before merge.

For each issue, include:

| Issue ID | File/Location | Severity | Category | Problem | Why It Matters | Recommended Fix | Recommended Test |
| -------- | ------------- | -------- | -------- | ------- | -------------- | --------------- | ---------------- |

Severity values:

- Critical
- High
- Medium
- Low

Categories may include:

- correctness
- security
- performance
- regression
- test coverage
- maintainability
- compatibility
- database
- API
- UI
- configuration
- deployment

### 4. Non-Blocking Issues and Risks

Use the same table format:

| Issue ID | File/Location | Severity | Category | Problem | Why It Matters | Recommended Fix | Recommended Test |
| -------- | ------------- | -------- | -------- | ------- | -------------- | --------------- | ---------------- |

### 5. Test Coverage Gaps

Use this table:

| Gap ID | Area | Missing or Weak Coverage | Recommended Test | Priority |
| ------ | ---- | ------------------------ | ---------------- | -------- |

### 6. Questions for the Author

Include only questions that are necessary to confirm correctness, product intent, deployment safety, or test coverage.

Use this table:

| Question ID | Area | Question | Why It Matters | Blocks Remediation? |
| ----------- | ---- | -------- | -------------- | ------------------- |

### 7. Suggested Validation Commands

List useful commands to validate the review findings, using this repository’s actual tooling where possible.

Examples:

```bash
git diff origin/develop...HEAD
mvn test
mvn verify
npm test
npm run test
npm run test:e2e
npx playwright test
```

Use only commands that appear relevant to this repository.

### 8. Final Review Recommendation

End with one of:

- **Approve with no significant concerns**
- **Approve with minor comments**
- **Request changes**
- **Needs more information before approval**

Explain the recommendation briefly.

## Required Deliverable 2: Remediation Plan Document

Create a markdown document at this unique path:

```text
docs/pr-reviews/<review-id>/pr-review-remediation-plan-<review-id>.md
```

This document must be based on the actual PR review findings.

Do not create a generic remediation plan.

The remediation plan must include the following sections.

### 1. Remediation Executive Summary

Include:

- review ID,
- path to the corresponding findings document,
- number of blocking issues,
- number of non-blocking issues,
- number of test coverage gaps,
- highest-priority fixes,
- overall remediation risk,
- recommended implementation order.

### 2. Issue-to-Remediation Matrix

Use this table:

| Issue ID | Severity | Category | Root Cause / Likely Cause | Proposed Remediation | Files Likely to Change | Tests Needed | Priority |
| -------- | -------- | -------- | ------------------------- | -------------------- | ---------------------- | ------------ | -------- |

Priority guidance:

- P0: Must fix before merge.
- P1: Should fix before merge.
- P2: Can fix soon after merge if accepted by team.
- P3: Cleanup or future improvement.

### 3. Detailed Remediation Steps

For each issue requiring remediation, include:

- issue ID,
- affected file and location,
- current behavior,
- desired behavior,
- specific code or configuration change recommended,
- files/classes/functions likely to change,
- test updates required,
- risk level,
- rollback considerations,
- validation steps.

### 4. Test Plan for Remediation

Use this table:

| Test ID | Related Issue ID | Test Type | Scenario | Assertions Required | Files Likely to Change | Priority |
| ------- | ---------------- | --------- | -------- | ------------------- | ---------------------- | -------- |

Test types may include:

- unit
- integration
- end-to-end
- Playwright
- API
- database
- security
- performance
- regression
- manual QA

### 5. Validation Plan

Use this table:

| Validation Item | Related Issue ID | Command / Method | Expected Result | Required Before Merge? |
| --------------- | ---------------- | ---------------- | --------------- | ---------------------- |

### 6. Open Questions and Assumptions

Document any unresolved questions that affect remediation.

Use this table:

| Item | Type | Description | Impact | Owner / Follow-Up |
| ---- | ---- | ----------- | ------ | ----------------- |

Type values:

- assumption
- open question
- product clarification
- QA clarification
- technical uncertainty
- environment uncertainty

## Required Deliverable 3: Remediation Execution Prompt

Create a separate markdown document at this unique path:

```text
docs/pr-reviews/<review-id>/pr-review-remediation-execution-prompt-<review-id>.md
```

This must be a complete prompt that can be pasted into Copilot later to implement the remediation.

The execution prompt must:

1. Reference the unique findings document path:
   `docs/pr-reviews/<review-id>/pr-review-findings-<review-id>.md`
2. Reference the unique remediation plan path:
   `docs/pr-reviews/<review-id>/pr-review-remediation-plan-<review-id>.md`
3. Include the actual issue IDs from the findings.
4. Include the actual files/classes/functions known from the review.
5. Include the actual remediation steps from the plan.
6. Include the actual test recommendations from the plan.
7. Include the actual validation commands recommended for this repository.
8. Clearly state which issues are P0/P1/P2/P3.
9. Clearly state that implementation should be limited to the planned remediation.
10. Clearly state that unrelated refactors, style churn, dependency changes, or behavior changes are not allowed unless directly required.

Do not leave placeholders where repository-specific details are known.

The execution prompt must include this structure:

```markdown
Act as a senior software engineer implementing remediation for a pull request review.

Use these documents as the authoritative source:

- docs/pr-reviews/<review-id>/pr-review-findings-<review-id>.md
- docs/pr-reviews/<review-id>/pr-review-remediation-plan-<review-id>.md

Your task is to implement the planned remediation for the identified PR review issues.

## Scope

[Include actual issue IDs and summaries.]

## Required Fixes

[Include actual remediation items.]

## Files Expected to Change

[Include actual files from the plan.]

## Tests to Add or Update

[Include actual tests from the plan.]

## Validation Commands

[Include actual commands from the plan.]

## Constraints

- Only fix the issues listed in the remediation plan.
- Do not make unrelated refactors.
- Do not change unrelated behavior.
- Preserve existing business behavior.
- Add or update tests for each confirmed fix.
- Document any issue that cannot be fixed and why.

## Final Response Required

After implementation, respond with:

1. Issues fixed.
2. Files changed.
3. Tests added or updated.
4. Commands run and results.
5. Any issues not fixed and why.
6. Remaining risks or open questions.
```

## Final Response Required for This Task

After completing the review, remediation plan, and execution prompt, respond with:

1. Review ID used.
2. Review artifact directory created.
3. Base branch used for comparison.
4. Summary of changed areas reviewed.
5. Blocking issues found.
6. Non-blocking issues and risks found.
7. Test coverage gaps found.
8. Recommended remediation summary.
9. Highest-priority P0/P1 remediation items.
10. Path to the PR review findings document.
11. Path to the remediation plan document.
12. Path to the remediation execution prompt document.
13. Suggested validation commands.
14. Final review recommendation.
15. Open questions or assumptions.

## Constraints

- Do not modify application code during this task.
- Do not modify tests during this task.
- Do not modify configuration during this task.
- Do not implement remediation during this task.
- Only create the required markdown review, remediation plan, and execution prompt documents.
- Do not write to shared fixed review file paths that will cause merge conflicts.
- Do not overwrite prior review artifacts.
- Do not invent files, classes, methods, endpoints, queries, or test commands.
- Use actual repository evidence.
- Clearly label hypotheses that require runtime validation.
- Preserve existing business behavior in all recommendations.
- Do not recommend broad refactors unless clearly required to fix a confirmed issue.
- The execution prompt must be specific to the findings and remediation plan.

## Quality Bar

This task is complete only when:

- a unique review ID and unique review artifact paths have been created,
- the current branch has been reviewed against `origin/develop`,
- changed code has been reviewed for correctness, security, performance, regressions, test coverage, maintainability, and compatibility,
- blocking and non-blocking issues have been documented,
- test gaps have been documented,
- remediation steps are concrete and prioritized,
- the remediation plan maps each issue to recommended fixes and tests,
- the execution prompt is specific enough for a follow-up implementation task,
- the final response clearly states whether the branch should be approved, changed, or clarified before merge,
- the generated artifact paths are unique enough to avoid merge conflicts across repeated reviews.
