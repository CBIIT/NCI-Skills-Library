---
name: defect-resolution-planning-with-complete-function-ui-parity
description: "Investigate a QA ticket and produce an implementation-ready plan for complete field-by-field, control-by-control, workflow-by-workflow, and pixel-level UI parity with the designated legacy application."
agent: agent
model: Claude Opus 4.6 (copilot)
---

# Complete Function UI-Parity Investigation and Remediation Planning

## Role

Act as a senior Java, Spring, Spring MVC/JSP, Vue.js, TypeScript, CSS, database, Playwright, Cucumber, accessibility-automation, and software-migration engineer.

Investigate the defects reported in the supplied QA ticket, but do not limit the investigation to the individual symptoms named in the ticket.

Use the reported ticket as the entry point for identifying the affected business function. Then perform a complete parity investigation of that function across the designated legacy application and the current NextGen workspace.

The investigation must compare the complete function:

- Page by page
- Route by route
- State by state
- Role by role
- Field by field
- Label by label
- Button by button
- Link by link
- Tab by tab
- Menu item by menu item
- Table column by table column
- Validation rule by validation rule
- Workflow step by workflow step
- API interaction by API interaction
- Persistence effect by persistence effect
- Visual region by visual region

This broader investigation is mandatory because previous attempts to fix the reported issues have not resolved the ticket and may have introduced additional regressions.

Treat prior diagnoses and attempted fixes as evidence to review, not as authoritative conclusions.

Approach the ticket as a fresh root-cause and complete-function parity investigation.

This is an investigation and planning task.

Do not modify production code, tests, application configuration, database schema, or persisted data during this task.

## Invocation and Input Format

Invoke the prompt using:

```text
/defect-resolution-planning-with-complete-function-ui-parity TICKET=CTRP-12345 QA_REPORT_PATH="/absolute/path/to/CTRP-12345.docx" LEGACY_APP_PATH="/absolute/path/to/legacy/repository"
```

Optional named arguments may be added:

```text
/defect-resolution-planning-with-complete-function-ui-parity TICKET=CTRP-12345 QA_REPORT_PATH="/absolute/path/to/CTRP-12345.docx" LEGACY_APP_PATH="/absolute/path/to/legacy/repository" LEGACY_BASE_URL="https://legacy.example.org" NEXTGEN_BASE_URL="https://nextgen.example.org" LEGACY_REF="release-4.x" NEXTGEN_REF="feature/CTRP-12345"
```

For multiple paths or values, use JSON-style arrays:

```text
/defect-resolution-planning-with-complete-function-ui-parity TICKET=CTRP-12345 QA_REPORT_PATH="/absolute/path/to/CTRP-12345.docx" LEGACY_APP_PATH="/absolute/path/to/legacy/repository" ASSOCIATED_DOCS_PATHS=["/absolute/path/to/acceptance-criteria.md","/absolute/path/to/test-notes.txt"] SCREENSHOT_PATHS=["/absolute/path/to/legacy.png","/absolute/path/to/nextgen.png"] FUNCTION_ENTRY_POINTS=["/trials/search","/trials/{id}/edit"] USER_ROLES=["Submitter","Reviewer","Administrator"]
```

Paths containing spaces must be quoted.

The current workspace root is always treated as:

```text
NEXTGEN_APP_PATH = current workspace root
```

## Required Inputs

The invocation must provide:

```text
TICKET = ticket identifier in CTRP-NNNNN format
QA_REPORT_PATH = absolute local path to the QA ticket or report
LEGACY_APP_PATH = absolute local path to the designated legacy application repository
```

## Optional Inputs

The invocation may provide:

```text
ASSOCIATED_DOCS_PATHS = JSON array of absolute paths to acceptance criteria, ticket attachments, investigation notes, logs, or other supporting documents

SCREENSHOT_PATHS = JSON array of explicit legacy, NextGen, expected, or actual screenshots

LEGACY_BASE_URL = URL of the designated running legacy application

NEXTGEN_BASE_URL = URL of the running NextGen application

LEGACY_REF = branch, tag, or commit identifying the legacy baseline

NEXTGEN_REF = branch, tag, or commit identifying the NextGen baseline

FUNCTION_ENTRY_POINTS = JSON array of known routes, menu entries, pages, or workflows belonging to the affected function

USER_ROLES = JSON array of roles or permission contexts that must be compared

TEST_DATA = record IDs, fixture names, database snapshots, tenants, organizations, accounts, or other data required for comparison

VIEWPORTS = JSON array of required viewport definitions

BROWSERS = JSON array of required browser projects

AUTH_CONTEXT = credential source, test account, authentication method, roles, permissions, scopes, claims, tenant, or organization context

EXPLICIT_PARITY_EXCEPTIONS = JSON array of user-approved deviations from legacy
```

Every parity exception must identify:

- Route or page
- Workflow state
- Role or permission context
- Exact field, button, control, text, behavior, or visual region
- Exact permitted difference
- Reason
- Approval source

Do not infer broad exceptions from general language.

## Missing-Input Behavior

Before beginning investigation, validate all required inputs.

If a required input is missing, empty, invalid, unreadable, or inaccessible, do not infer a value and do not continue with unsupported assumptions.

Return this copyable input template:

```text
TICKET=CTRP-NNNNN
QA_REPORT_PATH="/absolute/path/to/ticket.docx"
LEGACY_APP_PATH="/absolute/path/to/legacy/repository"

Optional:
ASSOCIATED_DOCS_PATHS=["/absolute/path/to/document.md"]
SCREENSHOT_PATHS=["/absolute/path/to/image.png"]
LEGACY_BASE_URL="https://legacy.example.org"
NEXTGEN_BASE_URL="https://nextgen.example.org"
LEGACY_REF="branch-tag-or-commit"
NEXTGEN_REF="branch-tag-or-commit"
FUNCTION_ENTRY_POINTS=["/known/route"]
USER_ROLES=["RoleName"]
TEST_DATA="description of required records or fixtures"
AUTH_CONTEXT="description of required authentication"
EXPLICIT_PARITY_EXCEPTIONS=[]
```

Do not silently substitute a guessed report path, legacy repository, ticket number, branch, environment, route, role, or dataset.

## Repository and Output Paths

Derive:

```text
NEXTGEN_APP_PATH = current workspace root
QA_REPORT_DIR = directory containing QA_REPORT_PATH
```

Create the following outputs:

```text
docs/qa/TICKET_RootCause_CorrectionPlan.md
.github/prompts/TICKET-execution.prompt.md
```

Optional sanitized evidence may be created under:

```text
docs/qa/TICKET_evidence/qa/
docs/qa/TICKET_evidence/legacy/
docs/qa/TICKET_evidence/nextgen/
docs/qa/TICKET_evidence/diff/
docs/qa/TICKET_evidence/dom/
docs/qa/TICKET_evidence/network/
docs/qa/TICKET_evidence/visual/
```

