---
name: cloud-one-github-actions-deployment-foundation
description: 'Shared NCI Cloud One Development deployment controls for GitHub Actions and AWS SAM. Use as the required foundation for the language-specific Python and Node.js Cloud One deployment skills; it covers account verification, exact OIDC trust, permission boundaries, GitHub environments, dry-run review, execution, and smoke-test completion.'
argument-hint: 'Provide GitHub repository (owner/repo), Cloud One Development account, runtime skill, and stack name'
user-invocable: false
---

# Cloud One GitHub Actions Deployment Foundation

Apply these shared controls to supported language-specific Cloud One deployment skills:

- [Python Lambda deployment](cloud-one-python-deploy.md)
- [Node.js Lambda deployment](cloud-one-nodejs-deploy.md)

Work only in the NCI Cloud One Development non-production tier. GitHub Actions is the deployment mechanism and authenticates to AWS through GitHub OIDC; never store AWS access keys in GitHub.

## Safety and platform invariants

- Verify the selected account ID before every IAM or CloudFormation mutation.
- Use an IAM role name beginning with `power-user` and attach the account's `PermissionBoundary_PowerUser` boundary when creating it.
- Scope OIDC trust to one exact GitHub repository and GitHub environment. Never use wildcard repository subjects.
- Query the repository's OIDC customization before composing trust. CBIIT repositories may use immutable organization and repository IDs in the `sub` claim.
- Never print, persist, or commit temporary AWS credentials. GitHub Actions uses OIDC and does not require a local AWS login for a normal deployment.
- Create and inspect a dry-run CloudFormation change set before executing deployment.
- Treat deleting or replacing an existing role or stack as destructive. Only replace a role created during the current workflow that has never been successfully used; otherwise stop and escalate.
- Complete read-only preflight first, then obtain one bundled user approval immediately before the first gated mutation when role creation, broad managed-policy attachment, or limited cleanup is required. Do not split known actions into separate approval requests.
- Treat user-selected tooling such as MCP-only or no-CLI operation as a constraint for that run, not as a permanent platform rule. Command examples describe equivalent operations and do not override the user's tool constraint.

## Shared inputs

Collect or derive:

1. App name and filesystem/repository slug. For a fresh repository created by this system, prefix the repository slug with `nci-ai-` (for example, `nci-ai-app-slug`).
2. GitHub repository as `<owner>/<repo>`.
3. GitHub deployment environment, normally `dev`.
4. Selected Cloud One Development AWS account and CLI profile.
5. AWS region, always `us-east-1` (N. Virginia). Never deploy to another region without explicit written authorization.
6. Stack name, normally `<app-slug>-dev`.
7. Deploy-role name, normally `power-user-<repo-slug>-github-actions-dev`.

Keep IAM role names at or below 64 characters. Shorten the app slug, not the required `power-user` prefix or the `nci-ai-` repository prefix.

## Minimize and bundle approvals

Treat an explicit request to deploy the application to the selected Development account as authorization for routine, in-scope work: read-only discovery, application and workflow edits, GitHub environment configuration, tests, SAM validation and build, commits and pushes, dry-run creation and inspection, execution of a reviewed non-destructive change set, smoke tests, and deployment-record updates. Do not ask the user to reconfirm each step.

Before requesting any approval, finish all available read-only preflight and resolve the exact account, repository, environment, stack, role, OIDC subject, permission boundary, policies, endpoint exposure, and expected CloudFormation resources.

If the deploy role is absent or another known gated action is required, ask once, immediately before the first such mutation, for a single approval envelope that identifies:

- the exact Development account, repository, environment, stack, and role;
- the exact OIDC trust subject and permission boundary;
- every broad or local managed policy to attach;
- whether the endpoint will be public;
- execution of the reviewed change set only when it contains the expected non-destructive resources;
- deletion and recreation only of an invalid, unused role created during the current run; and
- deletion only of an empty failed stack created during the current run.

After approval, perform every covered action without additional conversational confirmations. Reusing an existing role whose trust, boundary, and policies already match requires no new IAM approval. A fallback that uses a different authorized tool but keeps the same target, permissions, and effects is a notification, not a new approval; honor any user-requested fallback logging.

Stop and obtain a new approval only when new evidence introduces a material change outside the envelope: a different account, region, environment, or security posture; production deployment; modification or deletion of pre-existing resources; an unexpected CloudFormation deletion or replacement; undisclosed public exposure; external-team contact or ticket submission; or a fallback that materially expands scope or impact. Runtime permission dialogs imposed by the execution environment are separate and cannot always be bundled.

## Bind deployment identity and pass preflight

Before diagnosing a failure or mutating AWS or GitHub, bind the deployment to one exact identity tuple:

```text
GitHub repository + workflow + environment
→ AWS account + region + deploy role
→ CloudFormation stack
→ deployed endpoint
```

Verify evidence against this tuple. A workflow run, stack, API, WAF, role, or endpoint belonging to another repository or stack is unrelated evidence and must not drive remediation. Check whether the intended stack actually exists; do not infer deployment state from similarly named resources.

Before the first workflow dispatch, require all of the following:

