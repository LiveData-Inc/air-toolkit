"""Path utilities for AIR toolkit."""

from pathlib import Path


def expand_path(path: str | Path) -> Path:
    """Expand ~ and make path absolute.

    Args:
        path: Path to expand

    Returns:
        Absolute Path with ~ expanded
    """
    return Path(path).expanduser().resolve()


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
