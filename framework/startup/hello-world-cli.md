---
name: hello-world-cli
description: Creates a minimal, compliant hello-world local command line script in a supported NCI stack. Use this skill when the user wants a fresh CLI script scaffold, a local hello-world starting point, or a simple baseline to adjust before deeper development.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, Python, JavaScript
Framework: None required
---

# Hello World CLI Script Skill

Creates a minimal, runnable local command line script for NCI work. The goal is a small starting point that can be verified locally and then evolved into a real script.

## Purpose

Use this skill when the user asks for:

- a hello world command line script
- a starter CLI script for a new project
- a minimal local baseline before more development
- a CLI scaffold that follows NCI startup requirements

## Supported Initial Scope

This skill supports:

- local script execution only

GitHub Pages and AWS Lambda / managed service do not apply to a local command line script. If the user selected either target for a Local Command Line Script, tell them those targets do not apply and confirm local execution instead. Skip NCI Skills Registry registration and any cloud deployment phase for this app type.

This skill does not yet target:

- ServiceNow
- Snowflake
- Power Platform

## Inputs

- app name
- desired runtime or language
- project directory derived from the project name
- whether the repo is fresh or existing
- optional NCI constraints or security notes

## Output

Return:

1. a minimal CLI script scaffold
2. a run command for local execution
3. a smoke-test validation result
4. the project summary and next steps
5. any runtime or environment prerequisites that must be installed first

## Required Guardrails

- Do not use secrets or credentials in the script.
- Do not invent production settings or configuration.
- If the chosen runtime is not installed, tell the user before continuing.
- If the user chooses Python and Python is not installed, install it first or ask for permission to install it.
- Keep the implementation small and intentionally minimal: one script, no external dependencies.
- Do not over-engineer beyond a hello-world baseline.

## Workflow

1. Confirm the app name and language.
2. Check whether the selected runtime is installed.
3. If a required runtime is missing, tell the user and offer installation before continuing.
4. Create the minimal script structure.
5. Use the simplest working implementation for the selected language.
6. Print `Hello, World` to stdout along with the standard metadata variables.
7. Add a simple run command and a smoke-test verification step.
8. Run the script as part of this workflow; do not only tell the user how to run it.
9. Verify the script's stdout contains the expected greeting and metadata before reporting success.
10. After the user explicitly confirms the output, summarize the run command and what to do next.

## Metadata Variables

Include these standard variables in the script's printed output when available:

- `program_name`
- `author_name`
- `published_date`
- `version`
- `environment`
- `description`

If the user did not supply one of these, use a sensible default and note it in the generated summary.

## Default Implementation Guidance

### Python

```python
def main():
    print("Hello, World")
    print("program_name: hello-world-cli")
    print("author_name: CBIIT")
    print("version: 0.1.0")
    print("environment: local")


if __name__ == "__main__":
    main()
```

Run locally with:

```bash
python hello.py
```

### Node.js

```javascript
console.log("Hello, World");
console.log("program_name: hello-world-cli");
console.log("author_name: CBIIT");
console.log("version: 0.1.0");
console.log("environment: local");
```

Run locally with:

```bash
node hello.js
```

### Other languages

Use the simplest minimal implementation consistent with the user's choice and the supported NCI startup flow.

## Example Result

The generated script should print:

- `Hello, World`
- the available metadata variables

The result should include:

- a local run command
- a quick verification step (script output)
- a README snippet with usage notes

## Startup Invocation

When the startup flow determines the user wants a Local Command Line Script, invoke this skill to create the minimal starting point. This app type is local-only: skip NCI Skills Registry registration and cloud deployment once the script is built and verified locally.
