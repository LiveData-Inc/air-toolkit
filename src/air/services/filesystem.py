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

    On Windows, this requires either:
    - Developer Mode enabled (Windows 10+)
    - Administrator privileges
    - Falls back to directory junction on Windows if symlink fails

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
        # On Windows, target_is_directory=True is required for directory symlinks
        target.symlink_to(source.absolute(), target_is_directory=source.is_dir())
    except OSError as e:
        # Windows-specific handling
        if os.name == "nt":
            # Try creating a directory junction as fallback (doesn't require admin)
            try:
                import subprocess

                # Use mklink /J for junction (works without admin privileges)
                result = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(target.absolute()), str(source.absolute())],
                    capture_output=True,
                    text=True,
                    check=True
                )
                info(f"Created directory junction (Windows fallback): {target} -> {source}")
                return
            except subprocess.CalledProcessError:
                error(
                    f"Failed to create symlink or junction on Windows: {e}",
                    hint="Enable Developer Mode in Windows Settings > Update & Security > For developers, or run as Administrator",
                    exit_code=2,
                )
        else:
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
    """Find the AIR project root by looking for .air/air-config.json.

    Searches current directory and parents for both new location (.air/air-config.json)
    and legacy location (air-config.json in root).

    Returns:
        Path to project root, or None if not found
    """
    current = Path.cwd()

    # Check current directory and all parents
    for directory in [current] + list(current.parents):
        # Check new location first (.air/air-config.json)
        new_config_file = directory / ".air" / "air-config.json"
        if new_config_file.exists():
            return directory

        # Check legacy location for backward compatibility
        legacy_config_file = directory / "air-config.json"
        if legacy_config_file.exists():
            return directory

        # Also check for .air directory as indicator
        air_dir = directory / ".air"
        if air_dir.exists() and air_dir.is_dir():
            return directory

    return None


def get_config_path(project_root: Path) -> Path:
    """Get the path to air-config.json for a project.

    Checks new location (.air/air-config.json) first, falls back to legacy location
    (air-config.json in root) for backward compatibility.

    Args:
        project_root: Path to project root

    Returns:
        Path to config file (may not exist yet for new projects)
    """
    new_config = project_root / ".air" / "air-config.json"
    legacy_config = project_root / "air-config.json"

    # Return existing config if found, otherwise return new location
    if new_config.exists():
        return new_config
    elif legacy_config.exists():
        return legacy_config
    else:
        # For new projects, return the new location
        return new_config


def load_config(project_root: Path) -> "AirConfig":
    """Load AIR configuration from air-config.json.

    Uses get_config_path() to find config in new or legacy location.

    Args:
        project_root: Path to project root

    Returns:
        AirConfig instance

    Raises:
        SystemExit: If config file doesn't exist or is invalid
    """
    from air.core.models import AirConfig

    config_file = get_config_path(project_root)

    if not config_file.exists():
        error(
            f"Config file not found at {config_file}",
            hint="Run 'air upgrade --force' to migrate from legacy location or 'air init' to create a new project",
            exit_code=1,
        )

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
