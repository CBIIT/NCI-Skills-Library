"""NCI application dashboard (contract schemaVersion 1, template version 2).

Copy this file, ops_status.py, dashboard.html and the dashboard-data/ folder into the app root.
Adds:  GET /dashboard      -> HTML page
       GET /api/dashboard  -> JSON payload

No secrets are read or exposed. Build-time facts (tests, docs, issues, deployment)
come from dashboard-data/snapshot.json, written by scripts/build_dashboard_snapshot.py.
Operational Status (uptime and request statistics) comes from the scheduled probe in probe.py.
Usage counters are in memory and per running instance.
"""
import functools
import json
import os
import platform
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
# Bump when the template changes in a way an installed copy should be upgraded for. Skills detect this to install or upgrade.
DASHBOARD_TEMPLATE_VERSION = 2
# Only the NCI Skills Registry site may read /api/dashboard from a browser on another origin.
REGISTRY_ORIGIN = "https://cbiit.github.io"
_API_HEADERS = {"Cache-Control": "no-store", "Access-Control-Allow-Origin": REGISTRY_ORIGIN, "Vary": "Origin"}
_ROOT = Path(__file__).resolve().parent
_SNAPSHOT = _ROOT / "dashboard-data" / "snapshot.json"
_HTML = _ROOT / "dashboard.html"
_EXCLUDED_ROUTES = {"/health", "/dashboard", "/api/dashboard"}
_MAX_ROUTES = 50  # cap route cardinality so unmatched paths cannot grow memory

_lock = threading.Lock()
_started = time.time()


