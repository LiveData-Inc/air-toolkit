"""Date and time utilities for AIR toolkit."""

from datetime import datetime, timezone


def format_timestamp(dt: datetime | None = None) -> str:
    """Format datetime as YYYYMMDD-HHMM.

    Args:
        dt: Datetime to format (default: now)

    Returns:
        Formatted timestamp string
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    return dt.strftime("%Y%m%d-%H%M")


def parse_task_timestamp(filename: str) -> datetime | None:
    """Parse timestamp from task filename.

    Args:
        filename: Task filename (e.g., "20251003-1200-description.md")

    Returns:
        Parsed datetime, or None if invalid format
    """
    try:
        # Extract timestamp part (first 13 characters: YYYYMMDD-HHMM)
        timestamp_str = filename[:13]
        return datetime.strptime(timestamp_str, "%Y%m%d-%H%M")
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
