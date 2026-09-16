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
6. Build a tiny landing page or response that clearly says Hello, World.
7. Add a simple run command and a smoke-test verification step.
8. Summarize how to run it locally and what to do next.
9. If the app is targeted for AWS Lambda or managed services, keep the code compatible with a later deploy step without making the initial app overly complex.

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

The generated app should produce a page or response like:

Hello, World

and include:

- a local run command
- a quick verification step
- a README snippet with usage notes

## Startup Invocation

When the startup flow determines the user wants a web app, invoke this skill to create the minimal starting point. After the app is built and verified locally, continue with NCI Skills Registry registration and optional AWS dev deployment if requested.
