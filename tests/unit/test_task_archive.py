"""Unit tests for task archive service."""

import pytest
from pathlib import Path
from air.services.task_archive import (
    get_archive_path,
    archive_task,
    restore_task,
    find_task_in_archive,
    list_tasks,
    get_tasks_before_date,
    get_archive_stats,
)


class TestGetArchivePath:
    """Tests for get_archive_path function."""

    def test_by_month_strategy(self, tmp_path):
        """Test archive path with by-month strategy."""
        task_file = Path("20251003-1430-implement-feature.md")
        archive_root = tmp_path / "archive"

        path = get_archive_path(task_file, archive_root, "by-month")

        assert path == archive_root / "2025-10" / "20251003-1430-implement-feature.md"

    def test_by_quarter_strategy(self, tmp_path):
        """Test archive path with by-quarter strategy."""
        task_file = Path("20251003-1430-implement-feature.md")
        archive_root = tmp_path / "archive"

        path = get_archive_path(task_file, archive_root, "by-quarter")

        assert path == archive_root / "2025-Q4" / "20251003-1430-implement-feature.md"

    def test_flat_strategy(self, tmp_path):
        """Test archive path with flat strategy."""
        task_file = Path("20251003-1430-implement-feature.md")
        archive_root = tmp_path / "archive"

        path = get_archive_path(task_file, archive_root, "flat")

        assert path == archive_root / "20251003-1430-implement-feature.md"

    def test_different_months(self, tmp_path):
        """Test archive paths for different months."""
        archive_root = tmp_path / "archive"

        jan_task = Path("20250115-1000-task.md")
        jul_task = Path("20250720-1200-task.md")

        jan_path = get_archive_path(jan_task, archive_root, "by-month")
        jul_path = get_archive_path(jul_task, archive_root, "by-month")

        assert jan_path == archive_root / "2025-01" / "20250115-1000-task.md"
        assert jul_path == archive_root / "2025-07" / "20250720-1200-task.md"

    def test_different_quarters(self, tmp_path):
        """Test archive paths for different quarters."""
        archive_root = tmp_path / "archive"

        q1_task = Path("20250201-1000-task.md")
        q2_task = Path("20250501-1200-task.md")
        q3_task = Path("20250801-1400-task.md")
        q4_task = Path("20251101-1600-task.md")

        q1_path = get_archive_path(q1_task, archive_root, "by-quarter")
        q2_path = get_archive_path(q2_task, archive_root, "by-quarter")
        q3_path = get_archive_path(q3_task, archive_root, "by-quarter")
        q4_path = get_archive_path(q4_task, archive_root, "by-quarter")

        assert q1_path == archive_root / "2025-Q1" / "20250201-1000-task.md"
        assert q2_path == archive_root / "2025-Q2" / "20250501-1200-task.md"
        assert q3_path == archive_root / "2025-Q3" / "20250801-1400-task.md"
        assert q4_path == archive_root / "2025-Q4" / "20251101-1600-task.md"


class TestArchiveTask:
    """Tests for archive_task function."""

    def test_archive_task_success(self, tmp_path):
        """Test successful task archiving."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"

        # Create task file
        task_file = tasks_dir / "20251003-1430-implement-feature.md"
        task_file.write_text("# Task content")

        # Archive task
        archive_path = archive_task(task_file, archive_root, "by-month", dry_run=False)

        # Verify
        assert not task_file.exists()
        assert archive_path.exists()
        assert archive_path == archive_root / "2025-10" / "20251003-1430-implement-feature.md"
        assert archive_path.read_text() == "# Task content"

    def test_archive_task_dry_run(self, tmp_path):
        """Test dry run doesn't move file."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"

        task_file = tasks_dir / "20251003-1430-task.md"
        task_file.write_text("content")

        archive_path = archive_task(task_file, archive_root, "by-month", dry_run=True)

        # File should not be moved
        assert task_file.exists()
        assert not archive_path.exists()

    def test_archive_nonexistent_file(self, tmp_path):
        """Test archiving non-existent file raises error."""
        archive_root = tmp_path / "archive"
        task_file = tmp_path / "nonexistent.md"

        with pytest.raises(SystemExit):
            archive_task(task_file, archive_root, "by-month")

    def test_archive_creates_directory(self, tmp_path):
        """Test archive creates directory structure."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"

        task_file = tasks_dir / "20251003-1430-task.md"
        task_file.write_text("content")

        archive_path = archive_task(task_file, archive_root, "by-month")

        # Archive directory should be created
        assert (archive_root / "2025-10").exists()
        assert (archive_root / "2025-10").is_dir()

    def test_archive_duplicate_file(self, tmp_path):
        """Test archiving file that already exists in archive."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"

        task_file = tasks_dir / "20251003-1430-task.md"
        task_file.write_text("content")

        # Archive first time
        archive_task(task_file, archive_root, "by-month")

        # Try to archive again (create new file with same name)
        task_file.write_text("new content")

        with pytest.raises(SystemExit):
            archive_task(task_file, archive_root, "by-month")


