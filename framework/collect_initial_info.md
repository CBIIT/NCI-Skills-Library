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

Use a numbered multiple-choice format as the default for every question. Some IDEs support clickable buttons, but the startup flow must still work if the user answers by typing a number or choosing a button label. The system should always present numbered options first and accept either numeric selection or the matching option text.

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
2. What kind of app should we build: web app, API, CLI, script, or library?
3. Which language or framework do you want: Python, Node.js, .NET, Java, Go, or another option?
4. Should the app run locally only or target AWS Lambda / a managed-service environment?
5. What is the project name and desired working directory?

If the project is not fresh, the AI should inspect the existing project context and use that information to answer the remaining questions when possible instead of asking for redundant details.

Optional follow-up questions only if needed:

6. Are there any NCI-specific constraints, security controls, or deployment requirements?
7. Is this a first registration or an update to an existing registry entry?

Then do this:

- if the user selected a web app, invoke the hello-world-web-app skill in [startup/hello-world-web-app.md](startup/hello-world-web-app.md) to create the minimal app skeleton
- build a hello world app locally
- verify it runs successfully
- register it with the NCI Skills Registry using [startup/nci-skill-registration.md](startup/nci-skill-registration.md)
- if cloud deployment was selected, prepare the AWS dev environment and deploy the minimal app there

Only support local execution and AWS Lambda / managed-service environments in this phase.
Do not ask about ServiceNow, Snowflake, or Power Platform yet.
