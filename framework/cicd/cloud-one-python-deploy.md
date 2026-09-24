---
name: cloud-one-github-actions-lambda-deployment
description: 'Deploy a Python Lambda application to NCI Cloud One Development through GitHub Actions and AWS SAM. Use for Python applications that need the shared Cloud One OIDC, permission-boundary, dry-run, and verification controls. Do not use for Node.js applications or production deployment.'
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
- Local tests or smoke checks for the root and `/health` routes.

## Boundary-safe SAM template

Cloud One PowerUser guardrails can reject SAM-generated roles. Define the Lambda execution role explicitly with the required name prefix and permission boundary:

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

  AppApi:
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

Keep `OpenApiVersion: '3.0.1'` to avoid a duplicate hard-coded `Stage` stage. Grant only the additional runtime permissions the application needs.

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
python -m pip install -r requirements.txt
python -m unittest discover
sam validate --lint
sam build
```

Then follow the shared foundation to verify or create the deploy role, configure the GitHub `dev` environment, run and inspect the dry deployment, execute the reviewed change set, and smoke-test the root and `/health` routes.

## Python-specific failure checks

- Import failure: confirm required packages are present in `requirements.txt` and included in the SAM build artifact.
- Handler failure: confirm the SAM handler matches `<module>.<function>`, normally `function.lambda_handler`.
- Runtime rejected by SAM or Lambda: select a supported Python runtime for the target account and align the GitHub Actions Python version.
- API Gateway route mismatch: keep both `/` and `/{proxy+}` events and test the `/dev/` stage explicitly.

Do not treat a successful SAM build as deployment success. Apply every completion criterion in the shared foundation.
