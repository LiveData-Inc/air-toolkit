"""Unit tests for PR generator service."""

from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from air.services.pr_generator import (
    ChangeDetection,
    PRMetadata,
    _sanitize_branch_name,
    check_gh_cli_available,
    copy_contributions_to_resource,
    create_pr_with_gh,
    detect_changes,
    generate_pr_metadata,
    git_create_branch_and_commit,
    is_git_repository,
)


class TestDetectChanges:
    """Test change detection in contributions directory."""

    def test_no_contribution_directory(self, tmp_path):
        """Test when contribution directory doesn't exist."""
        contributions_dir = tmp_path / "contributions"
        result = detect_changes(contributions_dir, "docs")

        assert result.has_changes is False
        assert len(result.changed_files) == 0
        assert result.contribution_dir == contributions_dir / "docs"

    def test_empty_contribution_directory(self, tmp_path):
        """Test when contribution directory exists but is empty."""
        contributions_dir = tmp_path / "contributions"
        resource_dir = contributions_dir / "docs"
        resource_dir.mkdir(parents=True)

        result = detect_changes(contributions_dir, "docs")

        assert result.has_changes is False
        assert len(result.changed_files) == 0

    def test_with_files(self, tmp_path):
        """Test with files in contribution directory."""
        contributions_dir = tmp_path / "contributions"
        resource_dir = contributions_dir / "docs"
        resource_dir.mkdir(parents=True)

        # Create test files
        (resource_dir / "README.md").write_text("# Test")
        (resource_dir / "guide.md").write_text("# Guide")

        result = detect_changes(contributions_dir, "docs")

        assert result.has_changes is True
        assert len(result.changed_files) == 2
        assert all(f.is_file() for f in result.changed_files)

    def test_ignores_hidden_files(self, tmp_path):
        """Test that hidden files are ignored."""
        contributions_dir = tmp_path / "contributions"
        resource_dir = contributions_dir / "docs"
        resource_dir.mkdir(parents=True)

        # Create visible and hidden files
        (resource_dir / "README.md").write_text("# Test")
        (resource_dir / ".hidden").write_text("Hidden")
        hidden_dir = resource_dir / ".git"
        hidden_dir.mkdir()
        (hidden_dir / "config").write_text("config")

        result = detect_changes(contributions_dir, "docs")

        assert result.has_changes is True
        assert len(result.changed_files) == 1
        assert result.changed_files[0].name == "README.md"

    def test_nested_files(self, tmp_path):
        """Test with nested directory structure."""
        contributions_dir = tmp_path / "contributions"
        resource_dir = contributions_dir / "docs"
        subdir = resource_dir / "api"
        subdir.mkdir(parents=True)

        (resource_dir / "README.md").write_text("# Test")
        (subdir / "endpoints.md").write_text("# API")

        result = detect_changes(contributions_dir, "docs")

        assert result.has_changes is True
        assert len(result.changed_files) == 2


class TestGeneratePRMetadata:
    """Test PR metadata generation."""

    def test_custom_title_and_body(self, tmp_path):
        """Test with custom title and body."""
        tasks_dir = tmp_path / "tasks"
        result = generate_pr_metadata(
            "docs", tasks_dir, custom_title="Custom Title", custom_body="Custom Body"
        )

        assert result.title == "Custom Title"
        assert result.body == "Custom Body"
        assert result.branch_name == "air/custom-title"
        assert result.related_tasks == []

    def test_default_title_and_body(self, tmp_path):
        """Test with generated title and body."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()

        result = generate_pr_metadata("docs", tasks_dir)

        assert result.title == "Improvements to docs"
        assert "This PR contains improvements to docs" in result.body
        assert "## Summary" in result.body
        assert "## Changes" in result.body
        assert "AIR Toolkit" in result.body
        assert result.branch_name == "air/improvements-to-docs"

    def test_custom_title_only(self, tmp_path):
        """Test with custom title but generated body."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()

        result = generate_pr_metadata("docs", tasks_dir, custom_title="Add API docs")

        assert result.title == "Add API docs"
        assert "This PR contains improvements to docs" in result.body
        assert result.branch_name == "air/add-api-docs"

    def test_with_task_files(self, tmp_path):
        """Test PR metadata generation with task files."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()

        # Create task files
        task1 = tasks_dir / "20251004-1200-feature.md"
        task1.write_text(
            """# Task: Add new feature

