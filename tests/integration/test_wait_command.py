"""Integration tests for air wait command."""

import json
import os
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


class TestWaitCommand:
    """Test air wait command."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def project_with_resources(self, tmp_path):
        """Create project with linked resources."""
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        runner = CliRunner()

        # Initialize project
        result = runner.invoke(main, ["init", "test-project", "--mode=review"])
        assert result.exit_code == 0

        project_dir = tmp_path / "test-project"
        os.chdir(project_dir)

        # Create and link test repositories
        for i in range(3):
            test_repo = tmp_path / f"test-repo-{i}"
            test_repo.mkdir()
            (test_repo / "README.md").write_text(f"# Test Repo {i}")
            (test_repo / "main.py").write_text(f"print('repo {i}')")

            result = runner.invoke(main, ["link", "add", str(test_repo)])
            assert result.exit_code == 0

        yield project_dir

        # Restore directory
        os.chdir(original_dir)

    def test_wait_requires_flag(self, project_with_resources):
        """Test that wait requires --all or --agents."""
        runner = CliRunner()
        result = runner.invoke(main, ["wait"])

        assert result.exit_code == 1
        assert "Error: Specify --agents or --all" in result.output

    def test_wait_all_no_agents(self, project_with_resources):
        """Test wait --all when no agents are running."""
        runner = CliRunner()
        result = runner.invoke(main, ["wait", "--all"])

        assert result.exit_code == 0
        assert "All agents complete" in result.output

    def test_wait_all_json_no_agents(self, project_with_resources):
        """Test wait --all --format=json when no agents running."""
        runner = CliRunner()
        result = runner.invoke(main, ["wait", "--all", "--format=json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["success"] is True
        assert data["message"] == "All agents complete"
        assert data["agents"] == []

    def test_wait_specific_agents(self, project_with_resources):
        """Test wait --agents with specific agent IDs."""
        runner = CliRunner()

        # Spawn a quick background agent
        repos = list(Path("repos").glob("*"))
        if repos:
            result = runner.invoke(
                main,
                [
                    "analyze",
                    str(repos[0]),
                    "--background",
                    "--id=test-agent-1",
                ],
            )
            assert result.exit_code == 0

            # Wait for that specific agent
            result = runner.invoke(main, ["wait", "--agents=test-agent-1", "--timeout=30"])

            # Should complete successfully
            assert result.exit_code == 0
            assert "All agents complete" in result.output or "complete" in result.output.lower()

    def test_wait_all_with_background_agents(self, project_with_resources):
        """Test wait --all waits for background agents to complete."""
        runner = CliRunner()

        # Spawn multiple background agents
        repos = list(Path("repos").glob("*"))
        agent_ids = []
        for i, repo in enumerate(repos[:2]):  # Limit to 2 for speed
            agent_id = f"test-agent-{i}"
            agent_ids.append(agent_id)
            result = runner.invoke(
                main, ["analyze", str(repo), "--background", f"--id={agent_id}"]
            )
            assert result.exit_code == 0

        # Wait for all agents
        result = runner.invoke(main, ["wait", "--all", "--timeout=60"])

        # Should complete successfully
        assert result.exit_code == 0
        assert "complete" in result.output.lower()

    def test_wait_timeout(self, project_with_resources, tmp_path):
        """Test wait --timeout with no agents (completes immediately)."""
        runner = CliRunner()

        # Wait with timeout when no agents running
        result = runner.invoke(main, ["wait", "--all", "--timeout=2", "--interval=1"])

        # Should complete successfully (no agents to wait for)
        assert result.exit_code == 0
        assert "All agents complete" in result.output or "complete" in result.output.lower()

    def test_wait_json_format(self, project_with_resources):
        """Test wait --format=json output."""
        runner = CliRunner()

        # Spawn and wait
        repos = list(Path("repos").glob("*"))
        if repos:
            result = runner.invoke(
                main,
                ["analyze", str(repos[0]), "--background", "--id=json-test"],
            )
            assert result.exit_code == 0

            result = runner.invoke(
                main, ["wait", "--agents=json-test", "--format=json", "--timeout=30"]
            )

            # Should be valid JSON
            data = json.loads(result.output)
            assert "success" in data
            assert "agents" in data

    def test_wait_interval_option(self, project_with_resources):
        """Test wait --interval option."""
        runner = CliRunner()

        # Wait with custom interval
        result = runner.invoke(main, ["wait", "--all", "--interval=1"])

        # Should complete (no agents running)
        assert result.exit_code == 0

    def test_wait_nonexistent_agent(self, project_with_resources):
        """Test wait for agent that doesn't exist."""
        runner = CliRunner()

        # Wait for non-existent agent
        result = runner.invoke(
            main, ["wait", "--agents=does-not-exist", "--timeout=5"]
        )

        # Should complete immediately (no such agent)
        assert result.exit_code == 0


