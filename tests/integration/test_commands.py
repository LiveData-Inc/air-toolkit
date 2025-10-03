"""Integration tests for AIR commands."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def isolated_project(runner):
    """Create an isolated temporary directory for testing."""
    with runner.isolated_filesystem():
        yield Path.cwd()


class TestInitCommand:
    """Tests for air init command."""

    def test_init_creates_project(self, runner, isolated_project):
        """Test air init creates project structure."""
        result = runner.invoke(main, ["init", "test-project", "--mode=review"])

        assert result.exit_code == 0
        assert "Creating AIR project" in result.output
        assert "Project created successfully" in result.output

        # Check project structure
        project_dir = isolated_project / "test-project"
        assert project_dir.exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "CLAUDE.md").exists()
        assert (project_dir / "air-config.json").exists()
        assert (project_dir / ".gitignore").exists()

        # Check directories
        assert (project_dir / ".ai").exists()
        assert (project_dir / ".ai/tasks").exists()
        assert (project_dir / ".ai/context").exists()
        assert (project_dir / "review").exists()
        assert (project_dir / "analysis").exists()

    def test_init_review_mode(self, runner, isolated_project):
        """Test air init with review mode."""
        result = runner.invoke(main, ["init", "review-proj", "--mode=review"])

        assert result.exit_code == 0

        project_dir = isolated_project / "review-proj"
        assert (project_dir / "review").exists()
        assert not (project_dir / "collaborate").exists()
        assert not (project_dir / "contributions").exists()

    def test_init_collaborate_mode(self, runner, isolated_project):
        """Test air init with collaborate mode."""
        result = runner.invoke(main, ["init", "collab-proj", "--mode=collaborate"])

        assert result.exit_code == 0

        project_dir = isolated_project / "collab-proj"
        assert (project_dir / "collaborate").exists()
        assert (project_dir / "contributions").exists()
        assert not (project_dir / "review").exists()

    def test_init_mixed_mode(self, runner, isolated_project):
        """Test air init with mixed mode (default)."""
        result = runner.invoke(main, ["init", "mixed-proj"])

        assert result.exit_code == 0

        project_dir = isolated_project / "mixed-proj"
        assert (project_dir / "review").exists()
        assert (project_dir / "collaborate").exists()
        assert (project_dir / "contributions").exists()

    def test_init_current_directory(self, runner, isolated_project):
        """Test air init in current directory."""
        result = runner.invoke(main, ["init", ".", "--mode=review"])

        assert result.exit_code == 0
        assert (isolated_project / "air-config.json").exists()

    def test_init_no_track(self, runner, isolated_project):
        """Test air init without task tracking."""
        result = runner.invoke(main, ["init", "no-track", "--no-track"])

        assert result.exit_code == 0

        project_dir = isolated_project / "no-track"
        # .ai directory should still exist but without some files
        assert (project_dir / ".ai").exists()

    def test_init_config_content(self, runner, isolated_project):
        """Test air init creates valid config file."""
        result = runner.invoke(main, ["init", "config-test", "--mode=collaborate"])

        assert result.exit_code == 0

        config_path = isolated_project / "config-test" / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert config["version"] == "2.0.0"
        assert config["name"] == "config-test"
        assert config["mode"] == "collaborate"
        assert "resources" in config
        assert "review" in config["resources"]
        assert "collaborate" in config["resources"]


class TestValidateCommand:
    """Tests for air validate command."""

    def test_validate_not_in_project(self, runner, isolated_project):
        """Test air validate outside project."""
        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 1
        assert "Not an AIR project" in result.output

    def test_validate_valid_project(self, runner, isolated_project):
        """Test air validate on valid project."""
        # Create project first
        runner.invoke(main, ["init", "valid-proj", "--mode=review"])

        # Change to project directory
        import os
        os.chdir(isolated_project / "valid-proj")

        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 0
        assert "Project structure is valid" in result.output

    def test_validate_json_format(self, runner, isolated_project):
        """Test air validate with JSON output."""
        # Create project
        runner.invoke(main, ["init", "json-proj"])

        import os
        os.chdir(isolated_project / "json-proj")

        result = runner.invoke(main, ["validate", "--format=json"])

        assert result.exit_code == 0

        output = json.loads(result.output)
        assert output["success"] is True
        assert output["errors"] == []
        assert "project_root" in output

    def test_validate_missing_files(self, runner, isolated_project):
        """Test air validate detects missing files."""
        # Create project
        runner.invoke(main, ["init", "incomplete-proj"])

        project_dir = isolated_project / "incomplete-proj"

        # Remove required file
        (project_dir / "CLAUDE.md").unlink()

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 3
        assert "Validation failed" in result.output


class TestStatusCommand:
    """Tests for air status command."""

    def test_status_not_in_project(self, runner, isolated_project):
        """Test air status outside project."""
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 1
        assert "Not an AIR project" in result.output

    def test_status_new_project(self, runner, isolated_project):
        """Test air status on new project."""
        # Create project
        runner.invoke(main, ["init", "status-proj"])

        import os
        os.chdir(isolated_project / "status-proj")

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "AIR Project Status" in result.output
        assert "status-proj" in result.output
        assert "Resources: 0" in result.output

    def test_status_json_format(self, runner, isolated_project):
        """Test air status with JSON output."""
        # Create project
        runner.invoke(main, ["init", "json-status-proj", "--mode=review"])

        import os
        os.chdir(isolated_project / "json-status-proj")

        result = runner.invoke(main, ["status", "--format=json"])

        assert result.exit_code == 0

        output = json.loads(result.output)
        assert output["success"] is True
        assert output["project"]["name"] == "json-status-proj"
        assert output["project"]["mode"] == "review"
        assert output["resources"]["total"] == 0

    def test_status_shows_project_info(self, runner, isolated_project):
        """Test air status displays project information."""
        runner.invoke(main, ["init", "info-proj", "--mode=collaborate"])

        import os
        os.chdir(isolated_project / "info-proj")

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "info-proj" in result.output
        assert "collaborate" in result.output


class TestWorkflow:
    """Integration tests for complete workflows."""

    def test_full_workflow(self, runner, isolated_project):
        """Test complete init -> validate -> status workflow."""
        # Init
        result = runner.invoke(main, ["init", "workflow-test"])
        assert result.exit_code == 0

        import os
        os.chdir(isolated_project / "workflow-test")

        # Validate
        result = runner.invoke(main, ["validate"])
        assert result.exit_code == 0
        assert "valid" in result.output

        # Status
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "workflow-test" in result.output

    def test_workflow_with_json_output(self, runner, isolated_project):
        """Test workflow with JSON output at each step."""
        # Init
        runner.invoke(main, ["init", "json-workflow"])

        import os
        os.chdir(isolated_project / "json-workflow")

        # Validate with JSON
        result = runner.invoke(main, ["validate", "--format=json"])
        assert result.exit_code == 0
        validate_data = json.loads(result.output)
        assert validate_data["success"] is True

        # Status with JSON
        result = runner.invoke(main, ["status", "--format=json"])
        assert result.exit_code == 0
        status_data = json.loads(result.output)
        assert status_data["success"] is True
        assert status_data["project"]["name"] == "json-workflow"
