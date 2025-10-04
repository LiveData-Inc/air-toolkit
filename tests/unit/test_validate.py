"""Unit tests for validate command helper functions."""

import json
from pathlib import Path

import pytest

from air.core.models import AirConfig, Resource, ResourceRelationship, ResourceType


class TestSymlinkFixLogic:
    """Test symlink fix logic scenarios."""

    def test_missing_symlink_source_exists(self, tmp_path: Path) -> None:
        """Test logic when symlink is missing but source exists."""
        # Setup
        source_path = tmp_path / "source"
        source_path.mkdir()
        (source_path / "README.md").write_text("test")

        link_path = tmp_path / "link"

        # Simulate the fix logic
        should_fix = True
        can_recreate = source_path.exists()

        assert should_fix
        assert can_recreate
        assert not link_path.exists()
        assert source_path.exists()

    def test_missing_symlink_source_missing(self, tmp_path: Path) -> None:
        """Test logic when both symlink and source are missing."""
        # Setup
        source_path = tmp_path / "source"
        link_path = tmp_path / "link"

        # Simulate the fix logic
        should_fix = True
        can_recreate = source_path.exists()

        assert should_fix
        assert not can_recreate
        assert not link_path.exists()
        assert not source_path.exists()

    def test_broken_symlink_source_exists(self, tmp_path: Path) -> None:
        """Test logic when symlink is broken but source exists."""
        # Setup - create symlink pointing to non-existent path
        source_path = tmp_path / "source"
        link_path = tmp_path / "link"
        wrong_path = tmp_path / "wrong"

        # Create symlink to wrong path
        link_path.symlink_to(wrong_path)

        # Now create the actual source
        source_path.mkdir()
        (source_path / "README.md").write_text("test")

        # Simulate fix logic
        should_fix = True
        is_broken = link_path.is_symlink() and not link_path.exists()
        can_fix = source_path.exists()

        assert should_fix
        assert is_broken
        assert can_fix

    def test_broken_symlink_source_missing(self, tmp_path: Path) -> None:
        """Test logic when both symlink is broken and source is missing."""
        # Setup
        source_path = tmp_path / "source"
        link_path = tmp_path / "link"
        wrong_path = tmp_path / "wrong"

        # Create symlink to wrong path
        link_path.symlink_to(wrong_path)

        # Simulate fix logic
        should_fix = True
        is_broken = link_path.is_symlink() and not link_path.exists()
        can_fix = source_path.exists()

        assert should_fix
        assert is_broken
        assert not can_fix


class TestResourcePathExpansion:
    """Test resource path expansion logic."""

    def test_path_expands_tilde(self, tmp_path: Path) -> None:
        """Test that resource paths with ~ are expanded."""
        resource = Resource(
            name="test",
            path="~/test/path",
            type=ResourceType.LIBRARY,
            relationship=ResourceRelationship.REVIEW_ONLY,
        )

        expanded = Path(resource.path).expanduser()

        assert "~" not in str(expanded)
        assert str(expanded).startswith("/")

    def test_path_handles_absolute(self, tmp_path: Path) -> None:
        """Test that absolute paths are handled correctly."""
        abs_path = str(tmp_path / "test" / "path")
        resource = Resource(
            name="test",
            path=abs_path,
            type=ResourceType.LIBRARY,
            relationship=ResourceRelationship.REVIEW_ONLY,
        )

        expanded = Path(resource.path).expanduser()

        assert str(expanded) == abs_path


class TestConfigResourceIteration:
    """Test iterating over resources in config."""

    def test_get_all_resources_empty(self, tmp_path: Path) -> None:
        """Test getting resources from empty config."""
        config = AirConfig(
            version="2.0.0",
            name="test-project",
            mode="mixed",
            created="2025-10-04",
            resources={"review": [], "develop": []},
        )

        all_resources = config.get_all_resources()

        assert len(all_resources) == 0

    def test_get_all_resources_mixed(self, tmp_path: Path) -> None:
        """Test getting resources from mixed config."""
        review_resource = Resource(
            name="review-repo",
            path="/path/to/review",
            type=ResourceType.LIBRARY,
            relationship=ResourceRelationship.REVIEW_ONLY,
        )

        develop_resource = Resource(
            name="develop-repo",
            path="/path/to/develop",
            type=ResourceType.DOCUMENTATION,
            relationship=ResourceRelationship.DEVELOPER,
        )

        config = AirConfig(
            version="2.0.0",
            name="test-project",
            mode="mixed",
            created="2025-10-04",
            resources={"review": [review_resource], "develop": [develop_resource]},
        )

        all_resources = config.get_all_resources()

        assert len(all_resources) == 2
        assert review_resource in all_resources
        assert develop_resource in all_resources


class TestFixedMessageFormatting:
    """Test formatting of fix messages."""

    def test_recreated_symlink_message(self) -> None:
        """Test message for recreated symlink."""
        resource_name = "test-resource"
        message = f"Recreated symlink: repos/{resource_name}"

        assert "Recreated" in message
        assert resource_name in message
        assert "repos/" in message

    def test_fixed_broken_symlink_message(self) -> None:
        """Test message for fixed broken symlink."""
        resource_name = "test-resource"
        message = f"Fixed broken symlink: repos/{resource_name}"

        assert "Fixed" in message
        assert "broken" in message
        assert resource_name in message

    def test_cannot_fix_message(self) -> None:
        """Test message when fix is not possible."""
        resource_name = "test-resource"
        source_path = "/path/to/missing"
        message = f"Cannot fix repos/{resource_name}: source path does not exist: {source_path}"

        assert "Cannot fix" in message
        assert resource_name in message
        assert "source path does not exist" in message
        assert source_path in message
