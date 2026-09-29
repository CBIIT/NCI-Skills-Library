---
version: 1.0
name: github-mcp-actions
description: Use this skill when the user wants to perform actions directly on GitHub (issues, pull requests, comments, reviews, branches, labels, releases, workflow runs, repo settings) through a connected GitHub MCP server, instead of shelling out to `git`/`gh`. Covers discovering available GitHub MCP tools, choosing the right tool for the action, required confirmation gates for write/destructive operations, and NCI security guardrails. Trigger this skill whenever the user asks to open/comment/close/merge an issue or PR, create a branch or release, trigger a workflow, or otherwise "do something on GitHub" and a GitHub MCP server is available.
---

# GitHub MCP Server Actions Skill

Performs GitHub actions (read and write) through a connected GitHub MCP server rather than raw `git`/`gh` shell commands, when that server is available in the current session.

## Purpose

Give the agent a consistent, safe way to use GitHub MCP tools to:

- read issues, PRs, files, commits, workflow runs, and repo metadata
- create or update issues, PR comments, reviews, labels, branches, and releases
- trigger or inspect GitHub Actions workflow runs
- manage repo settings that the connected token is authorized for

## When to Use

Use this skill when:

- a GitHub MCP server is connected in the current session and the task is a GitHub action (not a local git operation)
- the user asks to open, comment on, label, close, or merge an issue or PR
- the user asks to create a branch, tag, or release on GitHub
- the user asks to trigger, cancel, or check a GitHub Actions workflow run
- the user asks to search GitHub issues/PRs/code across a repo or org

Do not use this skill when:

- no GitHub MCP server is connected — fall back to `gh`/`git` CLI commands instead
- the task is purely local (local commits, local branches, local file edits) with no GitHub-side effect
- the action requires credentials or scopes broader than what the connected server/token grants — stop and tell the user instead of trying to work around it

## Discover Available Tools First

GitHub MCP tool names and toolsets vary by server configuration (e.g., a hosted server may expose a different tool set than a self-hosted one, and toolsets like `issues`, `pull_requests`, `actions`, `repos` may be enabled or disabled independently). Before acting:

1. Use `tool_search` (or the equivalent tool-discovery mechanism) to find the currently loaded GitHub MCP tools — do not assume a fixed tool name exists.
2. If the needed capability isn't available, tell the user which toolset appears to be missing (e.g., "the `actions` toolset isn't enabled on this GitHub MCP server") rather than guessing at a tool name or silently switching to `gh`.
3. Prefer the MCP tool over an equivalent `gh`/`git` shell command whenever both are available and the MCP tool covers the need, so the action is auditable through the MCP session.

## Required Inputs

Collect or infer from context before calling a tool:

- target repository as `<owner>/<repo>`
- the specific object being acted on (issue/PR number, branch name, workflow file or run ID, release tag)
- the exact action (read vs. create vs. update vs. close/merge vs. delete)
- any content required for the action (issue/PR body, comment text, labels, review verdict)

Never fabricate a repository, issue number, PR number, or run ID. If it cannot be resolved from context, ask the user.

## Guardrails

- **Read actions are low-risk and can proceed without confirmation**: viewing issues/PRs, listing workflow runs, reading files, searching code.
- **Write actions that are easily reversible** (opening an issue, adding a label, posting a draft PR) may proceed once the required inputs are confirmed, but summarize what will be created before calling the tool.
- **Actions that are hard to reverse or affect shared state require explicit user confirmation before calling the tool**, including: commenting on an issue/PR, merging or closing a PR, closing an issue, deleting a branch or tag, creating or publishing a release, dismissing a review, force-pushing, or changing repo settings/permissions.
- Never use a GitHub MCP tool to bypass branch protection, required reviews, or status checks. If a write action is blocked by a repo rule, report the block — do not look for a workaround.
- Never print, log, or commit tokens, secrets, or credentials used by the MCP server connection.
- Treat rate-limit or permission-denied errors as a stop condition: report the exact error to the user rather than retrying with broader scopes or a different auth path.
- If the requested action would affect a repo outside the one the user is currently working in, confirm the target repo explicitly before proceeding.

## Workflow

1. Confirm the target repository and the exact object/action requested.
2. Discover the relevant GitHub MCP tool(s) for that action (see [Discover Available Tools First](#discover-available-tools-first)).
3. For a read action, call the tool and return the result.
4. For a write action, state clearly what will be created/changed and where, then apply the guardrail above: proceed directly for easily-reversible actions, or get explicit confirmation first for hard-to-reverse ones.
5. Call the tool with the confirmed inputs.
6. Report the result with a link to the affected GitHub object (issue/PR/release/run URL) and a one-line summary of what changed.
7. If the tool call fails, report the exact error and do not retry with elevated scope or a different credential path.

## Common Recipes

- **Open an issue**: confirm repo, title, and body → create → return the issue URL.
- **Comment on an issue or PR**: confirm repo, number, and exact comment text → get confirmation (comments are visible to others) → post → return the comment URL.
- **Review a PR**: read the diff/files via MCP tools, produce findings, then confirm before submitting a formal "approve"/"request changes"/"comment" review.
- **Merge a PR**: confirm the PR is approved and checks are green, get explicit user confirmation, then merge using the method (merge/squash/rebase) the user specifies.
- **Create a branch**: confirm repo and base branch, then create.
- **Trigger a workflow run**: confirm the workflow file, ref, and inputs, then dispatch; poll run status without an interactive log viewer.
- **Create a release**: confirm repo, tag, target commit/branch, and release notes, get explicit confirmation, then publish.

## Output

Return:

1. the action taken (or the read result)
2. a direct link to the affected GitHub object
3. any guardrail that blocked the action and why
4. next-step suggestions when relevant (e.g., "PR is open, want me to request a reviewer?")

## Quality Checklist

- [ ] Correct repository and object confirmed before acting
- [ ] Used a GitHub MCP tool discovered via tool search, not a guessed tool name
- [ ] Hard-to-reverse actions were confirmed with the user before execution
- [ ] No secrets, tokens, or credentials appear in the output
- [ ] Result includes a link to the affected GitHub object