def _iso(ts=None):
    return datetime.fromtimestamp(ts if ts is not None else time.time(), timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


_usage = {"since": _iso(_started), "total": 0, "errors": 0, "by_route": {}, "last_request_at": None}


def record_request(route, status):
    """Count one request. `route` must be a route template, never a raw URL with ids or query strings."""
    if route in _EXCLUDED_ROUTES:
        return
    with _lock:
        _usage["total"] += 1
        if status >= 500:
            _usage["errors"] += 1
        by_route = _usage["by_route"]
        key = route if (route in by_route or len(by_route) < _MAX_ROUTES) else "(other)"
        by_route[key] = by_route.get(key, 0) + 1
        _usage["last_request_at"] = _iso()


def track_tool(name):
    """Decorator for MCP tools: counts each call as route 'tool:<name>'."""
    def wrap(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            try:
                result = fn(*args, **kwargs)
            except Exception:
                record_request("tool:" + name, 500)
                raise
            record_request("tool:" + name, 200)
            return result
        return inner
    return wrap


def _snapshot():
    try:
        return json.loads(_SNAPSHOT.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _unavailable(reason):
    return {"status": "unavailable", "reason": reason}


def _not_applicable(reason):
    return {"status": "not_applicable", "reason": reason}


def _running_in_cloud():
    return bool(os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))


_CI_ONLY = {"deployment", "deploymentHistory"}

# What each snapshot-based section is, shown instead of an error when the app runs locally.
_LOCAL_NOTES = {
    "deployment": "the version, commit and stack that the deploy workflow released to Cloud One",
    "deploymentHistory": "recent runs of the GitHub Actions deploy workflow",
    "tests": "unit-test results recorded by the deploy workflow",
    "documentation": "the project documents published with the repository",
    "issues": "open GitHub issues for the repository",
    "dependencies": "known vulnerabilities in the app's dependencies (pip-audit and Dependabot)",
}


def _snapshot_block(snap, key):
    """Return a snapshot block, or say why it is missing: not applicable locally, unavailable in the cloud."""
    block = snap.get(key)
    ci_only_placeholder = key in _CI_ONLY and (block or {}).get("status") == "unavailable"
    if block and not (ci_only_placeholder and not _running_in_cloud()):
        return block
    if _running_in_cloud():
        return _unavailable("dashboard-data/snapshot.json was not built for this deployment")
    return _not_applicable(f"This is {_LOCAL_NOTES[key]}. It exists only for the Cloud One deployment, so it does not apply when running locally.")


UPTIME_TARGET_PERCENT = 99.0


def _summary(p):
    """Combine live health, monitoring freshness, and known engineering concerns."""
    bad, unknown, warn = [], [], []
    health = (p.get("health") or {}).get("status")
    if health == "degraded":
        bad.append("A live health check is failing")
    elif health != "ok":
        unknown.append("Live health is unavailable")

    ops = p.get("operations") or {}
    if ops.get("status") == "not_applicable":
        pass
    elif not ops or ops.get("status") == "unavailable":
        unknown.append("Synthetic monitoring is unavailable")
    else:
        probe = ops.get("probe") or {}
        last = probe.get("lastCheck") or {}
        if ops.get("stale") is not False:
            unknown.append("Synthetic monitoring is stale or its freshness is unknown")
        elif last.get("ok") is False:
            bad.append("The latest synthetic health check failed")
        elif last.get("ok") is not True:
            unknown.append("The latest synthetic health check is unavailable")
        if probe.get("recordError"):
            unknown.append("The latest synthetic check could not be recorded")
        if (ops.get("metrics") or {}).get("status") == "unavailable":
            unknown.append("CloudWatch metrics are unavailable")
        up = ((ops.get("uptime") or {}).get("24h") or {}).get("percent")
        if up is None:
            unknown.append("Synthetic availability has no reported checks")
        elif not ops.get("stale") and up < UPTIME_TARGET_PERCENT:
            warn.append(f"Synthetic availability over 24 hours is {up:g}%, below the {UPTIME_TARGET_PERCENT:g}% target")
        req = (ops.get("requests") or {}).get("24h") or {}
        if req.get("total") is None or (req["total"] > 0 and req.get("successPercent") is None):
            unknown.append("Function URL request metrics are unavailable")
        elif not ops.get("stale") and req.get("successPercent") is not None and req["successPercent"] < UPTIME_TARGET_PERCENT:
            warn.append(f"Only {req['successPercent']:g}% of Function URL requests avoided 5xx responses over 24 hours")
        if not ops.get("stale") and req.get("throttles"):
            warn.append(f"{req['throttles']} requests were throttled over 24 hours")

    failed = ((p.get("tests") or {}).get("summary") or {}).get("failed")
    if failed:
        warn.append(f"{failed} test(s) failed in the deployed build")
    alerts = (p.get("dependencies") or {}).get("totalAlerts")
    if alerts:
        warn.append("Dependency or security findings are present")
    status = "degraded" if bad else "unknown" if unknown else "attention" if warn else "ok"
    return {"status": status, "reasons": bad + unknown + warn, "lastDeployedAt": (p.get("deployment") or {}).get("builtAt")}


def build_payload(health_checks=None, operations=None):
    """Assemble the dashboard document. Never invents data: missing blocks say 'unavailable'.

    operations: optional callable returning the Operational Status block (uptime and request statistics).
    """
    snap = _snapshot()
    checks = [{"name": "Application", "status": "ok", "detail": "responding",
               "description": "The app itself is running and answered this request."}] + list(health_checks or [])
    overall = "ok" if all(c["status"] == "ok" for c in checks) else "degraded"
    with _lock:
        usage = {
            "scope": "this running instance since it started",
            "since": _usage["since"],
            "totalRequests": _usage["total"],
            "errorRequests": _usage["errors"],
            "byRoute": dict(_usage["by_route"]),
            "lastRequestAt": _usage["last_request_at"],
        }
    ops_block = operations() if callable(operations) else _not_applicable(
        "Uptime comes from a scheduled health-check probe that exists only in the Cloud One deployment.")
    payload = {
        "sampleData": bool(ops_block.get("sample")),
        "schemaVersion": SCHEMA_VERSION,
        "templateVersion": DASHBOARD_TEMPLATE_VERSION,
        "generatedAt": _iso(),
        "app": snap.get("app") or {"name": "Unknown application"},
        "health": {"status": overall, "checkedAt": _iso(), "checks": checks},
        "runtime": {
            "startedAt": _iso(_started),
            "uptimeSeconds": int(time.time() - _started),
            "language": "python " + platform.python_version(),
            "framework": snap.get("framework"),
        },
        "usage": usage,
        "deployment": _snapshot_block(snap, "deployment"),
        "tests": _snapshot_block(snap, "tests"),
        "documentation": _snapshot_block(snap, "documentation"),
        "issues": _snapshot_block(snap, "issues"),
        "operations": ops_block,
        "deploymentHistory": _snapshot_block(snap, "deploymentHistory"),
        "dependencies": _snapshot_block(snap, "dependencies"),
    }
    payload["summary"] = _summary(payload)
    return payload


def html_page():
    return _HTML.read_text(encoding="utf-8")


# ---- Flask -----------------------------------------------------------------
def register_flask(app, health_checks=None, operations=None):
    """Register routes and request counting on a Flask app.

    health_checks: optional callable returning extra check dicts. operations: optional callable returning the
    Operational Status block.
    """
    from flask import jsonify, request, Response

    @app.after_request
    def _count(response):
        rule = request.url_rule.rule if request.url_rule else "(unmatched)"
        record_request(rule, response.status_code)
        return response

    @app.get("/dashboard")
    def _dashboard_page():
        return Response(html_page(), mimetype="text/html")

    @app.get("/api/dashboard")
    def _dashboard_api():
        response = jsonify(build_payload(health_checks() if callable(health_checks) else health_checks, operations))
        response.headers.update(_API_HEADERS)
        return response


# ---- MCP server (official Python SDK, streamable HTTP) ---------------------
def register_fastmcp(mcp, health_checks=None, operations=None):
    """Add the dashboard routes to a FastMCP server. Only reachable over the HTTP transport, not stdio.

    Dashboard routes are plain HTTP routes, not MCP tools, so the server still exposes only its own tools.
    """
    from starlette.responses import HTMLResponse, JSONResponse

    @mcp.custom_route("/dashboard", methods=["GET"])
    async def _page(request):
        return HTMLResponse(html_page())

    @mcp.custom_route("/api/dashboard", methods=["GET"])
    async def _api(request):
        return JSONResponse(build_payload(health_checks() if callable(health_checks) else health_checks, operations), headers=_API_HEADERS)
