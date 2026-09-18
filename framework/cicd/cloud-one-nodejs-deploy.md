---
name: cloud-one-github-actions-nodejs-lambda-deployment
description: 'Deploy a Node.js Lambda or Express application to NCI Cloud One Development through GitHub Actions and AWS SAM. Use for Node.js apps that need boundary-safe Lambda roles, exact GitHub OIDC trust, dry-run review, and verified dev endpoints. Do not use for Python applications or production deployment.'
argument-hint: 'Provide app name, GitHub repository (owner/repo), and Cloud One Development account'
user-invocable: true
---

# Cloud One GitHub Actions Node.js Lambda Deployment

Deploy a Node.js application to the NCI Cloud One Development non-production tier. First read and apply the shared [Cloud One deployment foundation](cloud-one-deploy.md), then use the Node.js-specific application, SAM, workflow, validation, and failure guidance below.

## Node.js application contract

The repository must contain:

- `package.json` and a committed `package-lock.json`.
- A Lambda module that exports `handler`.
- `template.yaml` using a currently supported Node.js Lambda runtime.
- `.github/workflows/deploy.yml`.
- Local tests or smoke checks for the root and `/health` routes.

For an existing Express app, preserve a separately exported Express `app` for local execution and tests, and export a Lambda `handler` through a maintained serverless adapter. Keep local listening code in a separate entry point so importing the Lambda module does not open a port.

Example structure:

```text
app.js
server.js
public/
package.json
package-lock.json
template.yaml
.github/workflows/deploy.yml
```

Example Express boundary:

```javascript
const express = require('express');
const serverless = require('serverless-http');

const app = express();
app.use(express.static('public'));
app.get('/health', (_request, response) => response.json({ status: 'ok' }));

module.exports = {
  app,
  handler: serverless(app)
};
```

## Stage-aware static assets

Keep local static serving unchanged with `express.static('public')`, but do not use root-absolute asset URLs in the deployed HTML. API Gateway serves the application behind a stage prefix such as `/dev/`, so `<link rel="stylesheet" href="/styles.css">` requests the wrong host-root path.

Use document-relative asset URLs in HTML served through API Gateway:

```html
<link rel="stylesheet" href="styles.css">
<script src="app.js" defer></script>
<img src="images/logo.svg" alt="Application logo">
```

Keep these files under `public/`. A page loaded at `/dev/` will then request `/dev/styles.css`, `/dev/app.js`, and `/dev/images/logo.svg` while the local page continues to load the same files normally. Do not add a leading `/` to static asset paths and do not hard-code `/dev/` into the application.

Before deployment, inspect generated HTML for root-absolute local asset references such as `href="/styles.css"` or `src="/app.js"` and replace them with document-relative paths. After deployment, verify both the page and every referenced stylesheet/script/image through the stage-prefixed endpoint, for example `/dev/` and `/dev/styles.css`.

The local entry point may import `app` and listen on `127.0.0.1`. Do not call `listen` from the Lambda module.

## Boundary-safe SAM template

Cloud One PowerUser guardrails can reject SAM-generated roles. Define the Lambda execution role explicitly with the required name prefix and permission boundary.

Use this baseline, replacing `nodejs22.x` only when the target account's SAM validation requires a different supported Node.js runtime:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Parameters:
  ApiStageName:
    Type: String
    Default: dev

Globals:
  Function:
    Runtime: nodejs22.x
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

  AppApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: !Ref ApiStageName
      OpenApiVersion: '3.0.1'

  AppFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      CodeUri: .
      Role: !GetAtt AppFunctionExecutionRole.Arn
      Events:
        Root:
          Type: Api
          Properties:
            Path: /
            Method: ANY
            RestApiId: !Ref AppApi
        Proxy:
          Type: Api
          Properties:
            Path: /{proxy+}
            Method: ANY
            RestApiId: !Ref AppApi

Outputs:
  AppApiUrl:
    Description: API Gateway endpoint URL
    Value: !Sub https://${AppApi}.execute-api.${AWS::Region}.amazonaws.com/${ApiStageName}/
```

Keep `OpenApiVersion: '3.0.1'` to avoid a duplicate hard-coded `Stage` stage. Grant the execution role only the additional runtime permissions the app actually needs.

## GitHub Actions workflow

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

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: npm

      - name: Install and test
        run: |
          npm ci
          npm test

      - name: Setup Python for SAM CLI
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

Use `CAPABILITY_NAMED_IAM` because the template assigns an explicit execution-role name.

## Validate and deploy

Before pushing:

```bash
npm ci
npm test
sam validate --lint
sam build
```

Then follow the shared skill to:

1. Resolve the repository's exact OIDC subject.
2. Verify or create the boundary-constrained deploy role.
3. Obtain explicit approval immediately before attaching `PowerUserAccess` or any equivalent broad managed policy.
4. Configure the GitHub `dev` environment.
5. Commit and push the app and workflow.
6. Run and inspect the dry-run workflow before executing a deployment.
7. Run the execute workflow only after the change set is confirmed to target the selected Development account and stack.

After deployment, obtain `AppApiUrl` and require HTTP 200 from both `/dev/` and `/dev/health`. Record the account, region, stack, role ARN, workflow run, endpoint, and smoke-test result without recording credentials.

## Node.js-specific failure checks

- `Cannot find module`: confirm the dependency is in `dependencies`, not only `devDependencies`, and that `package-lock.json` is committed.
- Handler import or export failure: confirm the SAM handler matches `<module>.<export>`, normally `app.handler`.
- Local server starts during Lambda import: move `listen` into a separate local entry point.
- Stylesheet or script missing after deployment: check for root-absolute asset URLs beginning with `/`; use document-relative paths and verify the asset through the API Gateway stage prefix.
- Runtime rejected by SAM or Lambda: select a supported Node.js runtime for the target account and keep the GitHub Actions Node version aligned with it.
- API Gateway route mismatch: keep both `/` and `/{proxy+}` events and test the `/dev/` stage explicitly.

Do not treat a successful SAM build as deployment success. Completion requires exact OIDC trust, the permission boundary and policies, reviewed dry run, successful execute run, and HTTP 200 smoke tests for the deployed root and health routes.
