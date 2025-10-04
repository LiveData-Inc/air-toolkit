"""Tests for template service."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from air.services.templates import (
    get_template_path,
    render_template,
    render_assessment_templates,
    render_ai_templates,
    create_config_file,
    get_context_template,
)


def test_get_template_path():
    """Test get_template_path returns valid path."""
    template_path = get_template_path()

    assert template_path.exists()
    assert template_path.is_dir()
    assert template_path.name == "templates"


def test_render_template_readme():
    """Test rendering README template."""
    context = {
        "name": "test-project",
        "mode": "review",
        "created": "2025-10-03",
        "goals": ["Goal 1", "Goal 2"],
    }

    content = render_template("assessment/README.md.j2", context)

    assert "test-project" in content
    assert "review" in content
    assert "Goal 1" in content
    assert "Goal 2" in content


def test_render_template_claude_md():
    """Test rendering CLAUDE.md template."""
    context = {
        "name": "test-project",
        "mode": "develop",
        "created": "2025-10-03",
        "goals": [],
    }

    content = render_template("assessment/CLAUDE.md.j2", context)

    assert "test-project" in content
    assert "develop" in content
    assert "CRITICAL" in content
    assert "Task Tracking" in content


def test_render_template_gitignore():
    """Test rendering gitignore template."""
    context = {
        "name": "test-project",
        "mode": "mixed",
        "created": "2025-10-03",
        "goals": [],
    }

    content = render_template("assessment/gitignore.j2", context)

    assert "Python" in content
    assert "__pycache__" in content
    assert "repos/*" in content
    assert "contributions/*" in content


def test_render_assessment_templates_review():
    """Test rendering assessment templates for review mode."""
    templates = render_assessment_templates(
        project_name="review-project",
        mode="review",
        created=datetime(2025, 10, 3, 10, 0, 0),
        goals=["Analyze architecture"],
    )

    assert "README.md" in templates
    assert "CLAUDE.md" in templates
    assert ".gitignore" in templates

    # Check README content
    assert "review-project" in templates["README.md"]
    assert "review" in templates["README.md"]
    assert "Analyze architecture" in templates["README.md"]


def test_render_assessment_templates_develop():
    """Test rendering assessment templates for develop mode."""
    templates = render_assessment_templates(
        project_name="dev-project",
        mode="develop",
        created=datetime(2025, 10, 3, 10, 0, 0),
    )

    assert "README.md" in templates
    assert "CLAUDE.md" in templates
    assert ".gitignore" in templates

    # Check content is appropriate for develop mode
    assert "development" in templates["README.md"].lower()


def test_render_assessment_templates_mixed():
    """Test rendering assessment templates for mixed mode."""
    templates = render_assessment_templates(
        project_name="mixed-project",
        mode="mixed",
        created=datetime(2025, 10, 3, 10, 0, 0),
    )

    assert "README.md" in templates
    assert "mixed" in templates["README.md"]


def test_render_ai_templates():
    """Test rendering AI task tracking templates."""
    templates = render_ai_templates()

    assert ".air/README.md" in templates

    # Check README content
    readme = templates[".air/README.md"]
    assert "Task Tracking" in readme
    assert "YYYYMMDD-HHMM" in readme
    assert "Outcome" in readme


def test_create_config_file():
    """Test creating air-config.json content."""
    config_json = create_config_file(
        project_name="test-project",
        mode="review",
        created=datetime(2025, 10, 3, 10, 30, 0),
        goals=["Goal 1"],
    )

    # Parse JSON to validate
    config = json.loads(config_json)

    assert config["version"] == "2.0.0"
    assert config["name"] == "test-project"
    assert config["mode"] == "review"
    assert config["created"] == "2025-10-03T10:30:00"
    assert config["goals"] == ["Goal 1"]
    assert "review" in config["resources"]
    assert "develop" in config["resources"]


def test_create_config_file_no_goals():
    """Test creating config without goals."""
    config_json = create_config_file(
        project_name="test-project",
        mode="mixed",
        created=datetime(2025, 10, 3, 10, 30, 0),
    )

    config = json.loads(config_json)
    assert config["goals"] == []


def test_get_context_template_architecture():
    """Test getting architecture context template."""
    content = get_context_template("architecture")

    assert len(content) > 0
    assert "Architecture" in content
    assert "System Overview" in content
    assert "Design Patterns" in content


def test_get_context_template_language():
    """Test getting language context template."""
    content = get_context_template("language")

    assert len(content) > 0
    assert "Code Conventions" in content
    assert "Naming Conventions" in content
    assert "Testing" in content


def test_get_context_template_unknown():
    """Test getting unknown context template returns empty."""
    content = get_context_template("unknown")

    assert content == ""
