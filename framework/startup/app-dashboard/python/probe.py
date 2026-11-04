"""Scheduled uptime probe for the app dashboard.

Runs every hour (EventBridge schedule in template.yaml), separate from the app function, and:
  1. calls the public /health URL and records pass/fail as the custom CloudWatch metric
     NCI/AppDashboard HealthCheckSuccess (1 or 0) -- this history is what "uptime" means for a Lambda;
  2. reads the app's function-URL metrics (requests, 4xx/5xx, latency) and the health-check history;
  3. writes one summary document to the ops DynamoDB table, which the dashboard reads.

The app itself never calls CloudWatch. The document holds only numbers and timestamps: no URLs, hostnames,
request data or credentials.
"""
import json
import logging
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

NAMESPACE = "NCI/AppDashboard"
METRIC = "HealthCheckSuccess"
INTERVAL_MINUTES = 60
TIMEOUT_SECONDS = 10
WINDOWS = {"24h": timedelta(hours=24), "7d": timedelta(days=7)}
STATUS_KEY = "status"
LOG = logging.getLogger(__name__)


def iso(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check(url, opener=urllib.request.urlopen):
    """GET the health URL. Passes only on HTTP 200 with {"status": "ok"}."""
    started = time.monotonic()
    code = None
    ok = False
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "nci-uptime-probe", "Accept": "application/json"})
        with opener(request, timeout=TIMEOUT_SECONDS) as resp:
            code = resp.status
            body = json.loads(resp.read() or b"{}")
            ok = code == 200 and isinstance(body, dict) and body.get("status") == "ok"
    except urllib.error.HTTPError as err:
        code = err.code
    except (urllib.error.URLError, OSError, ValueError):
        pass
    return {"ok": ok, "httpStatus": code, "latencyMs": int((time.monotonic() - started) * 1000)}


def _query(qid, namespace, name, dims, stat, period):
    return {
        "Id": qid,
        "MetricStat": {
            "Metric": {"Namespace": namespace, "MetricName": name, "Dimensions": [{"Name": k, "Value": v} for k, v in dims.items()]},
            "Period": period,
            "Stat": stat,
        },
        "ReturnData": True,
    }


def _fetch(cloudwatch, queries, start, end):
    """Return {query id: [(timestamp, value), ...]} following pagination."""
    out = {q["Id"]: [] for q in queries}
    statuses = {}
    kwargs = {"MetricDataQueries": queries, "StartTime": start, "EndTime": end, "ScanBy": "TimestampAscending"}
    while True:
        resp = cloudwatch.get_metric_data(**kwargs)
        for result in resp.get("MetricDataResults", []):
            qid = result.get("Id")
            status = result.get("StatusCode")
            timestamps, values = result.get("Timestamps", []), result.get("Values", [])
            if qid not in out or status not in ("Complete", "PartialData") or len(timestamps) != len(values):
                raise RuntimeError("CloudWatch returned invalid or unavailable metric data")
            statuses[qid] = status
            out[qid].extend(zip(timestamps, values))
        if not resp.get("NextToken"):
            if any(statuses.get(qid) != "Complete" for qid in out):
                raise RuntimeError("CloudWatch returned incomplete metric data")
            return out
        kwargs["NextToken"] = resp["NextToken"]


def _total(points):
    return sum(v for _, v in points)


def _pct(part, whole):
    return round(100.0 * part / whole, 3) if whole else None