Do not store:

- Passwords
- Access tokens
- Session identifiers
- Cookies
- API keys
- Private keys
- Protected health information
- Personally identifiable information
- Production-only confidential records
- Other sensitive values

## Non-Negotiable Legacy-Parity Rule

The designated legacy application is the executable specification and the sole source of truth for the expected behavior and appearance of this parity task.

For every in-scope route, state, field, button, control, role, data condition, viewport, navigation path, validation outcome, error condition, and side effect, NextGen must reproduce the designated legacy application exactly under matched conditions.

Apply the following rules:

1. Directly observed behavior from the designated legacy application is authoritative.
2. Directly observed legacy appearance is authoritative.
3. The ticket identifies reported problems but does not override observed legacy behavior.
4. Existing NextGen behavior does not define correctness.
5. Existing NextGen tests do not define correctness.
6. Existing design-system behavior does not override legacy.
7. Framework defaults do not override legacy.
8. An intentional or previously approved NextGen difference remains a parity defect unless it appears in `EXPLICIT_PARITY_EXCEPTIONS`.
9. A visible or behavioral improvement over legacy is still a parity difference.
10. Do not infer what legacy probably intended.
11. When legacy source and legacy runtime behavior disagree, the designated runtime behavior wins.
12. When legacy differs by route, state, record, role, permission, browser condition, prior navigation, or viewport, preserve the corresponding state-specific behavior.
13. Do not choose one preferred legacy behavior and apply it uniformly when legacy is inconsistent.
14. Do not silently correct legacy labels, field order, button order, messages, layouts, validation, or interaction behavior.
15. Internal implementation may differ only when every client-observable behavior remains equivalent.
16. No unexplained or unauthorized difference may be omitted from the plan.
17. The investigation is incomplete while any discovered in-scope field, control, action, workflow state, or visual region lacks a parity disposition.

## Legacy Anomaly Preservation

Treat every reproducible legacy anomaly within the in-scope function as an observable requirement unless the exact anomaly has an explicit user-approved exception.

Examples include:

- Misspellings
- Unexpected capitalization
- Incorrect punctuation
- Duplicate labels
- Duplicate controls
- Missing labels
- Inconsistent terminology
- Unusual field ordering
- Unusual button ordering
- Disabled controls that appear as though they should be enabled
- Enabled controls that appear as though they should be disabled
- Buttons that do nothing
- Links that reload, fail, navigate unexpectedly, or do nothing
- Unexpected default values
- Stale values
- Missing values
- Validation that occurs at an unexpected time
- Unexpected validation messages
- Missing validation
- Blank states
- Incomplete rendering
- Clipping
- Overlap
- Truncation
- Overflow
- Broken responsive behavior
- Non-recoverable states
- Unexpected persistence behavior
- Unexpected cancellation behavior
- Unexpected browser-back or refresh behavior

Record every anomaly in a dedicated ledger.

Do not spread an anomaly beyond the exact state in which legacy exhibits it.

## Full-Function Scope Requirement

The investigation must not stop after reproducing the individual ticket symptoms.

Identify the complete affected business function.

The complete function includes, where applicable:

- All routes belonging to the feature
- All menu entry points
- Landing pages
- Search and list pages
- Detail pages
- Create pages
- Edit pages
- Copy or clone workflows
- Delete, deactivate, archive, restore, or remove workflows
- Approval, review, submit, reject, revoke, or transition workflows
- Tabs
- Sections
- Accordions
- Drawers
- Modals
- Confirmation dialogs
- Popovers
- Context menus
- Row actions
- Bulk actions
- Filters
- Sorting
- Pagination
- Exports
- Downloads
- Imports
- Attachments
- Audit history
- Related-record panels
- Error states
- Empty states
- Loading states
- Permission-denied states
- Read-only states
- Browser refresh and history behavior
- User-role variants
- Record lifecycle states
- Feature-flag variants

A route or component is in scope when it is required to complete, inspect, administer, or recover from the affected function.

Do not expand into unrelated business capabilities merely because they are linked from the same navigation system.

Document the boundary of the function and justify every exclusion.

## No Partial-Patch Rule

Do not create a correction plan based only on the ticket’s named controls or screenshots.

Before planning any fix:

1. Establish the complete function boundary.
2. Inventory all routes and pages.
3. Inventory all meaningful states.
4. Inventory every field.
5. Inventory every button and action control.
6. Inventory every other interactive control.
7. Pair each legacy item with its NextGen equivalent.
8. Compare behavior and appearance.
9. Identify every mismatch.
10. Review previous repair attempts.
11. Determine whether previous attempts introduced regressions.
12. Build a complete correction sequence.

Do not recommend a one-off patch that corrects the visible ticket symptom while leaving related fields, buttons, states, or workflows inconsistent.

## Stable Identifiers and Traceability

Assign stable identifiers:

```text
FUNC-01       Affected business function
PAGE-001      Route, page, modal, drawer, or major UI state
STATE-001     Distinct observable state of a page or workflow
FIELD-001     Logical field
BTN-001       Button or button-like action
CTRL-001      Other interactive control
FLOW-001      User workflow
PAIR-001      Matched legacy and NextGen state
ANOM-001      Legacy anomaly
ISSUE-001     Ticket-reported or discovered issue
DEFECT-001    Confirmed root-cause defect
TEST-001      Planned regression test
```

Maintain traceability:

```text
TICKET
-> FUNC
-> PAGE
-> STATE
-> FIELD / BTN / CTRL
-> PAIR
-> ISSUE
-> DEFECT
-> CORRECTION STEP
-> TEST
```

No discovered field, button, control, page, or state may be omitted from the traceability model.

## Function Boundary Discovery

Determine the function boundary from:

- Ticket language
- Ticket screenshots
- Associated documentation
- Legacy navigation
- Legacy routes
- JSPs and fragments
- Controllers and actions
- JavaScript
- Menus
- Vue routes
- Vue components
- NextGen API clients
- Backend controllers
- Page titles
- User workflows
- Existing tests
- Product terminology
- Data relationships

Document:

- Function name
- Business purpose
- Entry points
- Exit points
- User roles
- Record types
- Record states
- Dependencies
- Directly related subflows
- Explicit exclusions

When multiple functions are implicated, assign separate `FUNC-*` IDs and define their relationships.

## Route, Page, and State Inventory

Inventory all in-scope legacy and NextGen pages and states.

For each page or state, record:

