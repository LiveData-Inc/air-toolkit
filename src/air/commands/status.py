"""Show AIR project status."""

import json
import sys
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from air.core.models import AirConfig
from air.services.agent_manager import list_agents, get_agent_progress
from air.services.filesystem import get_project_root
from air.utils.console import error, info
from air.utils.dates import format_relative_time
from air.utils.tables import render_resource_table

console = Console()


@click.command()
@click.option(
    "--type",
    "resource_type",
    type=click.Choice(["review", "develop", "all"]),
    default="all",
    help="Filter by resource type",
)
@click.option(
    "--contributions",
    is_flag=True,
    help="Show contribution status for collaborative resources",
)
@click.option(
    "--agents",
    is_flag=True,
    help="Show agent status (v0.6.0+)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def status(
    resource_type: str, contributions: bool, agents: bool, output_format: str
) -> None:
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

    # Handle --agents flag
    if agents:
        show_agent_status(output_format)
        return

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
            config = AirConfig(**config_data)
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

    for resource in config.resources.get("develop", []):
        if resource_type in ["develop", "all"]:
            collaborate_resources.append(resource)

    # Count analysis files
    analysis_dir = project_root / "analysis"
    analysis_files = []
    if analysis_dir.exists():
        for file in analysis_dir.rglob("*.md"):
            if file.name != "SUMMARY.md":
                analysis_files.append(str(file.relative_to(project_root)))

    # Count task files
    task_dir = project_root / ".air/tasks"
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
                "develop": len(collaborate_resources),
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
            render_resource_table(
                review_resources,
                project_root,
                title="Review Resources",
                title_style="cyan",
                name_style="cyan",
            )
            console.print()

        if resource_type in ["develop", "all"] and collaborate_resources:
            render_resource_table(
                collaborate_resources,
                project_root,
                title="Collaborative Resources",
                title_style="green",
                name_style="green",
            )
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


def show_agent_status(output_format: str) -> None:
    """Show agent status.

    Args:
        output_format: Output format (human or json)
    """
    agent_list = list_agents()

    if output_format == "json":
        result = {
            "success": True,
            "agents": agent_list,
            "count": len(agent_list),
        }
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    if not agent_list:
        info("No agents found")
        console.print("\n[dim]Use 'air analyze --background' to spawn agents[/dim]\n")
        return

    # Create table
    table = Table(title="[bold]Active Agents[/bold]", show_header=True)
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="dim")
    table.add_column("Progress", style="green")

    for agent in agent_list:
        # Status emoji
        status = agent.get("status", "unknown")
        if status == "running":
            status_display = "⏳ Running"
            status_style = "yellow"
        elif status == "complete":
            status_display = "✓ Complete"
            status_style = "green"
        elif status == "failed":
            status_display = "✗ Failed"
            status_style = "red"
        else:
            status_display = f"? {status}"
            status_style = "dim"

        # Format time
        started = agent.get("started", "")
        if started:
            try:
                started_dt = datetime.fromisoformat(started)
                time_display = format_relative_time(started_dt)
            except Exception:
                time_display = started[:10]  # Just date
        else:
            time_display = ""

        # Get progress
        progress = get_agent_progress(agent["id"])

        table.add_row(
            agent["id"],
            f"[{status_style}]{status_display}[/{status_style}]",
            time_display,
            progress,
        )

    console.print()
    console.print(table)

    # Summary
    running = sum(1 for a in agent_list if a.get("status") == "running")
    complete = sum(1 for a in agent_list if a.get("status") == "complete")
    failed = sum(1 for a in agent_list if a.get("status") == "failed")

    console.print()
    console.print(
        f"[bold]Total:[/bold] {len(agent_list)} agents "
        f"([yellow]{running} running[/yellow], "
        f"[green]{complete} complete[/green], "
        f"[red]{failed} failed[/red])"
    )
    console.print()
