---
version: 1.1
name: github-mcp-actions
description: Use this skill when the user wants to perform actions directly on GitHub (issues, pull requests, comments, reviews, branches, labels, releases, workflow runs, repo settings, repository OIDC configuration) through a connected GitHub MCP server, instead of shelling out to `git`/`gh`. Covers discovering available GitHub MCP tools, choosing the right tool for the action, required confirmation gates for write/destructive operations, and NCI security guardrails. Trigger this skill whenever the user asks to open/comment/close/merge an issue or PR, create a branch or release, trigger a workflow, or otherwise "do something on GitHub" and a GitHub MCP server is available.
---

# GitHub MCP Server Actions Skill

Performs GitHub actions (read and write) through a connected GitHub MCP server rather than raw `git`/`gh` shell commands, when that server is available in the current session.

## Purpose

Give the agent a consistent, safe way to use GitHub MCP tools to:

- read issues, PRs, files, commits, workflow runs, repo metadata, and repository OIDC subject customization
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
- the user or another deployment skill needs the exact repository OIDC subject customization used for federated authentication

Do not use this skill when:

- no GitHub MCP server is connected — fall back to `gh`/`git` CLI commands instead
- the task is purely local (local commits, local branches, local file edits) with no GitHub-side effect
- the action requires credentials or scopes broader than what the connected server/token grants — stop and tell the user instead of trying to work around it

## Discover Available Tools First

GitHub MCP tool names and toolsets vary by server configuration (e.g., a hosted server may expose a different tool set than a self-hosted one, and toolsets like `issues`, `pull_requests`, `actions`, `repos` may be enabled or disabled independently). Before acting:

1. Use `tool_search` or the environment's complete callable-tool inventory to find every currently loaded GitHub MCP tool. Inspect deferred tools as well as tools shown in the initial prompt; do not treat an abbreviated initial tool list as proof that no GitHub MCP server is connected.
2. When available, call the tools equivalent to `github_list_installed_accounts` and `github_list_installations`. Record the visible organizations, whether each installation covers all or selected repositories, and whether the relevant account is present.
3. Call the repository-read tool equivalent to `github_get_repo` for every existing target repository. For startup registration, probe `CBIIT/NCI-Skills-Registry` before reading or updating it.
4. Build the capability matrix described below before performing the first GitHub-side action.
5. If a needed capability is unavailable, identify the missing toolset (for example, repository creation, Actions dispatch, environments, variables, or secrets) instead of guessing a tool name or silently switching to CLI.
6. Prefer MCP over equivalent `gh`, `git`, or raw HTTP operations whenever MCP covers the action and has verified target access.

## Required Preflight Capability Matrix

Before the first GitHub-side action, report a compact matrix with one row per planned operation:

| Operation | MCP capability available | Repository access verified | Allowed mechanism |
|---|---:|---:|---|
| Read or update registry | Yes/No | Yes/No | MCP or pending acknowledgment |
| Create or inspect app repository | Yes/No | Yes/No/Not yet created | MCP or pending acknowledgment |
| Configure environments, variables, or secrets | Yes/No | Yes/No | MCP or pending acknowledgment |
| Dispatch or inspect workflows | Yes/No | Yes/No | MCP or pending acknowledgment |
| Read repository OIDC subject customization | Yes/No | Yes/No | MCP or pending acknowledgment |

Adapt the rows to the actual plan. A connected server is not sufficient by itself: both the operation and target repository must be supported. Do not proceed until this matrix is reported.

## Fail-Closed Fallback Rule

Never silently fall back from MCP to `gh`, `git`, or raw GitHub HTTP calls. Consolidate every unsupported or access-blocked operation known during preflight into one fallback request that:

1. States each exact operation.
2. States the missing MCP toolset or exact repository-access error for that operation.
3. States the proposed fallback mechanism.
4. Waits for one user acknowledgment covering the complete stated fallback plan.

Ask again only if a materially different fallback is discovered later. Do not interpret the acknowledgment as approval for unlisted operations, and continue using MCP for every supported, access-verified action.

## Fresh Repository Access Gate

Repository creation may require an acknowledged CLI fallback when the MCP server does not expose that capability. Immediately after creating a repository:

1. Re-run the MCP repository-read check for the new `<owner>/<repo>`.
2. If it succeeds, update the matrix and use MCP for all supported follow-on actions.
3. If it returns `404`, inspect the installation inventory. When the organization installation uses selected repositories, explain that the new repository must be added to the GitHub App installation and stop GitHub work until access is granted.
4. Re-run the repository-read check after access is changed. Do not route MCP-supported writes through CLI to bypass a missing installation grant.

