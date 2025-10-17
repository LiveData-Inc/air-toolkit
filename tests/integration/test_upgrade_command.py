"""Integration tests for air upgrade command."""

import json
import os
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from air.cli import main


class TestUpgradeCommand:
    """Tests for air upgrade command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def old_project(self, tmp_path):
        """Create a simulated old AIR project (v0.5.x style)."""
        project_dir = tmp_path / "old-project"
        project_dir.mkdir()

        # Create old-style structure (missing new v0.6.0 features)
        (project_dir / ".air").mkdir()
        (project_dir / ".air" / "tasks").mkdir()
        (project_dir / ".air" / "context").mkdir()

        # Create old config (no version field, no agents)
        config = {
            "name": "old-project",
            "mode": "review",
            "created": "2025-10-01T10:00:00",
            "resources": {"review": [], "develop": []},
            "goals": [],
        }
        (project_dir / ".air/air-config.json").write_text(json.dumps(config, indent=2))

        # Create README
        (project_dir / "README.md").write_text("# Old Project\n")

        return project_dir

    def test_upgrade_not_in_project(self, runner):
        """Test upgrade fails when not in AIR project."""
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["upgrade"])
            assert result.exit_code == 1
            assert "Not in an AIR project" in result.output

    def test_upgrade_dry_run_default(self, runner, old_project):
        """Test upgrade defaults to dry-run mode."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        assert "Upgrade Plan" in result.output
        assert "Dry run mode" in result.output or "dry-run" in result.output.lower()
        assert "air upgrade --force" in result.output

        # Verify no changes were made
        assert not (old_project / ".air" / "agents").exists()
        assert not (old_project / "scripts").exists()

    def test_upgrade_explicit_dry_run(self, runner, old_project):
        """Test upgrade with --dry-run flag."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--dry-run"])

        assert result.exit_code == 0
        assert "Upgrade Plan" in result.output

        # Verify no changes were made
        assert not (old_project / ".air" / "agents").exists()
        assert not (old_project / "scripts").exists()

    def test_upgrade_detects_missing_directories(self, runner, old_project):
        """Test upgrade detects missing directories."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        # Should detect missing .air/agents, .air/shared, etc. (scripts removed in v0.6.4)
        assert ".air/agents" in result.output or "agents" in result.output

    def test_upgrade_detects_missing_scripts(self, runner, old_project):
        """Test upgrade no longer detects missing scripts (v0.6.4+)."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        # Scripts no longer auto-created - daily-analysis.sh replaced by `air daily` command
        # Test just verifies upgrade runs successfully

    def test_upgrade_detects_missing_config_fields(self, runner, old_project):
        """Test upgrade detects missing config fields."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        # Should detect missing version field
        assert ".air/air-config.json" in result.output or "Update" in result.output

    def test_upgrade_force_creates_directories(self, runner, old_project):
        """Test upgrade --force creates missing directories."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0
        assert "✓" in result.output or "Created" in result.output

        # Verify directories were created
        assert (old_project / ".air" / "agents").exists()
        assert (old_project / ".air" / "shared").exists()
        # Scripts directory no longer auto-created (v0.6.4+)
        assert (old_project / "analysis" / "reviews").exists()

    def test_upgrade_force_creates_scripts(self, runner, old_project):
        """Test upgrade --force no longer creates scripts (v0.6.4+)."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Scripts directory no longer auto-created (v0.6.4+)
        # daily-analysis.sh replaced by `air daily` command
        # Scripts directory is now optional for user scripts only
        scripts_dir = old_project / "scripts"
        assert not scripts_dir.exists()

    def test_upgrade_force_updates_config(self, runner, old_project):
        """Test upgrade --force updates config."""
        os.chdir(old_project)

        # Verify config missing version field
        config_before = json.loads((old_project / ".air/air-config.json").read_text())
        assert "version" not in config_before

        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Verify version field added
        config_after = json.loads((old_project / ".air/air-config.json").read_text())
        assert "version" in config_after
        assert config_after["version"] == "2.0.0"

        # Verify other fields preserved
        assert config_after["name"] == "old-project"
        assert config_after["mode"] == "review"

    def test_upgrade_creates_backup_by_default(self, runner, old_project):
        """Test upgrade creates backup by default."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Find backup directory
        backup_dirs = list(old_project.glob(".air-backup-*"))
        assert len(backup_dirs) == 1

        backup_dir = backup_dirs[0]
        assert (backup_dir / ".air/air-config.json").exists()

    def test_upgrade_no_backup_flag(self, runner, old_project):
        """Test upgrade --no-backup skips backup."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force", "--no-backup"])

        assert result.exit_code == 0

        # Verify no backup created
        backup_dirs = list(old_project.glob(".air-backup-*"))
        assert len(backup_dirs) == 0

    def test_upgrade_up_to_date_project(self, runner, old_project):
        """Test upgrade on already up-to-date project."""
        os.chdir(old_project)

        # First upgrade
        runner.invoke(main, ["upgrade", "--force"])

        # Second upgrade should show "up to date"
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        assert "up to date" in result.output.lower() or "No upgrades needed" in result.output

    def test_upgrade_preserves_user_data(self, runner, old_project):
        """Test upgrade preserves user data in .air/tasks."""
        # Create user task file
        task_file = old_project / ".air" / "tasks" / "20251001-1000-my-task.md"
        task_content = "# My Task\n\nUser content here"
        task_file.write_text(task_content)

        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Verify task file unchanged
        assert task_file.exists()
        assert task_file.read_text() == task_content

    def test_upgrade_preserves_existing_scripts(self, runner, old_project):
        """Test upgrade preserves existing user scripts (v0.6.4+)."""
        # Create custom script
        scripts_dir = old_project / "scripts"
        scripts_dir.mkdir()

        custom_script = scripts_dir / "my-custom-script.sh"
        custom_content = "#!/bin/bash\n# My custom script\n"
        custom_script.write_text(custom_content)

        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Upgrade no longer touches scripts directory (v0.6.4+)
        # User scripts are preserved exactly as-is
        assert custom_script.exists()
        assert custom_script.read_text() == custom_content