- GitHub repository access and the exact repository OIDC customization are verified.
- The `dev` environment exists.
- `AWS_REGION=us-east-1` and the intended `STACK_NAME` are present at the environment level.
- `AWS_DEPLOY_ROLE_ARN` is present and identifies the verified repository/environment-scoped role.
- The role trust, permission boundary, and attached policies match the selected account and repository.
- The workflow and SAM template target the same region, stack, environment, and endpoint architecture.
- Local tests, `sam validate --lint`, and `sam build` pass.

Do not dispatch a workflow merely to discover missing configuration. Fix incomplete preflight first. After dispatch, inspect only runs for the bound repository, workflow, ref, and inputs.

## Authenticate and verify the target

For a normal deployment, skip local IAM login. GitHub Actions authenticates to AWS through the repository's OIDC deploy role. Confirm that the `dev` GitHub environment already contains the correct `AWS_DEPLOY_ROLE_ARN`, `AWS_REGION`, and `STACK_NAME`, then let the workflow validate the target account.

Open `https://iam.cancer.gov/` in the IDE's integrated browser only when the account or OIDC role must be created or manually verified. Close the integrated browser page when that action is complete. Do not launch an external browser.

If AWS CLI commands are required for account or role setup, run them in the IDE's integrated terminal. The integrated browser cannot execute AWS CLI commands or replace their terminal output. Do not copy credentials into the repository or GitHub settings.

If the Development account does not exist and the user permits external intake, provide this request link:

`https://service.cancer.gov/ncisp?id=nci_sc_cat_item&sys_id=ef2bfbaf1bb49810abf0ddb6bc4bcbf4`

If the user's objective forbids external input, report the missing account as a blocker; do not open a ticket or contact another team. A missing deploy role is not a missing account: inspect the account prerequisites and use the self-service role workflow below when the current identity is authorized.

This workflow does not provision Cloud One accounts or authorize production deployment. Once the account and deploy role already exist, do not open the IAM portal as part of the deployment.

## Create or verify the GitHub repository

Create the private repository only when requested and absent. Verify access and capture its immutable ID together with the organization ID:

```bash
gh repo create <owner>/<repo> --private
gh api repos/<owner>/<repo> --jq '{name: .full_name, id: .id, url: .html_url}'
gh api orgs/<owner> --jq '{login, id}'
```

The language-specific skill defines the required application files, runtime, SAM template, tests, and GitHub Actions workflow.

## Create or verify the GitHub OIDC deploy role

### Resolve the exact OIDC subject

Do not assume the standard GitHub subject format. Query the repository first:

```bash
gh api repos/<owner>/<repo>/actions/oidc/customization/sub
```

- If `use_immutable_subject` is `true`, use `<sub_claim_prefix>:environment:dev`.
- Otherwise use `repo:<owner>/<repo>:environment:dev`.

An immutable subject resembles:

```text
repo:<owner>@<organization-id>/<repo>@<repository-id>:environment:dev
```

The numeric IDs are intentional. Do not substitute the human-readable subject when immutable subjects are enabled.

### Inspect account prerequisites

Using the selected AWS CLI profile, verify the OIDC provider, boundary, local guardrail policies, and any existing role:

```bash
aws iam list-open-id-connect-providers --profile <cloud-one-profile>
aws iam get-policy \
  --policy-arn arn:aws:iam::<account-id>:policy/PermissionBoundary_PowerUser \
  --profile <cloud-one-profile>
aws iam list-policies --scope Local --profile <cloud-one-profile> \
  --query 'Policies[?PolicyName==`poweruser-iam-actions` || PolicyName==`poweruser-deny-policy`].[PolicyName,Arn]' \
  --output table
aws iam get-role \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --profile <cloud-one-profile>
```

The expected provider ARN is:

```text
arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com
```

If the role exists, verify its exact trust subject, permission boundary, attached policies, and last-used information. Reuse it only when all values are correct.

### Create the role when absent

Construct an exact trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "<exact-subject>"
        }
      }
    }
  ]
}
```

Create the role with its boundary in the same API call:

```bash
aws iam create-role \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --assume-role-policy-document file://<trust-policy.json> \
  --permissions-boundary arn:aws:iam::<account-id>:policy/PermissionBoundary_PowerUser \
  --description 'GitHub Actions OIDC deployment role for <owner>/<repo> dev' \
  --profile <cloud-one-profile>
```

Do not attach `PowerUserAccess` until the bundled approval envelope identifies this exact role and policy set and explains that broad deployment permissions remain constrained by the permission boundary and exact OIDC trust. After that single approval, attach the policies used by the Cloud One PowerUser model without requesting separate confirmations:

```bash
aws iam attach-role-policy \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess \
  --profile <cloud-one-profile>
aws iam attach-role-policy \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess \
  --profile <cloud-one-profile>
aws iam attach-role-policy \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --policy-arn arn:aws:iam::<account-id>:policy/poweruser-iam-actions \
  --profile <cloud-one-profile>
aws iam attach-role-policy \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --policy-arn arn:aws:iam::<account-id>:policy/poweruser-deny-policy \
  --profile <cloud-one-profile>
