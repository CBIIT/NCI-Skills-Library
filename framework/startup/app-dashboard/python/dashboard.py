"""NCI application dashboard (contract schemaVersion 1).

Copy this file, dashboard.html and the dashboard-data/ folder into the app root.
Adds:  GET /dashboard      -> HTML page
       GET /api/dashboard  -> JSON payload

No secrets are read or exposed. Build-time facts (tests, docs, issues, deployment)
come from dashboard-data/snapshot.json, written by scripts/build_dashboard_snapshot.py.
Usage counters are in memory and per running instance.
"""
import functools
import json
import platform
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
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


def build_payload(health_checks=None):
    """Assemble the dashboard document. Never invents data: missing blocks say 'unavailable'."""
    snap = _snapshot()
    checks = [{"name": "process", "status": "ok", "detail": "responding"}] + list(health_checks or [])
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
    missing = "dashboard-data/snapshot.json was not built for this deployment"
    return {
        "schemaVersion": SCHEMA_VERSION,
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
        "deployment": snap.get("deployment") or _unavailable(missing),
        "tests": snap.get("tests") or _unavailable(missing),
        "documentation": snap.get("documentation") or _unavailable(missing),
        "issues": snap.get("issues") or _unavailable(missing),
    }


def html_page():
    return _HTML.read_text(encoding="utf-8")


# ---- Flask -----------------------------------------------------------------
def register_flask(app, health_checks=None):
    """Register routes and request counting on a Flask app. health_checks: optional callable returning extra check dicts."""
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
        response = jsonify(build_payload(health_checks() if callable(health_checks) else health_checks))
        response.headers.update(_API_HEADERS)
        return response


# ---- MCP server (official Python SDK, streamable HTTP) ---------------------
def register_fastmcp(mcp, health_checks=None):
    """Add the dashboard routes to a FastMCP server. Only reachable over the HTTP transport, not stdio.

    Dashboard routes are plain HTTP routes, not MCP tools, so the server still exposes only its own tools.
    """
    from starlette.responses import HTMLResponse, JSONResponse

    @mcp.custom_route("/dashboard", methods=["GET"])
    async def _page(request):
        return HTMLResponse(html_page())

    @mcp.custom_route("/api/dashboard", methods=["GET"])
    async def _api(request):
        return JSONResponse(build_payload(health_checks() if callable(health_checks) else health_checks), headers=_API_HEADERS)
