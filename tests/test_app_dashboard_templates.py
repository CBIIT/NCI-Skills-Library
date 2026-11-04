import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "framework/startup/app-dashboard"
PY_TEMPLATE_FILES = ("python/dashboard.py", "python/ops_status.py", "python/probe.py", "dashboard.html")


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DashboardTemplateVersionTest(unittest.TestCase):
    def test_version_marker_is_in_every_python_template_and_the_page(self):
        code = (DASHBOARD / "python/dashboard.py").read_text(encoding="utf-8")
        self.assertIn("DASHBOARD_TEMPLATE_VERSION = 2", code)
        self.assertIn('<meta name="nci-dashboard-template" content="2">', (DASHBOARD / "dashboard.html").read_text(encoding="utf-8"))

    def test_skill_documents_install_upgrade_and_the_marker(self):
        skill = (ROOT / "framework/startup/app-dashboard.md").read_text(encoding="utf-8")
        for text in (
            "## Existing projects: install or upgrade",
            "DASHBOARD_TEMPLATE_VERSION",
            "templateVersion",
            "verify only",
            "Show the plan first",
            "sam-dashboard-ops.yaml",
            "DASHBOARD_SAMPLE_DATA",
            "not_applicable",
        ):
            self.assertIn(text, skill)

    def test_startup_routes_existing_projects_to_the_dashboard_skill(self):
        startup = (ROOT / "framework/nci-startup.md").read_text(encoding="utf-8")
        self.assertIn("### Existing projects get the dashboard too", startup)
        self.assertIn("Existing projects: install or upgrade", startup)
        intake = (ROOT / "framework/startup/collect_initial_info.md").read_text(encoding="utf-8")
        self.assertIn("existing-project path", intake)

    def test_page_treats_blocks_older_templates_omit_as_unavailable_not_empty(self):
        page = (DASHBOARD / "dashboard.html").read_text(encoding="utf-8")
        for fallback in ("const ops = d.operations;", "const hist = d.deploymentHistory;", "const dep = d.dependencies;"):
            self.assertIn(fallback, page)

    def test_probe_resources_are_least_privilege_and_boundary_safe(self):
        fragment = (DASHBOARD / "python/sam-dashboard-ops.yaml").read_text(encoding="utf-8")
        self.assertIn("PermissionBoundary_PowerUser", fragment)
        self.assertIn("cloudwatch:namespace: NCI/AppDashboard", fragment)
        self.assertIn("dynamodb:PutItem", fragment)
        self.assertNotIn("dynamodb:*", fragment)
        self.assertNotIn("AdministratorAccess", fragment)
        self.assertIn("rate(1 hour)", fragment)


class DashboardPythonTemplateTest(unittest.TestCase):
    def setUp(self):
        self.module = load(DASHBOARD / "python/dashboard.py", "dashboard_template")
        self.ops = load(DASHBOARD / "python/ops_status.py", "ops_status_template")

    def test_local_payload_marks_cloud_only_sections_not_applicable(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AWS_LAMBDA_FUNCTION_NAME", None)
            with mock.patch.object(self.module, "_snapshot", return_value={}):
                payload = self.module.build_payload()
        self.assertEqual(payload["templateVersion"], 2)
        self.assertEqual(payload["schemaVersion"], 1)
        self.assertFalse(payload["sampleData"])
        for key in ("operations", "deployment", "deploymentHistory", "tests", "documentation", "issues", "dependencies"):
            self.assertEqual(payload[key]["status"], "not_applicable", key)
        self.assertEqual(payload["summary"]["status"], "ok")

    def test_cloud_payload_reports_missing_snapshot_as_unavailable(self):
        with mock.patch.dict(os.environ, {"AWS_LAMBDA_FUNCTION_NAME": "fn"}):
            with mock.patch.object(self.module, "_snapshot", return_value={}):
                payload = self.module.build_payload(operations=lambda: {"status": "unavailable", "reason": "probe has not reported"})
        self.assertEqual(payload["deployment"]["status"], "unavailable")
        self.assertEqual(payload["summary"]["status"], "unknown")

    def test_sample_data_is_flagged_and_never_used_in_the_cloud(self):
        with mock.patch.dict(os.environ, {"DASHBOARD_SAMPLE_DATA": "healthy"}):
            os.environ.pop("OPS_TABLE", None)
            os.environ.pop("AWS_LAMBDA_FUNCTION_NAME", None)
            local = self.ops.make_reader()()
            self.assertTrue(local["sample"])
            self.assertTrue(self.module.build_payload(operations=lambda: local)["sampleData"])
            os.environ["AWS_LAMBDA_FUNCTION_NAME"] = "fn"
            cloud = self.ops.make_reader()()
            self.assertEqual(cloud["status"], "not_applicable")
            self.assertNotIn("sample", cloud)

    def test_every_sample_scenario_maps_to_a_badge(self):
        expected = {"healthy": "ok", "attention": "attention", "degraded": "degraded", "stale": "unknown"}
        for scenario, badge in expected.items():
            block = self.ops.sample_operations(scenario)
            self.assertEqual(self.module.build_payload(operations=lambda block=block: block)["summary"]["status"], badge, scenario)


class DashboardInstalledCopyTest(unittest.TestCase):
    """Copy the Python templates into an empty project the way the skill does, then run the bundled tests there."""

    def test_bundled_tests_pass_in_a_fresh_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            for name in PY_TEMPLATE_FILES:
                shutil.copy(DASHBOARD / name, project / Path(name).name)
            (project / "scripts").mkdir()
            shutil.copy(DASHBOARD / "scripts/build_dashboard_snapshot.py", project / "scripts")
            shutil.copytree(DASHBOARD / "python/tests", project / "tests", ignore=shutil.ignore_patterns("__pycache__"))
            (project / "tests/__init__.py").write_text("", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."],
                cwd=project, capture_output=True, text=True, timeout=120,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
