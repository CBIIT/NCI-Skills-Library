---
name: cloud-one-github-actions-java-lambda-deployment
description: 'Deploy a Java 21 Maven Lambda application to NCI Cloud One Development through GitHub Actions and AWS SAM. Use for Java applications that need the shared Cloud One OIDC, permission-boundary, MCP-first GitHub, dry-run, registry, and verification controls. Do not use for Python or Node.js applications or production deployment.'
argument-hint: 'Provide app name, GitHub repository (owner/repo), and Cloud One Development account'
user-invocable: true
---

# Cloud One GitHub Actions Java Lambda Deployment

Deploy a Java 21 Maven application to the NCI Cloud One Development non-production tier. First read and apply the shared [Cloud One deployment foundation](cloud-one-deploy.md), then use the Java-specific application, SAM, workflow, validation, and failure guidance below.

## Java application contract

The repository must contain:

- `pom.xml` compiling with `maven.compiler.release=21`.
- A Lambda handler compatible with API Gateway v2 / Lambda Function URL events.
- A local server or test harness that exercises the same routing and rendering core as the Lambda handler.
- `template.yaml` using `Runtime: java21`.
- A `Makefile` when SAM needs a custom build to stage the shaded JAR.
- `.github/workflows/deploy.yml`.
- Tests for the root and `/health` routes, including a version 2 event for the Lambda handler.

Keep routing and response construction outside the transport adapters so local HTTP and Lambda tests exercise the same application behavior. Package runtime dependencies into one shaded JAR with Maven Shade. Align the Maven `finalName`, Makefile source JAR, and SAM handler exactly.

## Choose the endpoint architecture first

| Requirement | Architecture |
|---|---|
| Simple public Development web app or API that needs only HTTPS invocation | **Lambda Function URL** |
| Authentication or authorization at the gateway, request validation, throttling, usage plans, gateway-managed routing, or another explicit API management feature | **API Gateway**, only after confirming the account permits it |
| Private or sensitive application that cannot safely use a public URL | Do not use `AuthType: NONE`; select an approved authenticated architecture |

For a simple public Development application, use a Lambda Function URL by default. Record public exposure in the approval envelope.

## Boundary-safe Function URL SAM template

Cloud One PowerUser guardrails can reject SAM-generated roles. Define the execution role explicitly with the required name prefix and permission boundary. This baseline assumes Maven produces `target/app.jar` and the Makefile stages it for SAM:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: java21
    Architectures:
      - arm64
    MemorySize: 512
    Timeout: 15

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
    Metadata:
      BuildMethod: makefile
    Properties:
      Handler: gov.nih.nci.app.LambdaHandler::handleRequest
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

Use a custom SAM build only when needed. A minimal Makefile for the baseline is:

```makefile
.PHONY: build-AppFunction

build-AppFunction:
	mkdir -p "$(ARTIFACTS_DIR)/lib"
	cp target/app.jar "$(ARTIFACTS_DIR)/lib/app.jar"
```

Replace the example handler package and JAR name consistently. The dry-run review must contain only the expected execution role, function, Function URL, and public invoke permissions. Grant only additional runtime permissions the application requires.

If requirements select API Gateway, add the API resource and both `/` and `/{proxy+}` events, use `OpenApiVersion: '3.0.1'`, add an `ApiStageName` parameter, and pass it from the workflow. Confirm API Gateway creation is permitted before dispatching.

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

      - name: Setup Java
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven

      - name: Test and package
        run: mvn --batch-mode verify

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

Before publishing:

```bash
mvn -version
mvn --batch-mode verify
sam validate --lint
sam build
```

Require `mvn -version` to report Java 21. Start the local HTTP server or test harness, load the root through `http://localhost`, and require HTTP 200 from `/health`.

Then follow the shared foundation to verify or create the deploy role, configure and read back the GitHub `dev` environment, publish the source through MCP, run and inspect the dry deployment, execute the reviewed change set, smoke-test the exact Function URL root and `/health`, and reconcile the existing registry entry.

## Java-specific failure checks

- `UnsupportedClassVersionError`: Maven and Lambda runtime versions differ; compile and deploy with Java 21.
- `ClassNotFoundException` or `NoClassDefFoundError`: verify the shaded JAR contains the handler and runtime dependencies and that the Makefile stages it under `lib/`.
- Handler resolution failure: confirm SAM uses the exact fully qualified class and method.
- Function URL event mismatch: test with an API Gateway v2 payload (`version: "2.0"`) and return a response with status, headers, and body.
- `CodeUri` or JAR missing during `sam build`: run Maven packaging first and align `finalName`, the Makefile path, and `template.yaml`.
- Cold-start timeout: measure before increasing memory or timeout; do not mask handler or packaging failures.
- SAM-generated role rejected: use the explicit `power-user` execution role with the required boundary.
- Function URL returns 403: confirm the SAM-generated URL and public invoke permissions exist and that public exposure was intended.

Do not treat a successful Maven or SAM build as deployment success. Apply every completion criterion in the shared foundation.
