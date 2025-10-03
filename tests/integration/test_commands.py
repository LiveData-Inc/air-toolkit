"""Integration tests for AIR commands."""

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


@pytest.fixture
def runner():
    """Create Click CLI runner."""
    return CliRunner()


@pytest.fixture
def isolated_project(runner):
    """Create an isolated temporary directory for testing."""
    with runner.isolated_filesystem():
        yield Path.cwd()


class TestInitCommand:
    """Tests for air init command."""

    def test_init_creates_project(self, runner, isolated_project):
        """Test air init creates project structure."""
        result = runner.invoke(main, ["init", "test-project", "--mode=review"])

        assert result.exit_code == 0
        assert "Creating AIR project" in result.output
        assert "Project created successfully" in result.output

        # Check project structure
        project_dir = isolated_project / "test-project"
        assert project_dir.exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "CLAUDE.md").exists()
        assert (project_dir / "air-config.json").exists()
        assert (project_dir / ".gitignore").exists()

        # Check directories
        assert (project_dir / ".air").exists()
        assert (project_dir / ".air/tasks").exists()
        assert (project_dir / ".air/context").exists()
        assert (project_dir / "review").exists()
        assert (project_dir / "analysis").exists()

    def test_init_review_mode(self, runner, isolated_project):
        """Test air init with review mode."""
        result = runner.invoke(main, ["init", "review-proj", "--mode=review"])

        assert result.exit_code == 0

        project_dir = isolated_project / "review-proj"
        assert (project_dir / "review").exists()
        assert not (project_dir / "collaborate").exists()
        assert not (project_dir / "contributions").exists()

    def test_init_collaborate_mode(self, runner, isolated_project):
        """Test air init with collaborate mode."""
        result = runner.invoke(main, ["init", "collab-proj", "--mode=collaborate"])

        assert result.exit_code == 0

        project_dir = isolated_project / "collab-proj"
        assert (project_dir / "collaborate").exists()
        assert (project_dir / "contributions").exists()
        assert not (project_dir / "review").exists()

    def test_init_mixed_mode(self, runner, isolated_project):
        """Test air init with mixed mode (default)."""
        result = runner.invoke(main, ["init", "mixed-proj"])

        assert result.exit_code == 0

        project_dir = isolated_project / "mixed-proj"
        assert (project_dir / "review").exists()
        assert (project_dir / "collaborate").exists()
        assert (project_dir / "contributions").exists()

    def test_init_current_directory(self, runner, isolated_project):
        """Test air init in current directory."""
        result = runner.invoke(main, ["init", ".", "--mode=review"])

        assert result.exit_code == 0
        assert (isolated_project / "air-config.json").exists()

    def test_init_no_track(self, runner, isolated_project):
        """Test air init without task tracking."""
        result = runner.invoke(main, ["init", "no-track", "--no-track"])

        assert result.exit_code == 0

        project_dir = isolated_project / "no-track"
        # .air directory should still exist but without some files
        assert (project_dir / ".air").exists()

    def test_init_config_content(self, runner, isolated_project):
        """Test air init creates valid config file."""
        result = runner.invoke(main, ["init", "config-test", "--mode=collaborate"])

        assert result.exit_code == 0

        config_path = isolated_project / "config-test" / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert config["version"] == "2.0.0"
        assert config["name"] == "config-test"
        assert config["mode"] == "collaborate"
        assert "resources" in config
        assert "review" in config["resources"]
        assert "collaborate" in config["resources"]


class TestValidateCommand:
    """Tests for air validate command."""

    def test_validate_not_in_project(self, runner, isolated_project):
        """Test air validate outside project."""
        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 1
        assert "Not an AIR project" in result.output

    def test_validate_valid_project(self, runner, isolated_project):
        """Test air validate on valid project."""
        # Create project first
        runner.invoke(main, ["init", "valid-proj", "--mode=review"])

        # Change to project directory
        import os
        os.chdir(isolated_project / "valid-proj")

        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 0
        assert "Project structure is valid" in result.output

    def test_validate_json_format(self, runner, isolated_project):
        """Test air validate with JSON output."""
        # Create project
        runner.invoke(main, ["init", "json-proj"])

        import os
        os.chdir(isolated_project / "json-proj")

        result = runner.invoke(main, ["validate", "--format=json"])

        assert result.exit_code == 0

        output = json.loads(result.output)
        assert output["success"] is True
        assert output["errors"] == []
        assert "project_root" in output

    def test_validate_missing_files(self, runner, isolated_project):
        """Test air validate detects missing files."""
        # Create project
        runner.invoke(main, ["init", "incomplete-proj"])

        project_dir = isolated_project / "incomplete-proj"

        # Remove required file
        (project_dir / "CLAUDE.md").unlink()

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 3
        assert "Validation failed" in result.output


