import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class GitHubMcpGuardrailTest(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_startup_requires_fail_closed_mcp_preflight(self):
        startup = self.read("framework/nci-startup.md")

        self.assertIn("## GitHub MCP Preflight Gate", startup)
        self.assertIn("Discover all currently callable GitHub MCP tools", startup)
        self.assertIn("Build and report a per-operation capability matrix", startup)
        self.assertIn("Never silently fall back", startup)
        self.assertIn("one preflight fallback request", startup)
        self.assertIn("immediately verify it through the MCP repository-read tool", startup)

    def test_questionnaire_enforces_gate_before_registry(self):
        questionnaire = self.read("framework/startup/collect_initial_info.md")

        self.assertIn("Before the registry phase", questionnaire)
        self.assertIn("per-operation capability matrix", questionnaire)
        self.assertIn("Never silently switch", questionnaire)
        self.assertIn("one preflight fallback request", questionnaire)
        self.assertIn("new repository returns `404`", questionnaire)

    def test_github_skill_defines_discovery_and_fallback_controls(self):
        skill = self.read("framework/technology/github/github-mcp-actions.md")

        self.assertIn("## Required Preflight Capability Matrix", skill)
        self.assertIn("## Fail-Closed Fallback Rule", skill)
        self.assertIn("## Fresh Repository Access Gate", skill)
        self.assertIn("Inspect deferred tools", skill)
        self.assertIn("one user acknowledgment", skill)


if __name__ == "__main__":
    unittest.main()
