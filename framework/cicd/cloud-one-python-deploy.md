---
name: cloud-one-github-actions-lambda-deployment
description: 'Deploy a Python Lambda application to NCI Cloud One Development through GitHub Actions and AWS SAM. Use for Python applications that need the shared Cloud One OIDC, permission-boundary, MCP-first GitHub, dry-run, registry, and verification controls. Do not use for Node.js or Java applications or production deployment.'
argument-hint: 'Provide app name, GitHub repository (owner/repo), and Cloud One Development account'
user-invocable: true
---

# Cloud One GitHub Actions Python Lambda Deployment

Deploy a Python application to the NCI Cloud One Development non-production tier. First read and apply the shared [Cloud One deployment foundation](cloud-one-deploy.md), then use the Python-specific application, SAM, workflow, validation, and failure guidance below.

## Python application contract

The repository must contain:

- `function.py` exporting `lambda_handler`.
- `template.yaml` using a supported Python Lambda runtime.
- `requirements.txt`.
- `.github/workflows/deploy.yml`.
- Local tests for the root and `/health` routes, including an API Gateway v2/Lambda Function URL event when Function URL architecture is selected.

## Choose the endpoint architecture first

Select the endpoint before writing the SAM template:

| Requirement | Architecture |
|---|---|
| Simple public Development web app or API that needs only HTTPS invocation | **Lambda Function URL** |
| Authentication or authorization at the gateway, request validation, throttling, usage plans, gateway-managed routing, or another explicit API management feature | **API Gateway**, only after confirming the account permits it |
| Private or sensitive application that cannot safely use a public URL | Do not use `AuthType: NONE`; select an approved authenticated architecture |

For a simple public Development application, use a Lambda Function URL by default. Do not deploy API Gateway first merely to discover a known organizational restriction. Record public exposure in the approval envelope.

## Boundary-safe Function URL SAM template

Cloud One PowerUser guardrails can reject SAM-generated roles. Define the Lambda execution role explicitly with the required name prefix and permission boundary:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

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

  AppFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: function.lambda_handler
      CodeUri: .
      Role: !GetAtt AppFunctionExecutionRole.Arn
      FunctionUrlConfig:
        AuthType: NONE
        InvokeMode: BUFFERED

Outputs:
  AppUrl:
    Description: Public Lambda Function URL
    Value: !GetAtt AppFunctionUrl.FunctionUrl
  HealthCheckUrl:
    Description: Public health-check URL
    Value: !Sub '${AppFunctionUrl.FunctionUrl}health'
```

SAM synthesizes the Function URL and public invoke permissions. The dry-run review must contain only the expected execution role, function, URL, and invoke permissions. Grant only additional runtime permissions the application needs.

If requirements select API Gateway, add the API resource and both `/` and `/{proxy+}` events, use `OpenApiVersion: '3.0.1'`, add an `ApiStageName` parameter, and pass that parameter from the workflow. Confirm API Gateway creation is permitted before dispatching the deployment.

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

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install and test
        run: |
          python -m pip install -r requirements.txt
          python -m unittest discover

      - name: Setup SAM CLI
        run: pip install aws-sam-cli

      - name: Validate required variables
        run: |
          test -n "$AWS_REGION" || (echo "Missing variable: AWS_REGION" && exit 1)
          test -n "$STACK_NAME" || (echo "Missing variable: STACK_NAME" && exit 1)
          test "$AWS_REGION" = "us-east-1" || (echo "AWS_REGION must be us-east-1 (N. Virginia); got $AWS_REGION" && exit 1)

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
            --capabilities CAPABILITY_NAMED_IAM

      - name: Deploy
        if: ${{ !inputs.dry_run }}
        run: |
          sam deploy \
            --stack-name "$STACK_NAME" \
            --region "$AWS_REGION" \
            --resolve-s3 \
            --no-fail-on-empty-changeset \
            --capabilities CAPABILITY_NAMED_IAM
```

Use `CAPABILITY_NAMED_IAM` because the template assigns an explicit execution-role name.

## Validate and deploy

Before pushing:

```bash
python -m pip install -r requirements.txt
python -m unittest discover
sam validate --lint
sam build
```

Then follow the shared foundation to verify or create the deploy role, configure and read back the GitHub `dev` environment, pass the hard pre-dispatch gate, run and inspect the dry deployment, execute the reviewed change set, and smoke-test the exact root and `/health` URLs from the stack outputs. Function URLs have no stage-path prefix.

## Python-specific failure checks

- Import failure: confirm required packages are present in `requirements.txt` and included in the SAM build artifact.
- Handler failure: confirm the SAM handler matches `<module>.<function>`, normally `function.lambda_handler`.
- Runtime rejected by SAM or Lambda: select a supported Python runtime for the target account and align the GitHub Actions Python version.
- Function URL returns 403: confirm the SAM-generated URL and public invoke permissions exist and that public exposure was intended.
- Function URL handler mismatch: test with an API Gateway v2 payload (`version: "2.0"`) and confirm the adapter handles the root path and `/health`.
- API Gateway route mismatch, when API Gateway was intentionally selected: keep both `/` and `/{proxy+}` events, retain `OpenApiVersion: '3.0.1'`, and test the configured stage explicitly.

Do not treat a successful SAM build as deployment success. Apply every completion criterion in the shared foundation.
