"""Path utilities for AIR toolkit."""

import os
from pathlib import Path


def expand_path(path: str | Path) -> Path:
    """Expand ~ and make path absolute.

    Args:
        path: Path to expand

    Returns:
        Absolute Path with ~ expanded
    """
    return Path(path).expanduser().resolve()


def resolve_repo_path(path: str | Path) -> Path:
    """Resolve repository path with GIT_REPOS_PATH support.

    Behavior:
    - Paths starting with '/' are treated as absolute (no GIT_REPOS_PATH resolution)
    - Paths starting with '~' are expanded and treated as absolute
    - Other paths use GIT_REPOS_PATH if set, otherwise current directory

    Args:
        path: Path to resolve

    Returns:
        Absolute Path to repository

    Examples:
        # With GIT_REPOS_PATH=/home/user/repos
        resolve_repo_path("myproject")      # -> /home/user/repos/myproject
        resolve_repo_path("/abs/path")      # -> /abs/path (explicit absolute)
        resolve_repo_path("~/other")        # -> /home/user/other (~ expanded)

        # Without GIT_REPOS_PATH
        resolve_repo_path("myproject")      # -> /current/working/dir/myproject
    """
    path_str = str(path)

    # Explicit absolute path (starts with /) - don't use GIT_REPOS_PATH
    if path_str.startswith("/"):
        return Path(path).resolve()

    # Tilde expansion - treat as absolute
    if path_str.startswith("~"):
        return expand_path(path)

    # Relative path - use GIT_REPOS_PATH if available
    git_repos_path = os.getenv("GIT_REPOS_PATH")

    if git_repos_path:
        base_path = expand_path(git_repos_path)
        return (base_path / path).resolve()
    else:
        # No GIT_REPOS_PATH - resolve relative to current directory
        return Path(path).resolve()


def can_normalize_to_relative(absolute_path: str | Path) -> tuple[bool, str | None]:
    """Check if an absolute path can be normalized to relative under GIT_REPOS_PATH.

    Used for optional path normalization during upgrades (opt-in).

    Args:
        absolute_path: Absolute path to check

    Returns:
        Tuple of (can_normalize, relative_path_if_applicable)

    Examples:
        # With GIT_REPOS_PATH=/home/user/repos
        can_normalize_to_relative("/home/user/repos/myproject")
        # -> (True, "myproject")

        can_normalize_to_relative("/other/location/repo")
        # -> (False, None)
    """
    git_repos_path = os.getenv("GIT_REPOS_PATH")

    if not git_repos_path:
        return (False, None)

    try:
        abs_path = expand_path(absolute_path)
        base_path = expand_path(git_repos_path)

        # Check if within GIT_REPOS_PATH
        relative = abs_path.relative_to(base_path)

        # Verify the path still resolves correctly
        if resolve_repo_path(str(relative)) == abs_path:
            return (True, str(relative))
        else:
            return (False, None)
    except (ValueError, FileNotFoundError):
        return (False, None)


def ensure_dir(path: str | Path, parents: bool = True) -> Path:
    """Ensure directory exists.

    Args:
        path: Directory path
        parents: Create parent directories if needed

    Returns:
        Path object for directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=parents, exist_ok=True)
    return dir_path


def is_git_repo(path: str | Path) -> bool:
    """Check if path is a git repository.

    Args:
        path: Path to check

    Returns:
        True if git repository
    """
    git_dir = Path(path) / ".git"
    return git_dir.exists() and git_dir.is_dir()


def safe_filename(name: str) -> str:
    """Convert string to safe filename.

    Args:
        name: String to convert

    Returns:
        Safe filename string
    """
    import re
    # Replace spaces with hyphens
    safe = name.replace(" ", "-")
    # Remove unsafe characters
    safe = "".join(c for c in safe if c.isalnum() or c in "-_")
    # Replace multiple consecutive hyphens with single hyphen
    safe = re.sub(r"-+", "-", safe)
    # Convert to lowercase
    return safe.lower()
