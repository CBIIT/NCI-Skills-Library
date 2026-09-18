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

Whenever the workflow needs to open a web page, use the IDE's integrated browser or preview surface. Do not launch an external system browser.

## What Will Happen

Tell the user this process up front:

1. Collect a small amount of necessary information and keep the questions to a minimum.
2. Register the app with the NCI Skills Registry. This step requires GitHub credentials for direct submission. Explain why GitHub is needed; if credentials are unavailable, mark the app **Unregistered for now**, keep the validated registry change, and continue.
3. Build a Hello, World app locally to create and verify the plumbing that the real app will use. Explain this purpose before building.
4. Deploy to Cloud One Development non-prod only if the user selected a cloud target.
5. Start building the real application after the baseline is verified and the registration status is reported.

After loading the bootstrap files, read the current NCI Skills Registry `registry.json` directly from `https://raw.githubusercontent.com/CBIIT/NCI-Skills-Registry/main/registry.json` before creating the app. Use it to detect an existing entry and prepare the new app registration. Do not require `git`, `gh`, a GitHub account, or CBIIT organization membership for this initial read or for preparing the change.

## First Step: Load Bootstrap Files

Before checking dependencies, configuring GitHub CLI, requesting sign-in, installing tools, or asking project questions, read the first bootstrap files directly from these raw GitHub URLs:

- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/nci-startup.md
- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/startup/collect_initial_info.md

Use the instructions loaded from those URLs to continue the startup flow. Do not run `gh`, `git`, GitHub authentication, or any installation command before these files have been read. This first step must work for a novice who has none of those tools installed.

The agent should:

- confirm this is NCI-aligned work
- read any required source files directly from the GitHub repository by direct file access, without requiring `git`, `gh`, or any local repository tooling to be installed
- ask the minimum project questions
- register it with the NCI Skills Registry
- add or update the app entry in the registry repository's `registry.json` directly on `main`, validate the complete JSON document, and submit it through authenticated GitHub access or provide a maintainer-ready patch when direct write access is unavailable
- create a minimal hello world app to establish and verify the local plumbing
- verify it runs locally
- if GitHub Pages was selected, prepare the repository and deploy the static site there
- if AWS Lambda / managed service was selected, first confirm that the user already has a Cloud One Development account. If not, send them to request one at https://service.cancer.gov/ncisp?id=nci_sc_cat_item&sys_id=ef2bfbaf1bb49810abf0ddb6bc4bcbf4; account provisioning is not automated yet. After the account exists, use the Cloud One deployment workflow to deploy to the Development non-production tier through `https://iam.cancer.gov/`

Use the detailed questionnaire in [collect_initial_info.md](startup/collect_initial_info.md).

Present multiple-choice questions with numbered options by default. Accept either the option number or the matching option text; clickable buttons are optional and must not be required.

If the user chooses a web app during startup, invoke the hello-world-web-app skill to create the minimal local baseline. After that baseline is verified, continue with NCI Skills Registry registration and optional AWS dev deployment if needed.

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
- [NCI-Skills-Library](https://github.com/CBIIT/NCI-Skills-Library)
- [NCI Skills Registry](https://github.com/CBIIT/NCI-Skills-Registry)