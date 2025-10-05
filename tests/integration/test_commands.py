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
        assert (project_dir / "repos").exists()
        assert (project_dir / "analysis").exists()

    def test_init_review_mode(self, runner, isolated_project):
        """Test air init with review mode."""
        result = runner.invoke(main, ["init", "review-proj", "--mode=review"])

        assert result.exit_code == 0

        project_dir = isolated_project / "review-proj"
        assert (project_dir / "repos").exists()
        assert not (project_dir / "develop").exists()
        assert not (project_dir / "contributions").exists()

    def test_init_develop_mode(self, runner, isolated_project):
        """Test air init with develop mode."""
        result = runner.invoke(main, ["init", "dev-proj", "--mode=develop"])

        assert result.exit_code == 0

        project_dir = isolated_project / "dev-proj"
        # In develop mode, only .air/ is created - this IS your project
        assert (project_dir / ".air").exists()
        # No special resource directories in develop mode
        assert not (project_dir / "repos").exists()
        assert not (project_dir / "contributions").exists()
        assert not (project_dir / "analysis").exists()

    def test_init_mixed_mode(self, runner, isolated_project):
        """Test air init with mixed mode (default)."""
        result = runner.invoke(main, ["init", "mixed-proj"])

        assert result.exit_code == 0

        project_dir = isolated_project / "mixed-proj"
        # Mixed mode: repos for external assessment, contributions for PRs
        assert (project_dir / "repos").exists()
        assert (project_dir / "contributions").exists()
        assert (project_dir / "analysis").exists()
        assert (project_dir / ".air").exists()

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
        result = runner.invoke(main, ["init", "config-test", "--mode=develop"])

        assert result.exit_code == 0

        config_path = isolated_project / "config-test" / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert config["version"] == "2.0.0"
        assert config["name"] == "config-test"
        assert config["mode"] == "develop"
        assert "resources" in config
        assert "review" in config["resources"]
        assert "develop" in config["resources"]

    def test_init_interactive_mode(self, runner, isolated_project):
        """Test air init interactive mode."""
        # Simulate interactive input:
        # - Project name: interactive-test
        # - Create directory: y
        # - Mode: mixed
        # - Tracking: y
        # - Add goals: y
        # - Goal 1: Test goal 1
        # - Goal 2: Test goal 2
        # - Goal 3: (empty, finish)
        # - Confirm: y
        input_data = "\n".join([
            "interactive-test",  # project name
            "y",                 # create directory
            "",                  # mode (default: mixed)
            "",                  # tracking (default: yes)
            "y",                 # add goals
            "Test goal 1",       # goal 1
            "Test goal 2",       # goal 2
            "",                  # empty to finish goals
            "y",                 # confirm creation
        ])

        result = runner.invoke(main, ["init", "--interactive"], input=input_data)

        assert result.exit_code == 0
        assert "AIR Toolkit - Interactive Setup" in result.output
        assert "Project created successfully" in result.output

        # Check project was created
        project_dir = isolated_project / "interactive-test"
        assert project_dir.exists()
        assert (project_dir / "air-config.json").exists()

        # Check config contains goals
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert config["name"] == "interactive-test"
        assert config["mode"] == "mixed"
        assert "goals" in config
        assert len(config["goals"]) == 2
        assert "Test goal 1" in config["goals"]
        assert "Test goal 2" in config["goals"]

    def test_init_interactive_mode_cancelled(self, runner, isolated_project):
        """Test air init interactive mode when user cancels."""
        # Simulate cancelling at confirmation
        input_data = "\n".join([
            "cancelled-test",    # project name
            "y",                 # create directory
            "",                  # mode (default: mixed)
            "",                  # tracking (default: yes)
            "n",                 # no goals
            "n",                 # cancel at confirmation
        ])

        result = runner.invoke(main, ["init", "--interactive"], input=input_data)

        assert result.exit_code == 0
        assert "Cancelled" in result.output

        # Project should not be created
        project_dir = isolated_project / "cancelled-test"
        assert not project_dir.exists()

    def test_init_interactive_mode_current_directory(self, runner, isolated_project):
        """Test air init interactive mode in current directory."""
        # Use default project name (current directory)
        input_data = "\n".join([
            "",                  # use default name (current dir)
            "",                  # mode (default: mixed)
            "",                  # tracking (default: yes)
            "n",                 # no goals
            "y",                 # confirm
        ])

        result = runner.invoke(main, ["init", "--interactive"], input=input_data)

        assert result.exit_code == 0
        assert "Using current directory" in result.output
        assert (isolated_project / "air-config.json").exists()


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

    def test_validate_detects_missing_symlink(self, runner, isolated_project):
        """Test air validate detects resource configured but symlink missing."""
        import os
        import shutil

        # Create project
        runner.invoke(main, ["init", "missing-link-proj"])
        project_dir = isolated_project / "missing-link-proj"

        # Create a temp resource to link
        resource_dir = isolated_project / "temp-resource"
        resource_dir.mkdir()
        (resource_dir / "README.md").write_text("# Test Resource")

        os.chdir(project_dir)

        # Add resource link
        runner.invoke(
            main,
            [
                "link",
                "add",
                str(resource_dir),
                "--name",
                "test-resource",
                "--review",
                "--type=library",
            ],
        )

        # Now remove the symlink (but not the config entry)
        symlink_path = project_dir / "repos" / "test-resource"
        symlink_path.unlink()

        # Validate should detect missing symlink
        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 3
        assert "Missing resource: repos/test-resource" in result.output

    def test_validate_detects_broken_symlink(self, runner, isolated_project):
        """Test air validate detects broken symlink (target removed)."""
        import os
        import shutil

        # Create project
        runner.invoke(main, ["init", "broken-link-proj"])
        project_dir = isolated_project / "broken-link-proj"

        # Create a temp resource to link
        resource_dir = isolated_project / "temp-resource"
        resource_dir.mkdir()
        (resource_dir / "README.md").write_text("# Test Resource")

        os.chdir(project_dir)

        # Add resource link
        runner.invoke(
            main,
            [
                "link",
                "add",
                str(resource_dir),
                "--name",
                "test-resource",
                "--review",
                "--type=library",
            ],
        )

        # Remove the target directory (making symlink broken)
        shutil.rmtree(resource_dir)

        # Validate should detect broken symlink
        result = runner.invoke(main, ["validate"])

        assert result.exit_code == 3
        assert "Broken symlink: repos/test-resource" in result.output

    def test_validate_fix_recreates_missing_symlink(self, runner, isolated_project):
        """Test air validate --fix recreates missing symlinks."""
        import os
        import shutil

        # Create project
        runner.invoke(main, ["init", "fix-test-proj"])
        project_dir = isolated_project / "fix-test-proj"

        # Create a temp resource to link
        resource_dir = isolated_project / "temp-resource"
        resource_dir.mkdir()
        (resource_dir / "README.md").write_text("# Test Resource")

        os.chdir(project_dir)

        # Add resource link
        runner.invoke(
            main,
            [
                "link",
                "add",
                str(resource_dir),
                "--name",
                "test-resource",
                "--review",
                "--type=library",
            ],
        )

        # Remove the symlink
        symlink_path = project_dir / "repos" / "test-resource"
        symlink_path.unlink()

        # Validate --fix should recreate the symlink
        result = runner.invoke(main, ["validate", "--fix"])

        assert result.exit_code == 0
        assert "Fixed" in result.output or "Recreated symlink: repos/test-resource" in result.output
        assert symlink_path.exists()
        assert symlink_path.is_symlink()

    def test_validate_fix_handles_missing_source(self, runner, isolated_project):
        """Test air validate --fix reports error when source path doesn't exist."""
        import os
        import shutil

        # Create project
        runner.invoke(main, ["init", "fix-nosource-proj"])
        project_dir = isolated_project / "fix-nosource-proj"

        # Create a temp resource to link
        resource_dir = isolated_project / "temp-resource"
        resource_dir.mkdir()
        (resource_dir / "README.md").write_text("# Test Resource")

        os.chdir(project_dir)

        # Add resource link
        runner.invoke(
            main,
            [
                "link",
                "add",
                str(resource_dir),
                "--name",
                "test-resource",
                "--review",
                "--type=library",
            ],
        )

        # Remove BOTH the symlink and the source
        symlink_path = project_dir / "repos" / "test-resource"
        symlink_path.unlink()
        shutil.rmtree(resource_dir)

        # Validate --fix should report it can't fix
        result = runner.invoke(main, ["validate", "--fix"])

        assert result.exit_code == 3
        assert "Cannot fix repos/test-resource" in result.output
        assert "source path does not exist" in result.output


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
        runner.invoke(main, ["init", "info-proj", "--mode=develop"])

        import os
        os.chdir(isolated_project / "info-proj")

        result = runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "info-proj" in result.output
        assert "develop" in result.output


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
        assert (isolated_project / "repos").exists()
        assert not (isolated_project / "develop").exists()

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

        # Add resource using new flag format
        result = runner.invoke(
            main,
            ["link", "add", str(source_dir), "--name", "service-a", "--review", "--type=library"]
        )

        assert result.exit_code == 0
        assert "Linked review resource: service-a" in result.output

        # Verify symlink created
        link_path = project_dir / "repos/service-a"
        assert link_path.exists()
        assert link_path.is_symlink()
        assert link_path.resolve() == source_dir

        # Verify config updated
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["review"]) == 1
        assert config["resources"]["review"][0]["name"] == "service-a"
        assert config["resources"]["review"][0]["type"] == "library"
        assert config["resources"]["review"][0]["relationship"] == "review-only"

    def test_link_add_collaborate_resource(self, runner, isolated_project):
        """Test adding a development resource."""
        # Create AIR project
        runner.invoke(main, ["init", "dev-project", "--mode=mixed"])
        project_dir = isolated_project / "dev-project"

        # Create source directory
        source_dir = isolated_project / "docs"
        source_dir.mkdir()
        (source_dir / "index.md").write_text("Documentation")

        import os
        os.chdir(project_dir)

        # Add resource using new flag format
        result = runner.invoke(
            main,
            ["link", "add", str(source_dir), "--name", "docs", "--develop", "--type=documentation"]
        )

        assert result.exit_code == 0
        assert "Linked develop resource: docs" in result.output

        # Verify symlink goes to repos/ (all linked repos go there)
        link_path = project_dir / "repos/docs"
        assert link_path.exists()
        assert link_path.is_symlink()

        # Verify config
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["develop"]) == 1
        assert config["resources"]["develop"][0]["name"] == "docs"
        assert config["resources"]["develop"][0]["type"] == "documentation"
        assert config["resources"]["develop"][0]["relationship"] == "developer"

    def test_link_add_with_type_flag(self, runner, isolated_project):
        """Test adding resource with explicit type flag."""
        runner.invoke(main, ["init", "type-project"])
        project_dir = isolated_project / "type-project"

        source_dir = isolated_project / "service-lib"
        source_dir.mkdir()

        import os
        os.chdir(project_dir)

        result = runner.invoke(
            main,
            ["link", "add", str(source_dir), "--name", "service-lib", "--review", "--type=library"]
        )

        assert result.exit_code == 0
        assert "Linked review resource: service-lib" in result.output

        # Verify type in config
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert config["resources"]["review"][0]["type"] == "library"

    def test_link_add_nonexistent_path(self, runner, isolated_project):
        """Test error when source path doesn't exist."""
        runner.invoke(main, ["init", "path-error"])
        project_dir = isolated_project / "path-error"

        import os
        os.chdir(project_dir)

        result = runner.invoke(
            main,
            ["link", "add", "/nonexistent/path", "--name", "missing", "--review", "--type=library"]
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
        runner.invoke(main, ["link", "add", str(source1), "--name", "repo", "--review", "--type=library"])

        # Try to add with same name
        result = runner.invoke(main, ["link", "add", str(source2), "--name", "repo", "--review", "--type=library"])

        assert result.exit_code == 1
        assert "already linked" in result.output

    def test_link_add_defaults_to_review(self, runner, isolated_project):
        """Test that --review is the default when no relationship specified."""
        runner.invoke(main, ["init", "default-project", "--mode=mixed"])
        project_dir = isolated_project / "default-project"

        source_dir = isolated_project / "lib"
        source_dir.mkdir()

        import os
        os.chdir(project_dir)

        # No --review or --develop specified, should default to review
        result = runner.invoke(
            main,
            ["link", "add", str(source_dir), "--name", "lib", "--type=library"]
        )

        assert result.exit_code == 0
        assert "Linked review resource: lib" in result.output

        # Verify it's in review category
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["review"]) == 1
        assert config["resources"]["review"][0]["name"] == "lib"
        assert config["resources"]["review"][0]["relationship"] == "review-only"

    def test_link_add_auto_classify(self, runner, isolated_project):
        """Test non-interactive mode with auto-classification (no --type)."""
        runner.invoke(main, ["init", "auto-project", "--mode=mixed"])
        project_dir = isolated_project / "auto-project"

        # Create Python source directory
        source_dir = isolated_project / "python-lib"
        source_dir.mkdir()
        (source_dir / "setup.py").write_text("# Setup file")
        (source_dir / "main.py").write_text("print('hello')")

        import os
        os.chdir(project_dir)

        # Add without --type, should auto-classify
        result = runner.invoke(
            main,
            ["link", "add", str(source_dir), "--name", "python-lib", "--review"]
        )

        assert result.exit_code == 0
        assert "Auto-detecting resource type" in result.output
        assert "Linked review resource: python-lib" in result.output

        # Verify config has detected type
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert len(config["resources"]["review"]) == 1
        assert config["resources"]["review"][0]["name"] == "python-lib"
        assert config["resources"]["review"][0]["type"] == "library"

    def test_link_add_folder_name_default(self, runner, isolated_project):
        """Test non-interactive mode with folder name as default (no --name)."""
        runner.invoke(main, ["init", "name-default-project", "--mode=mixed"])
        project_dir = isolated_project / "name-default-project"

        # Create source directory with specific name
        source_dir = isolated_project / "my-awesome-repo"
        source_dir.mkdir()
        (source_dir / "README.md").write_text("# Awesome")

        import os
        os.chdir(project_dir)

        # Add without --name, should use folder name
        result = runner.invoke(
            main,
            ["link", "add", str(source_dir), "--review", "--type=documentation"]
        )

        assert result.exit_code == 0
        assert "Linked review resource: my-awesome-repo" in result.output

        # Verify symlink created with folder name
        link_path = project_dir / "repos/my-awesome-repo"
        assert link_path.exists()
        assert link_path.is_symlink()
        assert link_path.resolve() == source_dir

        # Verify config uses folder name
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        assert config["resources"]["review"][0]["name"] == "my-awesome-repo"

    def test_link_add_fully_automatic(self, runner, isolated_project):
        """Test non-interactive mode with all defaults (no --name, no --type)."""
        runner.invoke(main, ["init", "auto-full-project", "--mode=mixed"])
        project_dir = isolated_project / "auto-full-project"

        # Create Markdown documentation repo
        source_dir = isolated_project / "docs-repo"
        source_dir.mkdir()
        (source_dir / "README.md").write_text("# Documentation")
        (source_dir / "guide.md").write_text("# Guide")

        import os
        os.chdir(project_dir)

        # Add with only path, should use folder name and auto-classify
        result = runner.invoke(main, ["link", "add", str(source_dir)])

        assert result.exit_code == 0
        assert "Auto-detecting resource type" in result.output
        assert "Linked review resource: docs-repo" in result.output

        # Verify everything worked
        link_path = project_dir / "repos/docs-repo"
        assert link_path.exists()
        assert link_path.is_symlink()

        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            config = json.load(f)

        # Should use folder name
        assert config["resources"]["review"][0]["name"] == "docs-repo"
        # Should auto-detect as documentation
        assert config["resources"]["review"][0]["type"] == "documentation"
        # Should default to review
        assert config["resources"]["review"][0]["relationship"] == "review-only"

    def test_link_list_empty(self, runner, isolated_project):
        """Test listing when no resources linked."""
        runner.invoke(main, ["init", "empty-project"])
        project_dir = isolated_project / "empty-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["link", "list"])

        assert result.exit_code == 0
        assert "No resources linked" in result.output


