---
name: cloud-one-github-actions-lambda-deployment
description: 'Deploy a Python Lambda application to NCI Cloud One Development from GitHub Actions. Use when creating or repairing the GitHub OIDC deployment role, applying the Cloud One PowerUser permission boundary and guardrail policies, discovering immutable CBIIT repository trust subjects, scaffolding a boundary-safe SAM stack, or validating a dev deployment.'
argument-hint: 'Provide app name, GitHub repository (owner/repo), and Cloud One Development account'
user-invocable: true
---

# Cloud One GitHub Actions Lambda Deployment

Deploy a Python Lambda application to the NCI Cloud One Development non-production tier from a GitHub repository. GitHub Actions is the deployment mechanism and authenticates to AWS through GitHub OIDC; do not store AWS access keys in GitHub.

This procedure includes the deploy-role bootstrap proven in the Cloud One PowerUser account model. IAM creation is conditional: reuse a correct role when one already exists, and obtain explicit user approval immediately before attaching broad managed policies such as `PowerUserAccess`.

## Safety and platform invariants

- Work only in the user-selected Cloud One Development account. Verify the account ID before every IAM or CloudFormation mutation.
- Use an IAM role name beginning with `power-user` and attach the account's `PermissionBoundary_PowerUser` boundary at creation time.
- Scope OIDC trust to one exact GitHub repository and GitHub environment. Do not use wildcard repository subjects.
- Query the repository's OIDC customization before composing trust. CBIIT repositories may use immutable organization and repository IDs in the `sub` claim.
- Never print, persist, or commit temporary AWS credentials. Prefer AWS CLI IAM Identity Center/SSO sessions.
- Create a dry-run CloudFormation change set and inspect it before executing the deployment.
- Treat deleting/replacing an existing role or stack as destructive. Only replace a role created during the current workflow and never successfully used; otherwise stop and escalate.

## Required inputs

Collect or derive:

1. App name and filesystem/repository slug.
2. GitHub repository as `<owner>/<repo>`.
3. GitHub deployment environment, normally `dev`.
4. Selected Cloud One Development AWS account and CLI profile.
5. AWS region, normally `us-east-1`.
6. Stack name, normally `<app-slug>-dev`.
7. Deploy-role name, normally `power-user-<repo-slug>-github-actions-dev`.

Keep generated IAM role names at or below AWS's 64-character limit. Shorten the app slug—not the required `power-user` prefix—when necessary.

## Phase 1 — Authenticate and verify the target

Open `https://iam.cancer.gov/`, choose **AWS IAM Identity Center**, and select the intended Development account and PowerUser permission set. Configure or use a named AWS CLI SSO profile; do not copy credentials into the repository or GitHub settings.

```bash
aws sso login --profile <cloud-one-profile>
aws sts get-caller-identity --profile <cloud-one-profile>
```

Confirm the returned account ID and ARN with the user-selected account before continuing. If the Development account does not exist, request it at:

`https://service.cancer.gov/ncisp?id=nci_sc_cat_item&sys_id=ef2bfbaf1bb49810abf0ddb6bc4bcbf4`

This skill does not provision Cloud One accounts or authorize production deployment.

## Phase 2 — Create or verify the GitHub repository

```bash
# Create only when requested and absent.
gh repo create <owner>/<repo> --private --confirm

# Verify access and capture immutable IDs.
gh repo view <owner>/<repo> --json nameWithOwner,databaseId,url
gh api orgs/<owner> --jq '{login, id}'
```

Clone the repository if needed. It must contain at minimum:

- `function.py` — Lambda handler.
- `template.yaml` — AWS SAM template.
- `requirements.txt` — runtime dependencies.
- `.github/workflows/deploy.yml` — GitHub Actions deployment workflow.

## Phase 3 — Build a boundary-safe SAM template

Cloud One PowerUser guardrails can reject SAM's automatically generated Lambda execution role because its name does not start with `power-user` and it has no permission boundary. Define the execution role explicitly.

Use this baseline `template.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  ApiStageName:
    Type: String
    Default: dev

Globals:
  Function:
    Runtime: python3.12
    Timeout: 30

Resources:
  AppFunctionExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub power-user-${AWS::StackName}-lambda
      PermissionsBoundary: !Sub arn:${AWS::Partition}:iam::${AWS::AccountId}:policy/PermissionBoundary_PowerUser
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: lambda-basic-logs
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action:
                  - logs:CreateLogGroup
                  - logs:CreateLogStream
                  - logs:PutLogEvents
                Resource: !Sub arn:${AWS::Partition}:logs:${AWS::Region}:${AWS::AccountId}:*

  UsageApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref ApiStageName
      OpenApiVersion: '3.0.1'

  AppFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: function.lambda_handler
      CodeUri: .
      Role: !GetAtt AppFunctionExecutionRole.Arn
      Events:
        Root:
          Type: Api
          Properties:
            Path: /
            Method: ANY
            RestApiId: !Ref UsageApi
        Proxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref UsageApi

Outputs:
  AppApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub https://${UsageApi}.execute-api.${AWS::Region}.amazonaws.com/${ApiStageName}/
```