- Page ID
- State ID
- Function ID
- Legacy route
- NextGen route
- Page title
- Entry path
- Prior workflow state
- Role
- Permission context
- Record type
- Record state
- Selected tab
- Expanded or collapsed sections
- Filters
- Sort
- Page number
- Modal state
- Loading state
- Error state
- Empty state
- Relevant test data
- Screenshot evidence
- DOM evidence
- Network evidence
- Mapping confidence

A page existing in only one application is a parity finding.

A state supported in only one application is a parity finding.

## Complete Field-by-Field Comparison

Inventory every logical field in the complete function.

This includes:

- Text inputs
- Textareas
- Numeric inputs
- Date fields
- Time fields
- Date/time fields
- Select controls
- Multi-select controls
- Autocomplete controls
- Search fields
- Radio groups
- Checkboxes
- Toggle controls
- File fields
- Hidden values that affect observable behavior
- Read-only values
- Calculated values
- Generated values
- Table cells
- Summary values
- Audit values
- Metadata
- Labels without editable controls
- Fields shown only under particular roles or states
- Fields that exist only in legacy
- Fields that exist only in NextGen

Treat repeated table cells as a logical field definition plus representative row states unless individual rows behave differently.

For each `FIELD-*`, compare all applicable properties.

### Field Identity

Record:

- Function
- Page
- State
- Section
- Tab
- Legacy technical name
- NextGen technical name
- Legacy label
- NextGen label
- API property
- Backend DTO property
- Entity or domain property
- Database table and column
- Type
- Semantic purpose

### Field Placement and Appearance

Compare:

- Presence
- Absence
- Field order
- Section order
- Label position
- Label text
- Capitalization
- Punctuation
- Required indicator
- Help text
- Tooltip
- Placeholder
- Width
- Height
- Alignment
- Spacing
- Margin
- Padding
- Font
- Color
- Border
- Background
- Icon
- Wrapping
- Truncation
- Overflow
- Read-only appearance
- Disabled appearance
- Error appearance
- Focus appearance

### Field State

Compare:

- Visible
- Hidden
- Enabled
- Disabled
- Read-only
- Editable
- Required
- Optional
- Conditionally required
- Conditionally visible
- Conditionally editable
- Role-specific state
- Record-state-specific state
- Default value
- Empty value
- Null value
- Stale-value behavior
- Reset behavior
- Cancel behavior

### Field Input Behavior

Compare:

- Input type
- Keyboard behavior
- Tab order
- Focus behavior
- Select-all behavior
- Copy behavior
- Paste behavior
- Character restrictions
- Masking
- Auto-formatting
- Case conversion
- Trimming
- Whitespace handling
- Maximum length
- Minimum length
- Numeric range
- Decimal precision
- Date format
- Option values
- Option order
- Search or autocomplete behavior
- Clear behavior
- Default selection
- Browser autofill behavior
- Mouse behavior

### Field Validation

Compare:

- Validation rules
- Validation trigger
- Validation timing
- Validation order
- Client-side validation
- Server-side validation
- Required-field handling
- Cross-field validation
- Boundary values
- Error-message text
- Error-message position
- Error-message appearance
- Multiple-error behavior
- Focus after validation failure
- Whether invalid values remain visible
- Whether invalid values are persisted
- Whether validation resets

### Field Data and Persistence

Compare:

- Initial source
- API request mapping
- API response mapping
- Database mapping
- Create behavior
- Update behavior
- Partial-update behavior
- Save behavior
- Cancel behavior
- Reload behavior
- Refresh behavior
- Persistence after navigation
- Defaulting
- Null handling
- Empty-string handling
- Formatting
- Conversion
- Calculated value
- Audit behavior
- History behavior
- Side effects
- Role-based filtering
- Data loss
- Unexpected overwrites

### Field Display Surfaces

Compare the field everywhere it appears:

- Create form
- Edit form
- Read-only detail
- Search result
- Table
- Summary
- Modal
- Audit history
- Report
- Export
- Email
- Confirmation view

A field is not fully compared when only one of its surfaces has been examined.

## Required Field Parity Matrix

The final plan must include:

| Field ID | Page / State | Legacy Field | NextGen Field | Type | Order | Visibility | Editability | Requiredness | Default | Validation | Persistence | Display | Visual Difference | Functional Difference | Disposition |
| -------- | ------------ | ------------ | ------------- | ---- | ----- | ---------- | ----------- | ------------ | ------- | ---------- | ----------- | ------- | ----------------- | --------------------- | ----------- |

Every field discovered in either application must appear.

Additional NextGen-only fields are parity findings unless explicitly approved.

Missing legacy fields are parity findings.

## Complete Button-by-Button Comparison

Inventory every button and button-like action.

This includes:

- Primary buttons
- Secondary buttons
- Icon buttons
- Form submit controls
- Cancel controls
- Reset controls
- Save controls
- Save-and-continue controls
- Add controls
- Edit controls
- Delete controls
- Remove controls
- Archive controls
- Restore controls
- Approve controls
- Reject controls
- Submit controls
- Revoke controls
- Search controls
- Clear controls
- Export controls
- Upload controls
- Download controls
- Pagination controls
- Table row actions
- Bulk actions
- Menu actions
- Links that behave like buttons
- Clickable icons
- No-op controls
- Disabled controls
- Hidden actions
- Conditional actions

For each `BTN-*`, compare:

### Identity and Appearance

- Label
- Capitalization
- Punctuation
- Icon
- Tooltip
- Accessible name
- Position
- Order
- Grouping
- Size
- Width
- Height
- Color
- Border
- Background
- Font
- Spacing
- Hover state
- Focus state
- Active state
- Disabled state
- Loading state

### Availability

- Visible or hidden
- Enabled or disabled
- Role-specific visibility
- Role-specific enablement
- Record-state-specific visibility
- Record-state-specific enablement
- Data-dependent visibility
- Validation-dependent enablement
- Duplicate-click protection
- State after activation

### Activation

- Mouse click
- Double-click
- Keyboard activation
- Enter behavior
- Spacebar behavior
- Focus behavior
- Tab order
- No-op behavior
- Event propagation
- Confirmation behavior
- Modal behavior
- Loading indicator
- Delay
- Debounce
- Throttle
- Multiple-submit behavior

### Result

- Request made
- Request payload
- Request sequence
- Navigation
- Redirect
- URL
- Query string
- Browser-history behavior
- Page refresh
- Modal open or close
- Notification
- Error message
- Persisted side effect
- Audit side effect
- Related-record effect
- Returned state
- Failure behavior
- Retry behavior
- Cancel behavior

A button is not equivalent merely because both applications eventually reach the same business outcome.

The exact interaction sequence and intermediate state must be compared.

## Required Button Parity Matrix

The final plan must include:

