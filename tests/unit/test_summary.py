"""Tests for summary generation functionality."""

from datetime import datetime
from pathlib import Path

import pytest

from air.services.summary_generator import (
    generate_json_summary,
    generate_markdown_summary,
    generate_statistics,
    generate_text_summary,
)
from air.services.task_parser import TaskInfo, parse_task_file


class TestTaskParser:
    """Tests for task file parsing."""

    def test_parse_simple_task(self, tmp_path):
        """Test parsing a simple task file."""
        task_content = """# Task: Test Task

## Date
2025-10-03 14:00 UTC

## Prompt
Test prompt

## Actions Taken
1. First action
2. Second action

## Files Changed
- src/test.py

## Outcome
✅ Success

Completed successfully

## Notes
Test notes
"""
        task_file = tmp_path / "20251003-1400-test-task.md"
        task_file.write_text(task_content)

        info = parse_task_file(task_file)

        assert info.title == "Test Task"
        assert info.date == "2025-10-03 14:00 UTC"
        assert info.prompt == "Test prompt"
        assert len(info.actions) == 2
        assert "First action" in info.actions
        assert len(info.files_changed) == 1
        assert "src/test.py" in info.files_changed
        assert info.outcome == "success"
        assert info.notes == "Test notes"
        assert info.timestamp.year == 2025
        assert info.timestamp.month == 10
        assert info.timestamp.day == 3

    def test_parse_in_progress_task(self, tmp_path):
        """Test parsing an in-progress task."""
        task_content = """# Task: Ongoing Task

## Date
2025-10-03

## Prompt
Working on it

## Actions Taken
1. Started work

## Files Changed
- (to be documented)

## Outcome
⏳ In Progress

Still working

## Notes
"""
        task_file = tmp_path / "20251003-1500-ongoing.md"
        task_file.write_text(task_content)

        info = parse_task_file(task_file)

        assert info.outcome == "in_progress"
        assert len(info.files_changed) == 0  # Should skip placeholder

    def test_parse_task_with_multiple_files(self, tmp_path):
        """Test parsing task with many files changed."""
        task_content = """# Task: Big Change

## Date
2025-10-03

## Prompt
Large refactoring

## Actions Taken
1. Refactored

## Files Changed
- src/air/commands/task.py - Main implementation
- src/air/services/parser.py - Parser service
- tests/test_parser.py - Tests

## Outcome
✅ Success

## Notes
"""
        task_file = tmp_path / "20251003-1600-big.md"
        task_file.write_text(task_content)

        info = parse_task_file(task_file)

        assert len(info.files_changed) == 3
        assert any("task.py" in f for f in info.files_changed)


class TestStatistics:
    """Tests for statistics generation."""

    def test_generate_statistics_empty(self):
        """Test statistics with no tasks."""
        stats = generate_statistics([])

        assert stats["total_tasks"] == 0
        assert stats["success"] == 0
        assert stats["files_touched"] == 0

    def test_generate_statistics_with_tasks(self):
        """Test statistics with multiple tasks."""
        tasks = [
            TaskInfo(
                filename="task1.md",
                title="Task 1",
                date="2025-10-03",
                prompt="Test",
                actions=[],
                files_changed=["file1.py", "file2.py"],
                outcome="success",
                notes="",
                timestamp=datetime(2025, 10, 3, 10, 0),
            ),
            TaskInfo(
                filename="task2.md",
                title="Task 2",
                date="2025-10-03",
                prompt="Test",
                actions=[],
                files_changed=["file2.py", "file3.py"],
                outcome="in_progress",
                notes="",
                timestamp=datetime(2025, 10, 3, 11, 0),
            ),
        ]

        stats = generate_statistics(tasks)

        assert stats["total_tasks"] == 2
        assert stats["success"] == 1
        assert stats["in_progress"] == 1
        assert stats["files_touched"] == 3  # Unique files
        assert "2025-10-03" in stats["date_range"]


class TestMarkdownSummary:
    """Tests for markdown summary generation."""

    def test_generate_markdown_empty(self):
        """Test markdown generation with no tasks."""
        markdown = generate_markdown_summary([], "Test Project")

        assert "Test Project" in markdown
        assert "**Total Tasks:** 0" in markdown

    def test_generate_markdown_with_tasks(self):
        """Test markdown generation with tasks."""
        tasks = [
            TaskInfo(
                filename="task1.md",
                title="Implement Feature X",
                date="2025-10-03",
                prompt="Add new feature",
                actions=["Action 1", "Action 2"],
                files_changed=["src/feature.py"],
                outcome="success",
                notes="Done",
                timestamp=datetime(2025, 10, 3, 10, 0),
            ),
        ]

        markdown = generate_markdown_summary(tasks, "Test Project")

        assert "# Test Project - Task Summary" in markdown
        assert "✅ Implement Feature X" in markdown
        assert "**Total Tasks:** 1" in markdown
        assert "**Completed:** 1" in markdown
        assert "**Files Changed:** 1" in markdown
        assert "src/feature.py" in markdown

    def test_markdown_truncates_long_prompts(self):
        """Test that long prompts are truncated."""
        long_prompt = "A" * 250

        tasks = [
            TaskInfo(
                filename="task1.md",
                title="Task",
                date="2025-10-03",
                prompt=long_prompt,
                actions=[],
                files_changed=[],
                outcome="success",
                notes="",
                timestamp=datetime(2025, 10, 3),
            ),
        ]

        markdown = generate_markdown_summary(tasks)

        assert "..." in markdown
        assert len(markdown.split("**Prompt:**")[1].split("\n")[0]) < 220


class TestJSONSummary:
    """Tests for JSON summary generation."""

    def test_generate_json_valid(self):
        """Test that JSON output is valid."""
        import json

        tasks = [
            TaskInfo(
                filename="task1.md",
                title="Task 1",
                date="2025-10-03",
                prompt="Test",
                actions=["Action 1"],
                files_changed=["file1.py"],
                outcome="success",
                notes="",
                timestamp=datetime(2025, 10, 3, 10, 0),
            ),
        ]

        json_output = generate_json_summary(tasks, "Test Project")
        data = json.loads(json_output)  # Should not raise

        assert data["project"] == "Test Project"
        assert data["statistics"]["total_tasks"] == 1
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Task 1"
        assert data["tasks"][0]["outcome"] == "success"
        assert data["tasks"][0]["files_count"] == 1


class TestTextSummary:
    """Tests for text summary generation."""

    def test_generate_text_summary(self):
        """Test plain text summary generation."""
        tasks = [
            TaskInfo(
                filename="task1.md",
                title="Task 1",
                date="2025-10-03",
                prompt="Test",
                actions=[],
                files_changed=[],
                outcome="success",
                notes="",
                timestamp=datetime(2025, 10, 3, 10, 0),
            ),
        ]

        text = generate_text_summary(tasks)

        assert "AI TASK SUMMARY" in text
        assert "Total Tasks: 1" in text
        assert "Completed:   1" in text
        assert "RECENT TASKS" in text
        assert "Task 1" in text