class TestStatusCommand:
    """Tests for air status command."""

    def test_status_not_in_project(self, runner, isolated_project):
        """Test air status outside project."""
        result = runner.invoke(main, ["status"])

        assert result.exit_code == 1
        assert "Not an AIR project" in result.output

    def test_status_new_project(self, runner, isolated_project):
        """Test air status on new project."""
        # Create project
        runner.invoke(main, ["init", "status-proj"])

        import os
        os.chdir(isolated_project / "status-proj")

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "AIR Project Status" in result.output
        assert "status-proj" in result.output
        assert "Resources: 0" in result.output

    def test_status_json_format(self, runner, isolated_project):
        """Test air status with JSON output."""
        # Create project
        runner.invoke(main, ["init", "json-status-proj", "--mode=review"])

        import os
        os.chdir(isolated_project / "json-status-proj")

        result = runner.invoke(main, ["status", "--format=json"])

        assert result.exit_code == 0

        output = json.loads(result.output)
        assert output["success"] is True
        assert output["project"]["name"] == "json-status-proj"
        assert output["project"]["mode"] == "review"
        assert output["resources"]["total"] == 0

    def test_status_shows_project_info(self, runner, isolated_project):
        """Test air status displays project information."""
        runner.invoke(main, ["init", "info-proj", "--mode=collaborate"])

        import os
        os.chdir(isolated_project / "info-proj")

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "info-proj" in result.output
        assert "collaborate" in result.output


class TestWorkflow:
    """Integration tests for complete workflows."""

    def test_full_workflow(self, runner, isolated_project):
        """Test complete init -> validate -> status workflow."""
        # Init
        result = runner.invoke(main, ["init", "workflow-test"])
        assert result.exit_code == 0

        import os
        os.chdir(isolated_project / "workflow-test")

        # Validate
        result = runner.invoke(main, ["validate"])
        assert result.exit_code == 0
        assert "valid" in result.output

        # Status
        result = runner.invoke(main, ["status"])
        assert result.exit_code == 0
        assert "workflow-test" in result.output

    def test_workflow_with_json_output(self, runner, isolated_project):
        """Test workflow with JSON output at each step."""
        # Init
        runner.invoke(main, ["init", "json-workflow"])

        import os
        os.chdir(isolated_project / "json-workflow")

        # Validate with JSON
        result = runner.invoke(main, ["validate", "--format=json"])
        assert result.exit_code == 0
        validate_data = json.loads(result.output)
        assert validate_data["success"] is True

        # Status with JSON
        result = runner.invoke(main, ["status", "--format=json"])
        assert result.exit_code == 0
        status_data = json.loads(result.output)
        assert status_data["success"] is True
        assert status_data["project"]["name"] == "json-workflow"

