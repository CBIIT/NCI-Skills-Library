# NCI Startup Questions

Load this file after the startup bootstrap when you need the minimal questionnaire.

This questionnaire is loaded directly from the GitHub repository before any local setup. Before checking dependencies, configuring GitHub CLI, requesting sign-in, installing tools, or asking these questions, read the required files from these raw URLs:

- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/nci-startup.md
- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/collect_initial_info.md

Do not run `gh`, `git`, GitHub authentication, or any installation command before the direct URL reads are complete. Do not require `git`, `gh`, or other repo tooling to be installed in the current environment.

First say to the user:

"We will ask you a few basic questions to understand your app, then we will build a Hello, World application as the basis for us to adjust."

Then say:

"We will ask 5 required questions, one at a time, and up to 2 optional follow-up questions if needed. I will wait for your answer before asking the next question."

Ask exactly one question per message. Do not display the remaining questions as a batch or pre-fill answers for them. After each response, confirm or clarify that answer, then ask the next numbered question.

Use a numbered multiple-choice format for choice questions. Open-ended questions do not need numbered options. Some IDEs support clickable buttons, but the startup flow must still work if the user answers by typing a number or choosing a button label. The system should always present numbered options first for choice questions and accept either numeric selection or the matching option text.

Example format:

"1) Fresh repo\n2) Existing project"

Then the user may respond with either "1" or "Fresh repo".

Before any installation starts, the system must check the environment and notify the user about required dependencies. The first step is a dependency check, not installation.

The tool must explicitly check whether the following are present: Python, Git, GitHub CLI, and any runtime or CLI tooling required by the selected stack. The system should also verify whether the user has a GitHub account and whether GitHub sign-in is available.

If required tools are missing, the system must tell the user exactly what is missing and what it will install before proceeding. Example notification:

"Before we begin building, I need to check your environment. We found that the following dependencies are missing: Python, Git, and GitHub CLI. We will install these first, then continue with the Hello, World app and registry setup."

If the user chooses Python and Python is not installed on the machine, the system must tell the user up front: "Python is not installed on this machine. We can install it for you before continuing with the Hello, World app."

If the user does not have a GitHub account, the system must tell them up front: "You need a GitHub account before we can register this app with the NCI Skills Registry. Please sign in or create a GitHub account, then continue."

Only after this dependency summary is shown and confirmed should the system begin installation or implementation.

Then proceed with Question 1.

Required questions, in order:

1. Is this a fresh repo or an existing project?
2. What is the name of the project? This is an open-ended question. Use the project name as the page name and derive a repository-safe `Page-Name-With-Dashes` form when needed.
3. What is the name of the author? This is an open-ended question. Use the author or GitHub username from the current user, authenticated context, or workspace when it can be determined, and confirm the display name from the public GitHub profile when possible. If it cannot be determined, ask this question before continuing. For SSO, also ask the author to provide and confirm their NIH email address; never infer it from GitHub.
4. What kind of application and language should we build? Present these choices: web app with Python, web app with Node.js, static site for GitHub Pages, API with Python, CLI with Python, script with Python, library with Python, or I don't know. For a Python web app, use Flask automatically; do not ask the user to choose a Python framework. Do not offer Go or .NET in this initial flow.
5. Where should the app run? Present these choices: local only, GitHub Pages, or AWS Lambda / managed service.

If the project is not fresh, the AI should inspect the existing project context and use that information to answer the remaining questions when possible instead of asking for redundant details.

Optional follow-up questions only if needed:

6. Are there any NCI-specific constraints, security controls, or deployment requirements?
7. Is this a first registration or an update to an existing registry entry?

Conditional deployment question, only when AWS Lambda / managed service is selected:

- Use the Cloud One non-production Development tier. Sign in through `https://iam.cancer.gov/` using AWS IAM Identity Center.

Then do this:

- if the user selected a web app, invoke the hello-world-web-app skill in [startup/hello-world-web-app.md](startup/hello-world-web-app.md) to create the minimal app skeleton
- build a hello world app locally
- verify it runs successfully
- register it with the NCI Skills Registry using [startup/nci-skill-registration.md](startup/nci-skill-registration.md)
- if GitHub Pages was selected, prepare the repository for GitHub Pages and deploy the static site there
- if AWS Lambda / managed service was selected, invoke [CloudOneLambdaGitHubActionsDeploy.md](cicd/CloudOneLambdaGitHubActionsDeploy.md) and deploy to the Cloud One Development non-production tier through `https://iam.cancer.gov/`

Only support local execution, GitHub Pages, and AWS Lambda / managed-service environments in this phase.
Do not ask about ServiceNow, Snowflake, or Power Platform yet.
