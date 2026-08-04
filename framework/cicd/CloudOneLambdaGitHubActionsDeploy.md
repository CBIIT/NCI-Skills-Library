---
name: cloud-one-github-actions-lambda-deployment
description: 'Deploy a new Python Lambda application to NCI Cloud One (Sandbox or Development) from a fresh GitHub repository using GitHub Actions, OIDC role assumption, and SAM. Covers repo creation, environment variable and secret configuration, workflow scaffold, and post-deploy smoke tests.'
argument-hint: 'Provide app name, GitHub repo (owner/repo), target Cloud One tier (Sandbox or Development), and stack name'
user-invocable: true
---

# Cloud One GitHub Actions Lambda Deployment

Step-by-step guide to stand up a new Python Lambda application in NCI Cloud One using a GitHub repository and GitHub Actions as the sole deployment mechanism.

## Cloud One Tiers

| Tier | AWS Access Portal |
|---|---|
| **Sandbox** | `https://iam-stage.cancer.gov/` |
| **Development** | `https://iam.cancer.gov/` |

Open the access portal, choose **AWS IAM Identity Center**, select the target account and role, then use **Management Console** or copy temporary **Access Keys**.

## Required Inputs
Before starting, collect:
1. **App name** — used as the base for the stack name and SAM logical IDs
2. **GitHub repository** — `<owner>/<repo>` (must exist or be created as part of this process)
3. **Cloud One tier** — Sandbox or Development (determines access portal URL above)
4. **Stack name** — the CloudFormation stack name, e.g. `my-app-dev`; treat this as user-supplied and environment-specific
5. **AWS region** — default `us-east-2` unless the account requires otherwise
6. **AWS deploy role ARN** — IAM role for OIDC assumption (see [IAM Role Discovery](#iam-role-discovery))

## Phase 1 — GitHub Repository

### 1.1 Create or verify the repository
```bash
# Create (if it does not exist)
gh repo create <owner>/<repo> --private --confirm

# Or verify an existing repo is accessible
gh repo view <owner>/<repo>
```

### 1.2 Clone and set up the project structure
```bash
git clone https://github.com/<owner>/<repo>.git
cd <repo>
```

Your repository must contain at minimum:
- `src/app.py` — Lambda handler
- `template.yaml` — AWS SAM template
- `requirements.txt` — runtime dependencies
- `.github/workflows/deploy.yml` — deployment workflow (created in Phase 3)

## Phase 2 — SAM Template

Minimum `template.yaml` for a Python Lambda + API Gateway:

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
  AppFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/app.lambda_handler
      CodeUri: .
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

  UsageApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref ApiStageName

Outputs:
  AppApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub https://${UsageApi}.execute-api.${AWS::Region}.amazonaws.com/${ApiStageName}/
```

> **Note:** If CloudFormation returns an explicit SCP deny for `apigateway:POST` on `/apis/.../stages`, switch to a Lambda Function URL (`FunctionUrlAuthType: NONE`) instead of API Gateway. This is a platform policy restriction, not an IAM permissions gap.

## Phase 3 — GitHub Actions Workflow

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
          - qa
          - stage
          - prod
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

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Validate required inputs
        run: |
          test -n "$AWS_REGION"  || (echo "Missing variable: AWS_REGION"  && exit 1)
          test -n "$STACK_NAME"  || (echo "Missing variable: STACK_NAME"  && exit 1)

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Build
        run: sam build

      - name: Deploy (dry run — change set only)
        if: ${{ inputs.dry_run }}
        run: |
          sam deploy \
            --stack-name "$STACK_NAME" \
            --region "$AWS_REGION" \
            --resolve-s3 \
            --no-fail-on-empty-changeset \
            --no-execute-changeset \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides ApiStageName='${{ inputs.environment }}'

      - name: Deploy (execute)
        if: ${{ !inputs.dry_run }}
        run: |
          sam deploy \
            --stack-name "$STACK_NAME" \
            --region "$AWS_REGION" \
            --resolve-s3 \
            --no-fail-on-empty-changeset \
            --capabilities CAPABILITY_IAM \
            --parameter-overrides ApiStageName='${{ inputs.environment }}'
```

Add app-specific `--parameter-overrides` entries for any additional SAM parameters your template defines.

## Phase 4 — GitHub Environment Variables and Secrets

Configure these on the GitHub repository **for each environment** (`dev`, `qa`, `stage`, `prod`). Settings live at:
```
https://github.com/<owner>/<repo>/settings/environments
```

### Variables (non-secret, visible in logs)
Set at the environment level so each environment can target a different stack/region:

| Variable | Example value | Notes |
|---|---|---|
| `AWS_REGION` | `us-east-2` | AWS region for the CloudFormation stack |
| `STACK_NAME` | `my-app-dev` | CloudFormation stack name — **user-supplied per environment** |

Add any app-specific variables your SAM template needs here as well.

### Secrets (encrypted, redacted in logs)
Set at the environment level:

| Secret | Notes |
|---|---|
| `AWS_DEPLOY_ROLE_ARN` | IAM role assumed by GitHub Actions via OIDC (see below) |

Add any app-specific API tokens or credentials your Lambda needs at runtime here.

### Setting variables and secrets via GitHub CLI
```bash
# Variable — per environment
gh variable set AWS_REGION  --env dev --body "us-east-2"          -R <owner>/<repo>
gh variable set STACK_NAME  --env dev --body "my-app-dev"          -R <owner>/<repo>

# Secret — per environment (value prompted; never pass secrets as CLI arguments)
gh secret set AWS_DEPLOY_ROLE_ARN --env dev -R <owner>/<repo>
```

## Phase 5 — IAM Role Discovery

The deploy role must:
- Trust the GitHub OIDC provider (`token.actions.githubusercontent.com`)
- Allow `sts:AssumeRoleWithWebIdentity`
- Have a condition scoped to your repository and environment, e.g.:
  - `repo:<owner>/<repo>:environment:dev`

### Discover the role in the target account
```bash
# List candidate roles
aws iam list-roles --query 'Roles[?contains(RoleName, `deploy`) || contains(RoleName, `github`) || contains(RoleName, `oidc`)].RoleName' --output text

# Inspect trust policy for a candidate
aws iam get-role --role-name <RoleName> --query 'Role.AssumeRolePolicyDocument' --output json
```

If no role exists yet, request one through Cloud One / CBIIT intake with trust conditions scoped to your repo and environments.

Once you have the ARN, set it as the `AWS_DEPLOY_ROLE_ARN` secret in each GitHub environment.

## Phase 6 — First Deployment

### 6.1 Dry run (create change set only)
```bash
gh workflow run deploy.yml \
  -R <owner>/<repo> \
  -f environment=dev \
  -f dry_run=true
```
Review the change set in the Actions log before executing.

### 6.2 Execute deployment
```bash
gh workflow run deploy.yml \
  -R <owner>/<repo> \
  -f environment=dev \
  -f dry_run=false
```

### 6.3 Monitor the run
```bash
# Get the latest run ID
gh run list -R <owner>/<repo> --workflow deploy.yml --limit 3

# Poll status (non-interactive)
gh api repos/<owner>/<repo>/actions/runs/<run_id> \
  --jq '{status: .status, conclusion: (.conclusion // "running"), updated_at: .updated_at}'
```

> **Note:** The `Setup SAM CLI` step can appear stalled for 3–5 minutes; this is normal runner startup behavior. Wait at least 10 minutes before treating a run as genuinely stuck.

### 6.4 Extract the deployed endpoint
```bash
gh run view -R <owner>/<repo> <run_id> --log | grep -E "AppApiUrl|execute-api|lambda-url"
```

## Phase 7 — Post-Deploy Smoke Test
```bash
# Root route
curl -sf "https://<endpoint>/<stage>/" | head -c 500

# Health/status route (if implemented)
curl -sf "https://<endpoint>/<stage>/health"
```

Expected: HTTP 200 for both routes.

## Known Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| OIDC auth error in `configure-aws-credentials` | Trust policy missing repo/environment condition | Update role trust: add `repo:<owner>/<repo>:environment:<env>` |
| `Setup SAM CLI` appears stuck | Slow runner startup | Wait 10 min; cancel and retry once if still no progress |
| `ROLLBACK_COMPLETE` on first deploy | CloudFormation created the stack in a failed state | Delete the failed stack (`aws cloudformation delete-stack --stack-name <name>`) then redeploy |
| SCP deny on `apigateway:POST` | Organization policy blocks API Gateway stage creation | Use Lambda Function URL instead of API Gateway |
| `No changes to deploy. Stack ... is up to date.` | Code unchanged since last deploy | Expected; not a failure |
| Missing variable/secret error in validation step | Variable or secret not set in the GitHub environment | Set it via `gh variable set` / `gh secret set` for the target environment |
| `sam deploy` fails with "no S3 bucket" | `--resolve-s3` not in deploy command | Ensure `--resolve-s3` flag is present; do not pass `--s3-bucket` unless a known bucket is supplied |
