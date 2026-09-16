---
name: nci-skill-registration
description: Use this skill when an NCI skill needs to register itself with the NCI Skills Registry or update its registration after a major change. It helps skill owners and agents prepare a validated registry change. Produces a registry update or a reviewable pull request.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, JSON
Framework: GitHub Actions, JSON Schema

---

# NCI Skill Registration

## Purpose
Register an NCI skill the first time it is used and keep its registry metadata current when a major change occurs. The registry is the authoritative record of skill ownership, lifecycle status, versions, source repositories, and deployment environments.

## When to Use
Use this skill when:
- An NCI skill is being used for the first time and has no registry entry.
- A skill has a major or material change to its purpose, inputs, outputs, workflow, owner, version, or deployment environments.
- A skill's registration metadata or environment URLs need correction.
- A repository workflow is preparing a registry update after a release.

Do not use this skill when:
- The requested change is unrelated to the skill's registry metadata.
- The registry entry is already current and no material change has occurred.
- The change would expose a secret, credential, token, or other sensitive value.

## Inputs
- Stable kebab-case skill identifier.
- Skill name and description.
- Source repository URL.
- Required owner.
- NCI Owner.
- NCI DOC (division, office, or center).
- Creation date and last-updated date in ISO `YYYY-MM-DD` format.
- Current skill version or source revision, when available.
- Deployment status: `local-only`, `dev`, `qa`, `stage`, or `production`.
- URL for each deployed environment; local-only skills must not claim deployed URLs.
- Optional major-change summary and release notes.

## Starter Questions for the First Registration

Use these questions to bootstrap the first registry entry for a new NCI app or skill. Keep them short and practical.

### Core registration questions
- What is the app or skill name and the stable identifier you want to register?
- What is the NCI Owner for this app or skill?
- What is the NCI DOC (division, office, or center) associated with it?
- Unless you provide a different repository, use `https://github.com/CBIIT/<Application-Name>` as the source repository URL, replacing `<Application-Name>` with the application name in repository-safe form.
- If the GitHub username or organization cannot be inferred from the repository URL or the authenticated GitHub context, ask for the GitHub username before continuing.
- Do not ask for a Security Officer at this stage.
- What is the purpose of the app in one or two sentences?
- Is this a new registration or an update to an existing registry entry?
- What is the current version or source revision?
- What is the creation date and the last-updated date?
- What deployment status applies: `local-only`, `dev`, `qa`, `stage`, or `production`?
- Which environment URLs exist today, if any?
- What changed materially since the last registration, if this is an update?

### AWS Lambda / managed-service questions
- Is this app deployed as an AWS Lambda or in a managed-service pattern such as API Gateway, EventBridge, SQS, Step Functions, or ECS?
- Which AWS account, region, and environment are in use?
- What is the service name, function name, or runtime entry point?
- Is the deployment driven by SAM, Terraform, CDK, or GitHub Actions?
- What is the public or internal endpoint URL for each deployed environment?
- Are there any non-production environments for `dev`, `qa`, or `stage` that should be registered?
- Does the app rely on AWS resources that should be listed as part of its deployment context?
- Are there any secrets, credentials, or restricted data paths that should not be recorded in the registry?

### Explicitly unsupported environments for now
- Do not ask about or infer support for ServiceNow, Snowflake, or Power Platform in the initial bootstrap flow.
- If a user requests one of those environments, acknowledge it as future support and continue only with the supported local or AWS Lambda / managed-service path unless the user explicitly asks for a future-state design.

### Decision questions
- Is the app intended to be local-only, or is it already deployed to an environment?
- Does the app have a material change since the last registry version?
- Are there any blockers or missing metadata that should be documented before submission?

## Output
Return:
1. A validated registry entry or the minimal update required for the existing entry.
2. A concise summary of whether the entry was created or updated and why.
3. The proposed pull request URL, when repository automation is available.
4. Assumptions, risks, and any missing required information.

Never claim that a registry change was committed or merged unless the operation was confirmed by the GitHub API or repository tooling.

## Workflow
1. Confirm the skill identifier, source repository, owner, dates, version or revision, and deployment status.
2. Read the skill's registration metadata and compare it with the existing registry entry.
3. Determine whether this is a first registration or a material update. Do not create a no-op update.
4. Validate the proposed entry against `registry.schema.json` and reject missing owners, dates, invalid statuses, duplicate IDs, or invalid URLs.
5. Preserve the original `created_date` on updates and set `last_updated_date` to the date of the material change.
6. For `local-only`, keep environment URLs empty. For every other deployment status, include the URL for each environment that exists and identify environments that are not yet deployed.
7. Prepare the smallest registry change possible.
8. Submit the change as a pull request when authenticated repository automation is available. Never put credentials in the skill metadata or output.
9. Report the exact change, validation result, and pull request or failure details.

## Quality Checklist
- [ ] Stable skill ID is present and unchanged.
- [ ] Owner is present and unambiguous.
- [ ] `created_date` and `last_updated_date` are present and valid ISO dates.
- [ ] Existing `created_date` was preserved for an update.
- [ ] Deployment status is one of `local-only`, `dev`, `qa`, `stage`, or `production`.
- [ ] Environment URLs match the deployment information and use HTTP(S).
- [ ] Source repository is present and points to the skill's repository.
- [ ] Version, source revision, or material-change summary is recorded when available.
- [ ] Existing registry entries were not reformatted or changed unnecessarily.
- [ ] The registry schema validation passed.
- [ ] No secrets or sensitive data were added.
- [ ] The result distinguishes a prepared change from a submitted, merged, or deployed change.

## Guardrails
- Do not commit directly to the registry's protected branch when a pull request workflow is available.
- Do not use or request personal access tokens in skill content.
- Do not invent an owner, date, URL, version, deployment status, or approval.
- Do not overwrite a skill's original creation date.
- Do not register duplicate IDs.
- Treat first-use registration as a reviewable change, not as proof that the skill is approved for production use.
- Flag uncertainty clearly and stop when required metadata is missing.
- No secrets or sensitive data in outputs.
- Don't invent policy or compliance requirements.

## Additional Links
- [NCI-Skills-Library](https://github.com/CBIIT/NCI-Skills-Library)
- [Skills template](https://github.com/CBIIT/NCI-Skills-Library/blob/main/intake/skills__template.md)
- [NCI Skills Registry](https://github.com/CBIIT/NCI-Skills-Registry)
