#!/usr/bin/env python3
"""Build dashboard-data/snapshot.json for the NCI app dashboard (schemaVersion 1).

Run from the app root, locally or in CI before packaging:

    python scripts/build_dashboard_snapshot.py

Inputs
  dashboard.config.json        committed app metadata (see dashboard.config.example.json)
  dashboard-data/junit.xml     optional JUnit XML from the test run (pytest --junitxml, mvn surefire, node --test --test-reporter=junit)
  README.md, docs/**/*.md      documentation index
  dashboard-data/pip-audit.json optional `pip-audit -r requirements.txt -f json` output (dependency vulnerabilities)
  env: GITHUB_SHA, GITHUB_RUN_ID, GITHUB_REPOSITORY, GITHUB_SERVER_URL, STACK_NAME, AWS_REGION, ENVIRONMENT
  env: GITHUB_TOKEN            optional; only the automatic Actions token is expected, never a personal access token
                               (needs issues: read, actions: read for deploy history, security-events: read for Dependabot)
  env: GITHUB_WORKFLOW_REF     set by Actions; identifies the deploy workflow for the deploy history

Missing inputs produce {"status": "unavailable", "reason": ...}; nothing is invented.
The snapshot contains no secrets. Issue titles and vulnerable package names are included only for public repositories.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
OUT = ROOT / "dashboard-data" / "snapshot.json"
MAX_CASES = 300
MAX_ISSUES = 50
MAX_DEPLOYS = 8
MAX_GITHUB_PAGES = 100


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def unavailable(reason):
    return {"status": "unavailable", "reason": reason}


def load_config():
    path = ROOT / "dashboard.config.json"
    if not path.exists():
        sys.exit("dashboard.config.json not found; copy dashboard.config.example.json and fill it in")
    config = json.loads(path.read_text(encoding="utf-8"))
    for key in ("id", "name", "repository"):
        if not config.get(key):
            sys.exit(f"dashboard.config.json is missing required field: {key}")
    return config


def repo_slug(repository):
    match = re.match(r"^https://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$", repository or "")
    return match.group(1) if match else None


def deployment():
    env = os.environ
    if not any(env.get(k) for k in ("GITHUB_SHA", "STACK_NAME", "ENVIRONMENT")):
        return unavailable("not built in CI; local snapshot")
    run_url = None
    if env.get("GITHUB_RUN_ID") and env.get("GITHUB_REPOSITORY"):
        run_url = f"{env.get('GITHUB_SERVER_URL', 'https://github.com')}/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}"
    return {
        "environment": env.get("ENVIRONMENT") or "dev",
        "stackName": env.get("STACK_NAME"),
        "region": env.get("AWS_REGION"),
        "commit": env.get("GITHUB_SHA"),
        "builtAt": now(),
        "workflowRunUrl": run_url,
    }


def tests():
    path = ROOT / "dashboard-data" / "junit.xml"
    if not path.exists():
        return unavailable("no dashboard-data/junit.xml; run the tests with JUnit XML output before building the snapshot")
    root = ET.parse(path).getroot()
    cases = []
    for case in root.iter("testcase"):
        status = "passed"
        if case.find("failure") is not None or case.find("error") is not None:
            status = "failed"
        elif case.find("skipped") is not None:
            status = "skipped"
        cases.append({"suite": case.get("classname") or "", "name": case.get("name") or "", "status": status})
    count = lambda s: sum(1 for c in cases if c["status"] == s)
    return {
        "ranAt": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {"total": len(cases), "passed": count("passed"), "failed": count("failed"), "skipped": count("skipped")},
        "cases": cases[:MAX_CASES],
        "truncated": len(cases) > MAX_CASES,
    }


def documentation(config, commit):
    files = [p for p in [ROOT / "README.md", *sorted((ROOT / "docs").glob("**/*.md"))] if p.is_file()]
    if not files:
        return unavailable("no README.md or docs/*.md found")
    ref = commit or "main"
    items = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        title = rel
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
                break
        items.append({"title": title, "path": rel, "url": f"{config['repository'].rstrip('/')}/blob/{ref}/{rel}"})
    return {"items": items}


def github_get(url):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "nci-app-dashboard"}
    if os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def github_pages(url):
    items = []
    separator = "&" if "?" in url else "?"
    for page in range(1, MAX_GITHUB_PAGES + 1):
        batch = github_get(f"{url}{separator}per_page=100&page={page}")
        if not isinstance(batch, list):
            raise ValueError("GitHub returned an unexpected page")
        items.extend(batch)
        if len(batch) < 100:
            return items
    raise ValueError("GitHub pagination limit reached")


def issues(config):
    slug = repo_slug(config["repository"])
    if not slug:
        return unavailable("repository is not a github.com URL")
    try:
        repo = github_get(f"https://api.github.com/repos/{slug}")
        raw = github_pages(f"https://api.github.com/repos/{slug}/issues?state=open")
    except (urllib.error.URLError, OSError, ValueError) as err:
        return unavailable(f"GitHub issues could not be read ({type(err).__name__})")
    open_issues = [i for i in raw if "pull_request" not in i]
    block = {"open": len(open_issues), "fetchedAt": now(), "titlesIncluded": not repo.get("private", True)}
    if block["titlesIncluded"]:
        block["items"] = [
            {"number": i["number"], "title": i["title"], "url": i["html_url"], "labels": [l["name"] for l in i.get("labels", [])]}
            for i in open_issues[:MAX_ISSUES]
        ]
    return block


def is_public(slug):
    try:
        return not github_get(f"https://api.github.com/repos/{slug}").get("private", True)
    except (urllib.error.URLError, OSError, ValueError):
        return False


def deployment_history(config):
    slug = repo_slug(config["repository"])
    workflow_ref = os.environ.get("GITHUB_WORKFLOW_REF", "")
    match = re.search(r"/\.github/workflows/([^@/]+)@", workflow_ref)
    if not slug or not match:
        return unavailable("not built in GitHub Actions; deploy history is read from the deploy workflow's runs")
    try:
        raw = github_get(f"https://api.github.com/repos/{slug}/actions/workflows/{match.group(1)}/runs?per_page={MAX_DEPLOYS}")
    except (urllib.error.URLError, OSError, ValueError) as err:
        return unavailable(f"workflow runs could not be read ({type(err).__name__})")
    current = os.environ.get("GITHUB_RUN_ID")
    items = []
    for run in raw.get("workflow_runs", [])[:MAX_DEPLOYS]:
        title = run.get("display_title") or ""
        items.append({
            "runNumber": run.get("run_number"),
            # Runs started before the run-name was added are titled just "deploy", so their type is unknown.
            "dryRun": True if "dry run" in title.lower() else False if "deploy dev" in title.lower() else None,
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "commit": (run.get("head_sha") or "")[:12] or None,
            "startedAt": run.get("run_started_at") or run.get("created_at"),
            "url": run.get("html_url"),
            "current": str(run.get("id")) == current,
        })
    return {"fetchedAt": now(), "items": items}


def pip_audit(public):
    path = ROOT / "dashboard-data" / "pip-audit.json"
    if not path.exists():
        return unavailable("no dashboard-data/pip-audit.json; run pip-audit before building the snapshot")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError:
        return unavailable("dashboard-data/pip-audit.json is not valid JSON")
    deps = data.get("dependencies", []) if isinstance(data, dict) else data
    vulns = [
        {"package": d.get("name"), "version": d.get("version"), "id": v.get("id"), "fixVersions": v.get("fix_versions", [])}
        for d in deps for v in d.get("vulns", [])
    ]
    scanned_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    block = {"tool": "pip-audit", "scanned": "requirements.txt", "scannedAt": scanned_at,
             "packagesScanned": len(deps), "count": len(vulns), "detailsIncluded": public}
    if public:
        block["items"] = vulns
    return block


def dependabot(slug, public):
    try:
        raw = github_pages(f"https://api.github.com/repos/{slug}/dependabot/alerts?state=open")
    except urllib.error.HTTPError as err:
        return unavailable(f"Dependabot alerts could not be read (HTTP {err.code}); the workflow token may lack access")
    except (urllib.error.URLError, OSError, ValueError) as err:
        return unavailable(f"Dependabot alerts could not be read ({type(err).__name__})")
    by_severity = {}
    for alert in raw:
        sev = ((alert.get("security_advisory") or {}).get("severity") or "unknown").lower()
        by_severity[sev] = by_severity.get(sev, 0) + 1
    block = {"open": len(raw), "bySeverity": by_severity, "detailsIncluded": public, "fetchedAt": now()}
    if public:
        block["items"] = [
            {
                "package": ((alert.get("dependency") or {}).get("package") or {}).get("name"),
                "severity": (alert.get("security_advisory") or {}).get("severity"),
                "summary": (alert.get("security_advisory") or {}).get("summary"),
                "url": alert.get("html_url"),
            }
            for alert in raw[:MAX_ISSUES]
        ]
    return block


def dependencies(config):
    slug = repo_slug(config["repository"])
    public = is_public(slug) if slug else False
    audit = pip_audit(public)
    bot = dependabot(slug, public) if slug else unavailable("repository is not a github.com URL")
    if audit.get("status") == "unavailable" and bot.get("status") == "unavailable":
        return unavailable(f"{audit['reason']}; {bot['reason']}")
    # Both sources usually report the same advisories, so take the larger count rather than adding them.
    total = max(audit.get("count") or 0, bot.get("open") or 0)
    return {"fetchedAt": now(), "totalAlerts": total, "pipAudit": audit, "dependabot": bot}


def main():
    config = load_config()
    commit = os.environ.get("GITHUB_SHA")
    snapshot = {
        "snapshotVersion": 1,
        "app": {k: config.get(k) for k in ("id", "name", "description", "version", "owner", "repository", "appType", "skillsUsed")},
        "framework": config.get("framework"),
        "deployment": deployment(),
        "tests": tests(),
        "documentation": documentation(config, commit),
        "issues": issues(config),
        "deploymentHistory": deployment_history(config),
        "dependencies": dependencies(config),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    for block in ("deployment", "tests", "documentation", "issues", "deploymentHistory", "dependencies"):
        if snapshot[block].get("status") == "unavailable":
            print(f"  {block}: unavailable - {snapshot[block]['reason']}")


if __name__ == "__main__":
    main()