**Created:** 2025-10-04 12:00 UTC

## Prompt
Implement feature X

## Outcome
✓ Success
"""
        )

        result = generate_pr_metadata("docs", tasks_dir)

        assert "## Related Work" in result.body
        assert "Add new feature" in result.body
        assert len(result.related_tasks) == 1
        assert result.related_tasks[0] == "20251004-1200-feature"


class TestSanitizeBranchName:
    """Test branch name sanitization."""

    def test_simple_title(self):
        """Test simple title conversion."""
        result = _sanitize_branch_name("Add new feature")
        assert result == "air/add-new-feature"

    def test_special_characters(self):
        """Test removal of special characters."""
        result = _sanitize_branch_name("Fix bug #123 (urgent!)")
        assert result == "air/fix-bug-123-urgent"

    def test_multiple_spaces(self):
        """Test multiple spaces converted to single hyphen."""
        result = _sanitize_branch_name("Add    multiple    spaces")
        assert result == "air/add-multiple-spaces"

    def test_length_limit(self):
        """Test long title is truncated."""
        long_title = "A" * 100
        result = _sanitize_branch_name(long_title)
        assert len(result) <= 54  # air/ + 50 chars
        assert result.startswith("air/")

    def test_leading_trailing_hyphens(self):
        """Test leading/trailing hyphens are removed."""
        result = _sanitize_branch_name("--Feature--")
        assert result == "air/feature"

    def test_slashes_preserved(self):
        """Test slashes are preserved for branch hierarchies."""
        result = _sanitize_branch_name("feature/add-docs")
        assert result == "air/feature/add-docs"


class TestCheckGhCliAvailable:
    """Test gh CLI availability check."""

    @patch("subprocess.run")
    def test_gh_available(self, mock_run):
        """Test when gh CLI is available and authenticated."""
        mock_run.return_value = MagicMock(returncode=0)
        result = check_gh_cli_available()
        assert result is True
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_gh_not_authenticated(self, mock_run):
        """Test when gh CLI exists but not authenticated."""
        mock_run.return_value = MagicMock(returncode=1)
        result = check_gh_cli_available()
        assert result is False

    @patch("subprocess.run")
    def test_gh_not_installed(self, mock_run):
        """Test when gh CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()
        result = check_gh_cli_available()
        assert result is False

    @patch("subprocess.run")
    def test_gh_timeout(self, mock_run):
        """Test when gh CLI check times out."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("gh", 5)
        result = check_gh_cli_available()
        assert result is False


class TestCreatePRWithGh:
    """Test PR creation via gh CLI."""

    @patch("subprocess.run")
    def test_success(self, mock_run):
        """Test successful PR creation."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="https://github.com/owner/repo/pull/123\n"
        )

        success, result = create_pr_with_gh(
            Path("/repo"), "air/feature", "Add feature", "PR body", False, "main"
        )

        assert success is True
        assert result == "https://github.com/owner/repo/pull/123"

    @patch("subprocess.run")
    def test_draft_pr(self, mock_run):
        """Test draft PR creation."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="https://github.com/owner/repo/pull/123\n"
        )

        success, result = create_pr_with_gh(
            Path("/repo"), "air/feature", "Add feature", "PR body", True, "main"
        )

        assert success is True
        # Verify --draft was passed
        call_args = mock_run.call_args[0][0]
        assert "--draft" in call_args

    @patch("subprocess.run")
    def test_failure(self, mock_run):
        """Test PR creation failure."""
        mock_run.return_value = MagicMock(returncode=1, stderr="Error creating PR")

        success, result = create_pr_with_gh(
            Path("/repo"), "air/feature", "Add feature", "PR body", False, "main"
        )

        assert success is False
        assert "Error creating PR" in result

    @patch("subprocess.run")
    def test_timeout(self, mock_run):
        """Test timeout during PR creation."""
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired("gh", 30)

        success, result = create_pr_with_gh(
            Path("/repo"), "air/feature", "Add feature", "PR body", False, "main"
        )

        assert success is False
        assert "Timeout" in result


class TestCopyContributionsToResource:
    """Test copying contribution files."""

    def test_copy_single_file(self, tmp_path):
        """Test copying a single file."""
        contrib_dir = tmp_path / "contributions" / "docs"
        contrib_dir.mkdir(parents=True)
        resource_dir = tmp_path / "resource"
        resource_dir.mkdir()

        # Create source file
        source_file = contrib_dir / "README.md"
        source_file.write_text("# Test")

        result = copy_contributions_to_resource(
            contrib_dir, resource_dir, [source_file]
        )

        assert len(result) == 1
        assert result[0] == Path("README.md")
        assert (resource_dir / "README.md").exists()
        assert (resource_dir / "README.md").read_text() == "# Test"

    def test_copy_nested_files(self, tmp_path):
        """Test copying nested directory structure."""
        contrib_dir = tmp_path / "contributions" / "docs"
        resource_dir = tmp_path / "resource"
        resource_dir.mkdir()

        # Create nested structure
        api_dir = contrib_dir / "api"
        api_dir.mkdir(parents=True)
        source_file = api_dir / "endpoints.md"
        source_file.write_text("# API")

        result = copy_contributions_to_resource(
            contrib_dir, resource_dir, [source_file]
        )

        assert len(result) == 1
        assert result[0] == Path("api/endpoints.md")
        assert (resource_dir / "api" / "endpoints.md").exists()

    def test_copy_multiple_files(self, tmp_path):
        """Test copying multiple files."""
        contrib_dir = tmp_path / "contributions" / "docs"
        contrib_dir.mkdir(parents=True)
        resource_dir = tmp_path / "resource"
        resource_dir.mkdir()

        # Create multiple files
        file1 = contrib_dir / "README.md"
        file2 = contrib_dir / "GUIDE.md"
        file1.write_text("# README")
        file2.write_text("# Guide")

        result = copy_contributions_to_resource(
            contrib_dir, resource_dir, [file1, file2]
        )

        assert len(result) == 2
        assert (resource_dir / "README.md").exists()
        assert (resource_dir / "GUIDE.md").exists()


class TestGitCreateBranchAndCommit:
    """Test git branch creation and commit."""

    @patch("subprocess.run")
    def test_success(self, mock_run):
        """Test successful git operations."""
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        success, error = git_create_branch_and_commit(
            Path("/repo"),
            "air/feature",
            "Add feature",
            [Path("README.md"), Path("guide.md")],
        )

        assert success is True
        assert error == ""
        assert mock_run.call_count == 5  # checkout, add x2, commit, push

    @patch("subprocess.run")
    def test_branch_creation_failure(self, mock_run):
        """Test failure during branch creation."""
        mock_run.return_value = MagicMock(
            returncode=1, stderr="fatal: branch already exists"
        )

        success, error = git_create_branch_and_commit(
            Path("/repo"), "air/feature", "Add feature", [Path("README.md")]
        )

        assert success is False
        assert "Failed to create branch" in error

    @patch("subprocess.run")
    def test_commit_failure(self, mock_run):
        """Test failure during commit."""
        # Success for checkout and add, failure for commit
        mock_run.side_effect = [
            MagicMock(returncode=0),  # checkout
            MagicMock(returncode=0),  # add
            MagicMock(returncode=1, stderr="nothing to commit"),  # commit
        ]

        success, error = git_create_branch_and_commit(
            Path("/repo"), "air/feature", "Add feature", [Path("README.md")]
        )

        assert success is False
        assert "Failed to commit" in error

    @patch("subprocess.run")
    def test_push_failure(self, mock_run):
        """Test failure during push."""
        # Success until push
        mock_run.side_effect = [
            MagicMock(returncode=0),  # checkout
            MagicMock(returncode=0),  # add
            MagicMock(returncode=0),  # commit
            MagicMock(returncode=1, stderr="failed to push"),  # push
        ]

        success, error = git_create_branch_and_commit(
            Path("/repo"), "air/feature", "Add feature", [Path("README.md")]
        )

        assert success is False
        assert "Failed to push" in error


class TestIsGitRepository:
    """Test git repository detection."""

    def test_is_git_repo(self, tmp_path):
        """Test when directory is a git repository."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        assert is_git_repository(tmp_path) is True

    def test_not_git_repo(self, tmp_path):
        """Test when directory is not a git repository."""
        assert is_git_repository(tmp_path) is False

    def test_git_file_not_directory(self, tmp_path):
        """Test when .git exists but is a file, not directory."""
        git_file = tmp_path / ".git"
        git_file.write_text("gitdir: ../repo/.git")

        assert is_git_repository(tmp_path) is False
