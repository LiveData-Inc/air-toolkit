"""Unit tests for error handling utilities."""

from pathlib import Path

import pytest

from air.utils.errors import (
    ConfigurationError,
    GitError,
    GitHubCLIError,
    PathError,
    ProjectNotFoundError,
    ResourceError,
    ResourceNotFoundError,
    TaskError,
    ValidationError,
    _find_similar_names,
    _levenshtein_distance,
)


class TestLevenshteinDistance:
    """Test Levenshtein distance calculation."""

    def test_identical_strings(self):
        """Test distance of identical strings is 0."""
        assert _levenshtein_distance("test", "test") == 0

    def test_one_substitution(self):
        """Test one character substitution."""
        assert _levenshtein_distance("test", "best") == 1

    def test_one_insertion(self):
        """Test one character insertion."""
        assert _levenshtein_distance("test", "tests") == 1

    def test_one_deletion(self):
        """Test one character deletion."""
        assert _levenshtein_distance("tests", "test") == 1

    def test_completely_different(self):
        """Test completely different strings."""
        result = _levenshtein_distance("abc", "xyz")
        assert result == 3


class TestFindSimilarNames:
    """Test similar name finding."""

    def test_exact_match_included(self):
        """Test exact matches are included (distance = 0)."""
        result = _find_similar_names("docs", ["docs", "api", "lib"])
        assert "docs" in result

    def test_close_match(self):
        """Test finding close matches."""
        result = _find_similar_names("doc", ["docs", "api", "documentation"])
        assert "docs" in result

    def test_multiple_matches(self):
        """Test finding multiple similar names."""
        candidates = ["documentation", "docs", "docker", "api"]
        result = _find_similar_names("doc", candidates)
        assert len(result) <= 3  # Max 3 results
        assert "docs" in result

    def test_no_matches(self):
        """Test when no similar names found."""
        result = _find_similar_names("xyz", ["api", "lib", "service"])
        assert len(result) == 0

    def test_max_distance_respected(self):
        """Test max distance parameter is respected."""
        result = _find_similar_names("abc", ["def", "ghi", "jkl"], max_distance=1)
        assert len(result) == 0


class TestProjectNotFoundError:
    """Test ProjectNotFoundError."""

    def test_error_message(self):
        """Test error message format."""
        error = ProjectNotFoundError()
        assert error.message == "Not in an AIR project"
        assert "air init" in error.hint

    def test_with_current_dir(self):
        """Test error with current directory."""
        error = ProjectNotFoundError(Path("/tmp/test"))
        assert "/tmp/test" in error.details


class TestConfigurationError:
    """Test ConfigurationError."""

    def test_error_message(self):
        """Test error message format."""
        error = ConfigurationError("Invalid config")
        assert error.message == "Invalid config"
        assert "air-config.json" in error.hint

    def test_with_config_path(self):
        """Test error with config path."""
        config_path = Path("/tmp/air-config.json")
        error = ConfigurationError("Invalid config", config_path=config_path)
        assert str(config_path) in error.details

    def test_with_fix_suggestion(self):
        """Test error with fix suggestion."""
        error = ConfigurationError("Invalid config", fix_suggestion="Fix the syntax")
        assert error.hint == "Fix the syntax"

    def test_has_doc_link(self):
        """Test error includes documentation link."""
        error = ConfigurationError("Invalid config")
        assert error.doc_link is not None
        assert "SPECIFICATION" in error.doc_link


class TestResourceNotFoundError:
    """Test ResourceNotFoundError."""

    def test_error_message(self):
        """Test error message format."""
        error = ResourceNotFoundError("docs")
        assert "docs" in error.message
        assert "not found" in error.message

    def test_with_available_resources(self):
        """Test error with similar resource suggestions."""
        error = ResourceNotFoundError("doc", available_resources=["docs", "api", "lib"])
        assert "Did you mean" in error.hint
        assert "docs" in error.hint

    def test_without_available_resources(self):
        """Test error without available resources."""
        error = ResourceNotFoundError("docs", available_resources=[])
        assert "air link list" in error.hint


class TestResourceError:
    """Test ResourceError."""

    def test_error_message(self):
        """Test error message format."""
        error = ResourceError("Resource failed", resource_name="docs")
        assert error.message == "Resource failed"
        assert "docs" in error.details

    def test_with_suggestion(self):
        """Test error with suggestion."""
        error = ResourceError("Resource failed", suggestion="Try this fix")
        assert error.hint == "Try this fix"


class TestPathError:
    """Test PathError."""

    def test_error_message(self):
        """Test error message format."""
        path = Path("/tmp/test")
        error = PathError("Path not found", path)
        assert error.message == "Path not found"
        assert str(path) in error.details

    def test_with_suggestion(self):
        """Test error with suggestion."""
        path = Path("/tmp/test")
        error = PathError("Path not found", path, suggestion="Create the directory")
        assert error.hint == "Create the directory"


class TestGitError:
    """Test GitError."""

    def test_error_message(self):
        """Test error message format."""
        error = GitError("Git operation failed")
        assert error.message == "Git operation failed"
        assert "git is installed" in error.hint

    def test_with_git_output(self):
        """Test error with git output."""
        error = GitError("Git operation failed", git_output="fatal: not a git repository")
        assert "fatal" in error.details

    def test_with_suggestion(self):
        """Test error with suggestion."""
        error = GitError("Git operation failed", suggestion="Initialize git first")
        assert error.hint == "Initialize git first"


class TestGitHubCLIError:
    """Test GitHubCLIError."""

    def test_error_message(self):
        """Test error message format."""
        error = GitHubCLIError("gh not found")
        assert error.message == "gh not found"
        assert "brew install gh" in error.hint

    def test_has_doc_link(self):
        """Test error includes documentation link."""
        error = GitHubCLIError("gh not found")
        assert error.doc_link is not None
        assert "cli.github.com" in error.doc_link

    def test_with_gh_output(self):
        """Test error with gh output."""
        error = GitHubCLIError("gh not found", gh_output="command not found: gh")
        assert "command not found" in error.details


class TestTaskError:
    """Test TaskError."""

    def test_error_message(self):
        """Test error message format."""
        error = TaskError("Task not found")
        assert error.message == "Task not found"
        assert "air task list" in error.hint

    def test_with_task_id(self):
        """Test error with task ID."""
        error = TaskError("Task not found", task_id="20251004-1200")
        assert "20251004-1200" in error.details

    def test_with_suggestion(self):
        """Test error with suggestion."""
        error = TaskError("Task not found", suggestion="Use full task ID")
        assert error.hint == "Use full task ID"


class TestValidationError:
    """Test ValidationError."""

    def test_error_message(self):
        """Test error message format."""
        error = ValidationError("Validation failed")
        assert error.message == "Validation failed"
        assert "air validate" in error.hint

    def test_with_issues_list(self):
        """Test error with issues list."""
        issues = ["Issue 1", "Issue 2", "Issue 3"]
        error = ValidationError("Validation failed", issues=issues)
        assert "Issue 1" in error.details
        assert "Issue 2" in error.details
        assert "Issue 3" in error.details

    def test_with_many_issues(self):
        """Test error with many issues (truncation)."""
        issues = [f"Issue {i}" for i in range(10)]
        error = ValidationError("Validation failed", issues=issues)
        assert "Issue 0" in error.details
        assert "Issue 4" in error.details
        assert "and 5 more" in error.details

    def test_with_suggestion(self):
        """Test error with suggestion."""
        error = ValidationError("Validation failed", suggestion="Fix the config")
        assert error.hint == "Fix the config"