class TestWaitIntegration:
    """Integration tests for wait with real agent workflows."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def project_with_resources(self, tmp_path):
        """Create project with linked resources."""
        original_dir = os.getcwd()
        os.chdir(tmp_path)

        runner = CliRunner()

        # Initialize project
        result = runner.invoke(main, ["init", "test-project", "--mode=review"])
        assert result.exit_code == 0

        project_dir = tmp_path / "test-project"
        os.chdir(project_dir)

        # Create and link test repositories
        for i in range(3):
            test_repo = tmp_path / f"test-repo-{i}"
            test_repo.mkdir()
            (test_repo / "README.md").write_text(f"# Test Repo {i}")
            (test_repo / "main.py").write_text(f"print('repo {i}')")

            result = runner.invoke(main, ["link", "add", str(test_repo)])
            assert result.exit_code == 0

        yield project_dir

        # Restore directory
        os.chdir(original_dir)

    def test_parallel_analysis_workflow(self, project_with_resources):
        """Test complete parallel analysis workflow with wait."""
        runner = CliRunner()

        repos = list(Path("repos").glob("*"))[:2]  # Use 2 repos

        # Step 1: Spawn multiple agents
        agent_ids = []
        for i, repo in enumerate(repos):
            agent_id = f"parallel-{i}"
            agent_ids.append(agent_id)
            result = runner.invoke(
                main, ["analyze", str(repo), "--background", f"--id={agent_id}"]
            )
            assert result.exit_code == 0
            assert "Started background agent" in result.output

        # Step 2: Check status (should show running initially)
        result = runner.invoke(main, ["status", "--agents"])
        assert result.exit_code == 0
        # May show running or complete depending on timing

        # Step 3: Wait for all
        result = runner.invoke(main, ["wait", "--all", "--timeout=60"])
        assert result.exit_code == 0

        # Step 4: Check status again (should show complete)
        result = runner.invoke(main, ["status", "--agents"])
        assert result.exit_code == 0
        # Agents should be complete now

        # Step 5: Get findings
        result = runner.invoke(main, ["findings", "--all"])
        assert result.exit_code == 0

    def test_wait_shows_failed_agents(self, project_with_resources, tmp_path):
        """Test that wait detects failed agents."""
        runner = CliRunner()

        # Create a fake failed agent
        from datetime import datetime

        agent_dir = Path(".air/agents/failed-test")
        agent_dir.mkdir(parents=True, exist_ok=True)

        metadata = {
            "id": "failed-test",
            "status": "running",
            "started": datetime.now().isoformat(),
            "pid": 999998,  # Fake PID
        }

        (agent_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

        # Create stderr to indicate failure
        (agent_dir / "stderr.log").write_text("Error: Something went wrong")

        # Wait should detect this as failed
        # Note: The process check will mark it failed due to stderr
        result = runner.invoke(main, ["wait", "--all", "--timeout=10"])

        # Should exit with error due to failed agent
        assert result.exit_code == 1
        assert "failed" in result.output.lower()

    def test_sequential_wait_calls(self, project_with_resources):
        """Test multiple sequential wait calls."""
        runner = CliRunner()

        repos = list(Path("repos").glob("*"))

        if len(repos) >= 2:
            # First batch
            result = runner.invoke(
                main, ["analyze", str(repos[0]), "--background", "--id=seq-1"]
            )
            assert result.exit_code == 0

            result = runner.invoke(main, ["wait", "--agents=seq-1", "--timeout=30"])
            assert result.exit_code == 0

            # Second batch
            result = runner.invoke(
                main, ["analyze", str(repos[1]), "--background", "--id=seq-2"]
            )
            assert result.exit_code == 0

            result = runner.invoke(main, ["wait", "--agents=seq-2", "--timeout=30"])
            assert result.exit_code == 0
