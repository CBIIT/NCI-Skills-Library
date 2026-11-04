---
name: app-dashboard
description: Adds a dashboard web page (GET /dashboard) and a REST API (GET /api/dashboard) to every web app, REST API, or MCP server generated through the NCI startup flow. Shows health, runtime, usage, deployment, test cases, documentation, and outstanding issues, and publishes the API URL to the NCI Skills Registry as dashboardApiUrl.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, Python, JavaScript, HTML
Framework: Flask, Express, MCP Python SDK, GitHub Actions
---

# App Dashboard Skill

Every web app, REST API, and MCP server created through `nci-startup` gets the same two read-only endpoints:

| Route | Returns |
|---|---|
| `GET /dashboard` | A self-contained HTML page for people |
| `GET /api/dashboard` | The JSON document the page renders, for tools and the NCI Skills Registry |

The page and API always agree because the page only renders what `/api/dashboard` returns.

This skill does not apply to the local command-line script type (`hello-world-cli`), which has no HTTP surface.

## Template files

Copy these from `framework/startup/app-dashboard/` into the generated project. Do not rewrite them from memory; the templates are the tested implementation.

| Template | Copy to | Use for |
|---|---|---|
| `python/dashboard.py` | project root | Flask apps and APIs (`register_flask`), Python MCP servers (`register_fastmcp`) |
| `node/dashboard.mjs` | project root | Express apps and APIs (`registerDashboard`) |
| `dashboard.html` | project root, next to the module | All |
| `scripts/build_dashboard_snapshot.py` | `scripts/` | All |
| `dashboard.config.example.json` | `dashboard.config.json`, then fill in | All |

For Java or other runtimes, implement the same routes and the payload contract below by hand, and reuse `dashboard.html` unchanged.

## Payload contract (schemaVersion 1)

`GET /api/dashboard` returns HTTP 200 with `Cache-Control: no-store` and these top-level keys:

- `schemaVersion`: integer, currently `1`.
- `generatedAt`: ISO 8601 UTC time.
- `app`: `id`, `name`, `description`, `version`, `owner`, `repository`, `appType`, `skillsUsed`.
- `health`: `status` (`ok` or `degraded`), `checkedAt`, `checks[]` of `{name, status, detail}`.
- `runtime`: `startedAt`, `uptimeSeconds`, `language`, `framework`.
- `usage`: `scope`, `since`, `totalRequests`, `errorRequests`, `byRoute`, `lastRequestAt`.
- `deployment`: `environment`, `stackName`, `region`, `commit`, `builtAt`, `workflowRunUrl`.
- `tests`: `ranAt`, `summary {total, passed, failed, skipped}`, `cases[] {suite, name, status}`.
- `documentation`: `items[] {title, path, url}`.
- `issues`: `open`, `fetchedAt`, `titlesIncluded`, and `items[] {number, title, url, labels}` when titles are included.

Any block whose data does not exist is `{"status": "unavailable", "reason": "<why>"}`. Never fill a block with a guess, a placeholder, or a sample value. `usage` is counted in memory per running instance, so on Lambda it resets on cold start and covers only that instance; the `scope` field says so. Do not describe it as a global total.

## Where each section's data comes from

Runtime values (`health`, `runtime`, `usage`) are computed live. Everything else is a build-time snapshot, `dashboard-data/snapshot.json`, produced by `scripts/build_dashboard_snapshot.py`. This keeps the running app free of GitHub tokens and outbound calls.

| Section | Source | When missing |
|---|---|---|
| Deployment | `GITHUB_SHA`, `GITHUB_RUN_ID`, `STACK_NAME`, `AWS_REGION`, `ENVIRONMENT` in CI | `unavailable` for local builds |
| Test cases | JUnit XML at `dashboard-data/junit.xml` | `unavailable` until tests are run with JUnit output |
| Documentation | `README.md` and `docs/**/*.md`, linked to the repository at the built commit | `unavailable` |
| Outstanding issues | GitHub Issues API for the repository in `dashboard.config.json` | `unavailable` |

JUnit output commands: `pytest --junitxml=dashboard-data/junit.xml`, `mvn --batch-mode verify` (copy `target/surefire-reports/*.xml` content into one file or point the script at the merged report), or `node --test --test-reporter=junit --test-reporter-destination=dashboard-data/junit.xml`.

## Workflow