```

Policy names can differ between accounts. Discover and verify local policy ARNs instead of guessing when these names are absent.

### Verify the role

```bash
aws iam get-role \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --profile <cloud-one-profile> \
  --query 'Role.{Arn:Arn,Boundary:PermissionsBoundary.PermissionsBoundaryArn,Trust:AssumeRolePolicyDocument,LastUsed:RoleLastUsed}'
aws iam list-attached-role-policies \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --profile <cloud-one-profile>
```

Confirm the `power-user` prefix, `PermissionBoundary_PowerUser`, GitHub provider, `aud=sts.amazonaws.com`, exact repository/environment subject, and expected managed and local guardrail policies.

Some Cloud One guardrails permit `iam:CreateRole` but deny `iam:UpdateAssumeRolePolicy`. If a newly created role has incorrect trust, first confirm it was created in the current workflow and has never been successfully assumed. Only then may it be detached, deleted, and recreated. Never replace a pre-existing or active role without separate authorization.

## Configure the GitHub environment

Create the `dev` environment and set:

| Type | Name | Example |
|---|---|---|
| Variable | `AWS_REGION` | `us-east-1` |
| Variable | `STACK_NAME` | `my-app-dev` |
| Secret | `AWS_DEPLOY_ROLE_ARN` | Verified role ARN |

```bash
gh api --method PUT repos/<owner>/<repo>/environments/dev
gh variable set AWS_REGION --env dev --body 'us-east-1' -R <owner>/<repo>
gh variable set STACK_NAME --env dev --body '<app-slug>-dev' -R <owner>/<repo>
gh secret set AWS_DEPLOY_ROLE_ARN --env dev -R <owner>/<repo>
```

Allow `gh secret set` to prompt for the ARN. Do not put credentials in command arguments. The role ARN is not a credential, but the prompt preserves the secret-setting pattern.

These commands are CLI examples, not a requirement to use `gh`. Use an access-verified GitHub MCP capability or another user-authorized interface when selected for the run. After setting the values, read back the environment variables and secret metadata and complete the pre-dispatch gate; never use a failed workflow run as the first configuration check.

## Review, deploy, and verify

Run the language-specific tests and SAM validation before pushing. Commit and push the application and workflow, then run a dry deployment:

```bash
gh workflow run deploy.yml -R <owner>/<repo> -f environment=dev -f dry_run=true
gh run list -R <owner>/<repo> --workflow deploy.yml --limit 3
```

Inspect the workflow log and CloudFormation change set. Confirm the resources and changes are scoped to the selected Development account and stack. Execute only after that review:

```bash
gh workflow run deploy.yml -R <owner>/<repo> -f environment=dev -f dry_run=false
```

Poll without opening an interactive viewer:

```bash
gh api repos/<owner>/<repo>/actions/runs/<run-id> \
  --jq '{status: .status, conclusion: (.conclusion // "running"), updated_at: .updated_at}'
```

Once successful, obtain the application URL from stack outputs or the workflow log. Require HTTP 200 from the implemented root and health routes. Record the account, region, stack, role ARN, workflow run, endpoint, and smoke-test result without recording credentials.

## Shared failure checks

| Symptom | Likely cause | Resolution |
|---|---|---|
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` although the visible repo/environment looks correct | Repository uses an immutable OIDC subject | Query the repository customization and use `sub_claim_prefix:environment:<env>`. |
| `iam:UpdateAssumeRolePolicy` is denied | Boundary or deny policy blocks trust updates | Recreate only a role created in the current workflow that has never been used; otherwise escalate. |
| `iam:CreateRole` is denied for a SAM-generated role | Generated role lacks the `power-user` prefix or boundary | Define the Lambda execution role explicitly with both requirements. |
| CloudFormation requests IAM acknowledgement | Template assigns a role name | Deploy with `CAPABILITY_NAMED_IAM`. |
| `/Stage/` works but `/dev/` returns 403 | SAM synthesized a duplicate stage | Set `OpenApiVersion: '3.0.1'` on the `AWS::Serverless::Api`. |
| Initial stack is `ROLLBACK_COMPLETE` | A resource failed during stack creation | Inspect events and fix the cause. Delete and retry without another confirmation only when the stack is empty, was created during the current run, and cleanup was included in the approval envelope; otherwise obtain approval. |
| SAM setup appears stuck | Slow fresh runner setup | Wait up to 10 minutes; cancel and retry once if there is still no progress. |
| Explicit SCP deny on API Gateway creation | Organization policy blocks the operation | Capture the denial and use an approved alternative only after confirming the restriction. |
| `No changes to deploy` | Template and package are unchanged | Treat as success when the existing stack is healthy. |
| Missing variable or secret | GitHub environment is incomplete | Set the value on the `dev` environment and rerun. |

## Completion criteria

Deployment is complete only when:

1. The OIDC role has exact repository/environment trust, the required boundary, and verified policies.
2. The language-specific local checks passed.
3. The SAM dry run was reviewed before execution.
4. The execute run succeeded.
5. The deployed root and health routes return HTTP 200.
6. Deployment metadata was recorded without credentials.
