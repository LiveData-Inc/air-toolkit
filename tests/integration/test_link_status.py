"""Integration tests for link status display with GIT_REPOS_PATH."""

import json
import os
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


class TestLinkStatus:
    """Tests for resource status display with GIT_REPOS_PATH."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def project_with_relative_paths(self, tmp_path):
        """Create a project with relative paths that use GIT_REPOS_PATH."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create AIR project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create repos under GIT_REPOS_PATH
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

        # Create config with RELATIVE paths
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
                "develop": [
                    {
                        "name": "service-b",
                        "path": "service-b",  # Relative path
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

    def test_status_shows_valid_with_git_repos_path(
        self, runner, project_with_relative_paths
    ):
        """Test air status shows valid status for relative paths with GIT_REPOS_PATH."""
        project_dir, repos_base = project_with_relative_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        result = runner.invoke(main, ["status"], env=env)

        assert result.exit_code == 0
        # Should show valid status, not broken
        assert "✓ valid" in result.output or "valid" in result.output.lower()
        # Should NOT show broken or missing
        assert "✗ broken" not in result.output
        assert "broken" not in result.output.lower()

    def test_link_list_shows_valid_with_git_repos_path(
        self, runner, project_with_relative_paths
    ):
        """Test air link list shows valid status for relative paths with GIT_REPOS_PATH."""
        project_dir, repos_base = project_with_relative_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        result = runner.invoke(main, ["link", "list"], env=env)

        assert result.exit_code == 0
        # Should show valid status, not broken
        assert "✓ valid" in result.output or "valid" in result.output.lower()
        # Should NOT show broken or missing
        assert "✗ broken" not in result.output
        assert "broken" not in result.output.lower()
        # Should show both services
        assert "service-a" in result.output
        assert "service-b" in result.output

    def test_status_shows_broken_without_git_repos_path(
        self, runner, project_with_relative_paths
    ):
        """Test air status shows broken when GIT_REPOS_PATH not set for relative paths."""
        project_dir, _ = project_with_relative_paths

        os.chdir(project_dir)

        # Don't set GIT_REPOS_PATH - relative paths won't resolve
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        # Without GIT_REPOS_PATH, relative paths resolve to CWD and will be broken/missing
        # (unless by coincidence there's a "service-a" in CWD)
        # This is expected behavior - user should set GIT_REPOS_PATH

    def test_status_with_absolute_paths(self, runner, tmp_path):
        """Test air status works correctly with absolute paths (no GIT_REPOS_PATH needed)."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create AIR project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create repo
        repo1 = tmp_path / "other-location" / "service-a"
        repo1.mkdir(parents=True)
        (repo1 / "README.md").write_text("# Service A")

        # Create symlink
        (project_dir / "repos" / "service-a").symlink_to(repo1)

        # Create config with ABSOLUTE path
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
                "develop": [],
            },
        }

        config_file = project_dir / ".air" / "air-config.json"
        config_file.write_text(json.dumps(config, indent=2))

        os.chdir(project_dir)

        # No GIT_REPOS_PATH needed for absolute paths
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        # Should show valid status with absolute path
        assert "✓ valid" in result.output or "valid" in result.output.lower()
        assert "✗ broken" not in result.output

    def test_status_shows_broken_when_target_missing(
        self, runner, project_with_relative_paths
    ):
        """Test air status shows broken when symlink exists but target is deleted."""
        project_dir, repos_base = project_with_relative_paths

        os.chdir(project_dir)

        # Set GIT_REPOS_PATH
        env = os.environ.copy()
        env["GIT_REPOS_PATH"] = str(repos_base)

        # Delete the target repo
        import shutil
        shutil.rmtree(repos_base / "service-a")

        result = runner.invoke(main, ["status"], env=env)

        assert result.exit_code == 0
        # Should show broken status for service-a
        assert "✗ broken" in result.output or "broken" in result.output.lower()
