# NCI Startup Questions

Load this file after the startup bootstrap when you need the minimal questionnaire.

This questionnaire is loaded directly from the GitHub repository before any local setup. Before checking dependencies, configuring GitHub CLI, requesting sign-in, installing tools, or asking these questions, read the required files from these raw URLs:

- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/nci-startup.md
- https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/startup/collect_initial_info.md

Do not run `gh`, `git`, GitHub authentication, or any installation command before the direct URL reads are complete. Do not require `git`, `gh`, or other repo tooling to be installed in the current environment.

First say to the user:

"We will collect a small amount of necessary information, register the app if GitHub credentials are available, build a Hello, World app locally to establish the plumbing for the real app, deploy it to Cloud One Development non-prod if needed, and then begin the real application."

Then say:

"We will ask 5 required questions, one at a time, and only ask follow-up questions when required information cannot be discovered from context. I will wait for your answer before asking the next question."

Ask exactly one question per message. Do not display the remaining questions as a batch or pre-fill answers for them. After each response, confirm or clarify that answer, then ask the next numbered question.

Use a numbered multiple-choice format for choice questions. Open-ended questions do not need numbered options. Some IDEs support clickable buttons, but the startup flow must still work if the user answers by typing a number or choosing a button label. The system should always present numbered options first for choice questions and accept either numeric selection or the matching option text.

Format every question to the user in bold text, with a `####` line immediately before and immediately after the question, so it is visually unmistakable that an action is required. Do not bold the numbered options.

Example format:

"#### \n**Is this a fresh repo or an existing project?**\n\n1) Fresh repo\n2) Existing project\n#### "

Then the user may respond with either "1" or "Fresh repo".

Before any installation starts, the system must check the environment and notify the user about required dependencies. The first step is a dependency check, not installation.

The tool must explicitly check whether the following are present: Python, Git, GitHub CLI, and any runtime or CLI tooling required by the selected stack. A GitHub account and membership in the CBIIT GitHub Organization are helpful but are not prerequisites for creating the app or preparing its registry entry. Check for GitHub authentication only when the user wants the system to submit the registry change directly.

If required tools are missing, the system must tell the user exactly what is missing and what it will install before proceeding. Example notification:

"Before we begin building, I need to check your environment. We found that the following dependencies are missing: Python, Git, and GitHub CLI. We will install these first, then continue with the Hello, World app and registry setup."

If the user chooses Python and Python is not installed on the machine, the system must tell the user up front: "Python is not installed on this machine. We can install it for you before continuing with the Hello, World app."

If the user does not have a GitHub account, the system must tell them up front: "A GitHub account or CBIIT GitHub Organization membership is not required to build the app. I can prepare and validate the registry.json change locally. To submit it directly, you will need GitHub authentication or an NCI registry maintainer can submit the prepared change for you."

When the registry phase begins for a GitHub Pages or Cloud One target, explain that direct registration requires GitHub credentials because the validated app entry must be written to `registry.json` in the NCI Skills Registry. If credentials are unavailable, mark the app **Unregistered for now**, preserve the validated registry change for later submission, and continue with local build work. For a local-only target, skip registration and do not request GitHub credentials.

Before asking for identity information, resolve it from the current session, workspace metadata, authenticated provider context, GitHub profile, repository owner, or available local user metadata. Use the first reliable result, including a reliably discovered NIH email address, without asking the user to confirm it again. Do not ask "Who are you?" when the identity can be discovered. Never infer or guess an NIH email address.

Only after this dependency summary is shown and confirmed should the system begin installation or implementation.

Then proceed with Question 1.

Required questions, in order:

1. Is this a fresh repo or an existing project?
2. What is the name of the project? This is an open-ended question. Use the project name as the page name and derive a repository-safe `Page-Name-With-Dashes` form when needed.
3. What type of application should we build? Present these choices: Web Page, REST API Interface, MCP Server, or Local Command Line Script.
4. What language would you prefer the app to be written in? Present these choices: 1. Python, 2. Node.js, 3. Java, 4. I don't care or I don't know. This question is a preference signal only; if a required runtime or deployment skill is not available for the chosen language, tell the user before continuing and agree on a supported alternative.
5. Where should the app run? Present these choices: local only, GitHub Pages, or AWS Lambda / managed service.