| Button ID | Page / State | Legacy Label / Icon | NextGen Label / Icon | Order | Visibility | Enablement | Preconditions | Activation | Confirmation | Request / Action | Navigation | Side Effects | Failure Behavior | Visual Difference | Functional Difference | Disposition |
| --------- | ------------ | ------------------- | -------------------- | ----- | ---------- | ---------- | ------------- | ---------- | ------------ | ---------------- | ---------- | ------------ | ---------------- | ----------------- | --------------------- | ----------- |

Every button discovered in either application must appear.

## Other Interactive-Control Comparison

Inventory controls not classified as fields or buttons, including:

- Links
- Tabs
- Menus
- Menu items
- Breadcrumbs
- Accordions
- Expand/collapse controls
- Sort headers
- Pagination controls
- Table selection
- Row selection
- Drag-and-drop controls
- Resize controls
- Popovers
- Tooltips
- Tree controls
- Filters
- Chips
- Status badges with interaction
- Context menus
- Keyboard shortcuts
- Browser-history controls where application behavior is affected

For each `CTRL-*`, compare:

- Presence
- Label
- Order
- Visual state
- Interaction
- Keyboard behavior
- Focus behavior
- Navigation
- State retention
- Side effects
- Error behavior
- Role behavior
- Record-state behavior

## Workflow-by-Workflow Comparison

Inventory every meaningful user workflow in the function.

Examples include:

- Search
- Open detail
- Create
- Save
- Edit
- Cancel edit
- Delete
- Confirm delete
- Submit
- Review
- Approve
- Reject
- Revoke
- Clone
- Export
- Upload
- Download
- Navigate between tabs
- Return to search
- Refresh
- Use browser back
- Recover from validation
- Recover from error
- Resume interrupted workflow

For each `FLOW-*`, document:

- Preconditions
- Role
- Record state
- Starting route
- Input data
- Ordered user actions
- Intermediate states
- Network interactions
- Persistence effects
- Notifications
- Final route
- Final UI state
- Browser-history result
- Legacy result
- NextGen result
- Exact differences
- Related field IDs
- Related button IDs
- Related control IDs
- Related defect IDs

## State Matrix

Build a state matrix covering every materially distinct observable state.

Dimensions include, where applicable:

- Role
- Permission
- Tenant or organization
- Record type
- Record lifecycle state
- New versus existing record
- Valid versus invalid input
- Complete versus incomplete data
- Empty versus populated results
- Selected tab
- Filter state
- Sort state
- Pagination state
- Modal state
- Loading state
- Error state
- Success state
- Feature flag
- Browser state
- Viewport
- Prior navigation
- Refresh state

Do not create meaningless Cartesian-product combinations.

Create separate states when behavior or appearance differs materially.

Every omitted combination must have an applicability rationale.

## Matched Comparison Conditions

Before comparing a legacy and NextGen state, align:

- Browser engine
- Browser version
- Operating system where rendering depends on it
- Viewport
- Device scale factor
- Zoom
- Fonts
- Locale
- Timezone
- Role
- Permissions
- Tenant or organization
- Feature flags
- Route
- Prior navigation
- Record
- Record state
- Input values
- Validation state
- Selected tab
- Filter
- Sort
- Page number
- Modal state
- Focus state
- Hover state
- Scroll position
- Network state
- External dependencies

Document every unmatched condition and its effect on confidence.

Do not claim exact parity when a material condition remains unmatched.

## Visual Parity Requirements

For every paired state, compare:

- Visible text
- Labels
- Heading hierarchy
- Field order
- Button order
- Table columns
- Column order
- Row order
- Layout
- Position
- Dimensions
- Spacing
- Alignment
- Fonts
- Font sizes
- Font weights
- Line heights
- Colors
- Backgrounds
- Borders
- Radius
- Shadows
- Icons
- Images
- Required indicators
- Validation styling
- Selected states
- Disabled states
- Read-only states
- Focus states
- Hover states
- Empty states
- Loading states
- Error states
- Modal placement
- Scrollbars
- Clipping
- Overflow
- Wrapping
- Truncation
- Responsive behavior
- Animations and transitions when observable

Use:

- Screenshots
- DOM snapshots
- Computed styles
- Bounding boxes
- Accessibility-tree output where useful
- Browser traces
- Network evidence
- Video when interaction timing matters

Visual acceptance requires zero unexplained differences under matched deterministic conditions.

Do not:

- Raise screenshot thresholds to hide differences
- Mask a differing field or control
- Crop out an in-scope mismatch
- Regenerate a baseline from mismatched NextGen output
- Replace an exact check with a broad visibility check
- Dismiss a difference as minor
- Dismiss a difference because NextGen looks better

## Functional and Persistence Parity

For every field, action, and workflow, compare applicable:

- API request
- API request order
- Request body
- Query parameters
- Response
- Validation response
- Authentication
- Authorization
- Database writes
- Database updates
- Database deletes
- Audit entries
- History entries
- Related-record changes
- Events
- Notifications
- Background jobs
- Reload behavior
- Refresh behavior
- Data displayed after save
- Data displayed after reopening
- Transaction behavior
- Rollback behavior
- Duplicate submission
- Idempotency

Matching the immediate UI is insufficient when the persisted or downstream result differs.

Matching persistence is insufficient when the visible workflow differs.

## Previous-Attempt and Regression Analysis

Because multiple prior attempts have failed, inspect previous repair activity.

Search for:

- Commits containing `TICKET`
- Branches containing `TICKET`
- Pull-request references
- Ticket references in comments
- Modified tests
- Changed screenshots or visual baselines
- Reverted changes
- Follow-up fixes
- Workarounds
- Suppressed assertions
- Increased screenshot tolerances
- Disabled tests
- Added conditional logic
- Duplicated components
- Changed API contracts
- CSS overrides
- Feature flags

For every identifiable attempt, record:

- Attempt ID
- Commit, branch, or change set
- Files changed
- Diagnosis assumed
- Fix implemented
- Ticket symptom targeted
- Parity dimensions not evaluated
- Tests added or changed
- Whether tests encoded legacy behavior
- Why the attempt did not fully resolve the function
- Regressions introduced
- Current residual code
- Whether the change should be retained, revised, or reverted

Do not assume the newest attempted fix is the best foundation.

## Attempt and Regression Ledger

Use:

| Attempt ID | Commit / Change | Assumption | Files Changed | Intended Fix | Missing Analysis | Result | Regression Introduced | Recommended Disposition |
| ---------- | --------------- | ---------- | ------------- | ------------ | ---------------- | ------ | --------------------- | ----------------------- |

The correction plan must explicitly avoid repeating failed assumptions.

## Evidence Identifiers

Use stable evidence IDs:

```text
QA-EV-001
LEG-SS-001
LEG-DOM-001
LEG-NET-001
LEG-TRACE-001
NG-SS-001
NG-DOM-001
NG-NET-001
NG-TRACE-001
DIFF-SS-001
DIFF-DOM-001
DIFF-NET-001
PAIR-001
```

