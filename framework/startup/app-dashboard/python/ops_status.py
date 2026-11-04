"""Reads the uptime probe's latest summary (written by probe.py) for the dashboard's Operational Status section.

The app only does one DynamoDB GetItem here; all CloudWatch work happens in the scheduled probe.
"""
import json
import logging
import os
from datetime import datetime, timedelta, timezone

STALE_AFTER_SECONDS = 3 * 60 * 60  # three missed hourly runs
LOG = logging.getLogger(__name__)


def _unavailable(reason):
    return {"status": "unavailable", "reason": reason}


def _not_applicable(reason):
    return {"status": "not_applicable", "reason": reason}


def summarize(document, now=None):
    """Add freshness fields to a stored probe document."""
    now = now or datetime.now(timezone.utc)
    checked = datetime.strptime(document["checkedAt"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    age = int((now - checked).total_seconds())
    if age < -60:
        raise ValueError("probe timestamp is in the future")
    document["ageSeconds"] = age
    document["stale"] = age > STALE_AFTER_SECONDS
    return document


class OpsStatusReader:
    def __init__(self, table, api_errors=(OSError, RuntimeError)):
        self.table = table
        self.api_errors = api_errors

    def __call__(self):
        try:
            item = self.table.get_item(Key={"id": "status"}).get("Item")
        except self.api_errors:
            LOG.exception("Could not read synthetic monitoring results")
            return _unavailable("uptime probe results could not be read")
        if not item:
            return _unavailable("the uptime probe has not reported yet; it runs every hour after deployment")
        try:
            return summarize(json.loads(item["document"]))
        except (KeyError, TypeError, ValueError):
            LOG.warning("Synthetic monitoring results have an invalid format")
            return _unavailable("uptime probe results are not in the expected format")


def make_reader():
    table_name = os.environ.get("OPS_TABLE")
    if not table_name:
        scenario = os.environ.get("DASHBOARD_SAMPLE_DATA")
        if scenario and not os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
            return lambda: sample_operations(scenario)
        return lambda: _not_applicable(
            "Uptime comes from a scheduled health-check probe that exists only in the Cloud One deployment. "
            "Set DASHBOARD_SAMPLE_DATA=healthy to preview this section with sample data.")
    import boto3  # available in the Lambda runtime
    from botocore.exceptions import BotoCoreError, ClientError

    return OpsStatusReader(boto3.resource("dynamodb").Table(table_name), (OSError, RuntimeError, BotoCoreError, ClientError))


SAMPLE_SCENARIOS = ("healthy", "attention", "degraded", "stale")


def sample_operations(scenario="healthy", now=None):
    """Made-up Operational Status block for reviewing the page locally. Flagged sample=True; never used in the cloud."""
    now = now or datetime.now(timezone.utc)
    scenario = scenario if scenario in SAMPLE_SCENARIOS else "healthy"
    stamp = "%Y-%m-%dT%H:%M:%SZ"
    checked = now - timedelta(hours=4) if scenario == "stale" else now - timedelta(minutes=12)
    ok = scenario != "degraded"
    failing = scenario in ("attention", "degraded")
    passed24 = {"healthy": 24, "attention": 22, "degraded": 21, "stale": 24}[scenario]
    top = now.replace(minute=0, second=0, microsecond=0)
    bad_hours = {"degraded": (21, 22, 23), "attention": (5, 14)}.get(scenario, ())
    hourly = [{"hour": (top - timedelta(hours=23 - i)).strftime(stamp), "percent": 0.0 if i in bad_hours else 100.0} for i in range(24)]

    def window(total, e5, e4, ferr):
        return {"total": total, "serverErrors": e5, "clientErrors": e4, "successPercent": round(100.0 - 100.0 * e5 / total, 3),
                "latencyP95Ms": 410, "latencyP95At": checked.strftime(stamp), "latencyPeriodSeconds": 3600,
                "functionErrors": ferr, "throttles": 0}

    document = {
        "sample": True,
        "checkedAt": checked.strftime(stamp),
        "probe": {"intervalMinutes": 60, "lastCheck": {"ok": ok, "httpStatus": 200 if ok else 503, "latencyMs": 240, "at": checked.strftime(stamp)}},
        "uptime": {
            "24h": {"percent": round(100.0 * passed24 / 24, 3), "checksPassed": passed24, "checksRun": 24, "checksExpected": 24},
            "7d": {"percent": 96.429 if failing else 99.405, "checksPassed": 162 if failing else 167, "checksRun": 168, "checksExpected": 168},
        },
        "requests": {"24h": window(61, 3 if failing else 0, 2, 1 if failing else 0), "7d": window(402, 4 if failing else 0, 15, 2 if failing else 0)},
        "hourly24h": hourly,
    }
    return summarize(document, now=now)
