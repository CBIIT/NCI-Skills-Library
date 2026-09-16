# NCI Startup Questions

Load this file after the startup bootstrap when you need the minimal questionnaire.

Before asking these questions, read the required repository files directly from the GitHub repository by direct file access. Do not require `git`, `gh`, or other repo tooling to be installed in the current environment.

First say to the user:

"We will ask you a few basic questions to understand your app, then we will build a Hello, World application as the basis for us to adjust."

Then say:

"We will ask 5 required questions and up to 2 optional follow-up questions if needed."

When the AI environment supports it, present each multiple-choice question as clickable buttons rather than free-form text. This makes the startup flow faster and easier for the user.

Before proceeding with any implementation, the system should check the user's environment and required identities. The user must have a GitHub account available. If they do not, the system must tell them up front: "You need a GitHub account before we can register this app with the NCI Skills Registry. Please sign in or create a GitHub account, then continue."

The system should also attempt to sign the user in to GitHub early in the flow so that the app can be registered with the NCI Skills Registry as early as possible in the process.

Before proceeding with any implementation, the tool should explicitly check whether the selected runtime is installed. If the user chooses Python and Python is not installed on the machine, the system must tell the user up front: "Python is not installed on this machine. We can install it for you before continuing with the Hello, World app."

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

- if the user selected a web app, invoke the hello-world-web-app skill to create the minimal app skeleton
- build a hello world app locally
- verify it runs successfully
- register it with the NCI Skills Registry
- if cloud deployment was selected, prepare the AWS dev environment and deploy the minimal app there

Only support local execution and AWS Lambda / managed-service environments in this phase.
Do not ask about ServiceNow, Snowflake, or Power Platform yet.
