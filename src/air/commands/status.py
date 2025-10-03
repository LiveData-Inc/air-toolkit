"""Show AIR project status."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from air.core.models import AssessmentConfig
from air.services.filesystem import get_project_root
from air.utils.console import error

console = Console()


@click.command()
@click.option(
    "--type",
    "resource_type",
    type=click.Choice(["review", "collaborate", "all"]),
    default="all",
    help="Filter by resource type",
)
@click.option(
    "--contributions",
    is_flag=True,
    help="Show contribution status for collaborative resources",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def status(resource_type: str, contributions: bool, output_format: str) -> None:
    """Show AIR project status.

    Displays:
      - Project mode and configuration
      - Linked resources (review and collaborative)
      - Analysis documents created
      - Contribution status (if --contributions)

    \b
    Examples:
      air status
      air status --type=review
      air status --contributions
      air status --format=json
    """
    # Find project root
    project_root = get_project_root()
    if project_root is None:
        if output_format == "json":
            print(json.dumps({"success": False, "error": "Not an AIR project"}))
        else:
            error(
                "Not an AIR project",
                hint="Run 'air init' to create a new AIR project",
                exit_code=1,
            )

    # Load config
    config_path = project_root / "air-config.json"
    if not config_path.exists():
        if output_format == "json":
            print(json.dumps({"success": False, "error": "Missing air-config.json"}))
        else:
            error(
                "Missing air-config.json",
                hint="Project configuration not found",
                exit_code=1,
            )

    try:
        with open(config_path) as f:
            config_data = json.load(f)
            config = AssessmentConfig(**config_data)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Invalid config: {e}"}))
        else:
            error(f"Invalid config: {e}", exit_code=1)

    # Count resources
    review_resources = []
    collaborate_resources = []

    for resource in config.resources.get("review", []):
        if resource_type in ["review", "all"]:
            review_resources.append(resource)

    for resource in config.resources.get("collaborate", []):
        if resource_type in ["collaborate", "all"]:
            collaborate_resources.append(resource)

    # Count analysis files
    analysis_dir = project_root / "analysis"
    analysis_files = []
    if analysis_dir.exists():
        for file in analysis_dir.rglob("*.md"):
            if file.name != "SUMMARY.md":
                analysis_files.append(str(file.relative_to(project_root)))

    # Count task files
    task_dir = project_root / ".ai/tasks"
    task_count = 0
    if task_dir.exists():
        task_count = len(list(task_dir.glob("*.md")))

    # Output results
    if output_format == "json":
        result = {
            "success": True,
            "project": {
                "name": config.name,
                "mode": config.mode,
                "created": config.created.isoformat() if hasattr(config.created, 'isoformat') else str(config.created),
                "root": str(project_root),
            },
            "resources": {
                "review": len(review_resources),
                "collaborate": len(collaborate_resources),
                "total": len(review_resources) + len(collaborate_resources),
            },
            "analysis": {
                "files": len(analysis_files),
                "paths": analysis_files[:10],  # Limit to first 10
            },
            "tasks": {
                "count": task_count,
            },
        }
        print(json.dumps(result, indent=2))
        sys.exit(0)
    else:
        # Human-readable output
        console.print()
        console.print(
            Panel(
                f"[bold]{config.name}[/bold]\n"
                f"Mode: [cyan]{config.mode}[/cyan]\n"
                f"Created: {config.created.strftime('%Y-%m-%d') if hasattr(config.created, 'strftime') else config.created}",
                title="[bold]AIR Project Status[/bold]",
                border_style="blue",
            )
        )
        console.print()

        # Resources table
        if resource_type in ["review", "all"] and review_resources:
            table = Table(title="Review Resources", style="cyan")
            table.add_column("Name", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Path", style="dim")

            for resource in review_resources:
                table.add_row(
                    resource.name,
                    resource.type,
                    resource.path,
                )
            console.print(table)
            console.print()

        if resource_type in ["collaborate", "all"] and collaborate_resources:
            table = Table(title="Collaborative Resources", style="green")
            table.add_column("Name", style="green")
            table.add_column("Type", style="magenta")
            table.add_column("Path", style="dim")

            for resource in collaborate_resources:
                table.add_row(
                    resource.name,
                    resource.type,
                    resource.path,
                )
            console.print(table)
            console.print()

        # Summary
        console.print(f"[bold]Summary:[/bold]")
        console.print(f"  Resources: {len(review_resources) + len(collaborate_resources)}")
        console.print(f"  Analysis files: {len(analysis_files)}")
        console.print(f"  Task files: {task_count}")
        console.print()

        if len(review_resources) + len(collaborate_resources) == 0:
            console.print("[dim]No resources linked yet. Use 'air link' to add resources.[/dim]")
            console.print()
