import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest import mock

from scripts import build_dashboard_snapshot as snapshot


class SnapshotTest(unittest.TestCase):
    def test_issue_count_includes_all_pages_and_excludes_pull_requests(self):
        first = [{"number": number} for number in range(1, 101)]
        second = [{"number": 101}, {"number": 102, "pull_request": {}}]

        def github_get(url):
            if "/issues?" not in url:
                return {"private": True}
            return first if url.endswith("&page=1") else second

        with mock.patch.object(snapshot, "github_get", side_effect=github_get) as get:
            result = snapshot.issues({"repository": "https://github.com/example/private"})
        self.assertEqual(result["open"], 101)
        self.assertFalse(result["titlesIncluded"])
        self.assertEqual(get.call_count, 3)

    def test_dependabot_severity_counts_include_all_pages(self):
        first = [{"security_advisory": {"severity": "high"}} for _ in range(100)]
        second = [{"security_advisory": {"severity": "critical"}}]
        with mock.patch.object(snapshot, "github_get", side_effect=[first, second]):
            result = snapshot.dependabot("example/private", public=False)
        self.assertEqual(result["open"], 101)
        self.assertEqual(result["bySeverity"], {"high": 100, "critical": 1})
        self.assertIn("fetchedAt", result)

    def test_pip_audit_reports_when_the_audit_file_was_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "dashboard-data" / "pip-audit.json"
            path.parent.mkdir()
            path.write_text(json.dumps({"dependencies": [{"name": "example", "version": "1", "vulns": []}]}))
            expected = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            with mock.patch.object(snapshot, "ROOT", root):
                result = snapshot.pip_audit(public=False)
        self.assertEqual(result["scannedAt"], expected)
        self.assertEqual(result["count"], 0)


if __name__ == "__main__":
    unittest.main()
