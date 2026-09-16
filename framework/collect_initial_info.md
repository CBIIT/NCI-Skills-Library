# NCI Startup Questions

Load this file after the startup bootstrap when you need the minimal questionnaire.

Before asking these questions, read the required repository files directly from the GitHub repository by direct file access. Do not require `git`, `gh`, or other repo tooling to be installed in the current environment.

Ask these questions in order:

1. What kind of app should we build: web app, API, CLI, script, or library?
2. Which language or framework do you want: Python, Node.js, .NET, Java, Go, or another option?
3. Should the app run locally only or target AWS Lambda / a managed-service environment?
4. What is the project name and desired working directory?
5. Is this a fresh repo or an existing project?

Only ask these if needed:

6. Are there any NCI-specific constraints, security controls, or deployment requirements?
7. Is this a first registration or an update to an existing registry entry?

Then do this:

- create the minimal app skeleton
- build a hello world app locally
- verify it runs successfully
- register it with the NCI Skills Registry
- if cloud deployment was selected, prepare the AWS dev environment and deploy the minimal app there

Only support local execution and AWS Lambda / managed-service environments in this phase.
Do not ask about ServiceNow, Snowflake, or Power Platform yet.
