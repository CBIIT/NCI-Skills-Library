---
name: nci-startup
description: Minimal bootstrap for fresh AI-assisted NCI work. This is the first file to load. Type "start" to begin the NCI bootstrap flow.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown
Framework: NCI Skills Library

---

# NCI Startup

Load this file first. Then type:

start

## First Step: Load Bootstrap Files

Before checking dependencies, configuring GitHub CLI, requesting sign-in, installing tools, or asking project questions, read the first bootstrap files directly from these raw GitHub URLs:

- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/nci-startup.md
- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/collect_initial_info.md

Use the instructions loaded from those URLs to continue the startup flow. Do not run `gh`, `git`, GitHub authentication, or any installation command before these files have been read. This first step must work for a novice who has none of those tools installed.

The agent should:

- confirm this is NCI-aligned work
- read any required source files directly from the GitHub repository by direct file access, without requiring `git`, `gh`, or any local repository tooling to be installed
- ask the minimum project questions
- create a minimal hello world app
- verify it runs locally
- register it with the NCI Skills Registry
- if cloud deployment was selected, prepare the AWS dev environment and deploy the minimal app there

Use the detailed questionnaire in [collect_initial_info.md](collect_initial_info.md).

Present multiple-choice questions with numbered options by default. Accept either the option number or the matching option text; clickable buttons are optional and must not be required.

If the user chooses a web app during startup, invoke the hello-world-web-app skill to create the minimal local baseline. After that baseline is verified, continue with NCI Skills Registry registration and optional AWS dev deployment if needed.

## Repository Access Rule

This bootstrap must operate in environments without Git or GitHub CLI installed. The AI should access the required repository files directly from the GitHub repository source, not by cloning, fetching, or invoking `git` or `gh` commands.

Keep the initial support set limited to:

- local execution
- AWS Lambda / managed-service environments

Do not ask about ServiceNow, Snowflake, or Power Platform yet.

See also:

- [NCI Skill Registration](startup/nci-skill-registration.md)
- [Hello World Web App](startup/hello-world-web-app.md)
- [NCI-Skills-Library](https://github.com/CBIIT/NCI-Skills-Library)
- [NCI Skills Registry](https://github.com/CBIIT/NCI-Skills-Registry)