For every evidence item, record:

- Source
- Path
- Application
- Environment
- Route
- State
- Role
- Record
- Browser
- Viewport
- Locale
- Timezone
- Capture method
- Related fields
- Related buttons
- Related controls
- Related issue
- Related defect
- Confidence
- Limitations

Prefer direct runtime evidence over source-code inference.

## Input Validation

Before investigation, verify:

1. `TICKET` is supplied and matches `CTRP-NNNNN`.
2. `QA_REPORT_PATH` is absolute, exists, and is readable.
3. `LEGACY_APP_PATH` is absolute, exists, and is readable.
4. Every associated-document path exists and is readable.
5. Every explicit screenshot path exists and is readable.
6. The current workspace can be identified.
7. Required output directories can be created.
8. The legacy baseline can be identified.
9. The NextGen baseline can be identified.
10. The affected function can be identified.
11. At least one reliable source of legacy behavior is available.
12. Runtime comparison is possible or its limitations can be documented.
13. Required roles, data, and authentication can be established or their absence documented.
14. Prior attempts can be identified or their absence documented.

If legacy cannot be run but source is available, perform useful static analysis, but mark runtime and visual conclusions as unverified.

Do not claim complete parity without runtime comparison.

## Task Restrictions

During this investigation:

- Do not modify production code.
- Do not modify tests.
- Do not modify application configuration.
- Do not modify database schema.
- Do not modify persisted application data.
- Do not modify the legacy application.
- Do not implement remediation.
- Do not update visual baselines.
- Do not weaken assertions.
- Do not disable tests.
- Do not change screenshot tolerances.

The only files that may be created are:

```text
docs/qa/TICKET_RootCause_CorrectionPlan.md
.github/prompts/TICKET-execution.prompt.md
docs/qa/TICKET_evidence/**
```

Evidence must be sanitized and ticket-related.

## Required Investigation Sequence

Follow this sequence:

1. Validate all required inputs.
2. Record the legacy and NextGen repository baselines.
3. Read the QA report.
4. Read all associated documentation.
5. Inventory ticket screenshots and evidence.
6. Extract all ticket issues and acceptance criteria.
7. Review previous repair attempts.
8. Identify the affected business function.
9. Define and justify the full function boundary.
10. Inventory legacy routes and pages.
11. Inventory NextGen routes and pages.
12. Create page mappings.
13. Inventory legacy states.
14. Inventory NextGen states.
15. Create state mappings.
16. Inventory every legacy field.
17. Inventory every NextGen field.
18. Create field mappings.
19. Inventory every legacy button and action.
20. Inventory every NextGen button and action.
21. Create button mappings.
22. Inventory every other interactive control.
23. Create control mappings.
24. Inventory all workflows.
25. Create workflow mappings.
26. Establish matched runtime conditions.
27. Capture legacy evidence for every applicable state.
28. Capture NextGen evidence for every applicable state.
29. Pair corresponding states.
30. Compare fields.
31. Compare buttons.
32. Compare other controls.
33. Compare workflows.
34. Compare validation.
35. Compare navigation.
36. Compare persistence.
37. Compare error and empty states.
38. Compare role and record-state behavior.
39. Compare visual appearance.
40. Record every legacy anomaly.
41. Record every NextGen-only field, control, state, or behavior.
42. Identify root causes.
43. Group duplicate symptoms by root cause.
44. Classify every difference.
45. Review unit, integration, Cucumber, component, Playwright, and visual coverage.
46. Calculate parity-inventory and test-coverage metrics.
47. Create a dependency-ordered correction plan.
48. Create a complete regression strategy.
49. Create the implementation execution prompt.
50. Verify that every inventory item has a disposition.
51. Verify that no recommendation is a ticket-only patch.
52. Verify that no prior failed assumption has been repeated without new evidence.

## Difference Classification

Classify every issue as one of:

- **Confirmed field parity defect**
- **Confirmed button or action parity defect**
- **Confirmed control parity defect**
- **Confirmed workflow parity defect**
- **Confirmed navigation parity defect**
- **Confirmed validation parity defect**
- **Confirmed persistence parity defect**
- **Confirmed data-display parity defect**
- **Confirmed role or permission parity defect**
- **Confirmed visual parity defect**
- **Confirmed combined functional and visual parity defect**
- **Confirmed anomaly-preservation defect**
- **Extra NextGen field or control**
- **Missing legacy field or control**
- **Matches legacy**
- **Ticket conflicts with legacy**
- **Data or configuration parity defect**
- **Cannot verify**
- **Legacy baseline ambiguity**
- **Explicit approved exception**
- **Outside complete-function boundary**

Do not use “intentional NextGen improvement” as a no-change classification unless it is an explicit approved exception.

## Coverage Metrics

Calculate:

```text
Page inventory coverage =
paired or dispositioned in-scope pages
--------------------------------------
all discovered in-scope pages
```

```text
State coverage =
paired or dispositioned applicable states
-----------------------------------------
all identified applicable states
```

```text
Field inventory coverage =
paired or dispositioned fields
------------------------------
all fields discovered in either application
```

```text
Field behavioral parity coverage =
fields compared for all applicable behavior dimensions
------------------------------------------------------
all in-scope fields
```

```text
Button parity coverage =
buttons compared for all applicable states and outcomes
-------------------------------------------------------
all buttons discovered in either application
```

```text
Control parity coverage =
controls compared for all applicable states and outcomes
--------------------------------------------------------
all controls discovered in either application
```

```text
Workflow parity coverage =
fully compared workflows
------------------------
all in-scope workflows
```

```text
Visual-state coverage =
paired states with verified visual evidence
-------------------------------------------
all applicable visual states
```

The required planning target is:

```text
100% inventory and disposition coverage
```

A proposed correction or test does not count as verified implementation coverage.

## Test Coverage Requirements

For every confirmed defect, plan meaningful automated regression coverage at the appropriate levels.

### Unit Tests

Use unit tests for:

- Validation rules
- Field defaults
- Formatting
- Mapping
- Conditional visibility logic when independently testable
- Button eligibility logic
- Permission calculations
- State transitions
- Sorting and filtering logic
- Data conversion

### Integration Tests

Use integration tests for:

- Controller or API behavior
- Request binding
- Validation integration
- Authorization
- Persistence
- Transactions
- Audit behavior
- Error handling
- Serialization
- Related-record effects

### Cucumber Tests

Where Cucumber is supported, use it for:

- Business workflow acceptance
- Role-specific behavior
- Record-state behavior
- Field validation scenarios
- Save and reload behavior
- Cross-step workflows

### Playwright Tests

