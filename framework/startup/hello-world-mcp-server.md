---
name: hello-world-mcp-server
description: Creates a minimal, compliant hello-world MCP (Model Context Protocol) server in a supported NCI stack. Use this skill when the user wants a fresh MCP server scaffold, a local hello-world starting point, or a simple baseline to adjust before deeper development.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, Python, JavaScript
Framework: MCP Python SDK, MCP TypeScript SDK, AWS Lambda
---

# Hello World MCP Server Skill

Creates a minimal, runnable MCP server for NCI work. The goal is a small starting point that can be verified locally, registered, and then evolved into a real MCP server.

## Purpose

Use this skill when the user asks for:

- a hello world MCP server
- a starter MCP server for a new project
- a minimal local baseline before more development
- an MCP server scaffold that follows NCI startup and registry requirements

## Supported Initial Scope

This skill supports:

- local MCP server execution over stdio transport
- AWS Lambda / managed-service deployment patterns for later follow-on work, using a streamable HTTP transport

GitHub Pages does not apply to MCP servers because it only hosts static content. If the user selected GitHub Pages as the target for an MCP server, tell them GitHub Pages cannot host an MCP server and confirm local or AWS Lambda / managed service instead.

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

1. a minimal MCP server scaffold
2. a run command for local execution
3. a smoke-test validation result
4. the project summary and next steps
5. any runtime or environment prerequisites that must be installed first

## Required Guardrails

- Do not use secrets or credentials in the server.
- Do not invent production settings or cloud config.
- If the chosen runtime is not installed, tell the user before continuing.
- If the user chooses Python and Python is not installed, install it first or ask for permission to install it.
- For a Python Hello World MCP server, use the official MCP Python SDK (`mcp`) automatically. Do not ask the user to choose a different Python MCP framework.
- For a Node.js Hello World MCP server, use the official MCP TypeScript SDK (`@modelcontextprotocol/sdk`) automatically.
- Keep the implementation small and intentionally minimal: one server exposing exactly one tool.
- Do not over-engineer beyond a hello-world baseline.

## Workflow

1. Confirm the app name, language, and target environment.
2. Check whether the selected runtime is installed.
3. If a required runtime is missing, tell the user and offer installation before continuing.
4. Create the minimal MCP server structure.
5. Use the simplest working implementation for the selected stack.
6. Expose exactly one tool named `hello_world` that accepts no required arguments and returns the text `Hello, World` along with the standard metadata variables.
7. Include standard metadata variables such as program name, author, and published date in the tool's response or in server startup logging.
8. Add a simple run command and a smoke-test verification step.
9. Start the local MCP server as part of this workflow; do not only tell the user how to start it. Keep the server running for testing.
10. Verify the server locally by invoking the `hello_world` tool with an MCP-compatible client, or by using the SDK's built-in inspector/dev tool, and confirm the response text and metadata are present before reporting success.
11. After the user explicitly confirms the local tool response, summarize the running command and what to do next, and allow the deployment phase to begin.
12. If the app is targeted for AWS Lambda or managed services, keep the code compatible with a later deploy step (streamable HTTP transport instead of stdio) without making the initial server overly complex.

## Metadata Variables

Include these standard variables in the `hello_world` tool response or startup log when available:

- `program_name`
- `author_name`
- `published_date`
- `version`
- `environment`
- `description`

If the user did not supply one of these, use a sensible default and note it in the generated summary.

## Default Implementation Guidance

### Python

Use the official MCP Python SDK (`mcp`) with the `FastMCP` server helper:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("hello-world-mcp-server")


@mcp.tool()
def hello_world() -> str:
    """Return a minimal Hello, World greeting with app metadata."""
    return "Hello, World from hello-world-mcp-server (Python)"


if __name__ == "__main__":
    mcp.run()
```

Run locally over stdio with:

```bash
python server.py
```

### Node.js

Use the official MCP TypeScript SDK (`@modelcontextprotocol/sdk`):

```javascript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({ name: "hello-world-mcp-server", version: "1.0.0" });

server.tool("hello_world", {}, async () => ({
  content: [{ type: "text", text: "Hello, World from hello-world-mcp-server (Node.js)" }],
}));

const transport = new StdioServerTransport();
await server.connect(transport);
```

Run locally with:

```bash
node server.js
```

### Other languages

Use the simplest minimal MCP SDK consistent with the user's choice and the supported NCI startup flow. If no official SDK exists for the requested language, tell the user before continuing and agree on a supported alternative.

## Example Result

The generated server should expose:

- one tool: `hello_world`
- a response containing the greeting text and available metadata variables (program name, author, published date, version, environment)

The result should include:

- a local run command
- a quick verification step (tool invocation and expected response)
- a README snippet with usage notes
- standard metadata variables visible in the tool response or startup log

## Startup Invocation

When the startup flow determines the user wants an MCP server, invoke this skill to create the minimal starting point. After the server is built and verified locally, continue with NCI Skills Registry registration and optional AWS dev deployment if requested.