## Required Inputs

Collect or infer from context before calling a tool:

- target repository as `<owner>/<repo>`
- the specific object being acted on (issue/PR number, branch name, workflow file or run ID, release tag)
- the exact action (read vs. create vs. update vs. close/merge vs. delete)
- any content required for the action (issue/PR body, comment text, labels, review verdict)

Never fabricate a repository, issue number, PR number, or run ID. If it cannot be resolved from context, ask the user.

## Guardrails

- **Read actions are low-risk and can proceed without confirmation**: viewing issues/PRs, listing workflow runs, reading files, searching code, and reading repository OIDC subject customization.
- **Write actions that are easily reversible** (opening an issue, adding a label, posting a draft PR) may proceed once the required inputs are confirmed, but summarize what will be created before calling the tool.
- **Actions that are hard to reverse or affect shared state require explicit user confirmation before calling the tool**, including: commenting on an issue/PR, merging or closing a PR, closing an issue, deleting a branch or tag, creating or publishing a release, dismissing a review, force-pushing, or changing repo settings/permissions.
- Never use a GitHub MCP tool to bypass branch protection, required reviews, or status checks. If a write action is blocked by a repo rule, report the block — do not look for a workaround.
- Never print, log, or commit tokens, secrets, or credentials used by the MCP server connection.
- Treat rate-limit or permission-denied errors as a stop condition: report the exact error to the user rather than retrying with broader scopes or a different auth path.
- If the requested action would affect a repo outside the one the user is currently working in, confirm the target repo explicitly before proceeding.

## Workflow

1. Confirm the target repository and the exact object/action requested.
2. Complete discovery, installation inspection, repository-access probes, and the capability matrix.
3. For a read action, call the MCP tool and return the result.
4. For a write action, state clearly what will be created/changed and where, then apply the guardrail above: proceed directly for easily-reversible actions, or get explicit confirmation first for hard-to-reverse ones.
5. Call the MCP tool with the confirmed inputs.
6. If MCP lacks a capability or repository access, apply the consolidated fail-closed fallback rule before using another mechanism.
7. After a fallback creates a fresh repository, complete the fresh repository access gate before continuing.
8. Report the result with a link to the affected GitHub object (issue/PR/release/run URL) and a one-line summary of what changed.
9. If the MCP call fails, report the exact error and do not retry with elevated scope or a different credential path.

## Common Recipes

- **Open an issue**: confirm repo, title, and body → create → return the issue URL.
- **Comment on an issue or PR**: confirm repo, number, and exact comment text → get confirmation (comments are visible to others) → post → return the comment URL.
- **Review a PR**: read the diff/files via MCP tools, produce findings, then confirm before submitting a formal "approve"/"request changes"/"comment" review.
- **Merge a PR**: confirm the PR is approved and checks are green, get explicit user confirmation, then merge using the method (merge/squash/rebase) the user specifies.
- **Create a branch**: confirm repo and base branch, then create.
- **Trigger a workflow run**: confirm the workflow file, ref, and inputs, then dispatch; poll run status without an interactive log viewer.
- **Create a release**: confirm repo, tag, target commit/branch, and release notes, get explicit confirmation, then publish.
- **Read repository OIDC subject customization**: confirm the repository, then call the dedicated tool equivalent to `get_repository_oidc_customization`. Preserve and report the returned `use_default` and `include_claim_keys` fields exactly. If the capability is unavailable, apply the fail-closed fallback rule; never infer or construct the subject template from repository metadata.

## Output

Return:

1. the action taken (or the read result)
2. a direct link to the affected GitHub object
3. any guardrail that blocked the action and why
4. next-step suggestions when relevant (e.g., "PR is open, want me to request a reviewer?")

## Quality Checklist

- [ ] Correct repository and object confirmed before acting
- [ ] Inspected the complete callable-tool inventory, including deferred GitHub MCP tools
- [ ] Inspected connected accounts/installations and probed every existing target repository
- [ ] Reported a per-operation capability and access matrix before GitHub work
- [ ] Used GitHub MCP for every supported, access-verified action
- [ ] Consolidated known fallbacks into one request and obtained acknowledgment before use
- [ ] Verified MCP access after creating a fresh repository
- [ ] Hard-to-reverse actions were confirmed with the user before execution
- [ ] No secrets, tokens, or credentials appear in the output
- [ ] Result includes a link to the affected GitHub object
- [ ] Repository OIDC subject customization was read through the dedicated capability and never inferred
