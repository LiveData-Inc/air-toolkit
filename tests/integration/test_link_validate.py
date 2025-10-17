"""Integration tests for air link validate command."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


class TestLinkValidate:
    """Tests for air link validate command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def project_with_absolute_paths(self, tmp_path):
        """Create a project with absolute paths that can be normalized."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create AIR project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create fake repos
        repos_base = tmp_path / "repos"
        repos_base.mkdir()

        repo1 = repos_base / "service-a"
        repo1.mkdir()
        (repo1 / "README.md").write_text("# Service A")

        repo2 = repos_base / "service-b"
        repo2.mkdir()
        (repo2 / "README.md").write_text("# Service B")

        # Create symlinks
        (project_dir / "repos" / "service-a").symlink_to(repo1)
        (project_dir / "repos" / "service-b").symlink_to(repo2)

        # Create config with ABSOLUTE paths
        config = {
            "name": "test-project",
            "mode": "review",
            "version": "2.0.0",
            "created": "2025-10-01T10:00:00",
            "resources": {
                "review": [
                    {
                        "name": "service-a",
                        "path": str(repo1),  # Absolute path
                        "type": "service",
                        "relationship": "review-only",
                        "writable": False,
                    }
                ],
                "develop": [
                    {
                        "name": "service-b",
                        "path": str(repo2),  # Absolute path
                        "type": "service",
                        "relationship": "developer",
                        "writable": True,
                    }
                ],
            },
        }

        config_file = project_dir / ".air" / "air-config.json"
        config_file.write_text(json.dumps(config, indent=2))

        return project_dir, repos_base

    def test_validate_without_git_repos_path(self, runner, project_with_absolute_paths):
        """Test validate when GIT_REPOS_PATH is not set."""
        project_dir, _ = project_with_absolute_paths

        os.chdir(project_dir)
        result = runner.invoke(main, ["link", "validate"])

        assert result.exit_code == 0
        assert "GIT_REPOS_PATH" in result.output
        assert "not set" in result.output
        assert "All resource paths are optimal" in result.output

    def test_validate_with_git_repos_path_finds_suggestions(
        self, runner, project_with_absolute_paths
    ):
        """Test validate finds normalizable paths when GIT_REPOS_PATH is set."""
        project_dir, repos_base = project_with_absolute_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        result = runner.invoke(main, ["link", "validate"], env=env)

        assert result.exit_code == 0
        assert "GIT_REPOS_PATH" in result.output
        # Path may be line-wrapped by Rich, so check key components
        assert "repos" in result.output
        assert "Found 2 path(s) that can be optimized" in result.output
        assert "service-a" in result.output
        assert "service-b" in result.output
        assert "air link validate --fix" in result.output

    def test_validate_json_format(self, runner, project_with_absolute_paths):
        """Test validate with JSON output."""
        project_dir, repos_base = project_with_absolute_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        result = runner.invoke(main, ["link", "validate", "--format=json"], env=env)

        assert result.exit_code == 0

        data = json.loads(result.output)
        assert data["git_repos_path"] == str(repos_base)
        assert data["total_resources"] == 2
        assert data["normalizable_paths"] == 2
        assert len(data["suggestions"]) == 2

        # Check suggestions
        suggestions = {s["name"]: s for s in data["suggestions"]}
        assert "service-a" in suggestions
        assert "service-b" in suggestions
        assert suggestions["service-a"]["suggested_path"] == "service-a"
        assert suggestions["service-b"]["suggested_path"] == "service-b"

    def test_validate_fix_updates_config(self, runner, project_with_absolute_paths):
        """Test validate --fix updates the config."""
        project_dir, repos_base = project_with_absolute_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        # Run validate --fix (simulating user confirming)
        result = runner.invoke(
            main, ["link", "validate", "--fix"], env=env, input="y\n"
        )

        assert result.exit_code == 0
        assert "Updated 2 resource path(s)" in result.output

        # Verify config was updated
        config_file = project_dir / ".air" / "air-config.json"
        config = json.loads(config_file.read_text())

        # Paths should now be relative
        assert config["resources"]["review"][0]["path"] == "service-a"
        assert config["resources"]["develop"][0]["path"] == "service-b"

    def test_validate_fix_cancelled(self, runner, project_with_absolute_paths):
        """Test validate --fix can be cancelled."""
        project_dir, repos_base = project_with_absolute_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        # Run validate --fix and cancel
        result = runner.invoke(
            main, ["link", "validate", "--fix"], env=env, input="n\n"
        )

        assert result.exit_code == 0
        assert "Cancelled" in result.output

        # Verify config was NOT updated
        config_file = project_dir / ".air" / "air-config.json"
        config = json.loads(config_file.read_text())

        # Paths should still be absolute
        assert config["resources"]["review"][0]["path"].startswith("/")
        assert config["resources"]["develop"][0]["path"].startswith("/")

    def test_validate_no_suggestions_when_optimal(self, runner, tmp_path):
        """Test validate shows no suggestions when paths are already optimal."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create AIR project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create fake repo
        repos_base = tmp_path / "repos"
        repos_base.mkdir()
        repo1 = repos_base / "service-a"
        repo1.mkdir()
        (repo1 / "README.md").write_text("# Service A")

        # Create symlink
        (project_dir / "repos" / "service-a").symlink_to(repo1)

        # Create config with RELATIVE path (already optimal)
        config = {
            "name": "test-project",
            "mode": "review",
            "version": "2.0.0",
            "created": "2025-10-01T10:00:00",
            "resources": {
                "review": [
                    {
                        "name": "service-a",
                        "path": "service-a",  # Relative path
                        "type": "service",
                        "relationship": "review-only",
                        "writable": False,
                    }
                ],
                "develop": [],
            },
        }

        config_file = project_dir / ".air" / "air-config.json"
        config_file.write_text(json.dumps(config, indent=2))

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        result = runner.invoke(main, ["link", "validate"], env=env)

        assert result.exit_code == 0
        assert "All resource paths are optimal" in result.output
        assert "air link validate --fix" not in result.output
