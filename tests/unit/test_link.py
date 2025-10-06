"""Tests for link command helper functions."""

import json
import pytest
from pathlib import Path
from unittest.mock import mock_open, patch

from air.commands.link import load_config, save_config
from air.core.models import (
    AirConfig,
    ProjectMode,
    Resource,
    ResourceType,
    ResourceRelationship,
)


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, tmp_path):
        """Test loading valid configuration."""
        config_data = {
            "version": "2.0.0",
            "name": "test-project",
            "mode": "mixed",
            "resources": {
                "review": [
                    {
                        "name": "service-a",
                        "path": "/path/to/service-a",
                        "type": "library",
                        "relationship": "review-only",
                        "clone": False,
                    }
                ],
                "develop": [],
            },
            "goals": [],
            "created": "2025-10-03T14:00:00",
        }

        config_path = tmp_path / ".air/air-config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)

        config = load_config(tmp_path)

        assert config.name == "test-project"
        assert config.mode == ProjectMode.MIXED
        assert len(config.resources["review"]) == 1
        assert config.resources["review"][0].name == "service-a"

    def test_load_missing_config(self, tmp_path):
        """Test error when config file doesn't exist."""
        with pytest.raises(SystemExit) as excinfo:
            load_config(tmp_path)
        assert excinfo.value.code == 1

    def test_load_invalid_json(self, tmp_path):
        """Test error when config has invalid JSON."""
        config_path = tmp_path / ".air/air-config.json"
        with open(config_path, "w") as f:
            f.write("{ invalid json")

        with pytest.raises(SystemExit) as excinfo:
            load_config(tmp_path)
        assert excinfo.value.code == 2

    def test_load_invalid_schema(self, tmp_path):
        """Test error when config has invalid schema."""
        config_path = tmp_path / ".air/air-config.json"
        with open(config_path, "w") as f:
            json.dump({"invalid": "schema"}, f)

        with pytest.raises(SystemExit) as excinfo:
            load_config(tmp_path)
        assert excinfo.value.code == 2


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config(self, tmp_path):
        """Test saving configuration."""
        config = AirConfig(
            name="test-project",
            mode=ProjectMode.MIXED,
        )

        resource = Resource(
            name="service-a",
            path="/path/to/service-a",
            type=ResourceType.LIBRARY,
            relationship=ResourceRelationship.REVIEW_ONLY,
        )
        config.add_resource(resource, "review")

        save_config(tmp_path, config)

        config_path = tmp_path / ".air/air-config.json"
        assert config_path.exists()

        with open(config_path) as f:
            saved_data = json.load(f)

        assert saved_data["name"] == "test-project"
        assert saved_data["mode"] == "mixed"
        assert len(saved_data["resources"]["review"]) == 1
        assert saved_data["resources"]["review"][0]["name"] == "service-a"

    def test_save_config_trailing_newline(self, tmp_path):
        """Test that saved config has trailing newline."""
        config = AirConfig(
            name="test-project",
            mode=ProjectMode.MIXED,
        )

        save_config(tmp_path, config)

        config_path = tmp_path / ".air/air-config.json"
        with open(config_path, "rb") as f:
            content = f.read()

        assert content.endswith(b"\n")

    def test_save_config_permission_error(self, tmp_path):
        """Test error when cannot write config."""
        config = AirConfig(
            name="test-project",
            mode=ProjectMode.MIXED,
        )

        # Make directory read-only
        tmp_path.chmod(0o444)

        try:
            with pytest.raises(SystemExit) as excinfo:
                save_config(tmp_path, config)
            assert excinfo.value.code == 2
        finally:
            # Restore permissions for cleanup
            tmp_path.chmod(0o755)