class TestPRCommand:
    """Tests for air pr command."""

    def test_pr_not_in_air_project(self, runner, isolated_project):
        """Test error when not in AIR project."""
        result = runner.invoke(main, ["pr"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output

    def test_pr_list_no_collaborative_resources(self, runner, isolated_project):
        """Test listing when no collaborative resources exist."""
        runner.invoke(main, ["init", "test-project", "--mode=review"])
        project_dir = isolated_project / "test-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["pr"])

        assert result.exit_code == 0
        assert "No collaborative resources found" in result.output

    def test_pr_resource_not_found(self, runner, isolated_project):
        """Test error when resource doesn't exist."""
        runner.invoke(main, ["init", "test-project"])
        project_dir = isolated_project / "test-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["pr", "nonexistent"])

        assert result.exit_code == 1
        assert "Resource 'nonexistent' not found" in result.output

    def test_pr_not_collaborative_resource(self, runner, isolated_project):
        """Test error when resource is not collaborative."""
        runner.invoke(main, ["init", "test-project"])
        project_dir = isolated_project / "test-project"

        # Create a review-only resource
        source = isolated_project / "review-repo"
        source.mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", str(source), "--name", "docs", "--review"])

        result = runner.invoke(main, ["pr", "docs"])

        assert result.exit_code == 1
        assert "not a collaborative resource" in result.output

    def test_pr_not_git_repository(self, runner, isolated_project):
        """Test error when collaborative resource is not a git repo."""
        runner.invoke(main, ["init", "test-project"])
        project_dir = isolated_project / "test-project"

        # Create a collaborative resource (not a git repo)
        source = isolated_project / "collab-repo"
        source.mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", str(source), "--name", "docs", "--develop"])

        result = runner.invoke(main, ["pr", "docs"])

        assert result.exit_code == 1
        assert "not a git repository" in result.output

    def test_pr_no_contributions(self, runner, isolated_project):
        """Test when no contributions exist."""
        runner.invoke(main, ["init", "test-project"])
        project_dir = isolated_project / "test-project"

        # Create a collaborative git resource
        source = isolated_project / "collab-repo"
        source.mkdir()
        (source / ".git").mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", str(source), "--name", "docs", "--develop"])

        result = runner.invoke(main, ["pr", "docs"])

        assert result.exit_code == 0
        assert "No contributions found" in result.output

    def test_pr_dry_run(self, runner, isolated_project):
        """Test dry run mode."""
        runner.invoke(main, ["init", "test-project"])
        project_dir = isolated_project / "test-project"

        # Create collaborative git resource
        source = isolated_project / "collab-repo"
        source.mkdir()
        (source / ".git").mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", str(source), "--name", "docs", "--develop"])

        # Create contributions
        contrib_dir = project_dir / "contributions" / "docs"
        contrib_dir.mkdir(parents=True)
        (contrib_dir / "README.md").write_text("# Test")

        result = runner.invoke(main, ["pr", "docs", "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert "Creating PR for: docs" in result.output
        assert "Files: 1" in result.output

    def test_pr_list_collaborative_resources(self, runner, isolated_project):
        """Test listing collaborative resources with contributions."""
        runner.invoke(main, ["init", "test-project"])
        project_dir = isolated_project / "test-project"

        # Create two collaborative git resources
        source1 = isolated_project / "repo1"
        source1.mkdir()
        (source1 / ".git").mkdir()

        source2 = isolated_project / "repo2"
        source2.mkdir()
        (source2 / ".git").mkdir()

        import os
        os.chdir(project_dir)

        runner.invoke(main, ["link", "add", str(source1), "--name", "docs", "--develop"])
        runner.invoke(main, ["link", "add", str(source2), "--name", "api", "--develop"])

        # Create contributions for one resource
        contrib_dir = project_dir / "contributions" / "docs"
        contrib_dir.mkdir(parents=True)
        (contrib_dir / "README.md").write_text("# Test")

        result = runner.invoke(main, ["pr"])

        assert result.exit_code == 0
        assert "Collaborative Resources:" in result.output
        assert "docs" in result.output
        assert "api" in result.output

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

        runner.invoke(main, ["link", "add", str(review_src), "--name", "review-repo", "--review"])
        runner.invoke(main, ["link", "add", str(collab_src), "--name", "collab-repo", "--develop"])

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

        runner.invoke(main, ["link", "add", str(source_dir), "--name", "api", "--review", "--type=service"])

        result = runner.invoke(main, ["link", "list", "--format=json"])

        assert result.exit_code == 0

        output_data = json.loads(result.output)
        assert "review" in output_data
        assert "develop" in output_data
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
        runner.invoke(main, ["link", "add", str(source_dir), "--name", "to-remove", "--review"])

        link_path = project_dir / "repos/to-remove"
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
        runner.invoke(main, ["link", "add", str(source_dir), "--name", "keep-link", "--review"])
        result = runner.invoke(main, ["link", "remove", "keep-link", "--keep-link"])

        assert result.exit_code == 0
        assert "Keeping symlink" in result.output

        # Verify symlink still exists
        link_path = project_dir / "repos/keep-link"
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

    def test_link_remove_no_name_without_interactive(self, runner, isolated_project):
        """Test usage displayed when name not provided without -i flag."""
        runner.invoke(main, ["init", "noname-project"])
        project_dir = isolated_project / "noname-project"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["link", "remove"])

        assert result.exit_code == 1
        assert "Missing argument 'NAME'" in result.output
        assert "Usage:" in result.output  # Should show usage/help

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
        # New format: YYYYMMDD-NNN-HHMM-description.md
        assert len(filename) >= 23  # YYYYMMDD-NNN-HHMM-x.md = 23 chars minimum
        assert filename[:8].isdigit()  # YYYYMMDD
        assert filename[8] == "-"
        assert filename[9:12].isdigit()  # NNN (ordinal)
        assert filename[12] == "-"
        assert filename[13:17].isdigit()  # HHMM
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


class TestTaskStatusCommand:
    """Tests for air task status command."""

    def test_task_status_not_in_air_project(self, runner, isolated_project):
        """Test error when not in AIR project."""
        result = runner.invoke(main, ["task", "status", "20251003-1200"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output

    def test_task_status_task_not_found(self, runner, isolated_project):
        """Test error when task doesn't exist."""
        runner.invoke(main, ["init", "status-test"])
        project_dir = isolated_project / "status-test"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["task", "status", "nonexistent"])

        assert result.exit_code == 1
        assert "Task not found" in result.output

    def test_task_status_basic(self, runner, isolated_project):
        """Test viewing task status."""
        runner.invoke(main, ["init", "status-basic"])
        project_dir = isolated_project / "status-basic"

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

        # Get task ID from filename
        task_id = task_file.stem.split("-test-task")[0]

        # View status
        result = runner.invoke(main, ["task", "status", task_id])
        assert result.exit_code == 0
        assert "Test task" in result.output
        assert "Task Status" in result.output

    def test_task_status_json_format(self, runner, isolated_project):
        """Test JSON output format."""
        runner.invoke(main, ["init", "status-json"])
        project_dir = isolated_project / "status-json"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "json task"])

        # Find the task file
        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-json-task.md"))
        task_file = task_files[0]
        task_id = task_file.stem.split("-json-task")[0]

        # Get status as JSON
        result = runner.invoke(main, ["task", "status", task_id, "--format=json"])
        assert result.exit_code == 0

        # Parse JSON
        import json
        output = json.loads(result.output)

        assert "filename" in output
        assert "title" in output
        assert "outcome" in output
        assert output["title"] == "Json task"
        assert output["outcome"] == "in_progress"

    def test_task_status_completed_task(self, runner, isolated_project):
        """Test status of completed task."""
        runner.invoke(main, ["init", "status-complete"])
        project_dir = isolated_project / "status-complete"

        import os
        os.chdir(project_dir)

        # Create and complete a task
        runner.invoke(main, ["task", "new", "completed task"])

        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-completed-task.md"))
        task_file = task_files[0]
        task_id = task_file.stem.split("-completed-task")[0]

        # Complete it
        runner.invoke(main, ["task", "complete", task_id])

        # View status
        result = runner.invoke(main, ["task", "status", task_id])
        assert result.exit_code == 0
        assert "Completed task" in result.output
        assert "✅" in result.output or "Success" in result.output

    def test_task_status_archived_task(self, runner, isolated_project):
        """Test viewing status of archived task."""
        runner.invoke(main, ["init", "status-archive"])
        project_dir = isolated_project / "status-archive"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "archived task"])

        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-archived-task.md"))
        task_file = task_files[0]
        task_id = task_file.stem.split("-archived-task")[0]

        # Archive it
        runner.invoke(main, ["task", "archive", task_id])

        # View status of archived task
        result = runner.invoke(main, ["task", "status", task_id])
        assert result.exit_code == 0
        assert "Task found in archive" in result.output
        assert "Archived task" in result.output

    def test_task_status_partial_id(self, runner, isolated_project):
        """Test status with partial task ID."""
        runner.invoke(main, ["init", "status-partial"])
        project_dir = isolated_project / "status-partial"

        import os
        os.chdir(project_dir)

        # Create a task
        runner.invoke(main, ["task", "new", "partial id test"])

        tasks_dir = project_dir / ".air/tasks"
        task_files = list(tasks_dir.glob("*-partial-id-test.md"))
        task_file = task_files[0]

        # Use only date part of ID
        task_id = task_file.stem[:8]  # YYYYMMDD

        # View status with partial ID
        result = runner.invoke(main, ["task", "status", task_id])
        assert result.exit_code == 0
        assert "Partial id test" in result.output


