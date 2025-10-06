"""Path filtering for excluding external/vendor code from analysis."""

from pathlib import Path

# Common vendor/external directories to exclude by default
DEFAULT_EXCLUSIONS = [
    # Python
    ".poetry",
    ".venv",
    "venv",
    "env",
    "site-packages",
    "__pycache__",
    ".tox",
    ".nox",
    ".egg-info",
    ".eggs",

    # JavaScript/Node
    "node_modules",
    "bower_components",
    ".npm",

    # Go
    "vendor",
    "pkg",

    # Ruby
    ".bundle",

    # Rust
    "target",

    # Java
    ".gradle",
    ".m2",

    # General
    ".git",
    "build",
    "dist",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".hypothesis",
]


def should_exclude_path(path: Path, include_external: bool = False) -> bool:
    """Check if path should be excluded from analysis.

    Args:
        path: File or directory path (should be relative to repo root)
        include_external: If True, don't exclude vendor code

    Returns:
        True if should exclude, False otherwise

    Examples:
        >>> should_exclude_path(Path(".venv/lib/python3.10/site.py"))
        True
        >>> should_exclude_path(Path("src/main.py"))
        False
        >>> should_exclude_path(Path("node_modules/react/index.js"))
        True
        >>> should_exclude_path(Path("node_modules/react/index.js"), include_external=True)
        False
    """
    if include_external:
        return False

    # Check if any part of the path matches an exclusion pattern
    path_parts = path.parts

    for exclusion in DEFAULT_EXCLUSIONS:
        if exclusion in path_parts:
            return True

    return False


def get_exclusion_summary(excluded_dirs: set[str]) -> str:
    """Get human-readable summary of excluded directories.

    Args:
        excluded_dirs: Set of directory names that were excluded

    Returns:
        Comma-separated string of excluded directories

    Examples:
        >>> get_exclusion_summary({".venv", "node_modules"})
        '.venv, node_modules'
    """
    if not excluded_dirs:
        return ""

    # Sort for consistent output
    sorted_dirs = sorted(excluded_dirs)

    # Limit to first 5 to avoid cluttering output
    if len(sorted_dirs) <= 5:
        return ", ".join(sorted_dirs)
    else:
        first_five = ", ".join(sorted_dirs[:5])
        return f"{first_five}, +{len(sorted_dirs) - 5} more"


def find_excluded_directories(repo_path: Path) -> set[str]:
    """Find which excluded directories exist in the repository.

    Args:
        repo_path: Path to repository root

    Returns:
        Set of excluded directory names that exist in repo

    Examples:
        >>> find_excluded_directories(Path("/path/to/repo"))
        {'.venv', 'node_modules', 'build'}
    """
    excluded_dirs = set()

    for exclusion in DEFAULT_EXCLUSIONS:
        # Check if directory exists anywhere in repo
        matching = list(repo_path.glob(f"**/{exclusion}"))
        if matching:
            excluded_dirs.add(exclusion)

    return excluded_dirs
