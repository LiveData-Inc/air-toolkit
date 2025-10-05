"""Shell completion helpers for AIR CLI.

Provides dynamic completion functions for:
- Resource names (from air-config.json)
- Task IDs (from .air/tasks/)
- Analyzer focus types
- Developer resources (for PR commands)
"""

import json
from pathlib import Path
from typing import Any

import click

from air.core.models import ResourceRelationship
from air.services.filesystem import get_project_root


def complete_resource_names(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[str]:
    """Complete resource names from air-config.json.

    Args:
        ctx: Click context
        param: Parameter being completed
        incomplete: Partial string typed by user

    Returns:
        List of matching resource names
    """
    try:
        project_root = get_project_root()
        if not project_root:
            return []

        config_path = project_root / "air-config.json"
        if not config_path.exists():
            return []

        config = json.loads(config_path.read_text())
        resources = []

        # Extract all resource names from all relationship types
        for resource_list in config.get("resources", {}).values():
            resources.extend([r["name"] for r in resource_list])

        # Filter by incomplete string
        return [r for r in resources if r.startswith(incomplete)]
    except Exception:
        return []


def complete_developer_resources(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[str]:
    """Complete developer resource names only (for PR commands).

    Args:
        ctx: Click context
        param: Parameter being completed
        incomplete: Partial string typed by user

    Returns:
        List of matching developer resource names
    """
    try:
        project_root = get_project_root()
        if not project_root:
            return []

        config_path = project_root / "air-config.json"
        if not config_path.exists():
            return []

        config = json.loads(config_path.read_text())

        # Only get DEVELOPER resources
        developer_resources = config.get("resources", {}).get(
            ResourceRelationship.DEVELOPER.value, []
        )
        names = [r["name"] for r in developer_resources]

        # Filter by incomplete string
        return [n for n in names if n.startswith(incomplete)]
    except Exception:
        return []


def complete_task_ids(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[str]:
    """Complete task IDs from .air/tasks/ directory.

    Args:
        ctx: Click context
        param: Parameter being completed
        incomplete: Partial string typed by user

    Returns:
        List of matching task IDs (filenames without .md extension)
    """
    try:
        project_root = get_project_root()
        if not project_root:
            return []

        tasks_dir = project_root / ".air/tasks"
        if not tasks_dir.exists():
            return []

        # Get all task file stems (without .md extension)
        task_files = tasks_dir.glob("*.md")
        task_ids = [f.stem for f in task_files if not f.name.startswith("DESIGN-")]

        # Sort by newest first (reverse chronological)
        task_ids.sort(reverse=True)

        # Filter by incomplete string
        return [tid for tid in task_ids if tid.startswith(incomplete)]
    except Exception:
        return []


def complete_analyzer_focus(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[str]:
    """Complete analyzer focus types.

    Args:
        ctx: Click context
        param: Parameter being completed
        incomplete: Partial string typed by user

    Returns:
        List of matching focus types
    """
    focus_types = ["security", "performance", "quality", "architecture", "structure"]
    return [f for f in focus_types if f.startswith(incomplete)]


def complete_repo_paths(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[str]:
    """Complete repository paths from repos/ directory.

    Args:
        ctx: Click context
        param: Parameter being completed
        incomplete: Partial string typed by user

    Returns:
        List of matching repo paths (repos/*)
    """
    try:
        project_root = get_project_root()
        if not project_root:
            return []

        repos_dir = project_root / "repos"
        if not repos_dir.exists():
            return []

        # Get all directories/symlinks in repos/
        repo_paths = [f"repos/{p.name}" for p in repos_dir.iterdir() if p.is_dir()]

        # Filter by incomplete string
        return [r for r in repo_paths if r.startswith(incomplete)]
    except Exception:
        return []