class TestUpgradeEdgeCases:
    """Edge case tests for upgrade command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_upgrade_missing_config_file(self, runner, tmp_path):
        """Test upgrade creates config when missing."""
        project_dir = tmp_path / "broken-project"
        project_dir.mkdir()
        (project_dir / ".air").mkdir()

        # Create a repo symlink (orphaned since no config)
        fake_repo = tmp_path / "some-repo"
        fake_repo.mkdir()
        (fake_repo / "README.md").write_text("# Some Repo")

        repos_dir = project_dir / "repos"
        repos_dir.mkdir()
        (repos_dir / "some-repo").symlink_to(fake_repo)

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        # Should succeed and create config
        assert result.exit_code == 0
        assert (project_dir / ".air/air-config.json").exists()

        # Should show recovery needed for the orphaned repo
        output = result.output.lower()
        assert "recover" in output or "orphaned" in output

    def test_upgrade_invalid_json_config(self, runner, tmp_path):
        """Test upgrade handles invalid JSON in config."""
        project_dir = tmp_path / "invalid-project"
        project_dir.mkdir()
        (project_dir / ".air").mkdir()
        (project_dir / ".air/air-config.json").write_text("{ invalid json }")

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        # Should fail to parse JSON
        assert result.exit_code != 0

    def test_upgrade_partial_structure(self, runner, tmp_path):
        """Test upgrade with partially existing structure."""
        project_dir = tmp_path / "partial-project"
        project_dir.mkdir()

        # Create some v0.6.0 features but not all
        (project_dir / ".air").mkdir()
        (project_dir / ".air" / "agents").mkdir()  # This one exists
        # But .air/shared and scripts are missing

        config = {
            "name": "partial-project",
            "mode": "review",
            "version": "2.0.0",
            "resources": {"review": [], "develop": []},
        }
        (project_dir / ".air/air-config.json").write_text(json.dumps(config))

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0

        # Should only show missing items in upgrade plan
        # Not the ones that already exist
        output_lower = result.output.lower()

        # Scripts no longer auto-created (v0.6.4+), check for other upgrades
        # Should either show "up to date" or mention missing .air/shared
        assert "up to date" in output_lower or "shared" in output_lower

    def test_upgrade_detects_orphaned_repos(self, runner, tmp_path):
        """Test that upgrade detects symlinks in repos/ not in config."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create minimal project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create a symlink to a "repo" (use tmp dir as fake repo)
        fake_repo = tmp_path / "orphaned-repo"
        fake_repo.mkdir()
        (fake_repo / "README.md").write_text("# Orphaned Repo")

        orphaned_symlink = project_dir / "repos" / "orphaned-repo"
        orphaned_symlink.symlink_to(fake_repo)

        # Create config WITHOUT this repo
        config = {
            "name": "test-project",
            "mode": "review",
            "version": "2.0.0",
            "resources": {"review": [], "develop": []},
        }
        (project_dir / ".air/air-config.json").write_text(json.dumps(config))

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        output = result.output

        # Should detect orphaned repo
        assert "orphaned" in output.lower() or "recover" in output.lower()
        assert "1" in output  # 1 orphaned repo

    def test_upgrade_recovers_orphaned_repos(self, runner, tmp_path):
        """Test that upgrade --force recovers orphaned repos into config."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create minimal project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create a symlink to a "repo" (use tmp dir as fake repo)
        fake_repo = tmp_path / "my-library"
        fake_repo.mkdir()
        (fake_repo / "README.md").write_text("# My Library")
        (fake_repo / "setup.py").write_text("# Python library")

        orphaned_symlink = project_dir / "repos" / "my-library"
        orphaned_symlink.symlink_to(fake_repo)

        # Create config WITHOUT this repo
        config = {
            "name": "test-project",
            "mode": "review",
            "version": "2.0.0",
            "resources": {"review": [], "develop": []},
        }
        config_file = project_dir / ".air/air-config.json"
        config_file.write_text(json.dumps(config))

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Check that config was updated with recovered repo
        updated_config = json.loads(config_file.read_text())

        # Should have added the repo to review resources
        assert "review" in updated_config["resources"]
        review_resources = updated_config["resources"]["review"]

        # Should have at least one resource now
        assert len(review_resources) >= 1

        # Find the recovered repo
        recovered_repo = None
        for resource in review_resources:
            if resource["name"] == "my-library":
                recovered_repo = resource
                break

        assert recovered_repo is not None, "my-library should be in config"
        assert recovered_repo["path"] == str(fake_repo)
        assert recovered_repo["relationship"] == "review-only"
        assert "type" in recovered_repo

    def test_upgrade_skips_broken_symlinks(self, runner, tmp_path):
        """Test that upgrade ignores broken symlinks gracefully."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir()

        # Create minimal project structure
        (project_dir / ".air").mkdir()
        (project_dir / "repos").mkdir()

        # Create a broken symlink
        broken_symlink = project_dir / "repos" / "broken-link"
        broken_symlink.symlink_to("/nonexistent/path")

        # Create config
        config = {
            "name": "test-project",
            "mode": "review",
            "version": "2.0.0",
            "resources": {"review": [], "develop": []},
        }
        (project_dir / ".air/air-config.json").write_text(json.dumps(config))

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        # Should not crash, should ignore broken symlink
        assert result.exit_code == 0
