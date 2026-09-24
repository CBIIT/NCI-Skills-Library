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
- Obtain explicit user approval immediately before attaching `PowerUserAccess` or any equivalent broad managed policy.

## Shared inputs

Collect or derive:

1. App name and filesystem/repository slug.
2. GitHub repository as `<owner>/<repo>`.
3. GitHub deployment environment, normally `dev`.
4. Selected Cloud One Development AWS account and CLI profile.
5. AWS region, always `us-east-1` (N. Virginia). Never deploy to another region without explicit written authorization.
6. Stack name, normally `<app-slug>-dev`.
7. Deploy-role name, normally `power-user-<repo-slug>-github-actions-dev`.

Keep IAM role names at or below 64 characters. Shorten the app slug, not the required `power-user` prefix.

## Authenticate and verify the target

For a normal deployment, skip local IAM login. GitHub Actions authenticates to AWS through the repository's OIDC deploy role. Confirm that the `dev` GitHub environment already contains the correct `AWS_DEPLOY_ROLE_ARN`, `AWS_REGION`, and `STACK_NAME`, then let the workflow validate the target account.

Open `https://iam.cancer.gov/` in the IDE's integrated browser only when the account or OIDC role must be created or manually verified. Close the integrated browser page when that action is complete. Do not launch an external browser.

If AWS CLI commands are required for account or role setup, run them in the IDE's integrated terminal. The integrated browser cannot execute AWS CLI commands or replace their terminal output. Do not copy credentials into the repository or GitHub settings.

If the Development account does not exist, request it at:

`https://service.cancer.gov/ncisp?id=nci_sc_cat_item&sys_id=ef2bfbaf1bb49810abf0ddb6bc4bcbf4`

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

Immediately before attaching `PowerUserAccess`, explain that it grants broad deployment permissions constrained by the permission boundary and exact OIDC trust, then obtain explicit user approval. After approval, attach the policies used by the Cloud One PowerUser model:

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
| Initial stack is `ROLLBACK_COMPLETE` | A resource failed during stack creation | Inspect events, fix the cause, obtain authorization before deleting the failed stack, wait for deletion, and redeploy. |
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
