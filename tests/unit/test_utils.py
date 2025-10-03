"""Tests for utility modules."""

from datetime import datetime
from pathlib import Path

from air.utils.dates import format_timestamp, parse_task_timestamp, format_duration
from air.utils.paths import expand_path, safe_filename


def test_format_timestamp():
    """Test timestamp formatting."""
    dt = datetime(2025, 10, 3, 14, 30)
    assert format_timestamp(dt) == "20251003-1430"


def test_parse_task_timestamp():
    """Test parsing timestamp from filename."""
    filename = "20251003-1430-description.md"
    dt = parse_task_timestamp(filename)

    assert dt is not None
    assert dt.year == 2025
    assert dt.month == 10
    assert dt.day == 3
    assert dt.hour == 14
    assert dt.minute == 30


def test_parse_task_timestamp_invalid():
    """Test parsing invalid timestamp."""
    filename = "invalid-filename.md"
    dt = parse_task_timestamp(filename)
    assert dt is None


def test_format_duration():
    """Test duration formatting."""
    start = datetime(2025, 10, 3, 10, 0)
    end = datetime(2025, 10, 3, 12, 30)

    duration = format_duration(start, end)
    assert duration == "2h 30m"


def test_expand_path():
    """Test path expansion."""
    # Should expand ~ and make absolute
    path = expand_path("~/test")
    assert isinstance(path, Path)
    assert "~" not in str(path)
    assert path.is_absolute()


def test_safe_filename():
    """Test safe filename generation."""
    assert safe_filename("My Test File") == "my-test-file"
    assert safe_filename("Test@#$%File") == "testfile"
    assert safe_filename("UPPERCASE") == "uppercase"