After the initial questions are answered, explain what happens next:

"Next I will build and run a Hello, World application locally. If you selected GitHub Pages or Cloud One, I will also register the app, check the project into GitHub, and use the appropriate deployment workflow. This creates and verifies the plumbing for software development so we can quickly and iteratively build the site to your requirements. A local-only app does not require registry registration or GitHub credentials."

After the five required questions, begin the registry registration phase before building the Hello, World app only when the target is GitHub Pages or Cloud One. First infer the author/user, organization, and NIH email from the current session, workspace metadata, authenticated provider context, repository owner, GitHub profile, or local user metadata. Use any reliably discovered NIH email directly as the confirmed registration and SSO value; do not ask a redundant confirmation question such as "Should I use this NIH email?" If the author/user cannot be inferred, ask: "Who should be listed as the author/user for this application?" If the organization cannot be inferred, ask: "What organization should be listed for this application?" These are open-ended registration questions and must not be asked when the values are already known. Then resolve the NCI Owner, NCI DOC, GitHub username, and other registration metadata from the same sources. Ask for an NIH email only when it is required and cannot be reliably discovered. Skip this phase for a local-only target.

If the project is not fresh, the AI should inspect the existing project context and use that information to answer the remaining questions when possible instead of asking for redundant details.

Optional follow-up questions only if needed:

7. Are there any NCI-specific constraints, security controls, or deployment requirements?
8. Is this a first registration or an update to an existing registry entry?

Conditional deployment question, only when AWS Lambda / managed service is selected:

- Use the Cloud One non-production Development tier. Before deployment, confirm that the user already has an existing Cloud One Development account and that the GitHub OIDC deploy role is configured. If the account does not exist, direct the user to request it at https://service.cancer.gov/ncisp?id=nci_sc_cat_item&sys_id=ef2bfbaf1bb49810abf0ddb6bc4bcbf4. Skip the IAM login for normal GitHub Actions deployment. Open `https://iam.cancer.gov/` in the IDE's integrated browser only when account or role setup is required, and close it after that action. If AWS CLI commands are needed, run them in the IDE's integrated terminal; the browser cannot replace the CLI.

Then do this:

- if the target is GitHub Pages or Cloud One, register it with the NCI Skills Registry using [nci-skill-registration.md](nci-skill-registration.md)
- if the user selected a Web Page, invoke the hello-world-web-app skill in [hello-world-web-app.md](hello-world-web-app.md) to create the minimal app skeleton
- build a Hello, World app locally to establish the plumbing for the real application
- start the local HTTP server and open the running site in the IDE's integrated browser; do not launch an external system browser or stop at telling the user which command to run
- show the running page to the user and wait for explicit confirmation that the local page looks correct
- do not close the integrated browser page or load/invoke any cloud deployment skill until the user confirms the local page
- after confirmation, close the integrated browser page and verify it runs successfully from the local HTTP server
- if GitHub Pages was selected, prepare the repository for GitHub Pages and deploy the static site there
- if AWS Lambda / managed service was selected, load the shared [cloud-one-deploy.md](../cicd/cloud-one-deploy.md) foundation and invoke the deployment skill matching the selected language: [cloud-one-python-deploy.md](../cicd/cloud-one-python-deploy.md) for Python or [cloud-one-nodejs-deploy.md](../cicd/cloud-one-nodejs-deploy.md) for Node.js. Deploy only to the Cloud One Development non-production tier through `https://iam.cancer.gov/`

Only support local execution, GitHub Pages, and AWS Lambda / managed-service environments in this phase.
Do not ask about ServiceNow, Snowflake, or Power Platform yet.
