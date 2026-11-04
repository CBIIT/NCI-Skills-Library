import io
import json
import unittest
import unittest.mock
import urllib.error
from datetime import datetime, timedelta, timezone

import probe

NOW = datetime(2026, 11, 4, 18, 0, 0, tzinfo=timezone.utc)


class FakeCloudWatch:
    """Returns canned values per query id; records what was put."""

    def __init__(self, values, fail_get=False):
        self.values = values
        self.fail_get = fail_get
        self.put = []
        self.queries = []

    def put_metric_data(self, **kwargs):
        self.put.append(kwargs)

    def get_metric_data(self, MetricDataQueries, StartTime, EndTime, **_):
        if self.fail_get:
            raise RuntimeError("AccessDenied")
        self.queries.append(MetricDataQueries)
        window = "24h" if EndTime - StartTime <= timedelta(hours=24) else "7d"
        results = []
        for q in MetricDataQueries:
            if q["Id"] == "hourly":
                ts = [NOW.replace(minute=0) - timedelta(hours=1), NOW.replace(minute=0) - timedelta(hours=2)]
                results.append({"Id": "hourly", "StatusCode": "Complete", "Timestamps": ts, "Values": [1.0, 0.5]})
            else:
                v = self.values.get(window, {}).get(q["Id"])
                results.append({"Id": q["Id"], "StatusCode": "Complete", "Timestamps": [EndTime - timedelta(minutes=5)] if v is not None else [], "Values": [v] if v is not None else []})
        return {"MetricDataResults": results}


class FakeTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[Item["id"]] = Item

    def get_item(self, Key):
        item = self.items.get(Key["id"])
        return {"Item": item} if item else {}


class FakeResponse(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


VALUES = {
    "24h": {"req": 400, "e5": 2, "e4": 10, "lat": 180.4, "ferr": 1, "thr": 0, "hcok": 23, "hcn": 24},
    "7d": {"req": 2000, "e5": 4, "e4": 50, "lat": 210.0, "ferr": 2, "thr": 0, "hcok": 167, "hcn": 168},
}


class CheckTest(unittest.TestCase):
    def test_ok_requires_200_and_status_ok(self):
        ok = probe.check("https://x/health", opener=lambda req, timeout: FakeResponse(200, b'{"status": "ok"}'))
        self.assertTrue(ok["ok"])
        self.assertEqual(ok["httpStatus"], 200)
        degraded = probe.check("https://x/health", opener=lambda req, timeout: FakeResponse(200, b'{"status": "degraded"}'))
        self.assertFalse(degraded["ok"])
        invalid = probe.check("https://x/health", opener=lambda req, timeout: FakeResponse(200, b'[]'))
        self.assertFalse(invalid["ok"])

    def test_http_error_and_network_error_fail(self):
        def http_503(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 503, "Service Unavailable", {}, io.BytesIO(b""))

        def offline(req, timeout):
            raise urllib.error.URLError("down")

        self.assertEqual(probe.check("https://x/health", opener=http_503), {"ok": False, "httpStatus": 503, "latencyMs": unittest.mock.ANY})
        self.assertFalse(probe.check("https://x/health", opener=offline)["ok"])


class RunTest(unittest.TestCase):
    def _run(self, cloudwatch, ok=True):
        table = FakeTable()
        checker = lambda url: {"ok": ok, "httpStatus": 200 if ok else 503, "latencyMs": 42}
        doc = probe.run(NOW, checker, cloudwatch, table, "https://app.example/", "fn", "stack")
        return doc, table

    def test_records_metric_and_summarizes(self):
        cw = FakeCloudWatch(VALUES)
        doc, table = self._run(cw)
        self.assertEqual(cw.put[0]["MetricData"][0]["Value"], 1.0)
        self.assertEqual(doc["uptime"]["24h"], {"percent": 95.833, "checksPassed": 23, "checksRun": 24, "checksExpected": 24})
        self.assertEqual(doc["uptime"]["7d"]["checksExpected"], 168)
        self.assertEqual(doc["requests"]["24h"]["successPercent"], 99.5)
        self.assertEqual(doc["requests"]["24h"]["latencyP95Ms"], 180)
        self.assertEqual(doc["requests"]["24h"]["latencyPeriodSeconds"], 3600)
        self.assertEqual(doc["requests"]["24h"]["latencyP95At"], "2026-11-04T17:55:00Z")
        self.assertEqual(next(q for q in cw.queries[0] if q["Id"] == "lat")["MetricStat"]["Period"], 3600)
        self.assertEqual(len(doc["hourly24h"]), 24)
        self.assertEqual(doc["hourly24h"][-1]["hour"], "2026-11-04T18:00:00Z")  # current, partial hour
        self.assertIsNone(doc["hourly24h"][-1]["percent"])
        self.assertEqual(doc["hourly24h"][-2]["percent"], 100.0)
        self.assertEqual(doc["hourly24h"][-3]["percent"], 50.0)
        self.assertIsNone(doc["hourly24h"][0]["percent"])
        stored = json.loads(table.items["status"]["document"])
        self.assertEqual(stored["probe"]["lastCheck"]["at"], "2026-11-04T18:00:00Z")
        self.assertNotIn("app.example", table.items["status"]["document"])

    def test_failed_check_records_zero(self):
        cw = FakeCloudWatch(VALUES)
        doc, _ = self._run(cw, ok=False)
        self.assertEqual(cw.put[0]["MetricData"][0]["Value"], 0.0)
        self.assertFalse(doc["probe"]["lastCheck"]["ok"])

    def test_no_traffic_gives_no_percentages(self):
        doc, _ = self._run(FakeCloudWatch({}))
        self.assertIsNone(doc["uptime"]["24h"]["percent"])
        self.assertIsNone(doc["requests"]["24h"]["successPercent"])
        self.assertIsNone(doc["requests"]["24h"]["latencyP95Ms"])

    def test_metrics_failure_still_writes_last_check(self):
        doc, table = self._run(FakeCloudWatch(VALUES, fail_get=True))
        self.assertEqual(doc["metrics"]["status"], "unavailable")
        self.assertIn("status", table.items)

    def test_partial_metric_results_are_unavailable_not_zero(self):
        class PartialCloudWatch(FakeCloudWatch):
            def get_metric_data(self, **kwargs):
                data = super().get_metric_data(**kwargs)
                data["MetricDataResults"][0]["StatusCode"] = "PartialData"
                return data

        doc, _ = self._run(PartialCloudWatch(VALUES))
        self.assertEqual(doc["metrics"]["status"], "unavailable")
        self.assertNotIn("requests", doc)

    def test_latest_latency_is_not_maximum_of_separate_percentiles(self):
        class MultipleLatencyPoints(FakeCloudWatch):
            def get_metric_data(self, **kwargs):
                data = super().get_metric_data(**kwargs)
                result = next(r for r in data["MetricDataResults"] if r["Id"] == "lat")
                result["Timestamps"] = [NOW - timedelta(minutes=10), NOW - timedelta(minutes=5)]
                result["Values"] = [900.0, 120.0]
                return data

        doc, _ = self._run(MultipleLatencyPoints(VALUES))
        self.assertEqual(doc["requests"]["24h"]["latencyP95Ms"], 120)
        self.assertEqual(doc["requests"]["24h"]["latencyP95At"], "2026-11-04T17:55:00Z")


if __name__ == "__main__":
    unittest.main()
