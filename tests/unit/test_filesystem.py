"""Tests for filesystem service."""

import pytest
from pathlib import Path

from air.services.filesystem import (
    create_directory,
    create_file,
    create_symlink,
    is_symlink_valid,
    get_project_root,
    validate_project_structure,
)


def test_create_directory(tmp_path):
    """Test directory creation."""
    test_dir = tmp_path / "test_directory"
    create_directory(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()


def test_create_directory_with_parents(tmp_path):
    """Test directory creation with parent directories."""
    test_dir = tmp_path / "parent" / "child" / "grandchild"
    create_directory(test_dir)

    assert test_dir.exists()
    assert test_dir.is_dir()


def test_create_directory_exists_ok(tmp_path):
    """Test directory creation when directory already exists."""
    test_dir = tmp_path / "existing"
    test_dir.mkdir()

    # Should not raise error
    create_directory(test_dir, exist_ok=True)
    assert test_dir.exists()


def test_create_file(tmp_path):
    """Test file creation."""
    test_file = tmp_path / "test.txt"
    content = "Hello, World!"

    create_file(test_file, content, overwrite=True)

    assert test_file.exists()
    assert test_file.read_text() == content


def test_create_file_creates_parent_dirs(tmp_path):
    """Test file creation creates parent directories."""
    test_file = tmp_path / "parent" / "child" / "test.txt"
    content = "Test content"

    create_file(test_file, content, overwrite=True)

    assert test_file.exists()
    assert test_file.read_text() == content


def test_create_file_with_overwrite(tmp_path):
    """Test file overwrite."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Original content")

    new_content = "New content"
    create_file(test_file, new_content, overwrite=True)

    assert test_file.read_text() == new_content


def test_create_symlink(tmp_path):
    """Test symlink creation."""
    source = tmp_path / "source"
    source.mkdir()

    target = tmp_path / "target"
    create_symlink(source, target, overwrite=True)

    assert target.is_symlink()
    assert target.resolve() == source.resolve()


def test_create_symlink_to_file(tmp_path):
    """Test symlink to a file."""
    source = tmp_path / "source.txt"
    source.write_text("content")

    target = tmp_path / "target.txt"
    create_symlink(source, target, overwrite=True)

    assert target.is_symlink()
    assert target.read_text() == "content"


def test_is_symlink_valid_true(tmp_path):
    """Test is_symlink_valid returns True for valid symlink."""
    source = tmp_path / "source"
    source.mkdir()

    target = tmp_path / "target"
    target.symlink_to(source)

    assert is_symlink_valid(target) is True


def test_is_symlink_valid_broken(tmp_path):
    """Test is_symlink_valid returns False for broken symlink."""
    source = tmp_path / "source"
    target = tmp_path / "target"

    # Create symlink to non-existent source
    target.symlink_to(source)

    assert is_symlink_valid(target) is False


def test_is_symlink_valid_not_symlink(tmp_path):
    """Test is_symlink_valid returns False for non-symlink."""
    regular_file = tmp_path / "regular.txt"
    regular_file.write_text("content")

    assert is_symlink_valid(regular_file) is False


def test_get_project_root_with_config(tmp_path, monkeypatch):
    """Test get_project_root finds air-config.json."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    config_file = project_dir / "air-config.json"
    config_file.write_text("{}")

    subdir = project_dir / "subdir"
    subdir.mkdir()

    # Change to subdirectory
    monkeypatch.chdir(subdir)

    root = get_project_root()
    assert root == project_dir


def test_get_project_root_with_ai_dir(tmp_path, monkeypatch):
    """Test get_project_root finds .ai directory."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    ai_dir = project_dir / ".ai"
    ai_dir.mkdir()

    subdir = project_dir / "subdir"
    subdir.mkdir()

    # Change to subdirectory
    monkeypatch.chdir(subdir)

    root = get_project_root()
    assert root == project_dir


def test_get_project_root_not_found(tmp_path, monkeypatch):
    """Test get_project_root returns None when not in project."""
    monkeypatch.chdir(tmp_path)

    root = get_project_root()
    assert root is None


def test_validate_project_structure_valid(tmp_path):
    """Test validate_project_structure with valid structure."""
    # Create minimal review project
    (tmp_path / "README.md").write_text("# Test")
    (tmp_path / "CLAUDE.md").write_text("# Test")
    (tmp_path / "air-config.json").write_text("{}")
    (tmp_path / ".gitignore").write_text("")

    # Create directories
    for dir_name in [".ai", ".air/tasks", ".air/context", ".air/templates",
                      "scripts", "analysis", "repos", "analysis/reviews"]:
        (tmp_path / dir_name).mkdir(parents=True, exist_ok=True)

    errors = validate_project_structure(tmp_path, "review")
    assert errors == []


def test_validate_project_structure_missing_file(tmp_path):
    """Test validate_project_structure detects missing files."""
    # Create only some required files
    (tmp_path / "README.md").write_text("# Test")

    errors = validate_project_structure(tmp_path, "review")
    assert len(errors) > 0
    assert any("CLAUDE.md" in err for err in errors)


def test_validate_project_structure_missing_directory(tmp_path):
    """Test validate_project_structure detects missing directories."""
    # Create required files
    (tmp_path / "README.md").write_text("# Test")
    (tmp_path / "CLAUDE.md").write_text("# Test")
    (tmp_path / "air-config.json").write_text("{}")
    (tmp_path / ".gitignore").write_text("")

    # Create only some directories
    (tmp_path / ".ai").mkdir()

    errors = validate_project_structure(tmp_path, "review")
    assert len(errors) > 0
    assert any("review" in err or "analysis" in err for err in errors)


def test_validate_project_structure_invalid_mode(tmp_path):
    """Test validate_project_structure with invalid mode."""
    errors = validate_project_structure(tmp_path, "invalid_mode")
    assert len(errors) == 1
    assert "Invalid project mode" in errors[0]
