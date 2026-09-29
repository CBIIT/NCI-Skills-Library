---
name: hello-world-api
description: Creates a minimal, compliant hello-world REST API in a supported NCI stack. Use this skill when the user wants a fresh REST API scaffold, a local hello-world starting point, or a simple baseline to adjust before deeper development.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, Python, JavaScript
Framework: Flask, Express, Node.js, AWS Lambda
---

# Hello World API Skill

Creates a minimal, runnable REST API for NCI work. The goal is a small starting point that can be verified locally, registered, and then evolved into a real API.

## Purpose

Use this skill when the user asks for:

- a hello world REST API
- a starter API for a new project
- a minimal local baseline before more development
- a REST API scaffold that follows NCI startup and registry requirements

## Supported Initial Scope

This skill supports:

- local REST API execution
- AWS Lambda / managed-service deployment patterns for later follow-on work

GitHub Pages does not apply to a REST API because it only hosts static content. If the user selected GitHub Pages as the target for a REST API, tell them GitHub Pages cannot host a REST API and confirm local or AWS Lambda / managed service instead.

This skill does not yet target:

- ServiceNow
- Snowflake
- Power Platform

## Inputs

- app name
- desired runtime or language
- local or AWS target
- project directory derived from the project name
- whether the repo is fresh or existing
- optional NCI constraints or security notes

## Output

Return:

1. a minimal REST API scaffold
2. a run command for local execution
3. a smoke-test validation result
4. the project summary and next steps
5. any runtime or environment prerequisites that must be installed first

## Required Guardrails

- Do not use secrets or credentials in the API.
- Do not invent production settings or cloud config.
- If the chosen runtime is not installed, tell the user before continuing.
- If the user chooses Python and Python is not installed, install it first or ask for permission to install it.
- For a Python Hello World API, use Flask automatically. Do not ask the user to choose a Python framework.
- For a Node.js Hello World API, use Express automatically.
- Keep the implementation small and intentionally minimal.
- Do not over-engineer beyond a hello-world baseline.

## Workflow

1. Confirm the app name, language, and target environment. If the language is Python, select Flask automatically.
2. Check whether the selected runtime is installed.
3. If a required runtime is missing, tell the user and offer installation before continuing.
4. Create the minimal REST API structure.
5. Use the simplest working implementation for the selected stack.
6. Expose a `GET /` root route returning a JSON payload with a `message` field of `Hello, World` plus the standard metadata variables, and a `GET /health` route returning HTTP 200 with a JSON status payload.
7. Add a simple run command and a smoke-test verification step.
8. Start the local HTTP server as part of this workflow; do not only tell the user how to start it. Keep the server running for testing.
9. Verify both routes locally with `curl` (or an equivalent HTTP request) and confirm the root route returns the expected JSON body and the health route returns HTTP 200 before reporting success.
10. After the user explicitly confirms the local response, summarize the running URL and what to do next, and allow the deployment phase to begin.
11. If the app is targeted for AWS Lambda or managed services, keep the code compatible with a later deploy step without making the initial API overly complex.

## Metadata Variables

Include these standard variables in the root route's JSON response when available:

- `program_name`
- `author_name`
- `published_date`
- `version`
- `environment`
- `description`

If the user did not supply one of these, use a sensible default and note it in the generated summary.

## Default Implementation Guidance

### Python

Use Flask for a lightweight REST API:

```python
from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def hello_world():
    return jsonify(
        message="Hello, World",
        program_name="hello-world-api",
        author_name="CBIIT",
        version="0.1.0",
        environment="local",
    )


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


if __name__ == "__main__":
    app.run(debug=False)
```

Run locally with:

```bash
python app.py
```

Verify with:

```bash
curl -sf http://localhost:5000/ | head -c 500
curl -sf http://localhost:5000/health
```

### Node.js

Use Express for a minimal REST API:

```javascript
import express from "express";

const app = express();

app.get("/", (req, res) => {
  res.json({
    message: "Hello, World",
    program_name: "hello-world-api",
    author_name: "CBIIT",
    version: "0.1.0",
    environment: "local",
  });
});

app.get("/health", (req, res) => {
  res.status(200).json({ status: "ok" });
});

app.listen(3000);
```

Run locally with:

```bash
node server.js
```

Verify with:

```bash
curl -sf http://localhost:3000/ | head -c 500
curl -sf http://localhost:3000/health
```

### Other languages

Use the simplest minimal web framework consistent with the user's choice and the supported NCI startup flow.

## Example Result

The generated API should expose:

- `GET /` returning a JSON greeting with metadata variables
- `GET /health` returning HTTP 200 with a status payload

The result should include:

- a local run command
- a quick verification step (curl output for both routes)
- a README snippet with usage notes
- standard metadata variables visible in the root route response

## Startup Invocation

When the startup flow determines the user wants a REST API Interface, invoke this skill to create the minimal starting point. After the API is built and verified locally, continue with NCI Skills Registry registration and optional AWS dev deployment if requested.
