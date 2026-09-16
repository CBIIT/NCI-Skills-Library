---
name: hello-world-web-app
description: Creates a minimal, compliant hello-world web application in a supported NCI stack. Use this skill when the user wants a fresh web app scaffold, a local hello-world starting point, or a simple baseline to adjust before deeper development.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, Python, JavaScript, HTML
Framework: Flask, FastAPI, Express, Node.js, AWS Lambda
---

# Hello World Web App Skill

Creates a minimal, runnable web app for NCI work. The goal is a small starting point that can be verified locally, registered, and then evolved into a real app.

## Purpose

Use this skill when the user asks for:

- a hello world web application
- a starter app for a new project
- a minimal local baseline before more development
- a web app scaffold that follows NCI startup and registry requirements

## Supported Initial Scope

This skill supports:

- local web app execution
- AWS Lambda / managed-service deployment patterns for later follow-on work

This skill does not yet target:

- ServiceNow
- Snowflake
- Power Platform

## Inputs

- app name
- desired runtime and framework
- local or AWS Lambda target
- project directory
- whether the repo is fresh or existing
- optional NCI constraints or security notes

## Output

Return:

1. a minimal web app scaffold
2. a run command for local execution
3. a smoke-test validation result
4. the project summary and next steps
5. any runtime or environment prerequisites that must be installed first

## Required Guardrails

- Do not use secrets or credentials in the app.
- Do not invent production settings or cloud config.
- If the chosen runtime is not installed, tell the user before continuing.
- If the user chooses Python and Python is not installed, install it first or ask for permission to install it.
- Keep the implementation small and intentionally minimal.
- Do not over-engineer beyond a hello-world baseline.

## Workflow

1. Confirm the app name, language, and target environment.
2. Check whether the selected runtime is installed.
3. If a required runtime is missing, tell the user and offer installation before continuing.
4. Create the minimal web app structure.
5. Use the simplest working implementation for the selected stack.
6. Build a polished but intentionally simple hello-world landing page with a clean NCI-inspired layout.
7. Include standard metadata variables such as program name, author, and published date in the page.
8. Add a simple run command and a smoke-test verification step.
9. Summarize how to run it locally and what to do next.
10. If the app is targeted for AWS Lambda or managed services, keep the code compatible with a later deploy step without making the initial app overly complex.

## Page Design Requirements

The generated page must look simple, professional, and NCI-aligned. It should include:

- a compact header bar with the official NCI logo on the left
- the app/program name or application label immediately to the right of the logo
- a clean central message area that says Hello, World
- a short summary line or subtitle describing the app
- a footer with basic metadata, including at minimum:
  - Program name
  - Author
  - Date published
  - Version or status
  - Environment label such as Local or Dev

Use neutral colors, clear spacing, and a tidy layout. Avoid heavy branding, excessive animation, or complex styling.

## Header Requirement

The header should use the official NCI logo and follow the NCI Design System pattern. The logo should use the approved logo asset and should link to the NCI homepage or a relevant landing page.

Use the official NCI logo URL:

`https://www.cancer.gov/profiles/custom/cgov_site/themes/custom/cgov/static/images/design-elements/logos/nci-logo-full.svg`

A simple HTML/CSS structure should look like this:

```html
<header class="nci-header">
  <div class="nci-header__brand">
    <a href="https://www.cancer.gov" aria-label="National Cancer Institute home page">
      <img src="https://www.cancer.gov/profiles/custom/cgov_site/themes/custom/cgov/static/images/design-elements/logos/nci-logo-full.svg" alt="National Cancer Institute" />
    </a>
  </div>
  <div class="nci-header__title">
    <span>Program Name</span>
  </div>
</header>
```

```css
.nci-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #ffffff;
  border-bottom: 1px solid #dfe3e8;
  padding: 0.75rem 1.5rem;
}

.nci-header__brand img {
  display: block;
  height: 48px;
  width: auto;
}

.nci-header__title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #1a1a1a;
}
```

This keeps the header simple, professional, and aligned with the NCI design system while preserving the app name as the main label.

## Footer Requirement

The footer should closely match the official NCI government footer pattern shown in the standard design system, using:

- a solid dark blue background
- white text for all links and labels
- evenly spaced horizontal navigation links
- a centered NIH tagline line such as: "NIH ... Turning Discovery Into Health®"
- concise links such as Home, Policies, Accessibility, Viewing Files, FOIA, HHS, NIH, NCI, and USA.gov

A simple HTML/CSS structure should look like this:

```html
<footer class="nci-footer">
  <div class="nci-footer__links">
    <a href="#">Home</a>
    <span>|</span>
    <a href="#">Policies</a>
    <span>|</span>
    <a href="#">HHS Vulnerability Disclosure</a>
    <span>|</span>
    <a href="#">Accessibility</a>
    <span>|</span>
    <a href="#">Viewing Files</a>
    <span>|</span>
    <a href="#">FOIA</a>
  </div>
  <div class="nci-footer__orgs">
    <a href="#">U.S. Department of Health and Human Services</a>
    <span>|</span>
    <a href="#">National Institutes of Health</a>
    <span>|</span>
    <a href="#">National Cancer Institute</a>
    <span>|</span>
    <a href="#">USA.gov</a>
  </div>
  <div class="nci-footer__tagline">NIH ... Turning Discovery Into Health®</div>
</footer>
```

```css
.nci-footer {
  background: #0f6a9c;
  color: #ffffff;
  text-align: center;
  padding: 1.5rem 2rem 2rem;
  font-family: Arial, sans-serif;
}

.nci-footer__links,
.nci-footer__orgs {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.nci-footer a {
  color: #ffffff;
  text-decoration: none;
  font-weight: 600;
}

.nci-footer__tagline {
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}
```

Keep the footer minimal and readable; do not add heavy decoration or custom branding beyond the official style pattern.

## Metadata Variables

Use these standard variables in the rendered page when available:

- `program_name`
- `author_name`
- `published_date`
- `version`
- `environment`
- `description`

If the user did not supply one of these, use a sensible default and note it in the generated summary.

## Default Implementation Guidance

### Python

Use the simplest reliable web app for local execution, typically:

- Flask for a lightweight web app
- FastAPI if a more modern API-first baseline is preferred

### Node.js

Use:

- Express for a minimal web server

### .NET

Use:

- ASP.NET Core minimal app

### Other languages

Use the simplest minimal framework consistent with the user's choice and the supported NCI startup flow.

## Example Result

The generated app should produce a polished page with a layout similar to:

- Header: Program Name
- Main section: Hello, World
- Subtitle: A minimal NCI web application starter
- Footer: Author | Published Date | Version | Environment

The page should include:

- a local run command
- a quick verification step
- a README snippet with usage notes
- standard metadata variables visible on the page

## Startup Invocation

When the startup flow determines the user wants a web app, invoke this skill to create the minimal starting point. After the app is built and verified locally, continue with NCI Skills Registry registration and optional AWS dev deployment if requested.
