"""Tests for core models."""

import pytest
from datetime import datetime

from air.core.models import (
    AssessmentConfig,
    ProjectMode,
    Resource,
    ResourceType,
    ResourceRelationship,
)


def test_assessment_config_creation():
    """Test creating AssessmentConfig."""
    config = AssessmentConfig(
        name="test-project",
        mode=ProjectMode.MIXED,
    )

    assert config.name == "test-project"
    assert config.mode == ProjectMode.MIXED
    assert config.version == "2.0.0"
    assert isinstance(config.created, datetime)
    assert "review" in config.resources
    assert "collaborate" in config.resources


def test_add_resource():
    """Test adding resource to config."""
    config = AssessmentConfig(
        name="test-project",
        mode=ProjectMode.MIXED,
    )

    resource = Resource(
        name="service-a",
        path="/path/to/service-a",
        type=ResourceType.IMPLEMENTATION,
        relationship=ResourceRelationship.REVIEW_ONLY,
    )

    config.add_resource(resource, "review")

    assert len(config.resources["review"]) == 1
    assert config.resources["review"][0].name == "service-a"


def test_find_resource():
    """Test finding resource by name."""
    config = AssessmentConfig(
        name="test-project",
        mode=ProjectMode.MIXED,
    )

    resource = Resource(
        name="service-a",
        path="/path/to/service-a",
        type=ResourceType.IMPLEMENTATION,
        relationship=ResourceRelationship.REVIEW_ONLY,
    )

    config.add_resource(resource, "review")

    found = config.find_resource("service-a")
    assert found is not None
    assert found.name == "service-a"

    not_found = config.find_resource("non-existent")
    assert not_found is None


def test_resource_path_expansion():
    """Test that resource paths are expanded."""
    resource = Resource(
        name="test",
        path="~/repos/test",
        type=ResourceType.IMPLEMENTATION,
        relationship=ResourceRelationship.REVIEW_ONLY,
    )

    # Should expand ~ to home directory
    assert "~" not in resource.path
    assert resource.path.startswith("/")


def test_get_all_resources():
    """Test getting all resources from config."""
    config = AssessmentConfig(
        name="test-project",
        mode=ProjectMode.MIXED,
    )

    review_resource = Resource(
        name="service-a",
        path="/path/to/service-a",
        type=ResourceType.IMPLEMENTATION,
        relationship=ResourceRelationship.REVIEW_ONLY,
    )

    collab_resource = Resource(
        name="architecture",
        path="/path/to/architecture",
        type=ResourceType.DOCUMENTATION,
        relationship=ResourceRelationship.CONTRIBUTOR,
    )

    config.add_resource(review_resource, "review")
    config.add_resource(collab_resource, "collaborate")

    all_resources = config.get_all_resources()
    assert len(all_resources) == 2
    assert any(r.name == "service-a" for r in all_resources)
    assert any(r.name == "architecture" for r in all_resources)