class TestTaskListEnhanced:
    """Tests for enhanced task list filtering and sorting."""

    def test_task_list_filter_by_status(self, runner, isolated_project):
        """Test filtering tasks by status - verify flag works."""
        runner.invoke(main, ["init", "list-filter"])
        project_dir = isolated_project / "list-filter"

        import os
        os.chdir(project_dir)

        # Create a simple task
        runner.invoke(main, ["task", "new", "test task one"])

        # Test that status filter doesn't error
        result = runner.invoke(main, ["task", "list", "--status=in-progress"])
        assert result.exit_code == 0

        # Test other status values don't error
        result = runner.invoke(main, ["task", "list", "--status=success"])
        assert result.exit_code == 0

        result = runner.invoke(main, ["task", "list", "--status=all"])
        assert result.exit_code == 0

    def test_task_list_sort_by_title(self, runner, isolated_project):
        """Test sorting tasks by title."""
        runner.invoke(main, ["init", "list-sort"])
        project_dir = isolated_project / "list-sort"

        import os
        os.chdir(project_dir)

        # Create tasks with different titles
        runner.invoke(main, ["task", "new", "zebra task"])
        runner.invoke(main, ["task", "new", "alpha task"])

        # Sort by title
        result = runner.invoke(main, ["task", "list", "--sort=title"])
        assert result.exit_code == 0

        # Alpha should come before Zebra
        alpha_pos = result.output.lower().find("alpha task")
        zebra_pos = result.output.lower().find("zebra task")
        assert alpha_pos < zebra_pos

    def test_task_list_search_keyword(self, runner, isolated_project):
        """Test searching tasks by keyword."""
        runner.invoke(main, ["init", "list-search"])
        project_dir = isolated_project / "list-search"

        import os
        os.chdir(project_dir)

        # Create tasks
        runner.invoke(main, ["task", "new", "implement authentication"])
        runner.invoke(main, ["task", "new", "fix database issue"])

        # Search for "auth"
        result = runner.invoke(main, ["task", "list", "--search=auth"])
        assert result.exit_code == 0
        assert "authentication" in result.output.lower()
        assert "database" not in result.output.lower()

    def test_task_list_json_with_filters(self, runner, isolated_project):
        """Test JSON output with filters."""
        runner.invoke(main, ["init", "list-json"])
        project_dir = isolated_project / "list-json"

        import os
        os.chdir(project_dir)

        # Create tasks
        runner.invoke(main, ["task", "new", "test task"])

        # Get filtered list as JSON
        result = runner.invoke(main, ["task", "list", "--format=json"])
        assert result.exit_code == 0

        # Parse JSON
        import json
        output = json.loads(result.output)

        assert "active" in output
        assert "total_active" in output
        assert len(output["active"]) >= 1
        assert "title" in output["active"][0]
        assert "status" in output["active"][0]

    def test_task_list_combined_filters(self, runner, isolated_project):
        """Test combining multiple filters."""
        runner.invoke(main, ["init", "list-combined"])
        project_dir = isolated_project / "list-combined"

        import os
        os.chdir(project_dir)

        # Create tasks
        runner.invoke(main, ["task", "new", "authentication work"])
        runner.invoke(main, ["task", "new", "database work"])

        # Test combining search with other filters
        result = runner.invoke(main, ["task", "list", "--search=auth", "--sort=title"])
        assert result.exit_code == 0
        assert "authentication" in result.output.lower()

        # Test status filter combined with sort
        result = runner.invoke(main, ["task", "list", "--status=in-progress", "--sort=date"])
        assert result.exit_code == 0