Playwright must cover every in-scope field, button, control, and workflow surface.

For each field, Playwright should verify, as applicable:

- Presence
- Label
- Order
- Visibility
- Editability
- Requiredness
- Default
- Validation
- Save behavior
- Reload behavior
- Display formatting
- Role behavior
- Visual parity

For each button or action, Playwright should verify:

- Presence
- Label or icon
- Order
- Visibility
- Enablement
- Activation
- Confirmation
- Request
- Navigation
- Side effects
- Loading state
- Error state
- No-op behavior where applicable
- Visual parity

For each page or state, Playwright should capture a legacy-derived visual baseline where deterministic.

Do not create page-load-only coverage.

## Differential Playwright Strategy

Where practical, create a reusable comparison harness that:

1. Runs the same workflow against legacy and NextGen.
2. Uses matched browser and data conditions.
3. Captures field inventory.
4. Captures button and control inventory.
5. Captures text.
6. Captures accessibility names.
7. Captures bounding boxes.
8. Captures computed styles.
9. Captures screenshots.
10. Captures network interactions.
11. Captures navigation.
12. Captures persisted results.
13. Produces field-level, control-level, workflow-level, and pixel-level diffs.
14. Fails on every unexplained mismatch.

Do not generate expected baselines from mismatched NextGen output.

## Required Output Document

Create:

```text
docs/qa/TICKET_RootCause_CorrectionPlan.md
```

The document must contain the following sections.

### 1. Executive Summary

Include:

- Ticket
- QA report path
- Legacy path and reference
- NextGen reference
- Function name
- Function boundary
- Previous attempt count
- Page count
- State count
- Field count
- Button count
- Other-control count
- Workflow count
- Legacy anomaly count
- Confirmed defect count by category
- Ticket-only defects
- Additional complete-function defects
- Coverage percentages
- Highest-risk defects
- Recommended correction sequence
- Overall confidence

### 2. Input and Baseline Resolution

Use:

| Item | Value | Source | Validation Status | Notes |
| ---- | ----- | ------ | ----------------- | ----- |

Include all required and optional inputs.

### 3. Prior Attempt and Regression Ledger

Use:

| Attempt ID | Commit / Change | Assumption | Intended Fix | Files Changed | Tests Changed | Why It Failed | Regression Introduced | Disposition |
| ---------- | --------------- | ---------- | ------------ | ------------- | ------------- | ------------- | --------------------- | ----------- |

### 4. Complete Function Boundary

Document:

- Function purpose
- Entry points
- Exit points
- Routes
- Pages
- Roles
- Record states
- Included subflows
- Excluded areas
- Evidence supporting the boundary

### 5. Page and Route Inventory

Use:

| Page ID | Function | Legacy Route | NextGen Route | Purpose | Roles | States | Mapping | Evidence | Disposition |
| ------- | -------- | ------------ | ------------- | ------- | ----- | ------ | ------- | -------- | ----------- |

### 6. State Matrix

Use:

| State ID | Page ID | Role | Record State | Data Condition | Navigation Context | UI State | Legacy Evidence | NextGen Evidence | Paired? |
| -------- | ------- | ---- | ------------ | -------------- | ------------------ | -------- | --------------- | ---------------- | ------- |

### 7. Complete Field Inventory

Use:

| Field ID | Page / State | Section | Legacy Field | NextGen Field | Type | API / DTO | Database | Surfaces | Mapping Status |
| -------- | ------------ | ------- | ------------ | ------------- | ---- | --------- | -------- | -------- | -------------- |

### 8. Field-by-Field Parity Matrix

Use:

| Field ID | Page / State | Legacy Behavior | NextGen Behavior | Label / Order | Visibility / Editability | Default | Validation | Persistence | Display | Visual Difference | Functional Difference | Defect ID | Disposition |
| -------- | ------------ | --------------- | ---------------- | ------------- | ------------------------ | ------- | ---------- | ----------- | ------- | ----------------- | --------------------- | --------- | ----------- |

### 9. Complete Button and Action Inventory

Use:

| Button ID | Page / State | Legacy Label / Icon | NextGen Label / Icon | Purpose | Preconditions | Mapping Status |
| --------- | ------------ | ------------------- | -------------------- | ------- | ------------- | -------------- |

### 10. Button-by-Button Parity Matrix

Use:

| Button ID | Page / State | Legacy State | NextGen State | Order | Visibility | Enablement | Activation | Request | Navigation | Side Effects | Failure / No-Op | Visual Difference | Functional Difference | Defect ID | Disposition |
| --------- | ------------ | ------------ | ------------- | ----- | ---------- | ---------- | ---------- | ------- | ---------- | ------------ | --------------- | ----------------- | --------------------- | --------- | ----------- |

### 11. Other Control Inventory and Parity

Use:

| Control ID | Page / State | Type | Legacy Behavior | NextGen Behavior | Visual Difference | Functional Difference | Defect ID | Disposition |
| ---------- | ------------ | ---- | --------------- | ---------------- | ----------------- | --------------------- | --------- | ----------- |

### 12. Workflow Parity Matrix

Use:

| Flow ID | Role / State | Legacy Steps and Results | NextGen Steps and Results | Fields | Buttons | Controls | Persistence | Exact Differences | Defect IDs |
| ------- | ------------ | ------------------------ | ------------------------- | ------ | ------- | -------- | ----------- | ----------------- | ---------- |

### 13. Evidence Inventory

Use:

| Evidence ID | Application | Type | Path | Page / State | Related Fields / Controls | What It Shows | Confidence | Limitations |
| ----------- | ----------- | ---- | ---- | ------------ | ------------------------- | ------------- | ---------- | ----------- |

### 14. Visual Parity Matrix

Use:

| Pair ID | Page / State | Region | Legacy Appearance | NextGen Appearance | Exact Difference | Legacy Evidence | NextGen Evidence | Diff Evidence | Defect ID |
| ------- | ------------ | ------ | ----------------- | ------------------ | ---------------- | --------------- | ---------------- | ------------- | --------- |

### 15. Legacy Anomaly Preservation Ledger

Use:

| Anomaly ID | Page / State | Field / Control | Exact Legacy Anomaly | Preconditions | Required Reproduction | Evidence | Regression Test | Explicit Exception |
| ---------- | ------------ | --------------- | -------------------- | ------------- | --------------------- | -------- | --------------- | ------------------ |

### 16. Ticket-to-Complete-Function Issue Mapping

Use:

| Issue ID | Ticket Reported? | Discovered During Full Audit? | Page / State | Field / Button / Control | Description | Defect ID | Priority |
| -------- | ---------------- | ----------------------------- | ------------ | ------------------------ | ----------- | --------- | -------- |

### 17. Root-Cause Analysis