class TestTaskArchiveCommands:
    """Integration tests for task archive commands."""

    def test_task_list_empty(self, runner, isolated_project):
        """Test listing tasks in empty project."""
        # Create project
        runner.invoke(main, ["init", "task-project"])
        import os
        os.chdir(isolated_project / "task-project")

        # List tasks
        result = runner.invoke(main, ["task", "list"])
        assert result.exit_code == 0
        assert "Active Tasks" in result.output
        assert "No active tasks" in result.output

    def test_task_list_with_tasks(self, runner, isolated_project):
        """Test listing tasks with some task files."""
        # Create project
        runner.invoke(main, ["init", "task-project"])
        project_dir = isolated_project / "task-project"
        import os
        os.chdir(project_dir)

        # Create some task files
        tasks_dir = project_dir / ".air/tasks"
        task1 = tasks_dir / "20251003-1430-implement-feature.md"
        task2 = tasks_dir / "20251003-1500-fix-bug.md"
        task1.write_text("# Task 1")
        task2.write_text("# Task 2")

        # List tasks
        result = runner.invoke(main, ["task", "list"])
        assert result.exit_code == 0
        assert "20251003-1430-implement-feature.md" in result.output
        assert "20251003-1500-fix-bug.md" in result.output
        assert "Active: 2" in result.output

    def test_task_list_json_format(self, runner, isolated_project):
        """Test listing tasks with JSON output."""
        # Create project
        runner.invoke(main, ["init", "task-project"])
        project_dir = isolated_project / "task-project"
        import os
        os.chdir(project_dir)

        # Create task file
        tasks_dir = project_dir / ".air/tasks"
        task1 = tasks_dir / "20251003-1430-task.md"
        task1.write_text("# Task")

        # List with JSON
        result = runner.invoke(main, ["task", "list", "--format=json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["total_active"] == 1
        assert data["total_archived"] == 0
        assert len(data["active"]) == 1

    def test_task_archive_single_task(self, runner, isolated_project):
        """Test archiving a single task."""
        # Create project
        runner.invoke(main, ["init", "archive-project"])
        project_dir = isolated_project / "archive-project"
        import os
        os.chdir(project_dir)

        # Create task
        tasks_dir = project_dir / ".air/tasks"
        task_file = tasks_dir / "20251003-1430-old-task.md"
        task_file.write_text("# Old task")

        # Archive task
        result = runner.invoke(main, ["task", "archive", "20251003-1430"])
        assert result.exit_code == 0
        assert "Archived: 20251003-1430-old-task.md" in result.output

        # Verify task moved to archive
        assert not task_file.exists()
        archive_path = tasks_dir / "archive/2025-10/20251003-1430-old-task.md"
        assert archive_path.exists()

    def test_task_archive_multiple_tasks(self, runner, isolated_project):
        """Test archiving multiple tasks at once."""
        # Create project
        runner.invoke(main, ["init", "multi-archive"])
        project_dir = isolated_project / "multi-archive"
        import os
        os.chdir(project_dir)

        # Create tasks
        tasks_dir = project_dir / ".air/tasks"
        task1 = tasks_dir / "20251003-1430-task1.md"
        task2 = tasks_dir / "20251003-1500-task2.md"
        task1.write_text("# Task 1")
        task2.write_text("# Task 2")

        # Archive both tasks
        result = runner.invoke(main, ["task", "archive", "20251003-1430", "20251003-1500"])
        assert result.exit_code == 0
        assert "Archived 2 tasks" in result.output

        # Verify both moved
        assert not task1.exists()
        assert not task2.exists()

    def test_task_archive_all(self, runner, isolated_project):
        """Test archiving all tasks."""
        # Create project
        runner.invoke(main, ["init", "archive-all"])
        project_dir = isolated_project / "archive-all"
        import os
        os.chdir(project_dir)

        # Create multiple tasks
        tasks_dir = project_dir / ".air/tasks"
        for i in range(3):
            task = tasks_dir / f"2025100{i + 1}-1{i}00-task{i}.md"
            task.write_text(f"# Task {i}")

        # Archive all
        result = runner.invoke(main, ["task", "archive", "--all"])
        assert result.exit_code == 0
        assert "Archived 3 tasks" in result.output

    def test_task_archive_before_date(self, runner, isolated_project):
        """Test archiving tasks before a specific date."""
        # Create project
        runner.invoke(main, ["init", "date-archive"])
        project_dir = isolated_project / "date-archive"
        import os
        os.chdir(project_dir)

        # Create tasks with different dates
        tasks_dir = project_dir / ".air/tasks"
        old_task = tasks_dir / "20250915-1200-old.md"
        new_task = tasks_dir / "20251005-1400-new.md"
        old_task.write_text("# Old")
        new_task.write_text("# New")

        # Archive before Oct 1
        result = runner.invoke(main, ["task", "archive", "--before=2025-10-01"])
        assert result.exit_code == 0

        # Only old task should be archived
        assert not old_task.exists()
        assert new_task.exists()

    def test_task_archive_dry_run(self, runner, isolated_project):
        """Test dry run shows what would be archived."""
        # Create project
        runner.invoke(main, ["init", "dry-run-test"])
        project_dir = isolated_project / "dry-run-test"
        import os
        os.chdir(project_dir)

        # Create task
        tasks_dir = project_dir / ".air/tasks"
        task_file = tasks_dir / "20251003-1430-task.md"
        task_file.write_text("# Task")

        # Dry run
        result = runner.invoke(main, ["task", "archive", "--all", "--dry-run"])
        assert result.exit_code == 0
        assert "Would archive" in result.output
        assert "Dry run" in result.output

        # Task should still exist
        assert task_file.exists()

    def test_task_restore(self, runner, isolated_project):
        """Test restoring an archived task."""
        # Create project
        runner.invoke(main, ["init", "restore-test"])
        project_dir = isolated_project / "restore-test"
        import os
        os.chdir(project_dir)

        # Create and archive a task
        tasks_dir = project_dir / ".air/tasks"
        task_file = tasks_dir / "20251003-1430-task.md"
        task_file.write_text("# Task")
        runner.invoke(main, ["task", "archive", "20251003-1430"])

        # Restore task
        result = runner.invoke(main, ["task", "restore", "20251003-1430"])
        assert result.exit_code == 0
        assert "Restored: 20251003-1430-task.md" in result.output

        # Task should be back in active
        assert task_file.exists()
        archive_path = tasks_dir / "archive/2025-10/20251003-1430-task.md"
        assert not archive_path.exists()

    def test_task_list_with_archived(self, runner, isolated_project):
        """Test listing tasks with --all flag includes archived."""
        # Create project
        runner.invoke(main, ["init", "list-all-test"])
        project_dir = isolated_project / "list-all-test"
        import os
        os.chdir(project_dir)

        # Create active and archived tasks
        tasks_dir = project_dir / ".air/tasks"
        active_task = tasks_dir / "20251003-1500-active.md"
        old_task = tasks_dir / "20251003-1430-to-archive.md"
        active_task.write_text("# Active")
        old_task.write_text("# To Archive")

        # Archive one task
        runner.invoke(main, ["task", "archive", "20251003-1430"])

        # List with --all
        result = runner.invoke(main, ["task", "list", "--all"])
        assert result.exit_code == 0
        assert "Active Tasks" in result.output
        assert "Archived Tasks" in result.output
        assert "20251003-1500-active.md" in result.output
        assert "2025-10/20251003-1430-to-archive.md" in result.output

    def test_task_list_archived_only(self, runner, isolated_project):
        """Test listing only archived tasks."""
        # Create project
        runner.invoke(main, ["init", "archived-only-test"])
        project_dir = isolated_project / "archived-only-test"
        import os
        os.chdir(project_dir)

        # Create and archive task
        tasks_dir = project_dir / ".air/tasks"
        active_task = tasks_dir / "20251003-1500-active.md"
        old_task = tasks_dir / "20251003-1430-archived.md"
        active_task.write_text("# Active")
        old_task.write_text("# Archived")

        runner.invoke(main, ["task", "archive", "20251003-1430"])

        # List archived only
        result = runner.invoke(main, ["task", "list", "--archived"])
        assert result.exit_code == 0
        assert "Archived Tasks" in result.output
        assert "2025-10/20251003-1430-archived.md" in result.output
        assert "Active: 0" in result.output

    def test_task_archive_status(self, runner, isolated_project):
        """Test archive status command."""
        # Create project
        runner.invoke(main, ["init", "status-test"])
        project_dir = isolated_project / "status-test"
        import os
        os.chdir(project_dir)

        # Create and archive tasks
        tasks_dir = project_dir / ".air/tasks"
        task1 = tasks_dir / "20251003-1430-task1.md"
        task2 = tasks_dir / "20251003-1500-task2.md"
        task1.write_text("# Task 1")
        task2.write_text("# Task 2")

        runner.invoke(main, ["task", "archive", "--all"])

        # Check status
        result = runner.invoke(main, ["task", "archive-status"])
        assert result.exit_code == 0
        assert "Archive Statistics" in result.output
        assert "Total archived tasks: 2" in result.output
        assert "2025-10: 2 tasks" in result.output

    def test_task_archive_status_json(self, runner, isolated_project):
        """Test archive status with JSON output."""
        # Create project
        runner.invoke(main, ["init", "json-status-test"])
        project_dir = isolated_project / "json-status-test"
        import os
        os.chdir(project_dir)

        # Create and archive task
        tasks_dir = project_dir / ".air/tasks"
        task = tasks_dir / "20251003-1430-task.md"
        task.write_text("# Task")

        runner.invoke(main, ["task", "archive", "20251003-1430"])

        # Check status with JSON
        result = runner.invoke(main, ["task", "archive-status", "--format=json"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["total_archived"] == 1
        assert data["by_month"]["2025-10"] == 1


class TestInitInExistingProject:
    """Tests for air init in existing projects."""

    def test_init_no_args_current_directory(self, runner, isolated_project):
        """Test air init with no arguments initializes current directory."""
        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        assert "Initializing AIR in current directory" in result.output
        assert "AIR initialized in" in result.output

        # Check project structure in current directory
        assert (isolated_project / "air-config.json").exists()
        assert (isolated_project / "README.md").exists()
        assert (isolated_project / ".air").exists()

    def test_init_no_args_with_mode(self, runner, isolated_project):
        """Test air init with mode but no name."""
        result = runner.invoke(main, ["init", "--mode=review"])

        assert result.exit_code == 0
        assert "review" in result.output

        # Should be in current directory
        assert (isolated_project / "air-config.json").exists()
        assert (isolated_project / "review").exists()
        assert not (isolated_project / "collaborate").exists()

    def test_init_in_existing_directory_with_files(self, runner, isolated_project):
        """Test initializing AIR in directory with existing files."""
        # Create some existing files
        (isolated_project / "README.md").write_text("# Existing project")
        (isolated_project / "src").mkdir()
        (isolated_project / "src/main.py").write_text("print('hello')")

        result = runner.invoke(main, ["init"])

        assert result.exit_code == 0
        assert "Initializing AIR in directory with" in result.output
        assert "existing files" in result.output

        # AIR files should be created alongside existing ones
        assert (isolated_project / "air-config.json").exists()
        assert (isolated_project / ".air").exists()
        # Original files should still exist
        assert (isolated_project / "src/main.py").exists()

    def test_init_create_dir_flag(self, runner, isolated_project):
        """Test air init --create-dir creates new directory."""
        result = runner.invoke(main, ["init", "--create-dir", "new-proj"])

        assert result.exit_code == 0
        assert "Creating AIR project" in result.output

        project_dir = isolated_project / "new-proj"
        assert project_dir.exists()
        assert (project_dir / "air-config.json").exists()

    def test_init_create_dir_without_name_error(self, runner, isolated_project):
        """Test air init --create-dir without name fails."""
        result = runner.invoke(main, ["init", "--create-dir"])

        assert result.exit_code == 1
        assert "Must provide NAME" in result.output

    def test_init_already_initialized_error(self, runner, isolated_project):
        """Test air init fails if already initialized."""
        # First initialization
        runner.invoke(main, ["init"])

        # Second attempt should fail
        result = runner.invoke(main, ["init"])

        assert result.exit_code == 1
        assert "already an AIR project" in result.output

    def test_init_backward_compat_with_name(self, runner, isolated_project):
        """Test backward compatibility: air init <name> creates directory."""
        result = runner.invoke(main, ["init", "my-project"])

        assert result.exit_code == 0
        assert "Creating AIR project" in result.output

        # Should create new directory
        project_dir = isolated_project / "my-project"
        assert project_dir.exists()
        assert (project_dir / "air-config.json").exists()

    def test_init_dot_in_current_directory(self, runner, isolated_project):
        """Test air init . initializes current directory."""
        result = runner.invoke(main, ["init", "."])

        assert result.exit_code == 0
        assert "Initializing AIR in current directory" in result.output

        assert (isolated_project / "air-config.json").exists()

    def test_init_non_empty_directory_error(self, runner, isolated_project):
        """Test creating new project in non-empty directory fails."""
        # Create directory with content
        new_dir = isolated_project / "existing"
        new_dir.mkdir()
        (new_dir / "file.txt").write_text("content")

        result = runner.invoke(main, ["init", "existing"])

        assert result.exit_code == 1
        assert "Directory not empty" in result.output
