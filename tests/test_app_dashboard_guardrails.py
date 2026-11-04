import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = "framework/startup/app-dashboard"


class AppDashboardGuardrailTest(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_defines_routes_contract_and_guardrails(self):
        skill = self.read("framework/startup/app-dashboard.md")

        self.assertIn("name: app-dashboard", skill)
        self.assertIn("GET /dashboard", skill)
        self.assertIn("GET /api/dashboard", skill)
        self.assertIn("## Payload contract (schemaVersion 1)", skill)
        self.assertIn('{"status": "unavailable"', skill)
        self.assertIn("Do not invent test results", skill)
        self.assertIn("Issue titles are included only when the GitHub repository is public", skill)
        self.assertIn("never `*`", skill)
        self.assertIn("dashboardApiUrl", skill)

    def test_template_files_exist(self):
        for name in (
            "python/dashboard.py",
            "node/dashboard.mjs",
            "dashboard.html",
            "scripts/build_dashboard_snapshot.py",
            "dashboard.config.example.json",
        ):
            self.assertTrue((ROOT / DASHBOARD / name).is_file(), name)

    def test_templates_do_not_use_wildcard_cors_or_innerhtml(self):
        for name in ("python/dashboard.py", "node/dashboard.mjs", "dashboard.html"):
            text = self.read(f"{DASHBOARD}/{name}")
            self.assertNotIn('Allow-Origin": "*"', text, name)
            self.assertNotIn("innerHTML", text.replace("never innerHTML", ""), name)

    def test_templates_exclude_health_and_dashboard_from_usage(self):
        for name in ("python/dashboard.py", "node/dashboard.mjs"):
            text = self.read(f"{DASHBOARD}/{name}")
            for route in ("/health", "/dashboard", "/api/dashboard"):
                self.assertIn(f'"{route}"', text, f"{name} {route}")

    def test_three_app_types_require_dashboard_and_cli_does_not(self):
        for name in ("hello-world-web-app", "hello-world-api", "hello-world-mcp-server"):
            text = self.read(f"framework/startup/{name}.md")
            self.assertIn("## Dashboard Requirement", text, name)
            self.assertIn("app-dashboard.md", text, name)
        self.assertNotIn("app-dashboard", self.read("framework/startup/hello-world-cli.md"))

    def test_mcp_server_keeps_single_tool_baseline(self):
        text = self.read("framework/startup/hello-world-mcp-server.md")
        self.assertIn("not MCP tools", text)
        self.assertIn("exactly one tool", text)

    def test_startup_deploy_and_registration_reference_dashboard(self):
        self.assertIn("app-dashboard.md", self.read("framework/nci-startup.md"))
        deploy = self.read("framework/cicd/cloud-one-deploy.md")
        self.assertIn("## Dashboard in the deploy workflow", deploy)
        self.assertIn("build_dashboard_snapshot.py", deploy)
        self.assertIn("dashboardApiUrl", deploy)
        self.assertIn("dashboardApiUrl", self.read("framework/startup/nci-skill-registration.md"))


if __name__ == "__main__":
    unittest.main()
