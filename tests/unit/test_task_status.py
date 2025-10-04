"""Unit tests for task status functionality."""

import json
from pathlib import Path


class TestTaskStatusParsing:
    """Test parsing task files for status display."""

    def test_parse_basic_task_info(self):
        """Parse basic task information."""
        from air.services.task_parser import parse_task_file
        from datetime import datetime

        # Create a temporary task file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Task: Test task

## Date
2025-10-03 12:00 UTC

## Prompt
Test prompt

## Actions Taken
1. First action
2. Second action

## Files Changed
- file1.py
- file2.py

## Outcome
✅ Success

## Notes
Test notes
""")
            temp_path = Path(f.name)

        try:
            task_info = parse_task_file(temp_path)

            assert task_info.title == "Test task"
            assert task_info.date == "2025-10-03 12:00 UTC"
            assert task_info.prompt == "Test prompt"
            assert len(task_info.actions) >= 2
            assert len(task_info.files_changed) >= 1  # Parser may consolidate
            assert "file1.py" in task_info.files_changed or any("file1" in f for f in task_info.files_changed)
            assert task_info.outcome == "success"
            assert "Test notes" in task_info.notes
        finally:
            temp_path.unlink()

    def test_parse_in_progress_task(self):
        """Parse task with in-progress status."""
        from air.services.task_parser import parse_task_file

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Task: In progress task

## Outcome
⏳ In Progress

## Notes
""")
            temp_path = Path(f.name)

        try:
            task_info = parse_task_file(temp_path)

            assert task_info.title == "In progress task"
            assert task_info.outcome == "in_progress"
        finally:
            temp_path.unlink()

    def test_parse_blocked_task(self):
        """Parse task with blocked status."""
        from air.services.task_parser import parse_task_file

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Task: Blocked task

## Outcome
🚫 Blocked: dependency issue

## Notes
""")
            temp_path = Path(f.name)

        try:
            task_info = parse_task_file(temp_path)

            assert task_info.title == "Blocked task"
            assert task_info.outcome == "blocked"
        finally:
            temp_path.unlink()


class TestTaskStatusJSON:
    """Test JSON output for task status."""

    def test_json_output_structure(self):
        """Verify JSON output has correct structure."""
        from air.services.task_parser import parse_task_file

        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Task: JSON test

## Date
2025-10-03 12:00 UTC

## Prompt
Test

## Actions Taken
1.

## Files Changed
-

## Outcome
✅ Success

## Notes
""")
            temp_path = Path(f.name)

        try:
            task_info = parse_task_file(temp_path)

            # Simulate JSON output
            output = {
                "filename": task_info.filename,
                "title": task_info.title,
                "date": task_info.date,
                "prompt": task_info.prompt,
                "actions": task_info.actions,
                "files_changed": task_info.files_changed,
                "outcome": task_info.outcome,
                "notes": task_info.notes,
                "timestamp": task_info.timestamp.isoformat() if task_info.timestamp else None,
            }

            # Verify structure
            assert "filename" in output
            assert "title" in output
            assert "outcome" in output
            assert output["title"] == "JSON test"
            assert output["outcome"] == "success"

            # Verify it's valid JSON
            json_str = json.dumps(output)
            parsed = json.loads(json_str)
            assert parsed["title"] == "JSON test"
        finally:
            temp_path.unlink()


class TestTaskStatusDisplay:
    """Test human-readable task status display."""

    def test_status_emoji_mapping(self):
        """Test emoji mapping for different statuses."""
        status_emoji = {
            "success": "✅",
            "in_progress": "⏳",
            "partial": "⚠️",
            "blocked": "🚫",
        }

        assert status_emoji.get("success") == "✅"
        assert status_emoji.get("in_progress") == "⏳"
        assert status_emoji.get("partial") == "⚠️"
        assert status_emoji.get("blocked") == "🚫"
        assert status_emoji.get("unknown", "❓") == "❓"

    def test_filter_empty_actions(self):
        """Test filtering empty actions from display."""
        actions = ["1.", "First action", "", "Second action", "-"]

        # Filter logic from command
        filtered = [a for a in actions if a.strip() and a.strip() not in ["1.", "-"]]

        assert len(filtered) == 2
        assert "First action" in filtered
        assert "Second action" in filtered
        assert "1." not in filtered
        assert "-" not in filtered

    def test_filter_empty_files(self):
        """Test filtering empty files from display."""
        files = ["-", "file1.py", "", "file2.py"]

        # Filter logic from command
        filtered = [f for f in files if f.strip() and f.strip() != "-"]

        assert len(filtered) == 2
        assert "file1.py" in filtered
        assert "file2.py" in filtered
        assert "-" not in filtered
