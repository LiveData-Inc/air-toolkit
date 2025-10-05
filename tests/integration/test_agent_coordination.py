"""Integration tests for agent coordination (v0.6.0)."""

import json
import os
import time
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


class TestAgentCoordination:
    """Tests for parallel agent execution."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def isolated_project(self, tmp_path):
        """Create isolated test directory."""
        return tmp_path

    def test_analyze_command_inline(self, runner, isolated_project):
        """Test analyze command in inline mode."""
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create test repository
        test_repo = isolated_project / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")
        (test_repo / "main.py").write_text("print('hello')")

        # Change to project directory
        os.chdir(project_dir)

        # Link repository
        runner.invoke(main, ["link", "add", str(test_repo), "--type=library"])

        # Run inline analysis
        result = runner.invoke(main, ["analyze", "repos/test-repo"])

        assert result.exit_code == 0
        assert "Analyzing:" in result.output
        assert "Analysis complete:" in result.output

        # Verify findings file created
        findings_file = project_dir / "analysis/reviews/test-repo-findings.json"
        assert findings_file.exists()

    def test_analyze_command_background(self, runner, isolated_project):
        """Test analyze command in background mode."""
        # Change to temp directory first
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create test repository
        test_repo = isolated_project / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")

        # Change to project directory
        os.chdir(project_dir)

        # Link repository
        runner.invoke(main, ["link", "add", str(test_repo), "--type=documentation"])

        # Run background analysis
        result = runner.invoke(
            main,
            ["analyze", "repos/test-repo", "--background", "--id=test-bg"]
        )

        assert result.exit_code == 0
        assert "Started background agent: test-bg" in result.output

        # Verify agent directory created
        agent_dir = project_dir / ".air/agents/test-bg"
        assert agent_dir.exists()

        # Verify metadata file
        metadata_file = agent_dir / "metadata.json"
        assert metadata_file.exists()

        metadata = json.loads(metadata_file.read_text())
        assert metadata["id"] == "test-bg"
        assert metadata["command"] == "analyze"
        assert metadata["status"] == "running"

        # Wait for agent to complete
        time.sleep(2)

        # Verify stdout log exists
        stdout_file = agent_dir / "stdout.log"
        assert stdout_file.exists()

    def test_status_agents_command(self, runner, isolated_project):
        """Test status --agents command."""
        # Change to temp directory first
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create test repository
        test_repo = isolated_project / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")

        # Change to project directory
        os.chdir(project_dir)

        # Link repository
        runner.invoke(main, ["link", "add", str(test_repo)])

        # Run background analysis
        runner.invoke(
            main,
            ["analyze", "repos/test-repo", "--background", "--id=agent-1"]
        )

        # Check agent status
        result = runner.invoke(main, ["status", "--agents"])

        assert result.exit_code == 0
        assert "agent-1" in result.output
        assert "Active Agents" in result.output or "Total:" in result.output

    def test_status_agents_json_format(self, runner, isolated_project):
        """Test status --agents with JSON format."""
        # Change to temp directory first
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create test repository
        test_repo = isolated_project / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")

        # Change to project directory
        os.chdir(project_dir)

        # Link repository
        runner.invoke(main, ["link", "add", str(test_repo)])

        # Run background analysis
        runner.invoke(
            main,
            ["analyze", "repos/test-repo", "--background", "--id=agent-json"]
        )

        # Check agent status in JSON
        result = runner.invoke(main, ["status", "--agents", "--format=json"])

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["success"] is True
        assert len(data["agents"]) >= 1
        assert data["agents"][0]["id"] == "agent-json"

    def test_findings_command(self, runner, isolated_project):
        """Test findings --all command."""
        # Change to temp directory first
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create test repository
        test_repo = isolated_project / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")

        # Change to project directory
        os.chdir(project_dir)

        # Link repository
        runner.invoke(main, ["link", "add", str(test_repo)])

        # Run analysis
        runner.invoke(main, ["analyze", "repos/test-repo"])

        # View findings
        result = runner.invoke(main, ["findings", "--all"])

        assert result.exit_code == 0
        assert "Total:" in result.output

    def test_findings_json_format(self, runner, isolated_project):
        """Test findings with JSON format."""
        # Change to temp directory first
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create test repository
        test_repo = isolated_project / "test-repo"
        test_repo.mkdir()
        (test_repo / "README.md").write_text("# Test")

        # Change to project directory
        os.chdir(project_dir)

        # Link repository
        runner.invoke(main, ["link", "add", str(test_repo)])

        # Run analysis
        runner.invoke(main, ["analyze", "repos/test-repo"])

        # View findings in JSON
        result = runner.invoke(main, ["findings", "--all", "--format=json"])

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["success"] is True
        assert isinstance(data["findings"], list)
        assert data["count"] >= 1

    def test_multiple_parallel_analyses(self, runner, isolated_project):
        """Test running multiple analyses in parallel."""
        # Change to temp directory first
        os.chdir(isolated_project)

        # Create AIR project
        runner.invoke(main, ["init", "test-project", "--mode=mixed"])
        project_dir = isolated_project / "test-project"

        # Create three test repositories
        for i in range(3):
            test_repo = isolated_project / f"repo-{i}"
            test_repo.mkdir()
            (test_repo / "README.md").write_text(f"# Repo {i}")
            (test_repo / "main.py").write_text("print('test')")

        # Change to project directory
        os.chdir(project_dir)

        # Link all repositories
        for i in range(3):
            runner.invoke(main, ["link", "add", str(isolated_project / f"repo-{i}")])

        # Spawn three background agents
        for i in range(3):
            result = runner.invoke(
                main,
                [
                    "analyze",
                    f"repos/repo-{i}",
                    "--background",
                    f"--id=agent-{i}"
                ]
            )
            assert result.exit_code == 0

        # Check that all agents are tracked
        result = runner.invoke(main, ["status", "--agents", "--format=json"])
        data = json.loads(result.output)
        assert data["count"] >= 3

        # Wait for agents to complete
        time.sleep(3)

        # Check findings from all analyses
        result = runner.invoke(main, ["findings", "--all", "--format=json"])
        data = json.loads(result.output)
        # Should have findings from multiple repos
        assert data["count"] >= 3
