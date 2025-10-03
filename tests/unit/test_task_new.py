"""Tests for task new command functionality."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from air.utils.dates import format_timestamp
from air.utils.paths import safe_filename


class TestTaskNewHelpers:
    """Tests for task new helper functions."""

    def test_format_timestamp(self):
        """Test timestamp formatting for task files."""
        dt = datetime(2025, 10, 3, 14, 30)
        timestamp = format_timestamp(dt)
        assert timestamp == "20251003-1430"

    def test_safe_filename_with_spaces(self):
        """Test converting description to safe filename."""
        assert safe_filename("implement feature X") == "implement-feature-x"

    def test_safe_filename_with_special_chars(self):
        """Test removing special characters."""
        assert safe_filename("fix bug: login @issue") == "fix-bug-login-issue"

    def test_safe_filename_with_multiple_spaces(self):
        """Test handling multiple spaces."""
        assert safe_filename("test   multiple   spaces") == "test-multiple-spaces"

    def test_task_filename_format(self):
        """Test complete task filename format."""
        timestamp = "20251003-1430"
        description = safe_filename("implement feature X")
        filename = f"{timestamp}-{description}.md"
        assert filename == "20251003-1430-implement-feature-x.md"


class TestTaskTemplate:
    """Tests for task template rendering."""

    def test_template_has_required_sections(self):
        """Test that task template has all required sections."""
        from air.services.templates import render_template

        context = {
            "title": "Test Task",
            "date": "2025-10-03 14:30 UTC",
            "prompt": "Test prompt",
            "description": "Test description",
        }

        content = render_template("ai/task.md.j2", context)

        # Check required sections
        assert "# Task: Test Task" in content
        assert "## Date" in content
        assert "2025-10-03 14:30 UTC" in content
        assert "## Prompt" in content
        assert "Test prompt" in content
        assert "## Actions Taken" in content
        assert "## Files Changed" in content
        assert "## Outcome" in content
        assert "⏳ In Progress" in content
        assert "## Notes" in content
        assert "Test description" in content

    def test_template_with_minimal_context(self):
        """Test template with minimal required fields."""
        from air.services.templates import render_template

        context = {
            "title": "Simple Task",
            "date": "2025-10-03",
            "prompt": "Do something",
            "description": "Working on task",
        }

        content = render_template("ai/task.md.j2", context)
        assert "# Task: Simple Task" in content
        assert "Do something" in content

    def test_template_escapes_special_characters(self):
        """Test that template handles special characters."""
        from air.services.templates import render_template

        context = {
            "title": "Task with 'quotes' and \"double quotes\"",
            "date": "2025-10-03",
            "prompt": "Prompt with <html> & special chars",
            "description": "Description with special chars",
        }

        content = render_template("ai/task.md.j2", context)
        assert "Task with 'quotes'" in content
        assert "special chars" in content
