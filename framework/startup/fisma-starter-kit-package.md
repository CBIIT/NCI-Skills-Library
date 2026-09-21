---
name: fisma-starter-kit-package
description: Creates a draft FISMA Starter Kit helper package for generated NCI applications, especially Cloud One managed-service targets. Use after local verification and before Cloud One deployment.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown
Framework: NCI Skills Library
---

# FISMA Starter Kit Package

Create a draft `ato/fisma-starter-kit/` package for generated applications that need early RMF Step 1 and 2 support.

This package supports, but does not replace, the official NCI FISMA Starter Kit templates. Official reference files live in `reference/nci-fisma-starter-kit/`.

## When To Use

Use this package when:

- The generated app targets Cloud One Development.
- The user asks for ATO, FISMA, security, privacy, or compliance starter materials.
- The app will process NIH/NCI user identity, program data, sensitive data, or authenticated workflows.

Do not generate this package by default for local-only apps unless the user asks for ATO preparation.

## Output Structure

Create these files in the generated application repository:

```text
ato/fisma-starter-kit/
  README.md
  fips-199-system-categorization.md
  business-impact-analysis.md
  privacy-impact-assessment.md
  e-authentication-risk-assessment.md
  source-notes.md
```

## Source Helpers

Use these framework helpers as the source pattern:

- `framework/governance/fisma-starter-kit/fips-199-system-categorization-helper.md`
- `framework/governance/fisma-starter-kit/business-impact-analysis-helper.md`
- `framework/governance/fisma-starter-kit/privacy-impact-assessment-helper.md`
- `framework/governance/fisma-starter-kit/e-authentication-risk-assessment-helper.md`

## Populate From Known Context

Use known startup, registry, GitHub, and Cloud One deployment context before asking follow-up questions.

Known values often include:

- project name
- project slug
- application type
- runtime language
- local verification URL
- target environment
- GitHub repository
- registry status
- NCI Owner
- NCI DOC
- author/user
- NIH email when reliably discovered
- Cloud One region
- CloudFormation stack name
- GitHub Actions workflow name
- deployment endpoint after deployment

Ask follow-up questions only for required fields that cannot be inferred.

## Minimum Generated Content

Every generated FISMA Starter Kit helper file must include:

- source official template name
- generated date
- project name
- known context values
- open questions
- assumptions
- owner/security review checklist
- clear notice that the file is a draft helper, not the official completed form

## Timing

For Cloud One targets:

1. Build and show the local Hello World app.
2. Obtain user confirmation that the local page or API works.
3. Generate the FISMA Starter Kit helper package.
4. Continue to GitHub check-in and Cloud One deployment.
5. Update the package with deployment evidence after Cloud One smoke tests pass.

## Guardrails

- Do not invent impact levels, recovery objectives, data classifications, or privacy conclusions.
- Use draft suggestions only when they are clearly labeled as needing owner/security review.
- Do not claim ATO approval.
- Do not copy official template language beyond short labels and field names needed for interoperability.
- Do not store secrets, access keys, tokens, or sensitive credentials in the package.