Use:

| Defect ID | Symptoms | Root Cause | Affected Pages / Fields / Controls | Evidence | Prior Attempt Relationship | Confidence |
| --------- | -------- | ---------- | ---------------------------------- | -------- | -------------------------- | ---------- |

### 18. Confirmed Defect Inventory

Use:

| Defect ID | Category | Ticket or Audit | Current NextGen Result | Required Legacy Result | Files Likely to Change | Priority | Risk |
| --------- | -------- | --------------- | ---------------------- | ---------------------- | ---------------------- | -------- | ---- |

### 19. No-Change, Conflict, and Exception Items

Use:

| Item | Category | Legacy Result | NextGen Result | Ticket Result | Decision | Evidence |
| ---- | -------- | ------------- | -------------- | ------------- | -------- | -------- |

### 20. Dependency-Ordered Correction Plan

Use:

| Step | Defect IDs | Objective | Required Legacy Result | Proposed NextGen Change | Files Likely to Change | Dependencies | Regression Risk | Validation |
| ---- | ---------- | --------- | ---------------------- | ----------------------- | ---------------------- | ------------ | --------------- | ---------- |

The plan must avoid independent one-off fixes when several symptoms share a root cause.

### 21. Existing Test Coverage Assessment

Use:

| Field / Button / Flow / Defect | Test Level | Existing Test | Current Assertion | Legacy-Derived? | Coverage Quality | Gap | Action |
| ------------------------------ | ---------- | ------------- | ----------------- | --------------- | ---------------- | --- | ------ |

### 22. Test Traceability Matrix

Use:

| Test ID | Defect ID | Page / State | Field IDs | Button IDs | Control IDs | Flow IDs | Test Level | Required Assertions | Proposed File |
| ------- | --------- | ------------ | --------- | ---------- | ----------- | -------- | ---------- | ------------------- | ------------- |

### 23. Playwright Full-Function Parity Plan

Use:

| Test ID | Page / State | Role | Scenario | Fields Asserted | Buttons Asserted | Controls Asserted | Functional Assertions | Visual Assertion | Legacy Baseline | Fixtures |
| ------- | ------------ | ---- | -------- | --------------- | ---------------- | ----------------- | --------------------- | ---------------- | --------------- | -------- |

Every page, state, field, button, control, and workflow must map to meaningful coverage or a documented blocker.

### 24. Coverage Metrics

Report:

| Metric                           | Numerator | Denominator | Percentage | Target | Status |
| -------------------------------- | --------: | ----------: | ---------: | -----: | ------ |
| Page inventory coverage          |           |             |            |   100% |        |
| State coverage                   |           |             |            |   100% |        |
| Field inventory coverage         |           |             |            |   100% |        |
| Field behavioral parity coverage |           |             |            |   100% |        |
| Button parity coverage           |           |             |            |   100% |        |
| Other-control parity coverage    |           |             |            |   100% |        |
| Workflow parity coverage         |           |             |            |   100% |        |
| Visual-state coverage            |           |             |            |   100% |        |
| Defect regression-test coverage  |           |             |            |   100% |        |

### 25. Recommended Commands

Use only repository-supported commands.

| Command | Application | Purpose | Scope | Expected Result |
| ------- | ----------- | ------- | ----- | --------------- |

### 26. Manual Side-by-Side Verification

Use:

| Verification ID | Page / State | Preconditions | Legacy Steps | NextGen Steps | Fields to Compare | Buttons to Compare | Visual Regions | Acceptance Criteria |
| --------------- | ------------ | ------------- | ------------ | ------------- | ----------------- | ------------------ | -------------- | ------------------- |

Acceptance requires zero unexplained differences.

### 27. Regression Risks

Use:

| Risk ID | Area | Description | Likelihood | Impact | Mitigation |
| ------- | ---- | ----------- | ---------- | ------ | ---------- |

### 28. Blockers, Open Questions, and Limitations

Use:

| Item | Type | Description | Affected Coverage | Required Follow-Up |
| ---- | ---- | ----------- | ----------------- | ------------------ |

Do not use an open question to avoid recording observable legacy behavior.

## Required Execution Prompt

After completing the investigation plan, create:

```text
.github/prompts/TICKET-execution.prompt.md
```

The execution prompt must reference:

```text
docs/qa/TICKET_RootCause_CorrectionPlan.md
```

It must be populated with the actual findings from the completed plan.

It must include:

1. Ticket and input paths
2. Legacy and NextGen baselines
3. Complete function boundary
4. Prior attempt and regression ledger
5. Page and route inventory
6. State matrix
7. Complete field inventory
8. Field-by-field parity matrix
9. Complete button inventory
10. Button-by-button parity matrix
11. Other-control parity matrix
12. Workflow parity matrix
13. Legacy anomaly ledger
14. Confirmed defects
15. Dependency-ordered corrections
16. Files expected to change
17. Test traceability
18. Playwright full-function parity coverage
19. Visual baselines
20. Validation commands
21. Manual side-by-side checks
22. Completion criteria
23. Remaining limitations

## Execution Prompt Required Structure

Use:

