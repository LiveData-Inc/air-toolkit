"""Integration tests for review commands."""

import json
import subprocess
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def git_repo(tmp_path):
    """Create a temporary git repository."""
    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()

    # Initialize git repo
    subprocess.run(["git", "init"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    # Create initial commit
    (repo_dir / "README.md").write_text("# Test Project")
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=repo_dir,
        check=True,
        capture_output=True,
    )

    return repo_dir


class TestReviewCommand:
    """Tests for air review command."""

    def test_review_help(self, runner):
        """Test air review --help."""
        result = runner.invoke(main, ["review", "--help"])

        assert result.exit_code == 0
        assert "Generate code review context" in result.output
        assert "--format" in result.output

    def test_review_not_git_repo(self, runner, tmp_path):
        """Test air review in non-git directory."""
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(main, ["review"])

            assert result.exit_code == 1
            assert "Not a git repository" in result.output
        finally:
            os.chdir(original_cwd)

    def test_review_uncommitted_changes_json(self, runner, git_repo):
        """Test air review with uncommitted changes in JSON format."""
        import os

        # Make some changes to existing file
        (git_repo / "README.md").write_text("# Test Project\n\nNew content!")

        # Change to repo directory
        original_cwd = Path.cwd()
        try:
            os.chdir(git_repo)

            result = runner.invoke(main, ["review", "--format=json"])

            assert result.exit_code == 0

            # Parse JSON output
            data = json.loads(result.output)

            assert data["mode"] == "local-review"
            assert "changes" in data
            assert "diff" in data["changes"]
            assert "README.md" in data["changes"]["diff"]
            assert "New content" in data["changes"]["diff"]

        finally:
            os.chdir(original_cwd)

    def test_review_no_changes(self, runner, git_repo):
        """Test air review with no changes."""
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(git_repo)

            result = runner.invoke(main, ["review", "--format=json"])

            assert result.exit_code == 0

            # Parse JSON output
            data = json.loads(result.output)

            assert data["mode"] == "local-review"
            assert data["changes"]["stats"]["files_changed"] == 0

        finally:
            os.chdir(original_cwd)


class TestClaudeCommand:
    """Tests for air claude command."""

    def test_claude_help(self, runner):
        """Test air claude --help."""
        result = runner.invoke(main, ["claude", "--help"])

        assert result.exit_code == 0
        assert "AI assistant helper commands" in result.output

    def test_claude_context_help(self, runner):
        """Test air claude context --help."""
        result = runner.invoke(main, ["claude", "context", "--help"])

        assert result.exit_code == 0
        assert "Get comprehensive project context" in result.output

    def test_claude_context_not_air_project(self, runner, tmp_path):
        """Test air claude context in non-AIR directory."""
        import os

        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)

            result = runner.invoke(main, ["claude", "context", "--format=json"])

            assert result.exit_code == 0

            # Parse JSON output
            data = json.loads(result.output)

            assert "note" in data
            assert "Not an AIR project" in data["note"]

        finally:
            os.chdir(original_cwd)

    def test_claude_context_air_project(self, runner, isolated_project):
        """Test air claude context in AIR project."""
        import os

        # Create AIR project
        result = runner.invoke(main, ["init", "test-project"])
        assert result.exit_code == 0

        project_dir = isolated_project / "test-project"

        original_cwd = Path.cwd()
        try:
            os.chdir(project_dir)

            result = runner.invoke(main, ["claude", "context", "--format=json"])

            assert result.exit_code == 0

            # Parse JSON output
            data = json.loads(result.output)

            assert "project" in data
            assert data["project"]["name"] == "test-project"
            assert "recent_tasks" in data

        finally:
            os.chdir(original_cwd)


@pytest.fixture
def isolated_project(runner):
    """Create an isolated temporary directory for testing."""
    with runner.isolated_filesystem():
        yield Path.cwd()
