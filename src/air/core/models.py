"""Data models for AIR toolkit."""

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProjectMode(StrEnum):
    """Assessment project mode."""

    REVIEW = "review"
    DEVELOP = "develop"
    MIXED = "mixed"


class ResourceType(StrEnum):
    """Type of linked resource."""

    LIBRARY = "library"
    DOCUMENTATION = "documentation"
    SERVICE = "service"


class ResourceRelationship(StrEnum):
    """Relationship to resource."""

    REVIEW_ONLY = "review-only"
    DEVELOPER = "developer"


class ContributionStatus(StrEnum):
    """Status of a contribution."""

    PROPOSED = "proposed"
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MERGED = "merged"


class TaskOutcome(StrEnum):
    """Task completion status."""

    IN_PROGRESS = "in-progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    BLOCKED = "blocked"


class Contribution(BaseModel):
    """Proposed contribution to development resource."""

    source: str  # Path in contributions/
    target: str  # Target path in resource
    status: ContributionStatus
    pr_url: str | None = None
    created: datetime = Field(default_factory=datetime.now)


class Resource(BaseModel):
    """Linked resource (review or development)."""

    name: str
    path: str
    type: ResourceType
    technology_stack: str | None = None  # e.g., "Python/FastAPI", "TypeScript/React"
    relationship: ResourceRelationship
    writable: bool = False  # Default to read-only for safety (AI cannot make changes)
    branch: str = "main"  # Default branch for AI to work on
    clone: bool = False
    outputs: list[str] = Field(default_factory=list)
    contributions: list[Contribution] = Field(default_factory=list)

    @field_validator("path")
    @classmethod
    def expand_path(cls, v: str) -> str:
        """Expand ~ in paths."""
        from pathlib import Path

        return str(Path(v).expanduser())


class AirConfig(BaseModel):
    """Project configuration (air-config.json)."""

    version: str = "2.0.0"
    name: str
    mode: ProjectMode
    created: datetime = Field(default_factory=datetime.now)
    resources: dict[str, list[Resource]] = Field(
        default_factory=lambda: {"review": [], "develop": []}
    )
    goals: list[str] = Field(default_factory=list)

    def add_resource(self, resource: Resource, resource_category: str) -> None:
        """Add a resource to the configuration.

        Args:
            resource: Resource to add
            resource_category: "review" or "develop"
        """
        if resource_category not in self.resources:
            self.resources[resource_category] = []
        self.resources[resource_category].append(resource)

    def get_all_resources(self) -> list[Resource]:
        """Get all resources regardless of category."""
        all_resources = []
        for resources_list in self.resources.values():
            all_resources.extend(resources_list)
        return all_resources

    def find_resource(self, name: str) -> Resource | None:
        """Find resource by name.

        Args:
            name: Resource name

        Returns:
            Resource if found, None otherwise
        """
        for resource in self.get_all_resources():
            if resource.name == name:
                return resource
        return None


class TaskFile(BaseModel):
    """Parsed task file."""

    filename: str
    timestamp: datetime
    description: str
    prompt: str | None = None
    actions: list[str] = Field(default_factory=list)
    files_changed: dict[str, str] = Field(default_factory=dict)  # path -> description
    outcome: TaskOutcome = TaskOutcome.IN_PROGRESS
    notes: str | None = None

    @classmethod
    def from_file(cls, path: str) -> "TaskFile":
        """Parse task file from markdown.

        Args:
            path: Path to task file

        Returns:
            Parsed TaskFile

        Raises:
            ValueError: If file format is invalid
        """
        # TODO: Implement markdown parsing
        raise NotImplementedError("Task file parsing not yet implemented")

    def to_markdown(self) -> str:
        """Render task as markdown.

        Returns:
            Markdown string
        """
        # TODO: Implement markdown rendering
        raise NotImplementedError("Task file rendering not yet implemented")


class ProjectStructure(BaseModel):
    """Expected project directory structure."""

    mode: ProjectMode
    directories: list[str]
    required_files: list[str]
    optional_files: list[str]

    @classmethod
    def for_mode(cls, mode: ProjectMode) -> "ProjectStructure":
        """Get expected structure for project mode.

        Args:
            mode: Project mode

        Returns:
            ProjectStructure for that mode
        """
        if mode == ProjectMode.REVIEW:
            # Assessment project: repos/ for symlinks, analysis/ for findings
            return cls(
                mode=mode,
                directories=[".air", ".air/tasks", ".air/context", ".air/templates",
                           ".air/agents", ".air/shared",
                           "repos", "analysis", "analysis/reviews"],
                required_files=["README.md", "CLAUDE.md", "air-config.json", ".gitignore"],
                optional_files=["repos-to-link.txt"],
            )
        elif mode == ProjectMode.DEVELOP:
            # Development project: just add .air/ for task tracking
            # No special directories - this is your actual project
            return cls(
                mode=mode,
                directories=[".air", ".air/tasks", ".air/context", ".air/templates",
                           ".air/agents", ".air/shared"],
                required_files=["air-config.json"],
                optional_files=[],
            )
        else:  # MIXED
            # Developing this project AND assessing external repos
            return cls(
                mode=mode,
                directories=[".air", ".air/tasks", ".air/context", ".air/templates",
                           ".air/agents", ".air/shared",
                           "repos", "analysis", "analysis/reviews"],
                required_files=["README.md", "CLAUDE.md", "air-config.json", ".gitignore"],
                optional_files=["repos-to-link.txt"],
            )