class TestRestoreTask:
    """Tests for restore_task function."""

    def test_restore_task_success(self, tmp_path):
        """Test successful task restoration."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive" / "2025-10"
        archive_root.mkdir(parents=True)

        # Create archived task
        archived_task = archive_root / "20251003-1430-implement-feature.md"
        archived_task.write_text("# Task content")

        # Restore task
        restored_path = restore_task("20251003-1430", tasks_dir, archive_root.parent)

        # Verify
        assert not archived_task.exists()
        assert restored_path.exists()
        assert restored_path == tasks_dir / "20251003-1430-implement-feature.md"
        assert restored_path.read_text() == "# Task content"

    def test_restore_nonexistent_task(self, tmp_path):
        """Test restoring non-existent task raises error."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"
        archive_root.mkdir(parents=True)

        with pytest.raises(SystemExit):
            restore_task("nonexistent", tasks_dir, archive_root)

    def test_restore_task_already_exists(self, tmp_path):
        """Test restoring task that already exists in active."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive" / "2025-10"
        archive_root.mkdir(parents=True)

        # Create archived task
        archived_task = archive_root / "20251003-1430-task.md"
        archived_task.write_text("archived content")

        # Create active task with same name
        active_task = tasks_dir / "20251003-1430-task.md"
        active_task.write_text("active content")

        with pytest.raises(SystemExit):
            restore_task("20251003-1430", tasks_dir, archive_root.parent)


class TestFindTaskInArchive:
    """Tests for find_task_in_archive function."""

    def test_find_task_by_id(self, tmp_path):
        """Test finding task by ID."""
        archive_root = tmp_path / "archive"
        month_dir = archive_root / "2025-10"
        month_dir.mkdir(parents=True)

        task_file = month_dir / "20251003-1430-implement-feature.md"
        task_file.write_text("content")

        found = find_task_in_archive("20251003-1430", archive_root)

        assert found == task_file

    def test_find_task_by_filename(self, tmp_path):
        """Test finding task by full filename."""
        archive_root = tmp_path / "archive"
        month_dir = archive_root / "2025-10"
        month_dir.mkdir(parents=True)

        task_file = month_dir / "20251003-1430-implement-feature.md"
        task_file.write_text("content")

        found = find_task_in_archive("20251003-1430-implement-feature.md", archive_root)

        assert found == task_file

    def test_find_task_not_found(self, tmp_path):
        """Test finding non-existent task returns None."""
        archive_root = tmp_path / "archive"
        archive_root.mkdir()

        found = find_task_in_archive("nonexistent", archive_root)

        assert found is None

    def test_find_task_searches_subdirs(self, tmp_path):
        """Test finding task searches all subdirectories."""
        archive_root = tmp_path / "archive"

        # Create tasks in different months
        oct_dir = archive_root / "2025-10"
        oct_dir.mkdir(parents=True)
        sep_dir = archive_root / "2025-09"
        sep_dir.mkdir(parents=True)

        oct_task = oct_dir / "20251015-1200-task1.md"
        oct_task.write_text("oct")
        sep_task = sep_dir / "20250920-1400-task2.md"
        sep_task.write_text("sep")

        found_oct = find_task_in_archive("20251015-1200", archive_root)
        found_sep = find_task_in_archive("20250920-1400", archive_root)

        assert found_oct == oct_task
        assert found_sep == sep_task


class TestListTasks:
    """Tests for list_tasks function."""

    def test_list_active_tasks_only(self, tmp_path):
        """Test listing only active tasks."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"

        # Create active tasks
        task1 = tasks_dir / "20251003-1430-task1.md"
        task1.write_text("task1")
        task2 = tasks_dir / "20251003-1500-task2.md"
        task2.write_text("task2")

        result = list_tasks(tasks_dir, archive_root, include_archived=False)

        assert len(result["active"]) == 2
        assert len(result["archived"]) == 0
        assert task1 in result["active"]
        assert task2 in result["active"]

    def test_list_include_archived(self, tmp_path):
        """Test listing active and archived tasks."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive" / "2025-09"
        archive_root.mkdir(parents=True)

        # Create active tasks
        active_task = tasks_dir / "20251003-1430-active.md"
        active_task.write_text("active")

        # Create archived tasks
        archived_task = archive_root / "20250920-1200-archived.md"
        archived_task.write_text("archived")

        result = list_tasks(tasks_dir, archive_root.parent, include_archived=True)

        assert len(result["active"]) == 1
        assert len(result["archived"]) == 1
        assert active_task in result["active"]
        assert archived_task in result["archived"]

    def test_list_archived_only(self, tmp_path):
        """Test listing only archived tasks."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive" / "2025-09"
        archive_root.mkdir(parents=True)

        # Create active task
        active_task = tasks_dir / "20251003-1430-active.md"
        active_task.write_text("active")

        # Create archived task
        archived_task = archive_root / "20250920-1200-archived.md"
        archived_task.write_text("archived")

        result = list_tasks(tasks_dir, archive_root.parent, archived_only=True)

        assert len(result["active"]) == 0
        assert len(result["archived"]) == 1
        assert archived_task in result["archived"]

    def test_list_tasks_sorted(self, tmp_path):
        """Test tasks are sorted by date (newest first)."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()
        archive_root = tmp_path / "tasks" / "archive"

        # Create tasks in different order
        task1 = tasks_dir / "20251001-1000-old.md"
        task2 = tasks_dir / "20251003-1500-new.md"
        task3 = tasks_dir / "20251002-1200-middle.md"

        task1.write_text("old")
        task2.write_text("new")
        task3.write_text("middle")

        result = list_tasks(tasks_dir, archive_root)

        # Should be sorted newest first
        assert result["active"][0] == task2
        assert result["active"][1] == task3
        assert result["active"][2] == task1


class TestGetTasksBeforeDate:
    """Tests for get_tasks_before_date function."""

    def test_filter_tasks_before_date(self, tmp_path):
        """Test filtering tasks before a date."""
        tasks_dir = tmp_path

        task1 = tasks_dir / "20250915-1200-old.md"
        task2 = tasks_dir / "20251005-1400-new.md"
        task3 = tasks_dir / "20250925-1000-middle.md"

        task1.write_text("old")
        task2.write_text("new")
        task3.write_text("middle")

        tasks = [task1, task2, task3]
        filtered = get_tasks_before_date(tasks, "2025-10-01")

        assert len(filtered) == 2
        assert task1 in filtered
        assert task3 in filtered
        assert task2 not in filtered

    def test_invalid_date_format(self, tmp_path):
        """Test invalid date format raises error."""
        task = tmp_path / "20251003-1430-task.md"
        task.write_text("content")

        with pytest.raises(SystemExit):
            get_tasks_before_date([task], "invalid-date")

    def test_empty_list(self, tmp_path):
        """Test empty task list returns empty."""
        filtered = get_tasks_before_date([], "2025-10-01")
        assert filtered == []

    def test_malformed_filename(self, tmp_path):
        """Test malformed filenames are skipped."""
        tasks_dir = tmp_path

        good_task = tasks_dir / "20250915-1200-task.md"
        bad_task = tasks_dir / "invalid-filename.md"

        good_task.write_text("good")
        bad_task.write_text("bad")

        filtered = get_tasks_before_date([good_task, bad_task], "2025-10-01")

        assert len(filtered) == 1
        assert good_task in filtered


class TestGetArchiveStats:
    """Tests for get_archive_stats function."""

    def test_get_archive_stats_by_month(self, tmp_path):
        """Test getting archive statistics by month."""
        archive_root = tmp_path / "archive"

        # Create tasks in different months
        oct_dir = archive_root / "2025-10"
        oct_dir.mkdir(parents=True)
        sep_dir = archive_root / "2025-09"
        sep_dir.mkdir(parents=True)

        (oct_dir / "task1.md").write_text("1")
        (oct_dir / "task2.md").write_text("2")
        (sep_dir / "task3.md").write_text("3")

        stats = get_archive_stats(archive_root)

        assert stats["total_archived"] == 3
        assert stats["by_month"]["2025-10"] == 2
        assert stats["by_month"]["2025-09"] == 1

    def test_get_archive_stats_by_quarter(self, tmp_path):
        """Test getting archive statistics by quarter."""
        archive_root = tmp_path / "archive"

        q3_dir = archive_root / "2025-Q3"
        q3_dir.mkdir(parents=True)
        q4_dir = archive_root / "2025-Q4"
        q4_dir.mkdir(parents=True)

        (q3_dir / "task1.md").write_text("1")
        (q4_dir / "task2.md").write_text("2")
        (q4_dir / "task3.md").write_text("3")

        stats = get_archive_stats(archive_root)

        assert stats["total_archived"] == 3
        assert stats["by_quarter"]["2025-Q3"] == 1
        assert stats["by_quarter"]["2025-Q4"] == 2

    def test_get_archive_stats_empty(self, tmp_path):
        """Test getting stats from empty archive."""
        archive_root = tmp_path / "archive"
        archive_root.mkdir()

        stats = get_archive_stats(archive_root)

        assert stats["total_archived"] == 0
        assert stats["by_month"] == {}
        assert stats["by_quarter"] == {}

    def test_get_archive_stats_nonexistent(self, tmp_path):
        """Test getting stats from non-existent archive."""
        archive_root = tmp_path / "archive"

        stats = get_archive_stats(archive_root)

        assert stats["total_archived"] == 0
        assert stats["by_month"] == {}
        assert stats["by_quarter"] == {}
