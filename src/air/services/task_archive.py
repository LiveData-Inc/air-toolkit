"""Task archive service for AIR toolkit."""

from datetime import datetime
from pathlib import Path
from typing import Literal

from air.utils.console import error

ArchiveStrategy = Literal["by-month", "by-quarter", "flat"]


def get_archive_path(
    task_file: Path, archive_root: Path, strategy: ArchiveStrategy = "by-month"
) -> Path:
    """Calculate archive path for a task file based on strategy.

    Args:
        task_file: Path to task file
        archive_root: Root archive directory (e.g., .air/tasks/archive/)
        strategy: Archive organization strategy

    Returns:
        Full path where task should be archived

    Examples:
        >>> get_archive_path(
        ...     Path("20251003-1430-task.md"),
        ...     Path(".air/tasks/archive"),
        ...     "by-month"
        ... )
        Path('.air/tasks/archive/2025-10/20251003-1430-task.md')
    """
    filename = task_file.name

    # Extract date from filename (YYYYMMDD-HHMM-description.md)
    try:
        date_part = filename.split("-")[0]  # YYYYMMDD
        year = date_part[:4]
        month = date_part[4:6]
        quarter = str((int(month) - 1) // 3 + 1)
    except (IndexError, ValueError):
        # If can't parse date, use current date
        now = datetime.now()
        year = str(now.year)
        month = f"{now.month:02d}"
        quarter = str((now.month - 1) // 3 + 1)

    if strategy == "by-month":
        return archive_root / f"{year}-{month}" / filename
    elif strategy == "by-quarter":
        return archive_root / f"{year}-Q{quarter}" / filename
    else:  # flat
        return archive_root / filename


def archive_task(
    task_file: Path,
    archive_root: Path,
    strategy: ArchiveStrategy = "by-month",
    dry_run: bool = False,
) -> Path:
    """Archive a task file by moving it to the archive directory.

    Args:
        task_file: Path to task file to archive
        archive_root: Root archive directory
        strategy: Archive organization strategy (default: by-month)
        dry_run: If True, only show what would be done

    Returns:
        Path where task was (or would be) archived

    Raises:
        SystemExit: If task file doesn't exist or archive fails
    """
    if not task_file.exists():
        error(
            f"Task file not found: {task_file}",
            hint="Check the task ID is correct",
            exit_code=1,
        )

    archive_path = get_archive_path(task_file, archive_root, strategy)

    if dry_run:
        return archive_path

    # Create archive directory if needed
    archive_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if file already exists in archive
    if archive_path.exists():
        error(
            f"Task already archived: {archive_path}",
            hint="Use --overwrite to replace, or restore first",
            exit_code=1,
        )

    # Move file to archive
    try:
        task_file.rename(archive_path)
    except OSError as e:
        error(
            f"Failed to archive task: {e}",
            hint="Check file permissions",
            exit_code=2,
        )

    return archive_path


def restore_task(task_id: str, tasks_root: Path, archive_root: Path) -> Path:
    """Restore an archived task back to active tasks.

    Args:
        task_id: Task ID (e.g., "20251003-1430" or full filename)
        tasks_root: Root tasks directory (e.g., .air/tasks/)
        archive_root: Root archive directory (e.g., .air/tasks/archive/)

    Returns:
        Path where task was restored

    Raises:
        SystemExit: If task not found in archive or restore fails
    """
    # Find task in archive
    archived_task = find_task_in_archive(task_id, archive_root)

    if not archived_task:
        error(
            f"Task not found in archive: {task_id}",
            hint="Use 'air task list --archived' to see archived tasks",
            exit_code=1,
        )

    # Determine restore path
    restore_path = tasks_root / archived_task.name

    # Check if file already exists in active tasks
    if restore_path.exists():
        error(
            f"Task already exists in active tasks: {restore_path}",
            hint="Archive it first or use a different task",
            exit_code=1,
        )

    # Move file from archive to active
    try:
        archived_task.rename(restore_path)
    except OSError as e:
        error(
            f"Failed to restore task: {e}",
            hint="Check file permissions",
            exit_code=2,
        )

    return restore_path


def find_task_in_archive(task_id: str, archive_root: Path) -> Path | None:
    """Find a task file in the archive by ID.

    Args:
        task_id: Task ID (e.g., "20251003-1430" or full filename)
        archive_root: Root archive directory

    Returns:
        Path to archived task file, or None if not found
    """
    if not archive_root.exists():
        return None

    # Add .md extension if not present
    if not task_id.endswith(".md"):
        pattern = f"{task_id}-*.md"
    else:
        pattern = task_id

    # Search all subdirectories in archive
    for task_file in archive_root.rglob(pattern):
        if task_file.is_file():
            return task_file

    return None


def list_tasks(
    tasks_root: Path,
    archive_root: Path,
    include_archived: bool = False,
    archived_only: bool = False,
) -> dict[str, list[Path]]:
    """List task files with optional archive inclusion.

    Args:
        tasks_root: Root tasks directory (e.g., .air/tasks/)
        archive_root: Root archive directory (e.g., .air/tasks/archive/)
        include_archived: Include archived tasks in results
        archived_only: Only return archived tasks

    Returns:
        Dictionary with keys 'active' and 'archived', each containing list of Paths
    """
    result: dict[str, list[Path]] = {"active": [], "archived": []}

    # Get active tasks (exclude archive directory)
    if not archived_only and tasks_root.exists():
        for task_file in sorted(tasks_root.glob("*.md"), reverse=True):
            if task_file.is_file():
                result["active"].append(task_file)

    # Get archived tasks
    if (include_archived or archived_only) and archive_root.exists():
        for task_file in sorted(archive_root.rglob("*.md"), reverse=True):
            if task_file.is_file():
                result["archived"].append(task_file)

    return result


def get_tasks_before_date(tasks: list[Path], before_date: str) -> list[Path]:
    """Filter tasks created before a given date.

    Args:
        tasks: List of task file paths
        before_date: Date string in YYYY-MM-DD format

    Returns:
        Filtered list of tasks before the date
    """
    try:
        cutoff = datetime.strptime(before_date, "%Y-%m-%d")
    except ValueError:
        error(
            f"Invalid date format: {before_date}",
            hint="Use YYYY-MM-DD format (e.g., 2025-10-01)",
            exit_code=1,
        )

    filtered = []
    for task_file in tasks:
        # Extract date from filename (YYYYMMDD-HHMM-description.md)
        try:
            date_part = task_file.name.split("-")[0]  # YYYYMMDD
            task_date = datetime.strptime(date_part, "%Y%m%d")
            if task_date < cutoff:
                filtered.append(task_file)
        except (IndexError, ValueError):
            # Skip files that don't match expected format
            continue

    return filtered


def get_archive_stats(archive_root: Path) -> dict[str, int]:
    """Get statistics about archived tasks.

    Args:
        archive_root: Root archive directory

    Returns:
        Dictionary with archive statistics
    """
    stats = {
        "total_archived": 0,
        "by_month": {},
        "by_quarter": {},
    }

    if not archive_root.exists():
        return stats

    for task_file in archive_root.rglob("*.md"):
        if task_file.is_file():
            stats["total_archived"] += 1

            # Determine which month/quarter based on parent directory
            parent = task_file.parent.name
            if parent and parent != archive_root.name:
                # Month format: 2025-10
                if len(parent) == 7 and parent[4] == "-" and parent[:4].isdigit():
                    stats["by_month"][parent] = stats["by_month"].get(parent, 0) + 1

                # Quarter format: 2025-Q3
                if "Q" in parent:
                    stats["by_quarter"][parent] = stats["by_quarter"].get(parent, 0) + 1

    return stats
