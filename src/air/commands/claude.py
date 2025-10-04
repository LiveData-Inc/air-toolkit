"""Claude Code helper commands for AIR toolkit."""

import json
from pathlib import Path

import click
from rich.console import Console

from air.core.models import AirConfig
from air.services.filesystem import get_project_root
from air.utils.console import info

console = Console()


@click.group()
def claude() -> None:
    """AI assistant helper commands.

    These commands provide optimized output for AI assistants like Claude Code.
    They return structured data that's easy for AI to parse and use.
    """
    pass


@claude.command("context")
@click.option(
    "--format",
    type=click.Choice(["json", "markdown"]),
    default="json",
    help="Output format",
)
def context(format: str) -> None:
    """Get comprehensive project context for AI assistants.

    Returns project status, recent tasks, linked resources, and coding standards
    in a format optimized for AI consumption.

    \b
    Examples:
      air claude context                # JSON output (default)
      air claude context --format=markdown  # Human-readable markdown
    """
    project_root = get_project_root()

    context_data = {}

    if project_root:
        # Get AIR project status
        config_path = project_root / "air-config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)
                    config = AirConfig(**config_data)

                context_data["project"] = {
                    "name": config.name,
                    "mode": config.mode,
                    "resources": {
                        "review": len(config.resources.get("review", [])),
                        "develop": len(config.resources.get("develop", [])),
                    },
                }
            except Exception:
                context_data["project"] = {"error": "Could not load project status"}
        else:
            context_data["project"] = {"error": "No air-config.json found"}

        # Get recent tasks
        tasks_dir = project_root / ".air" / "tasks"
        if tasks_dir.exists():
            try:
                task_files = sorted(
                    [f for f in tasks_dir.glob("*.md") if f.name != "TASKS.md"],
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )[:10]

                context_data["recent_tasks"] = [
                    {
                        "file": str(f.relative_to(project_root)),
                        "name": f.stem,
                    }
                    for f in task_files
                ]
            except Exception:
                context_data["recent_tasks"] = []
        else:
            context_data["recent_tasks"] = []

        # Get coding standards
        context_dir = project_root / ".air" / "context"
        if context_dir.exists():
            standards = list(context_dir.glob("*.md"))
            context_data["standards"] = [
                {
                    "name": s.stem,
                    "path": str(s.relative_to(project_root)),
                }
                for s in standards
            ]
        else:
            context_data["standards"] = []

        # Get project goals
        config_path = project_root / "air-config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    context_data["goals"] = config.get("goals", [])
            except Exception:
                context_data["goals"] = []

    else:
        # Not an AIR project, provide minimal context
        context_data = {
            "note": "Not an AIR project",
            "hint": "Run 'air init' to create an AIR project",
            "cwd": str(Path.cwd()),
        }

    # Output
    if format == "json":
        console.print_json(data=context_data)
    else:
        # Markdown format
        console.print("# AIR Project Context\n")

        if "project" in context_data:
            proj = context_data["project"]
            if "error" not in proj:
                console.print(f"**Project:** {proj.get('name')}")
                console.print(f"**Mode:** {proj.get('mode')}")

                resources = proj.get("resources", {})
                total = len(resources.get("review", [])) + len(resources.get("develop", []))
                console.print(f"**Resources:** {total} linked\n")

        if context_data.get("recent_tasks"):
            console.print("## Recent Tasks\n")
            for task in context_data["recent_tasks"][:5]:
                console.print(f"- {task['description']} ({task['status']})")
            console.print()

        if context_data.get("standards"):
            console.print("## Coding Standards\n")
            for std in context_data["standards"]:
                console.print(f"- {std['name']}: {std['path']}")
            console.print()

        if context_data.get("goals"):
            console.print("## Project Goals\n")
            for goal in context_data["goals"]:
                console.print(f"- {goal}")
            console.print()

        if "note" in context_data:
            info(context_data["note"], hint=context_data.get("hint"))
