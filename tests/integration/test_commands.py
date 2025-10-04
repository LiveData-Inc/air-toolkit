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


@pytest.fixture
def air_project(runner, isolated_project):
    """Create an initialized AIR project for testing."""
    result = runner.invoke(main, ["init", "test-project", "--mode=mixed"])
    assert result.exit_code == 0
    project_dir = isolated_project / "test-project"
    return project_dir


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


class TestLinkCommand:
    """Tests for air link commands."""

    def test_link_add_review_resource(self, runner, isolated_project):
        """Test adding a review resource."""
        # Create AIR project
        runner.invoke(main, ["init", "link-project", "--mode=mixed"])
        project_dir = isolated_project / "link-project"

        # Create source directory to link
        source_dir = isolated_project / "service-a"
        source_dir.mkdir()
        (source_dir / "README.md").write_text("Service A")

        # Change to project directory
        import os
        os.chdir(project_dir)

        # Add resource
        result = runner.invoke(
            main,
            ["link", "add", f"service-a:{source_dir}", "--review"]
        )

        assert result.exit_code == 0
        assert "Linked review resource: service-a" in result.output

        # Verify symlink created
        link_path = project_dir / "review/service-a"
        assert link_path.exists()
        assert link_path.is_symlink()
        assert link_path.resolve() == source_dir

        # Verify config updated
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["review"]) == 1
        assert config["resources"]["review"][0]["name"] == "service-a"
        assert config["resources"]["review"][0]["type"] == "implementation"
        assert config["resources"]["review"][0]["relationship"] == "review-only"

    def test_link_add_collaborate_resource(self, runner, isolated_project):
        """Test adding a collaborative resource."""
        # Create AIR project
        runner.invoke(main, ["init", "collab-project", "--mode=mixed"])
        project_dir = isolated_project / "collab-project"

        # Create source directory
        source_dir = isolated_project / "docs"
        source_dir.mkdir()
        (source_dir / "index.md").write_text("Documentation")

        import os
        os.chdir(project_dir)

        # Add resource
        result = runner.invoke(
            main,
            ["link", "add", f"docs:{source_dir}", "--collaborate", "--type=documentation"]
        )

        assert result.exit_code == 0
        assert "Linked collaborate resource: docs" in result.output

        # Verify symlink
        link_path = project_dir / "collaborate/docs"
        assert link_path.exists()
        assert link_path.is_symlink()

        # Verify config
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["collaborate"]) == 1
        assert config["resources"]["collaborate"][0]["name"] == "docs"
        assert config["resources"]["collaborate"][0]["type"] == "documentation"
        assert config["resources"]["collaborate"][0]["relationship"] == "contributor"

    def test_link_add_default_review_mode(self, runner, isolated_project):
        """Test that default mode is review when no flag specified."""
        runner.invoke(main, ["init", "default-project", "--mode=mixed"])
        project_dir = isolated_project / "default-project"

        source_dir = isolated_project / "lib"
        source_dir.mkdir()

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["link", "add", f"lib:{source_dir}"])

        assert result.exit_code == 0
        assert "Defaulting to review mode" in result.output
        assert "Linked review resource: lib" in result.output

    def test_link_add_invalid_format(self, runner, isolated_project):
        """Test error when NAME:PATH format is invalid."""
        runner.invoke(main, ["init", "error-project"])
        project_dir = isolated_project / "error-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["link", "add", "invalid-format"])

        assert result.exit_code == 1
        assert "Invalid format" in result.output

    def test_link_add_nonexistent_path(self, runner, isolated_project):
        """Test error when source path doesn't exist."""
        runner.invoke(main, ["init", "path-error"])
        project_dir = isolated_project / "path-error"

        import os
        os.chdir(project_dir)

        result = runner.invoke(
            main,
            ["link", "add", "missing:/nonexistent/path", "--review"]
        )

        assert result.exit_code == 1
        assert "Path does not exist" in result.output

    def test_link_add_duplicate_name(self, runner, isolated_project):
        """Test error when resource name already exists."""
        runner.invoke(main, ["init", "dup-project"])
        project_dir = isolated_project / "dup-project"

        source1 = isolated_project / "source1"
        source1.mkdir()
        source2 = isolated_project / "source2"
        source2.mkdir()

        import os
        os.chdir(project_dir)

        # Add first resource
        runner.invoke(main, ["link", "add", f"repo:{source1}", "--review"])

        # Try to add with same name
        result = runner.invoke(main, ["link", "add", f"repo:{source2}", "--review"])

        assert result.exit_code == 1
        assert "already linked" in result.output

    def test_link_list_empty(self, runner, isolated_project):
        """Test listing when no resources linked."""
        runner.invoke(main, ["init", "empty-project"])
        project_dir = isolated_project / "empty-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["link", "list"])

        assert result.exit_code == 0
        assert "No resources linked" in result.output

    def test_link_list_human_format(self, runner, isolated_project):
        """Test listing resources in human-readable format."""
        runner.invoke(main, ["init", "list-project", "--mode=mixed"])
        project_dir = isolated_project / "list-project"

        # Create and link resources
        review_src = isolated_project / "review-repo"
        review_src.mkdir()
        collab_src = isolated_project / "collab-repo"
        collab_src.mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", f"review-repo:{review_src}", "--review"])
        runner.invoke(main, ["link", "add", f"collab-repo:{collab_src}", "--collaborate"])

        result = runner.invoke(main, ["link", "list"])

        assert result.exit_code == 0
        assert "Review Resources (Read-Only)" in result.output
        assert "Collaborative Resources" in result.output
        assert "review-repo" in result.output
        assert "collab-repo" in result.output
        assert "Total: 2 resources" in result.output

    def test_link_list_json_format(self, runner, isolated_project):
        """Test listing resources in JSON format."""
        runner.invoke(main, ["init", "json-project", "--mode=mixed"])
        project_dir = isolated_project / "json-project"

        source_dir = isolated_project / "api"
        source_dir.mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", f"api:{source_dir}", "--review", "--type=service"])

        result = runner.invoke(main, ["link", "list", "--format=json"])

        assert result.exit_code == 0

        output_data = json.loads(result.output)
        assert "review" in output_data
        assert "collaborate" in output_data
        assert len(output_data["review"]) == 1
        assert output_data["review"][0]["name"] == "api"
        assert output_data["review"][0]["type"] == "service"

    def test_link_remove(self, runner, isolated_project):
        """Test removing a linked resource."""
        runner.invoke(main, ["init", "remove-project"])
        project_dir = isolated_project / "remove-project"

        source_dir = isolated_project / "to-remove"
        source_dir.mkdir()

        import os
        os.chdir(project_dir)

        # Add resource
        runner.invoke(main, ["link", "add", f"to-remove:{source_dir}", "--review"])

        link_path = project_dir / "review/to-remove"
        assert link_path.exists()

        # Remove resource
        result = runner.invoke(main, ["link", "remove", "to-remove"])

        assert result.exit_code == 0
        assert "Removed resource: to-remove" in result.output

        # Verify symlink removed
        assert not link_path.exists()

        # Verify config updated
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["review"]) == 0

    def test_link_remove_keep_link(self, runner, isolated_project):
        """Test removing resource but keeping symlink."""
        runner.invoke(main, ["init", "keep-project"])
        project_dir = isolated_project / "keep-project"

        source_dir = isolated_project / "keep-link"
        source_dir.mkdir()

        import os
        os.chdir(project_dir)

        # Add and remove with --keep-link
        runner.invoke(main, ["link", "add", f"keep-link:{source_dir}", "--review"])
        result = runner.invoke(main, ["link", "remove", "keep-link", "--keep-link"])

        assert result.exit_code == 0
        assert "Keeping symlink" in result.output

        # Verify symlink still exists
        link_path = project_dir / "review/keep-link"
        assert link_path.exists()

        # But config updated
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["review"]) == 0

    def test_link_remove_nonexistent(self, runner, isolated_project):
        """Test error when removing non-existent resource."""
        runner.invoke(main, ["init", "notfound-project"])
        project_dir = isolated_project / "notfound-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["link", "remove", "nonexistent"])

        assert result.exit_code == 1
        assert "Resource not found" in result.output

    def test_link_not_in_air_project(self, runner, isolated_project):
        """Test error when running link command outside AIR project."""
        result = runner.invoke(main, ["link", "list"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output


class TestTaskNewCommand:
    """Tests for air task new command."""

    def test_task_new_creates_file(self, runner, isolated_project):
        """Test creating a new task file."""
        # Create AIR project
        runner.invoke(main, ["init", "task-project"])
        project_dir = isolated_project / "task-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["task", "new", "implement feature X"])

        assert result.exit_code == 0
        assert "Task file created" in result.output
        assert "implement-feature-x.md" in result.output

        # Verify file exists
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-implement-feature-x.md"))
        assert len(task_files) == 1

        # Verify file content
        task_content = task_files[0].read_text()
        assert "# Task: Implement feature x" in task_content
        assert "## Date" in task_content
        assert "## Prompt" in task_content
        assert "implement feature X" in task_content
        assert "## Actions Taken" in task_content
        assert "## Files Changed" in task_content
        assert "## Outcome" in task_content
        assert "⏳ In Progress" in task_content
        assert "## Notes" in task_content

    def test_task_new_with_prompt(self, runner, isolated_project):
        """Test creating task with custom prompt."""
        runner.invoke(main, ["init", "prompt-project"])
        project_dir = isolated_project / "prompt-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(
            main,
            ["task", "new", "fix bug Y", "--prompt", "Fix the critical login issue"]
        )

        assert result.exit_code == 0

        # Verify prompt in file
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-fix-bug-y.md"))
        assert len(task_files) == 1

        task_content = task_files[0].read_text()
        assert "Fix the critical login issue" in task_content

    def test_task_new_filename_format(self, runner, isolated_project):
        """Test that task filename has correct format."""
        runner.invoke(main, ["init", "format-project"])
        project_dir = isolated_project / "format-project"

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["task", "new", "test task"])

        # Verify filename format: YYYYMMDD-HHMM-description.md
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-test-task.md"))
        assert len(task_files) == 1

        filename = task_files[0].name
        # Should start with timestamp: YYYYMMDD-HHMM
        assert len(filename) >= 18  # YYYYMMDD-HHMM-x.md = 18 chars minimum
        assert filename[:8].isdigit()  # YYYYMMDD
        assert filename[8] == "-"
        assert filename[9:13].isdigit()  # HHMM
        assert filename.endswith("-test-task.md")

    def test_task_new_not_in_air_project(self, runner, isolated_project):
        """Test error when not in AIR project."""
        result = runner.invoke(main, ["task", "new", "test"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output

    def test_task_new_special_characters(self, runner, isolated_project):
        """Test task with special characters in description."""
        runner.invoke(main, ["init", "special-project"])
        project_dir = isolated_project / "special-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(
            main,
            ["task", "new", "fix: bug @#$ with login"]
        )

        assert result.exit_code == 0

        # Verify filename sanitization
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-fix-bug-with-login.md"))
        assert len(task_files) == 1

    def test_task_new_shows_in_list(self, runner, isolated_project):
        """Test that new task appears in task list."""
        runner.invoke(main, ["init", "list-test"])
        project_dir = isolated_project / "list-test"

        import os
        os.chdir(project_dir)

        # Create task
        runner.invoke(main, ["task", "new", "test task"])

        # List tasks
        result = runner.invoke(main, ["task", "list"])

        assert result.exit_code == 0
        assert "test-task.md" in result.output
        assert "Active: 1" in result.output

    def test_task_new_multiple_tasks(self, runner, isolated_project):
        """Test creating multiple tasks."""
        runner.invoke(main, ["init", "multi-task"])
        project_dir = isolated_project / "multi-task"

        import os
        os.chdir(project_dir)

        # Create multiple tasks
        runner.invoke(main, ["task", "new", "task one"])

        # Wait a moment to ensure different timestamps
        import time
        time.sleep(0.1)

        runner.invoke(main, ["task", "new", "task two"])

        # List tasks
        result = runner.invoke(main, ["task", "list"])

        assert result.exit_code == 0
        assert "task-one.md" in result.output
        assert "task-two.md" in result.output
        assert "Active: 2" in result.output


class TestSummaryCommand:
    """Tests for air summary command."""

    def test_summary_not_in_air_project(self, runner, isolated_project):
        """Test error when not in AIR project."""
        result = runner.invoke(main, ["summary"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output

    def test_summary_no_tasks(self, runner, isolated_project):
        """Test summary with no task files."""
        runner.invoke(main, ["init", "empty-summary"])
        project_dir = isolated_project / "empty-summary"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["summary"])

        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_summary_with_tasks(self, runner, isolated_project):
        """Test summary with task files."""
        runner.invoke(main, ["init", "summary-test"])
        project_dir = isolated_project / "summary-test"

        import os
        os.chdir(project_dir)

        # Create a few tasks
        runner.invoke(main, ["task", "new", "task one"])
        runner.invoke(main, ["task", "new", "task two"])

        # Mark one as complete by updating its file
        import time
        time.sleep(0.1)
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-task-one.md"))
        if task_files:
            content = task_files[0].read_text()
            content = content.replace("⏳ In Progress", "✅ Success")
            task_files[0].write_text(content)

        result = runner.invoke(main, ["summary"])

        assert result.exit_code == 0
        assert "Task Summary" in result.output or "TASK SUMMARY" in result.output

    def test_summary_json_format(self, runner, isolated_project):
        """Test summary with JSON output."""
        runner.invoke(main, ["init", "json-summary"])
        project_dir = isolated_project / "json-summary"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "test task"])

        result = runner.invoke(main, ["summary", "--format=json"])

        assert result.exit_code == 0

        # Verify JSON is valid
        output_data = json.loads(result.output)
        assert "statistics" in output_data
        assert "tasks" in output_data
        assert output_data["statistics"]["total_tasks"] >= 1

    def test_summary_text_format(self, runner, isolated_project):
        """Test summary with plain text output."""
        runner.invoke(main, ["init", "text-summary"])
        project_dir = isolated_project / "text-summary"

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["task", "new", "simple task"])

        result = runner.invoke(main, ["summary", "--format=text"])

        assert result.exit_code == 0
        assert "AI TASK SUMMARY" in result.output
        assert "Total Tasks:" in result.output

    def test_summary_output_to_file(self, runner, isolated_project):
        """Test writing summary to file."""
        runner.invoke(main, ["init", "file-summary"])
        project_dir = isolated_project / "file-summary"

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["task", "new", "documented task"])

        output_file = project_dir / "SUMMARY.md"
        result = runner.invoke(main, ["summary", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "Task Summary" in content
        assert "documented task" in content.lower()

    def test_summary_since_filter(self, runner, isolated_project):
        """Test filtering tasks by date."""
        runner.invoke(main, ["init", "since-summary"])
        project_dir = isolated_project / "since-summary"

        import os
        os.chdir(project_dir)

        # Create tasks
        runner.invoke(main, ["task", "new", "old task"])

        import time
        time.sleep(0.1)

        runner.invoke(main, ["task", "new", "new task"])

        # Get a future date (tomorrow in UTC to avoid timezone issues near midnight)
        from datetime import datetime, timedelta, timezone
        future_date = (datetime.now(timezone.utc) + timedelta(days=2)).strftime("%Y-%m-%d")

        # Filter to only show tasks since future date (should be none)
        result = runner.invoke(main, ["summary", "--since", future_date])

        assert result.exit_code == 0
        assert "No tasks found since" in result.output

    def test_summary_invalid_date_format(self, runner, isolated_project):
        """Test error with invalid date format."""
        runner.invoke(main, ["init", "date-error"])
        project_dir = isolated_project / "date-error"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["summary", "--since", "bad-date"])

        assert result.exit_code == 1
        assert "Invalid date format" in result.output


class TestTaskCompleteCommand:
    """Tests for air task complete command."""

    def test_task_complete_not_in_air_project(self, runner, isolated_project):
        """Test error when not in AIR project."""
        result = runner.invoke(main, ["task", "complete", "20251003-1200"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output

    def test_task_complete_task_not_found(self, runner, isolated_project):
        """Test error when task doesn't exist."""
        runner.invoke(main, ["init", "complete-test"])
        project_dir = isolated_project / "complete-test"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["task", "complete", "nonexistent"])

        assert result.exit_code == 1
        assert "Task not found" in result.output

    def test_task_complete_basic(self, runner, isolated_project):
        """Test marking a task as complete."""
        runner.invoke(main, ["init", "complete-basic"])
        project_dir = isolated_project / "complete-basic"

        import os
        os.chdir(project_dir)

        # Create a task
        result = runner.invoke(main, ["task", "new", "test task"])
        assert result.exit_code == 0

        # Find the task file
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-test-task.md"))
        assert len(task_files) == 1
        task_file = task_files[0]

        # Verify initial state (⏳ In Progress)
        content = task_file.read_text()
        assert "⏳ In Progress" in content

        # Get task ID from filename
        task_id = task_file.stem.split("-test-task")[0]

        # Complete the task
        result = runner.invoke(main, ["task", "complete", task_id])
        assert result.exit_code == 0
        assert "Task marked as complete" in result.output

        # Verify outcome was updated
        updated_content = task_file.read_text()
        assert "✅ Success" in updated_content
        assert "⏳ In Progress" not in updated_content

    def test_task_complete_with_notes(self, runner, isolated_project):
        """Test completing a task with notes."""
        runner.invoke(main, ["init", "complete-notes"])
        project_dir = isolated_project / "complete-notes"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "task with notes"])

        # Find the task file
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-task-with-notes.md"))
        assert len(task_files) == 1
        task_file = task_files[0]

        task_id = task_file.stem.split("-task-with")[0]

        # Complete with notes
        result = runner.invoke(
            main, ["task", "complete", task_id, "--notes", "All tests passing"]
        )
        assert result.exit_code == 0

        # Verify notes were added
        updated_content = task_file.read_text()
        assert "✅ Success" in updated_content
        assert "**Completed:** All tests passing" in updated_content

    def test_task_complete_preserves_existing_notes(self, runner, isolated_project):
        """Test that completing preserves existing notes."""
        runner.invoke(main, ["init", "complete-preserve"])
        project_dir = isolated_project / "complete-preserve"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "preserve test"])

        # Find and modify task file to add existing notes
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-preserve-test.md"))
        task_file = task_files[0]

        content = task_file.read_text()
        content = content.replace("## Notes\n", "## Notes\n\nOriginal notes here\n")
        task_file.write_text(content)

        task_id = task_file.stem.split("-preserve")[0]

        # Complete with additional notes
        runner.invoke(
            main, ["task", "complete", task_id, "--notes", "Finished successfully"]
        )

        # Verify both old and new notes are present
        updated_content = task_file.read_text()
        assert "Original notes here" in updated_content
        assert "**Completed:** Finished successfully" in updated_content

    def test_task_complete_partial_id_match(self, runner, isolated_project):
        """Test completing task with partial ID."""
        runner.invoke(main, ["init", "complete-partial"])
        project_dir = isolated_project / "complete-partial"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "partial match test"])

        # Find the task file
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-partial-match-test.md"))
        task_file = task_files[0]

        # Use only first few chars of timestamp
        task_id = task_file.stem[:8]  # YYYYMMDD

        # Complete with partial ID
        result = runner.invoke(main, ["task", "complete", task_id])
        assert result.exit_code == 0

        # Verify it worked
        updated_content = task_file.read_text()
        assert "✅ Success" in updated_content

    def test_task_complete_updates_blocked_task(self, runner, isolated_project):
        """Test completing a blocked task."""
        runner.invoke(main, ["init", "complete-blocked"])
        project_dir = isolated_project / "complete-blocked"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "blocked task"])

        # Find and modify to be blocked
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-blocked-task.md"))
        task_file = task_files[0]

        content = task_file.read_text()
        content = content.replace("⏳ In Progress", "🚫 Blocked: dependency issue")
        task_file.write_text(content)

        task_id = task_file.stem.split("-blocked")[0]

        # Complete it
        result = runner.invoke(main, ["task", "complete", task_id])
        assert result.exit_code == 0

        # Verify it's now success, not blocked
        updated_content = task_file.read_text()
        assert "✅ Success" in updated_content
        assert "🚫 Blocked" not in updated_content
