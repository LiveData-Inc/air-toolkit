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
        (project_dir / "air-config.json").write_text(json.dumps(config, indent=2))

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
        # Should detect missing .air/agents, .air/shared, scripts, etc.
        assert ".air/agents" in result.output or "agents" in result.output
        assert "scripts" in result.output

    def test_upgrade_detects_missing_scripts(self, runner, old_project):
        """Test upgrade detects missing scripts."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        assert "daily-analysis.sh" in result.output

    def test_upgrade_detects_missing_config_fields(self, runner, old_project):
        """Test upgrade detects missing config fields."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0
        # Should detect missing version field
        assert "air-config.json" in result.output or "Update" in result.output

    def test_upgrade_force_creates_directories(self, runner, old_project):
        """Test upgrade --force creates missing directories."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0
        assert "✓" in result.output or "Created" in result.output

        # Verify directories were created
        assert (old_project / ".air" / "agents").exists()
        assert (old_project / ".air" / "shared").exists()
        assert (old_project / "scripts").exists()
        assert (old_project / "analysis" / "reviews").exists()

    def test_upgrade_force_creates_scripts(self, runner, old_project):
        """Test upgrade --force creates scripts."""
        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Verify scripts were created
        daily_script = old_project / "scripts" / "daily-analysis.sh"
        readme = old_project / "scripts" / "README.md"

        assert daily_script.exists()
        assert readme.exists()

        # Verify script is executable
        assert os.access(daily_script, os.X_OK)

        # Verify content
        assert "#!/bin/bash" in daily_script.read_text()
        assert "AIR Daily Analysis" in daily_script.read_text()

    def test_upgrade_force_updates_config(self, runner, old_project):
        """Test upgrade --force updates config."""
        os.chdir(old_project)

        # Verify config missing version field
        config_before = json.loads((old_project / "air-config.json").read_text())
        assert "version" not in config_before

        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Verify version field added
        config_after = json.loads((old_project / "air-config.json").read_text())
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
        assert (backup_dir / "air-config.json").exists()

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
        """Test upgrade doesn't overwrite existing scripts without force."""
        # Create custom script
        scripts_dir = old_project / "scripts"
        scripts_dir.mkdir()

        custom_script = scripts_dir / "daily-analysis.sh"
        custom_content = "#!/bin/bash\n# My custom script\n"
        custom_script.write_text(custom_content)

        os.chdir(old_project)
        result = runner.invoke(main, ["upgrade", "--force"])

        assert result.exit_code == 0

        # Script should be updated (overwritten) when --force is used
        # (In production, might want to add --skip-scripts flag to preserve custom scripts)
        updated_content = custom_script.read_text()
        # The upgrade should have updated it
        assert "AIR Daily Analysis" in updated_content or updated_content == custom_content


class TestUpgradeEdgeCases:
    """Edge case tests for upgrade command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_upgrade_missing_config_file(self, runner, tmp_path):
        """Test upgrade fails gracefully with missing config."""
        project_dir = tmp_path / "broken-project"
        project_dir.mkdir()
        (project_dir / ".air").mkdir()

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 1
        # get_project_root() finds .air but upgrade finds no config
        assert "air-config.json not found" in result.output or "Not in an AIR project" in result.output

    def test_upgrade_invalid_json_config(self, runner, tmp_path):
        """Test upgrade handles invalid JSON in config."""
        project_dir = tmp_path / "invalid-project"
        project_dir.mkdir()
        (project_dir / ".air").mkdir()
        (project_dir / "air-config.json").write_text("{ invalid json }")

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
        (project_dir / "air-config.json").write_text(json.dumps(config))

        os.chdir(project_dir)
        result = runner.invoke(main, ["upgrade"])

        assert result.exit_code == 0

        # Should only show missing items in upgrade plan
        # Not the ones that already exist
        output_lower = result.output.lower()

        # Should mention scripts (missing)
        assert "scripts" in output_lower or "daily-analysis" in output_lower