def collect(cloudwatch, function_name, stack, now):
    """Uptime and request statistics for each window, plus an hourly uptime strip for the last 24 hours."""
    fn = {"FunctionName": function_name}
    hc = {"Stack": stack}
    end = now.replace(second=0, microsecond=0)
    end -= timedelta(minutes=end.minute % INTERVAL_MINUTES)
    period = INTERVAL_MINUTES * 60
    uptime, requests, hourly = {}, {}, []
    for label, span in WINDOWS.items():
        queries = [
            _query("req", "AWS/Lambda", "UrlRequestCount", fn, "Sum", period),
            _query("e5", "AWS/Lambda", "Url5xxCount", fn, "Sum", period),
            _query("e4", "AWS/Lambda", "Url4xxCount", fn, "Sum", period),
            _query("lat", "AWS/Lambda", "UrlRequestLatency", fn, "p95", period),
            _query("ferr", "AWS/Lambda", "Errors", fn, "Sum", period),
            _query("thr", "AWS/Lambda", "Throttles", fn, "Sum", period),
            _query("hcok", NAMESPACE, METRIC, hc, "Sum", period),
            _query("hcn", NAMESPACE, METRIC, hc, "SampleCount", period),
        ]
        if label == "24h":
            queries.append(_query("hourly", NAMESPACE, METRIC, hc, "Average", 3600))
        data = _fetch(cloudwatch, queries, end - span, end)

        passed, run = int(_total(data["hcok"])), int(_total(data["hcn"]))
        uptime[label] = {
            "percent": _pct(passed, run),
            "checksPassed": passed,
            "checksRun": run,
            "checksExpected": int(span.total_seconds() // (INTERVAL_MINUTES * 60)),
        }
        total, e5 = int(_total(data["req"])), int(_total(data["e5"]))
        latest_latency = max(data["lat"], key=lambda point: point[0], default=None)
        requests[label] = {
            "total": total,
            "serverErrors": e5,
            "clientErrors": int(_total(data["e4"])),
            "successPercent": round(100.0 - _pct(e5, total), 3) if total else None,
            "latencyP95Ms": round(latest_latency[1]) if latest_latency else None,
            "latencyP95At": iso(latest_latency[0]) if latest_latency else None,
            "latencyPeriodSeconds": period,
            "functionErrors": int(_total(data["ferr"])),
            "throttles": int(_total(data["thr"])),
        }
        if label == "24h":
            by_hour = {ts.astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0): v for ts, v in data["hourly"]}
            first = (now - span).astimezone(timezone.utc).replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
            for i in range(24):
                hour = first + timedelta(hours=i)
                value = by_hour.get(hour)
                hourly.append({"hour": iso(hour), "percent": None if value is None else round(100.0 * value, 1)})
    return {"metricsThrough": iso(end), "uptime": uptime, "requests": requests, "hourly24h": hourly}


def run(now, checker, cloudwatch, table, app_url, function_name, stack, api_errors=(OSError, RuntimeError)):
    result = checker(app_url.rstrip("/") + "/health")
    result["at"] = iso(now)
    document = {"checkedAt": iso(now), "probe": {"intervalMinutes": INTERVAL_MINUTES, "lastCheck": result}}
    try:
        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[{"MetricName": METRIC, "Dimensions": [{"Name": "Stack", "Value": stack}], "Timestamp": now, "Value": 1.0 if result["ok"] else 0.0, "Unit": "Count"}],
        )
    except api_errors as err:
        LOG.exception("Could not record the synthetic health check")
        document["probe"]["recordError"] = type(err).__name__
    try:
        document.update(collect(cloudwatch, function_name, stack, now))
    except api_errors as err:
        LOG.exception("Could not collect dashboard metrics")
        document["metrics"] = {"status": "unavailable", "reason": f"CloudWatch metrics could not be read ({type(err).__name__})"}
    table.put_item(Item={"id": STATUS_KEY, "updatedAt": iso(now), "document": json.dumps(document)})
    return document


def handler(event, context):
    import boto3  # available in the Lambda runtime
    from botocore.exceptions import BotoCoreError, ClientError

    document = run(
        now=datetime.now(timezone.utc),
        checker=check,
        cloudwatch=boto3.client("cloudwatch"),
        table=boto3.resource("dynamodb").Table(os.environ["OPS_TABLE"]),
        app_url=os.environ["APP_URL"],
        function_name=os.environ["APP_FUNCTION"],
        stack=os.environ["METRIC_STACK"],
        api_errors=(OSError, RuntimeError, BotoCoreError, ClientError),
    )
    print(json.dumps({"healthCheckOk": document["probe"]["lastCheck"]["ok"], "httpStatus": document["probe"]["lastCheck"]["httpStatus"]}))
    return {"ok": document["probe"]["lastCheck"]["ok"]}