```markdown
---
description: "Implement complete field-by-field, button-by-button, workflow, persistence, and visual parity remediation for TICKET."
---

Act as a senior full-stack engineer implementing the completed parity remediation for TICKET.

Use this investigation and correction plan as the authoritative implementation plan:

docs/qa/TICKET_RootCause_CorrectionPlan.md

## Inputs and Baselines

[Insert the actual paths, repository references, runtime URLs, roles, data, browser conditions, and comparison limitations.]

## Non-Negotiable Parity Rule

The designated legacy application is the executable specification for this task.

Implement the exact observed legacy behavior and appearance for every in-scope page, state, field, button, control, workflow, role, data condition, and visual region.

Do not implement only the individual ticket symptoms.

Do not declare completion until the entire affected function has been brought into parity.

Do not infer intended legacy behavior.

Do not replace legacy behavior with an improved, normalized, modernized, design-system-compliant, or otherwise different result.

Only the explicit approved exceptions listed in the plan may differ.

## Complete Function Boundary

[Insert the actual function boundary, routes, pages, roles, states, and exclusions.]

## Previous Attempts and Regressions

[Insert the actual prior-attempt ledger and identify changes that must be retained, revised, or reverted.]

Do not repeat a prior assumption without new supporting evidence.

## Required Field-by-Field Corrections

[Insert every field mismatch, its state, exact legacy behavior, exact NextGen behavior, required correction, affected files, and tests.]

Every field in the plan must have a final disposition.

## Required Button-by-Button Corrections

[Insert every button or action mismatch, its state, exact legacy behavior, required action, affected files, and tests.]

Every button and button-like action in the plan must have a final disposition.

## Required Other-Control Corrections

[Insert every link, tab, menu, table action, filter, sort, pagination, modal, and other control mismatch.]

## Required Workflow Corrections

[Insert every workflow mismatch, ordered user actions, intermediate states, navigation, persistence, and final outcome.]

## Required Visual Corrections

[Insert every visual mismatch and verified legacy baseline.]

Do not update a visual baseline from mismatched NextGen output.

## Legacy Anomalies That Must Be Preserved

[Insert the complete anomaly ledger.]

Do not correct or normalize an anomaly without an explicit approved exception.

## Files Expected to Change

[Insert repository-specific files, components, styles, controllers, services, APIs, DTOs, repositories, tests, fixtures, and visual baselines.]

## Required Test Implementation

[Insert the test traceability matrix.]

Tests must cover the complete affected function rather than only ticket examples.

## Required Playwright Coverage

[Insert every required Playwright scenario.]

Playwright coverage must validate:

- Every field
- Every button
- Every interactive control
- Every material state
- Every workflow
- Persistence
- Navigation
- Validation
- Role behavior
- Visual parity

Do not create page-load-only tests.

## Required Visual Baselines

[Insert verified legacy baseline sources and comparison conditions.]

Do not increase tolerances, mask in-scope differences, crop mismatches, or regenerate expected images from a mismatched NextGen result.

## Validation Commands

[Insert repository-supported commands.]

## Manual Side-by-Side Verification

[Insert page-by-page, field-by-field, button-by-button manual verification steps.]

## Constraints

- Implement the complete plan, not only ticket symptoms.
- Do not leave a discovered field, button, control, state, workflow, or visual mismatch unresolved.
- Do not make unrelated changes.
- Do not change the legacy application.
- Do not weaken tests.
- Do not remove exact assertions.
- Do not hide differences with screenshot tolerance or masking.
- Do not introduce NextGen-only controls or behavior without an explicit exception.
- Do not omit a legacy field or action because it appears obsolete.
- Do not repeat previous failed fixes without addressing their root-cause shortcomings.
- Preserve unrelated working-tree changes.
- Document any blocked item.

## Completion Criteria

Implementation is complete only when:

1. Every page in the function has a disposition.
2. Every material state has a disposition.
3. Every field has been compared and corrected or explicitly excepted.
4. Every button has been compared and corrected or explicitly excepted.
5. Every other interactive control has been compared and corrected or explicitly excepted.
6. Every workflow has been compared and corrected or explicitly excepted.
7. Field order, labels, defaults, validation, persistence, and display match legacy.
8. Button labels, order, visibility, enablement, actions, navigation, and side effects match legacy.
9. Role-specific and record-state-specific behavior matches legacy.
10. Empty, loading, validation, success, and error states match legacy.
11. Every recorded legacy anomaly is reproduced or explicitly excepted.
12. Visual comparisons show zero unexplained differences.
13. Every confirmed defect has regression coverage.
14. Full-function Playwright regression passes.
15. Targeted unit and integration tests pass.
16. Full relevant regression suites pass.
17. Previous attempt regressions are corrected.
18. No new complete-function regression is introduced.
19. No unexplained or unapproved mismatch remains.

## Final Response Required

After implementation, report:

1. Ticket defects fixed
2. Additional complete-function defects fixed
3. Previous failed changes revised or reverted
4. Fields compared and corrected
5. Buttons compared and corrected
6. Other controls compared and corrected
7. Workflows compared and corrected
8. Legacy anomalies reproduced
9. Visual differences corrected
10. Files changed
11. Tests added or updated
12. Playwright scenarios added or updated
13. Visual baselines used
14. Commands run and results
15. Manual parity checks
16. Remaining blockers
17. Remaining explicit exceptions
18. Final coverage metrics
```

## Final Response Required From the Investigation

After creating the plan and execution prompt, report:

1. Ticket
2. QA report path
3. Associated documents reviewed
4. Legacy repository and reference
5. NextGen repository and reference
6. Runtime environments
7. Complete function boundary
8. Previous repair attempts
9. Regressions introduced by previous attempts
10. Page and state counts
11. Field count
12. Button count
13. Other-control count
14. Workflow count
15. Legacy anomaly count
16. Ticket-reported defects
17. Additional complete-function defects
18. Root causes
19. Field-by-field parity summary
20. Button-by-button parity summary
21. Workflow parity summary
22. Visual parity summary
23. Existing test coverage
24. Planned unit and integration coverage
25. Planned Cucumber coverage
26. Planned Playwright coverage
27. Planned visual coverage
28. Coverage metrics
29. Correction-plan path
30. Execution-prompt path
31. Recommended commands
32. Open blockers and limitations

## Constraints

- Do not make application changes during investigation.
- Do not make test changes during investigation.
- Do not modify application configuration during investigation.
- Do not modify database schema or data during investigation.
- Do not modify the legacy application.
- Do not limit the analysis to ticket-named controls.
- Do not stop after reproducing the ticket.
- Do not omit fields or buttons without a disposition.
- Do not assume existing tests are correct.
- Do not assume previous diagnoses are correct.
- Do not accept page-load-only testing.
- Do not accept visual similarity without exact comparison.
- Do not classify a stable visible difference as minor.
- Do not update baselines from mismatched NextGen output.
- Do not hide mismatches with masks or tolerances.
- Do not invent legacy behavior.
- Do not invent routes, fields, buttons, tests, or commands.
- Clearly distinguish confirmed evidence from inference.
- Clearly document unavailable evidence and its effect on confidence.
- Preserve the distinction between ticket issues and additional full-function parity defects.

## Quality Bar

This task is complete only when:

- Required inputs have been validated.
- The complete function boundary has been established.
- Previous attempts have been reviewed.
- Regressions from previous attempts have been identified.
- Every route and page has been inventoried.
- Every material state has been inventoried.
- Every field has been inventoried.
- Every button and button-like action has been inventoried.
- Every other interactive control has been inventoried.
- Every workflow has been inventoried.
- Every legacy item has been paired with NextGen or recorded as missing.
- Every NextGen-only item has been recorded.
- Every field has been compared for appearance, state, validation, persistence, and display.
- Every button has been compared for appearance, state, activation, navigation, and side effects.
- Every workflow has been compared from entry through final persisted state.
- Every material visual state has legacy and NextGen evidence.
- Every discovered difference has been classified.
- Every confirmed defect has a root cause or supported root-cause candidate.
- Every confirmed defect has a correction step.
- Every confirmed defect has a regression-test plan.
- Every legacy anomaly has a disposition.
- Every inventory and coverage metric has been calculated.
- The execution prompt is populated from actual findings.
- No recommendation is merely a ticket-only patch.
- No unexplained or unauthorized complete-function parity difference remains omitted from the plan.
