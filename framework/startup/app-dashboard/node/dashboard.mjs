// NCI application dashboard (contract schemaVersion 1). Express version.
//
// Copy this file, dashboard.html and the dashboard-data/ folder into the app root.
// Adds:  GET /dashboard      -> HTML page
//        GET /api/dashboard  -> JSON payload
// No secrets are read or exposed. Build-time facts come from dashboard-data/snapshot.json,
// written by scripts/build_dashboard_snapshot.py. Usage counters are in memory, per running instance.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const SCHEMA_VERSION = 1;
// Only the NCI Skills Registry site may read /api/dashboard from a browser on another origin.
const REGISTRY_ORIGIN = "https://cbiit.github.io";
const EXCLUDED = new Set(["/health", "/dashboard", "/api/dashboard"]);
const MAX_ROUTES = 50;
const started = Date.now();
const iso = (ms = Date.now()) => new Date(ms).toISOString().replace(/\.\d{3}Z$/, "Z");

const usage = { since: iso(started), total: 0, errors: 0, byRoute: {}, lastRequestAt: null };

export function recordRequest(route, status) {
  if (EXCLUDED.has(route)) return;
  usage.total += 1;
  if (status >= 500) usage.errors += 1;
  const key = route in usage.byRoute || Object.keys(usage.byRoute).length < MAX_ROUTES ? route : "(other)";
  usage.byRoute[key] = (usage.byRoute[key] ?? 0) + 1;
  usage.lastRequestAt = iso();
}

function snapshot() {
  try {
    return JSON.parse(readFileSync(path.join(ROOT, "dashboard-data", "snapshot.json"), "utf8"));
  } catch {
    return {};
  }
}

const unavailable = (reason) => ({ status: "unavailable", reason });

export function buildPayload(extraChecks = []) {
  const snap = snapshot();
  const checks = [{ name: "process", status: "ok", detail: "responding" }, ...extraChecks];
  const missing = "dashboard-data/snapshot.json was not built for this deployment";
  return {
    schemaVersion: SCHEMA_VERSION,
    generatedAt: iso(),
    app: snap.app ?? { name: "Unknown application" },
    health: { status: checks.every((c) => c.status === "ok") ? "ok" : "degraded", checkedAt: iso(), checks },
    runtime: {
      startedAt: iso(started),
      uptimeSeconds: Math.floor((Date.now() - started) / 1000),
      language: `node ${process.version}`,
      framework: snap.framework ?? null,
    },
    usage: {
      scope: "this running instance since it started",
      since: usage.since,
      totalRequests: usage.total,
      errorRequests: usage.errors,
      byRoute: { ...usage.byRoute },
      lastRequestAt: usage.lastRequestAt,
    },
    deployment: snap.deployment ?? unavailable(missing),
    tests: snap.tests ?? unavailable(missing),
    documentation: snap.documentation ?? unavailable(missing),
    issues: snap.issues ?? unavailable(missing),
  };
}

// Register routes and request counting. Call before other routes so counting sees every request.
export function registerDashboard(app, healthChecks = () => []) {
  app.use((req, res, next) => {
    res.on("finish", () => recordRequest(req.route?.path ?? "(unmatched)", res.statusCode));
    next();
  });
  app.get("/dashboard", (req, res) => {
    res.type("html").send(readFileSync(path.join(ROOT, "dashboard.html"), "utf8"));
  });
  app.get("/api/dashboard", (req, res) => {
    res.set({ "Cache-Control": "no-store", "Access-Control-Allow-Origin": REGISTRY_ORIGIN, Vary: "Origin" }).json(buildPayload(healthChecks()));
  });
}
