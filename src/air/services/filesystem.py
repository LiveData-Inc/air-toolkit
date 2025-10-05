"""Filesystem operations for AIR toolkit."""

import json
import os
import shutil
from pathlib import Path
from typing import Any

from air.utils.console import error, info, success


def create_directory(path: Path, exist_ok: bool = True) -> None:
    """Create a directory, optionally allowing it to exist.

    Args:
        path: Directory path to create
        exist_ok: If True, don't raise error if directory exists

    Raises:
        OSError: If directory creation fails
    """
    try:
        path.mkdir(parents=True, exist_ok=exist_ok)
    except OSError as e:
        error(f"Failed to create directory {path}: {e}", exit_code=2)


def create_file(path: Path, content: str, overwrite: bool = False) -> None:
    """Create a file with given content.

    Args:
        path: File path to create
        content: File content
        overwrite: If True, overwrite existing file

    Raises:
        FileExistsError: If file exists and overwrite is False
    """
    if path.exists() and not overwrite:
        error(
            f"File already exists: {path}",
            hint="Use --force to overwrite",
            exit_code=1,
        )

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as e:
        error(f"Failed to create file {path}: {e}", exit_code=2)


def create_symlink(source: Path, target: Path, overwrite: bool = False) -> None:
    """Create a symbolic link.

    Args:
        source: Source path (what to link to)
        target: Target path (where to create the link)
        overwrite: If True, overwrite existing link

    Raises:
        FileExistsError: If target exists and overwrite is False
    """
    if target.exists() or target.is_symlink():
        if not overwrite:
            error(
                f"Link target already exists: {target}",
                hint="Use --force to overwrite",
                exit_code=1,
            )
        target.unlink()

    if not source.exists():
        error(
            f"Link source does not exist: {source}",
            hint="Check the path and try again",
            exit_code=1,
        )

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(source.absolute())
    except OSError as e:
        error(f"Failed to create symlink {target} -> {source}: {e}", exit_code=2)


def copy_directory(source: Path, target: Path, overwrite: bool = False) -> None:
    """Copy a directory recursively.

    Args:
        source: Source directory
        target: Target directory
        overwrite: If True, overwrite existing directory

    Raises:
        FileExistsError: If target exists and overwrite is False
    """
    if target.exists():
        if not overwrite:
            error(
                f"Target directory already exists: {target}",
                hint="Use --force to overwrite",
                exit_code=1,
            )
        shutil.rmtree(target)

    if not source.exists():
        error(f"Source directory does not exist: {source}", exit_code=1)

    try:
        shutil.copytree(source, target)
    except OSError as e:
        error(f"Failed to copy directory {source} to {target}: {e}", exit_code=2)


def is_symlink_valid(path: Path) -> bool:
    """Check if a symlink points to a valid location.

    Args:
        path: Path to check

    Returns:
        True if path is a valid symlink, False otherwise
    """
    if not path.is_symlink():
        return False

    try:
        # This will raise if the link is broken
        path.resolve(strict=True)
        return True
    except (OSError, RuntimeError):
        return False


def ensure_empty_directory(path: Path) -> None:
    """Ensure a directory exists and is empty.

    Args:
        path: Directory path

    Raises:
        FileExistsError: If directory exists and is not empty
    """
    if path.exists():
        if any(path.iterdir()):
            error(
                f"Directory is not empty: {path}",
                hint="Use a different directory or remove existing files",
                exit_code=1,
            )
    else:
        create_directory(path)


def get_project_root() -> Path | None:
    """Find the AIR project root by looking for air-config.json.

    Searches current directory and parents.

    Returns:
        Path to project root, or None if not found
    """
    current = Path.cwd()

    # Check current directory and all parents
    for directory in [current] + list(current.parents):
        config_file = directory / "air-config.json"
        if config_file.exists():
            return directory

        # Also check for .ai directory as indicator
        ai_dir = directory / ".ai"
        if ai_dir.exists() and ai_dir.is_dir():
            return directory

    return None


def load_config(project_root: Path) -> "AirConfig":
    """Load AIR configuration from air-config.json.

    Args:
        project_root: Path to project root

    Returns:
        AirConfig instance

    Raises:
        SystemExit: If config file doesn't exist or is invalid
    """
    from air.core.models import AirConfig

    config_file = project_root / "air-config.json"
    if not config_file.exists():
        error(f"Config file not found: {config_file}", exit_code=1)

    try:
        config_data = json.loads(config_file.read_text())
        return AirConfig(**config_data)
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in config file: {e}", exit_code=1)
    except Exception as e:
        error(f"Failed to load config: {e}", exit_code=1)


def validate_project_structure(project_root: Path, mode: str) -> list[str]:
    """Validate that project has expected structure for its mode.

    Args:
        project_root: Project root directory
        mode: Project mode (review, collaborate, mixed)

    Returns:
        List of validation errors (empty if valid)
    """
    from air.core.models import ProjectMode, ProjectStructure

    errors = []

    # Get expected structure
    try:
        project_mode = ProjectMode(mode)
        expected = ProjectStructure.for_mode(project_mode)
    except ValueError:
        return [f"Invalid project mode: {mode}"]

    # Check required files
    for file in expected.required_files:
        file_path = project_root / file
        if not file_path.exists():
            errors.append(f"Missing required file: {file}")

    # Check directories
    for directory in expected.directories:
        dir_path = project_root / directory
        if not dir_path.exists():
            errors.append(f"Missing directory: {directory}")
        elif not dir_path.is_dir():
            errors.append(f"Not a directory: {directory}")

    return errors