`OpenApiVersion: '3.0.1'` prevents SAM from synthesizing an additional hard-coded `Stage` stage. Add only the least-privilege runtime permissions the function needs to the execution role.

If CloudFormation returns an explicit organization/SCP deny for API Gateway creation, document the exact denial before considering a Lambda Function URL. Do not preemptively change architectures.

## Phase 4 — Create the GitHub Actions workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: deploy

on:
  workflow_dispatch:
    inputs:
      environment:
        description: Deployment environment
        required: true
        type: choice
        options:
          - dev
      dry_run:
        description: Create a change set without execution
        required: true
        type: boolean
        default: true

env:
  AWS_REGION: ${{ vars.AWS_REGION }}
  STACK_NAME: ${{ vars.STACK_NAME }}

jobs:
  deploy:
    name: Deploy to ${{ inputs.environment }}
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}

    permissions:
      id-token: write
      contents: read

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Setup SAM CLI
        run: pip install aws-sam-cli

      - name: Validate required variables
        run: |
          test -n "$AWS_REGION" || (echo "Missing variable: AWS_REGION" && exit 1)
          test -n "$STACK_NAME" || (echo "Missing variable: STACK_NAME" && exit 1)

      - name: Configure AWS credentials with OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Validate and build
        run: |
          sam validate --lint
          sam build

      - name: Deploy dry run
        if: ${{ inputs.dry_run }}
        run: |
          sam deploy \
            --stack-name "$STACK_NAME" \
            --region "$AWS_REGION" \
            --resolve-s3 \
            --no-fail-on-empty-changeset \
            --no-execute-changeset \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameter-overrides ApiStageName='${{ inputs.environment }}'

      - name: Deploy
        if: ${{ !inputs.dry_run }}
        run: |
          sam deploy \
            --stack-name "$STACK_NAME" \
            --region "$AWS_REGION" \
            --resolve-s3 \
            --no-fail-on-empty-changeset \
            --capabilities CAPABILITY_NAMED_IAM \
            --parameter-overrides ApiStageName='${{ inputs.environment }}'
```

Use `CAPABILITY_NAMED_IAM` because the template assigns an explicit execution-role name. Add app-specific parameter overrides only when the template defines them.

## Phase 5 — Create or verify the GitHub OIDC deploy role

### 5.1 Resolve the exact GitHub OIDC subject

Do not assume the standard GitHub subject format. Query the repository first:

```bash
gh api repos/<owner>/<repo>/actions/oidc/customization/sub
```

Interpret the response:

- If `use_immutable_subject` is `true`, use `<sub_claim_prefix>:environment:dev`.
- Otherwise use `repo:<owner>/<repo>:environment:dev`.

An immutable subject resembles:

```text
repo:<owner>@<organization-id>/<repo>@<repository-id>:environment:dev
```

The numeric IDs are intentional. Do not substitute the human-readable subject if immutable subjects are enabled.

### 5.2 Inspect account prerequisites

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

The expected GitHub provider ARN is:

```text
arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com
```

If the role exists, verify its exact trust subject, permission boundary, attached policies, and last-used information. Reuse it only when all values are correct.

### 5.3 Create the role when absent

Construct a trust policy containing:

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
          "token.actions.githubusercontent.com:sub": "<exact-subject-from-5.1>"
        }
      }
    }
  ]
}
```

Create the role with the boundary in the same API call:

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

Policy names can differ between accounts. Discover and verify local policy ARNs rather than guessing when these exact names are absent.

### 5.4 Verify the finished role

```bash
aws iam get-role \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --profile <cloud-one-profile> \
  --query 'Role.{Arn:Arn,Boundary:PermissionsBoundary.PermissionsBoundaryArn,Trust:AssumeRolePolicyDocument,LastUsed:RoleLastUsed}'
aws iam list-attached-role-policies \
  --role-name power-user-<repo-slug>-github-actions-dev \
  --profile <cloud-one-profile>
```

Confirm:

- Role name begins with `power-user`.
- Boundary is `PermissionBoundary_PowerUser`.
- Trust has the GitHub provider, `aud=sts.amazonaws.com`, and the exact repository/environment subject.
- Expected managed and local guardrail policies are attached.