1. Confirm the app type is web app, REST API, or MCP server. Skip this skill for the CLI type.
2. Copy the templates listed above. Create `dashboard.config.json` from the example using the values already collected during startup (name, description, owner, repository, version, app type, skills used). Do not ask the user again for values they already provided.
3. Wire the routes into the app:
   - Flask: `import dashboard` then `dashboard.register_flask(app)` after `app = Flask(__name__)`.
   - Express: `import { registerDashboard } from "./dashboard.mjs"` then `registerDashboard(app)` before the other routes.
   - Python MCP server: `dashboard.register_fastmcp(mcp)`, wrap each tool function with `@dashboard.track_tool("<tool name>")`, and serve over the streamable HTTP transport. The routes are plain HTTP routes, not MCP tools, so the "exactly one tool" baseline is unchanged. Over stdio there is no HTTP surface, so verify the dashboard with the HTTP transport.
4. Add a `tests/` test that fetches `/api/dashboard` and checks `schemaVersion == 1`, `health.status == "ok"`, and that `GET /dashboard` returns HTML. Run the tests with JUnit XML output into `dashboard-data/junit.xml`.
5. Run `python scripts/build_dashboard_snapshot.py`, start the local server, and open `http://localhost:<port>/dashboard` in the integrated browser. Never verify with `file://`. Confirm every section renders either data or an explicit "Not available" line, and that no `{{` placeholders appear.
6. Verify the JSON with `curl -sf http://localhost:<port>/api/dashboard` and confirm the keys above.
7. Include the dashboard URL and API URL in the project summary. Keep the page open until the user verifies it, as with the Hello World gate.
8. For cloud deployment, follow the dashboard steps in the Cloud One deployment foundation: run the snapshot script in the deploy workflow before `sam build`, smoke-test `/dashboard` and `/api/dashboard`, and record `dashboardApiUrl` in the registry entry.

## Registry link

After a successful deployment, the registry entry gets `dashboardApiUrl`, the absolute HTTP(S) URL of `/api/dashboard` for the deployed environment. The NCI Skills Registry reads it to show a live summary per application. Set it only after the deployed URL returned HTTP 200 with a valid payload. For local-only or undeployed apps, omit the field.

## Required Guardrails

- Read-only and unauthenticated routes expose only the payload above. Do not add environment variables, hostnames, IP addresses, file paths, stack traces, request bodies, headers, query strings, user identifiers, or credentials.
- `/api/dashboard` sends `Access-Control-Allow-Origin` for `https://cbiit.github.io` only (the Registry site), never `*`, so other websites cannot read it from a user's browser.
- Count requests by route template (for example `/items/<id>`), never by raw URL. Do not record user data.
- Insert every value into the page with `textContent`, never `innerHTML`. Only `http:` and `https:` links are rendered.
- Issue titles are included only when the GitHub repository is public. For a private repository, include the count and set `titlesIncluded` to `false`. Do not include issue bodies or comments.
- If the app's audience is not `public` or `nci-wide`, or its data sensitivity is `pii-phi`, keep the dashboard but tell the user it is reachable by anyone who can reach the app, and confirm before deploying.
- Do not put tokens in the snapshot, config, or workflow. In CI use only the automatic `GITHUB_TOKEN` with read access to issues. Never request or store a personal access token.
- Do not invent test results, issue counts, or deployment facts. Use `unavailable`.
- Do not over-engineer: no database, no background threads, no outbound calls from the running app.

## Quality Checklist

- [ ] `/dashboard` and `/api/dashboard` both return HTTP 200 locally.
- [ ] `schemaVersion` is `1` and every section is present, populated or `unavailable` with a reason.
- [ ] `/health` is unchanged and still returns HTTP 200.
- [ ] `/health`, `/dashboard`, and `/api/dashboard` are excluded from usage counts.
- [ ] A dashboard test exists and its result appears in the Test cases section.
- [ ] No secrets or sensitive values appear in the payload or snapshot.
- [ ] After deployment, both URLs return HTTP 200 on the deployed endpoint and `dashboardApiUrl` is in the registry entry.

## Related

- [Hello World Web App](hello-world-web-app.md), [Hello World API](hello-world-api.md), [Hello World MCP Server](hello-world-mcp-server.md)
- [Cloud One deployment foundation](../cicd/cloud-one-deploy.md)
- [NCI Skill Registration](nci-skill-registration.md)
