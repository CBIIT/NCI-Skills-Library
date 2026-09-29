---
name: nci-startup
description: Minimal bootstrap for fresh AI-assisted NCI work. Loading this file begins the NCI bootstrap flow; "start" is an optional explicit trigger.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown
Framework: NCI Skills Library

---

# NCI Startup

Load this file first. Loading it is sufficient to begin the bootstrap flow. Do not wait for a command. If the interface asks for a response, either a blank response or `start` means begin immediately.

The agent should begin immediately after this file is loaded, whether the user types `start`, submits a blank response, or types nothing further.

Whenever the workflow needs to open a web page, use the IDE's integrated browser or preview surface. Do not launch an external system browser. For the local Hello World gate, keep the integrated browser page open until the user verifies the page; close it only after that verification is complete. For Cloud One deployment, skip IAM login when the GitHub OIDC deploy role is already configured; use the integrated browser only for account or role setup.

## What Will Happen

Tell the user this process up front:

1. Collect a small amount of necessary information and keep the questions to a minimum.
2. If the target is GitHub Pages or Cloud One, register the app with the NCI Skills Registry. This step requires GitHub credentials for direct submission. Explain why GitHub is needed; if credentials are unavailable, mark the app **Unregistered for now**, keep the validated registry change, and continue. For a local-only target, skip registration and do not request GitHub credentials.
3. Build a Hello, World app locally to create and verify the plumbing that the real app will use. Explain this purpose before building.
4. After the user verifies the running local page, deploy to Cloud One Development non-prod only if the user selected a cloud target.
5. Start building the real application after the baseline is verified and the registration status is reported.

After loading the bootstrap files, read the current NCI Skills Registry `registry.json` directly from `https://raw.githubusercontent.com/CBIIT/NCI-Skills-Registry/main/registry.json` only when the target is GitHub Pages or Cloud One. Use it to detect an existing entry and prepare the new app registration. For a local-only target, skip the registry read. Do not require `git`, `gh`, a GitHub account, or CBIIT organization membership for this initial read or for preparing the change.

## First Step: Load Bootstrap Files

Immediately tell the user, in bold: **"We need to fetch the appropriate files to inform the startup."**

Before checking dependencies, configuring GitHub CLI, requesting sign-in, installing tools, or asking project questions, obtain the first bootstrap files:

- `framework/nci-startup.md`
- `framework/startup/collect_initial_info.md`

First check whether the NCI-Skills-Library repository is already available locally (for example, already cloned in the current workspace or at a known local path). If a local copy is found, read the bootstrap files from that local copy instead of fetching from GitHub, and tell the user: "Using the locally installed NCI-Skills-Library instead of fetching from GitHub." Only when no local copy is found, read the files directly from these raw GitHub URLs:

- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/nci-startup.md
- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/startup/collect_initial_info.md

Use the instructions loaded from the local copy or those URLs to continue the startup flow. Do not run `gh`, `git`, GitHub authentication, or any installation command before these files have been read. This first step must work for a novice who has none of those tools installed.

The agent should:

- confirm this is NCI-aligned work
- read any required source files directly from the GitHub repository by direct file access, without requiring `git`, `gh`, or any local repository tooling to be installed
- ask the minimum project questions
- if the target is GitHub Pages or Cloud One, register it with the NCI Skills Registry
- if the target is GitHub Pages or Cloud One, add or update the app entry in the registry repository's `registry.json` directly on `main`, validate the complete JSON document, and submit it through authenticated GitHub access or provide a maintainer-ready patch when direct write access is unavailable
- create a minimal hello world app to establish and verify the local plumbing
- start the local server, show the page in the IDE's integrated browser, and wait for the user's explicit verification before continuing
- verify it runs locally
- if GitHub Pages was selected, prepare the repository and deploy the static site there
- if AWS Lambda / managed service was selected, first confirm that the user already has a Cloud One Development account. If not, send them to request one at https://service.cancer.gov/ncisp?id=nci_sc_cat_item&sys_id=ef2bfbaf1bb49810abf0ddb6bc4bcbf4; account provisioning is not automated yet. After the account exists, use the Cloud One deployment workflow to deploy to the Development non-production tier through `https://iam.cancer.gov/`