class TestClassifyCommand:
    """Tests for air classify command."""

    def test_classify_not_in_air_project(self, runner, isolated_project):
        """Test error when not in AIR project."""
        result = runner.invoke(main, ["classify"])

        assert result.exit_code == 1
        assert "Not in an AIR project" in result.output

    def test_classify_no_resources(self, runner, isolated_project):
        """Test classify with no linked resources."""
        runner.invoke(main, ["init", "classify-empty"])
        project_dir = isolated_project / "classify-empty"

        import os
        os.chdir(project_dir)

        result = runner.invoke(main, ["classify"])

        assert result.exit_code == 0
        assert "No linked resources" in result.output

    def test_classify_python_project(self, runner, isolated_project):
        """Test classifying a Python project."""
        runner.invoke(main, ["init", "classify-python"])
        project_dir = isolated_project / "classify-python"

        # Create a Python project to classify
        python_proj = isolated_project / "python-app"
        python_proj.mkdir()
        (python_proj / "app.py").write_text("print('hello')")
        (python_proj / "requirements.txt").write_text("flask>=2.0.0")

        import os
        os.chdir(project_dir)

        # Link it
        runner.invoke(main, ["link", "add", str(python_proj), "--name", "python-app", "--review"])

        # Classify
        result = runner.invoke(main, ["classify"])

        assert result.exit_code == 0
        assert "python-app" in result.output
        assert "Classified" in result.output

    def test_classify_json_output(self, runner, isolated_project):
        """Test JSON output format."""
        runner.invoke(main, ["init", "classify-json"])
        project_dir = isolated_project / "classify-json"

        # Create a docs project
        docs_proj = isolated_project / "docs-project"
        docs_proj.mkdir()
        docs_dir = docs_proj / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Docs")
        (docs_dir / "guide.md").write_text("# Guide")

        import os
        os.chdir(project_dir)

        # Link it
        runner.invoke(main, ["link", "add", str(docs_proj), "--name", "docs-project", "--review"])

        # Classify with JSON output
        result = runner.invoke(main, ["classify", "--format=json"])

        assert result.exit_code == 0

        # Parse JSON
        import json
        output = json.loads(result.output)

        assert "total" in output
        assert "resources" in output
        assert len(output["resources"]) == 1
        assert output["resources"][0]["name"] == "docs-project"
        assert "detected_type" in output["resources"][0]
        assert "confidence" in output["resources"][0]

    def test_classify_verbose_output(self, runner, isolated_project):
        """Test verbose output shows details."""
        runner.invoke(main, ["init", "classify-verbose"])
        project_dir = isolated_project / "classify-verbose"

        # Create a service project
        service_proj = isolated_project / "my-service"
        service_proj.mkdir()
        (service_proj / "Dockerfile").write_text("FROM python:3.11")
        (service_proj / "app.py").write_text("from flask import Flask")

        import os
        os.chdir(project_dir)

        # Link it
        runner.invoke(main, ["link", "add", str(service_proj), "--name", "my-service", "--review"])

        # Classify with verbose
        result = runner.invoke(main, ["classify", "--verbose"])

        assert result.exit_code == 0
        assert "my-service" in result.output
        assert "Languages:" in result.output or "Reasoning:" in result.output

    def test_classify_update_config(self, runner, isolated_project):
        """Test --update flag updates air-config.json."""
        runner.invoke(main, ["init", "classify-update"])
        project_dir = isolated_project / "classify-update"

        # Create a docs project
        docs_proj = isolated_project / "docs-update"
        docs_proj.mkdir()
        docs_dir = docs_proj / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Docs")
        (docs_dir / "api.md").write_text("# API")

        import os
        os.chdir(project_dir)

        # Link it with wrong type (implementation)
        runner.invoke(main, ["link", "add", str(docs_proj), "--name", "docs-update", "--review"])

        # Classify with update
        result = runner.invoke(main, ["classify", "--update"])

        assert result.exit_code == 0

        # Verify config was updated
        config_path = project_dir / "air-config.json"
        with open(config_path) as f:
            import json
            config = json.load(f)

        # Find the resource
        resource = config["resources"]["review"][0]
        assert resource["name"] == "docs-update"
        # Should be classified as documentation
        assert resource["type"] == "documentation"

    def test_classify_specific_resource(self, runner, isolated_project):
        """Test classifying a specific resource by name."""
        runner.invoke(main, ["init", "classify-specific"])
        project_dir = isolated_project / "classify-specific"

        # Create two projects
        proj1 = isolated_project / "proj-one"
        proj1.mkdir()
        (proj1 / "app.py").write_text("print('one')")

        proj2 = isolated_project / "proj-two"
        proj2.mkdir()
        (proj2 / "main.py").write_text("print('two')")

        import os
        os.chdir(project_dir)

        # Link both
        runner.invoke(main, ["link", "add", str(proj1), "--name", "proj-one", "--review"])
        runner.invoke(main, ["link", "add", str(proj2), "--name", "proj-two", "--review"])

        # Classify only proj-one
        result = runner.invoke(main, ["classify", "proj-one"])

        assert result.exit_code == 0
        assert "proj-one" in result.output
        # proj-two should not be mentioned
        assert "proj-two" not in result.output or "Classified 1 resource" in result.output

    def test_classify_nonexistent_resource(self, runner, isolated_project):
        """Test error when classifying non-existent resource."""
        runner.invoke(main, ["init", "classify-notfound"])
        project_dir = isolated_project / "classify-notfound"

        import os
        os.chdir(project_dir)

        # First add a resource so we're not testing empty list
        dummy_proj = isolated_project / "dummy"
        dummy_proj.mkdir()
        runner.invoke(main, ["link", "add", str(dummy_proj), "--name", "dummy", "--review"])

        result = runner.invoke(main, ["classify", "nonexistent"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()
