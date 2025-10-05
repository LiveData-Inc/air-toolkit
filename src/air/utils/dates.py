"""Date and time utilities for AIR toolkit."""

from datetime import datetime, timezone
from pathlib import Path


def format_timestamp(dt: datetime | None = None, ordinal: int | None = None) -> str:
    """Format datetime as YYYYMMDD-NNN-HHMM (new format) or YYYYMMDD-HHMM (legacy).

    Args:
        dt: Datetime to format (default: now)
        ordinal: Daily task ordinal (e.g., 001). If provided, uses new format.

    Returns:
        Formatted timestamp string

    Examples:
        format_timestamp(ordinal=5) -> "20251005-005-1430"
        format_timestamp() -> "20251005-1430" (legacy format)
    """
    if dt is None:
        dt = datetime.now(timezone.utc)

    if ordinal is not None:
        # New format: YYYYMMDD-NNN-HHMM
        return f"{dt.strftime('%Y%m%d')}-{ordinal:03d}-{dt.strftime('%H%M')}"
    else:
        # Legacy format: YYYYMMDD-HHMM
        return dt.strftime("%Y%m%d-%H%M")


def get_next_ordinal(tasks_dir: Path | None = None, date: datetime | None = None) -> int:
    """Get next available task ordinal for the given date.

    Args:
        tasks_dir: Directory containing task files (default: .air/tasks)
        date: Date to check (default: today)

    Returns:
        Next available ordinal (e.g., 1, 2, 3...)
    """
    if tasks_dir is None:
        tasks_dir = Path(".air/tasks")

    if date is None:
        date = datetime.now(timezone.utc)

    date_prefix = date.strftime("%Y%m%d")

    if not tasks_dir.exists():
        return 1

    # Count existing tasks for this date (both formats)
    # New format: YYYYMMDD-NNN-HHMM-*.md
    # Legacy format: YYYYMMDD-HHMM-*.md
    existing = list(tasks_dir.glob(f"{date_prefix}-*.md"))

    # Filter out DESIGN-* and TASKS.md files
    task_files = [
        f for f in existing
        if not f.name.startswith("DESIGN-") and f.name != "TASKS.md"
    ]

    return len(task_files) + 1


def parse_task_timestamp(filename: str) -> datetime | None:
    """Parse timestamp from task filename.

    Handles both formats:
    - New: YYYYMMDD-NNN-HHMM-description.md
    - Legacy: YYYYMMDD-HHMM-description.md

    Args:
        filename: Task filename

    Returns:
        Parsed datetime, or None if invalid format
    """
    try:
        parts = filename.split("-")

        if len(parts) >= 4 and len(parts[1]) == 3 and parts[1].isdigit():
            # New format: YYYYMMDD-NNN-HHMM-...
            date_str = parts[0]  # YYYYMMDD
            time_str = parts[2]  # HHMM
            timestamp_str = f"{date_str}-{time_str}"
            return datetime.strptime(timestamp_str, "%Y%m%d-%H%M")
        elif len(parts) >= 3:
            # Legacy format: YYYYMMDD-HHMM-...
            timestamp_str = filename[:13]
            return datetime.strptime(timestamp_str, "%Y%m%d-%H%M")
        else:
            return None
    except (ValueError, IndexError):
        return None


def format_duration(start: datetime, end: datetime | None = None) -> str:
    """Format duration between two datetimes.

    Args:
        start: Start datetime
        end: End datetime (default: now)

    Returns:
        Formatted duration string (e.g., "2h 30m")
    """
    if end is None:
        end = datetime.now(timezone.utc)

    duration = end - start
    hours = duration.seconds // 3600
    minutes = (duration.seconds % 3600) // 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")

    return " ".join(parts) if parts else "< 1m"


def format_relative_time(dt: datetime) -> str:
    """Format datetime as relative time (e.g., '2 minutes ago').

    Args:
        dt: Datetime to format

    Returns:
        Relative time string
    """
    # Handle both naive and aware datetimes
    now = datetime.now()
    if dt.tzinfo is not None:
        now = datetime.now(timezone.utc)

    diff = now - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago" if minutes > 1 else "1m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago" if hours > 1 else "1h ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days}d ago" if days > 1 else "1d ago"
    else:
        # More than a week, show date
        return dt.strftime("%Y-%m-%d")