Use the detailed questionnaire in [collect_initial_info.md](startup/collect_initial_info.md).

Present multiple-choice questions with numbered options by default. Accept either the option number or the matching option text; clickable buttons are optional and must not be required.

Whenever the assistant needs feedback from the user — a numbered question, an open-ended question, a confirmation, an approval, or waiting for the user to say "done" or otherwise signal readiness before continuing — precede and follow that request with its own line of hash characters (`####`), and put the request itself in bold. Do not bold numbered options. This applies everywhere in the startup flow, not only to the required questions in [collect_initial_info.md](startup/collect_initial_info.md).

If the user chooses a Web Page during startup, invoke the hello-world-web-app skill to create the minimal local baseline. If the user chooses REST API Interface during startup, invoke the hello-world-api skill to create the minimal local baseline. If the user chooses MCP Server during startup, invoke the hello-world-mcp-server skill to create the minimal local baseline. If the user chooses Local Command Line Script during startup, invoke the hello-world-cli skill to create the minimal local baseline; this app type is local-only and skips registry registration and cloud deployment. After that baseline is verified, continue with NCI Skills Registry registration and optional AWS dev deployment if needed.

## GitHub MCP Preflight Gate

Before the first GitHub-side action — including reading or updating the registry, creating or verifying a repository, committing GitHub-hosted content, opening a pull request, configuring deployment, or checking a workflow run — load [github-mcp-actions.md](technology/github/github-mcp-actions.md) and complete its GitHub MCP preflight gate.

The gate must:

1. Discover all currently callable GitHub MCP tools, including deferred tools exposed through the environment's equivalent of tool search or callable-tool inventory.
2. Inspect the connected GitHub App accounts and installations when those tools are available.
3. Verify MCP access to every existing target repository, beginning with `CBIIT/NCI-Skills-Registry` for a registered cloud or GitHub Pages target.
4. Build and report a per-operation capability matrix identifying which planned GitHub actions are supported and access-verified through MCP.
5. Use MCP for every supported, access-verified GitHub action.

This gate is fail-closed. Never silently fall back to `gh`, `git`, or raw GitHub HTTP calls. Consolidate all known unsupported or access-blocked operation classes into one preflight fallback request so the user is not asked repeatedly. State each exact operation, the missing MCP capability or repository-access failure, and the proposed fallback mechanism. Wait for the user to acknowledge that consolidated fallback plan before executing it, using the required bold request between `####` lines. Ask again only if a materially different fallback becomes necessary later.

For a fresh repository, a repository-creation capability may be absent from the MCP server. After an acknowledged fallback creates the repository, immediately verify it through the MCP repository-read tool. If that check returns `404` and the GitHub App installation uses selected repositories, stop and ask the user or an organization administrator to add the repository to the installation. Do not use CLI for later MCP-supported actions while repository access remains unresolved.

## Repository Access Rule

This bootstrap must operate in environments without Git or GitHub CLI installed. The AI should access the required repository files directly from the GitHub repository source, not by cloning, fetching, or invoking `git` or `gh` commands.

Keep the initial support set limited to:

- local execution
- GitHub Pages
- AWS Lambda / managed-service environments

Do not ask about ServiceNow, Snowflake, or Power Platform yet.

See also:

- [NCI Skill Registration](startup/nci-skill-registration.md)
- [Hello World Web App](startup/hello-world-web-app.md)
- [GitHub MCP Actions](technology/github/github-mcp-actions.md)
- [NCI-Skills-Library](https://github.com/CBIIT/NCI-Skills-Library)
- [NCI Skills Registry](https://github.com/CBIIT/NCI-Skills-Registry)