Some Cloud One guardrails allow `iam:CreateRole` but deny `iam:UpdateAssumeRolePolicy`. If a newly created role has incorrect trust, first confirm it was created in this workflow and has never been successfully assumed. Only then may it be detached/deleted and recreated with the corrected trust. Never replace a pre-existing or active role without separate authorization.

## Phase 6 — Configure the GitHub environment

Create the `dev` environment and set:

| Type | Name | Example |
|---|---|---|
| Variable | `AWS_REGION` | `us-east-1` |
| Variable | `STACK_NAME` | `my-app-dev` |
| Secret | `AWS_DEPLOY_ROLE_ARN` | ARN verified in Phase 5 |

```bash
gh variable set AWS_REGION --env dev --body 'us-east-1' -R <owner>/<repo>
gh variable set STACK_NAME --env dev --body '<app-slug>-dev' -R <owner>/<repo>
gh secret set AWS_DEPLOY_ROLE_ARN --env dev -R <owner>/<repo>
```

Allow `gh secret set` to prompt for the ARN. Do not place sensitive values directly in command arguments. The role ARN itself is not a credential, but using the prompt keeps the secret-setting pattern safe and consistent.

## Phase 7 — Validate, deploy, and smoke test

Run local validation before pushing when the SAM CLI is available:

```bash
sam validate --lint
sam build
```

Commit and push the application and workflow. Then run a dry deployment:

```bash
gh workflow run deploy.yml -R <owner>/<repo> -f environment=dev -f dry_run=true
gh run list -R <owner>/<repo> --workflow deploy.yml --limit 3
```

Inspect the GitHub Actions log and CloudFormation change set. After confirming the planned resources are scoped to the intended stack/account, execute:

```bash
gh workflow run deploy.yml -R <owner>/<repo> -f environment=dev -f dry_run=false
```

Poll without opening an interactive viewer:

```bash
gh api repos/<owner>/<repo>/actions/runs/<run-id> \
  --jq '{status: .status, conclusion: (.conclusion // "running"), updated_at: .updated_at}'
```

The SAM CLI setup can take several minutes on a fresh runner. Once successful, obtain `AppApiUrl` from the stack outputs or workflow log and test:

```bash
curl -fsS 'https://<api-id>.execute-api.<region>.amazonaws.com/dev/'
curl -fsS 'https://<api-id>.execute-api.<region>.amazonaws.com/dev/health'
```

Require HTTP 200 from the implemented routes. Record the account, region, stack, role ARN, run ID, endpoint, and smoke-test result in the deployment handoff or registry without recording credentials.

## Diagnosing known failures

| Symptom | Likely cause | Resolution |
|---|---|---|
| `Not authorized to perform sts:AssumeRoleWithWebIdentity` although the visible repo/environment looks correct | Repository uses an immutable OIDC subject | Query `repos/<owner>/<repo>/actions/oidc/customization/sub`; use `sub_claim_prefix:environment:<env>`. CloudTrail `AssumeRoleWithWebIdentity` events can confirm the presented subject. |
| `iam:UpdateAssumeRolePolicy` is denied | Cloud One PowerUser boundary/deny policy blocks trust updates | Recreate only a role created in this workflow that has never been used; otherwise escalate to an IAM administrator. |
| `iam:CreateRole` is denied for a SAM-generated role | Generated execution-role name lacks the `power-user` prefix or required boundary | Define the Lambda execution role explicitly with the prefix and `PermissionBoundary_PowerUser`. |
| CloudFormation requests IAM acknowledgement for a named role | Template uses `RoleName` | Deploy with `CAPABILITY_NAMED_IAM`. |
| `/Stage/` works but `/dev/` returns 403 | SAM synthesized a duplicate default stage | Set `OpenApiVersion: '3.0.1'` on `AWS::Serverless::Api` and redeploy. |
| First deployment leaves the stack in `ROLLBACK_COMPLETE` | A resource failed during initial stack creation | Inspect stack events, fix the cause, obtain authorization to delete the failed stack, wait for deletion, and redeploy. |
| `Setup SAM CLI` appears stuck | Slow runner setup | Wait up to 10 minutes; cancel and retry once if there is still no progress. |
| Explicit SCP deny on API Gateway creation | Organization policy blocks the operation | Capture the denial and use an approved alternative such as a Lambda Function URL only after confirming the restriction. |
| `No changes to deploy` | Template and packaged code are unchanged | Expected; treat as success when the existing stack is healthy. |
| Missing variable or secret | GitHub environment was not configured | Set the value specifically on the `dev` environment and rerun. |

## Completion criteria

The deployment is complete only when:

1. The GitHub Actions OIDC role has exact repository/environment trust, the required boundary, and verified policies.
2. The SAM dry run was reviewed before execution.
3. The execute run succeeded.
4. The root and health routes return HTTP 200 at the intended `/dev/` stage.
5. Deployment metadata was recorded without credentials.
