"""Generate summary of AI tasks."""

from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.markdown import Markdown

from air.core.models import AssessmentConfig
from air.services.filesystem import get_project_root
from air.services.summary_generator import (
    generate_json_summary,
    generate_markdown_summary,
    generate_text_summary,
)
from air.services.task_parser import get_all_task_info
from air.utils.console import error, info, success

console = Console()


@click.command()
@click.option(
    "--output",
    type=click.Path(),
    help="Output file for summary (default: stdout)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["markdown", "json", "text"]),
    default="markdown",
    help="Output format",
)
@click.option(
    "--since",
    help="Only include tasks since date (YYYY-MM-DD)",
)
def summary(output: str | None, output_format: str, since: str | None) -> None:
    """Generate summary of all AI task files.

    Compiles information from all task files in .air/tasks/ into a
    comprehensive summary document.

    \b
    Examples:
      air summary
      air summary --output=SUMMARY.md
      air summary --since=2025-10-01
      air summary --format=json
    """
    # Validate project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    tasks_dir = project_root / ".air/tasks"
    if not tasks_dir.exists():
        error(
            ".air/tasks directory not found",
            hint="Run 'air init' to initialize project structure",
            exit_code=1,
        )

    # Parse since date
    since_dt = None
    if since:
        try:
            since_dt = datetime.strptime(since, "%Y-%m-%d")
        except ValueError:
            error(
                f"Invalid date format: {since}",
                hint="Use YYYY-MM-DD format (e.g., 2025-10-01)",
                exit_code=1,
            )

    # Get project name
    config_path = project_root / "air-config.json"
    project_name = "AIR Project"
    if config_path.exists():
        try:
            import json

            with open(config_path) as f:
                config_data = json.load(f)
                project_name = config_data.get("name", "AIR Project")
        except Exception:
            pass  # Use default name if config can't be read

    # Only show info message if not JSON output to stdout
    if not (output_format == "json" and not output):
        info("Generating task summary...")

    # Parse all task files
    task_info_list = get_all_task_info(tasks_dir, since_dt)

    if not task_info_list:
        if output_format == "json":
            # Return empty JSON structure
            print(json.dumps({"project": project_name, "statistics": {"total_tasks": 0}, "tasks": []}, indent=2))
        else:
            info("No tasks found")
            if since:
                console.print(f"[dim]No tasks found since {since}[/dim]")
            else:
                console.print("[dim]No task files in .air/tasks/[/dim]")
        return

    # Generate summary in requested format
    if output_format == "json":
        summary_content = generate_json_summary(task_info_list, project_name)
    elif output_format == "text":
        summary_content = generate_text_summary(task_info_list)
    else:  # markdown
        summary_content = generate_markdown_summary(task_info_list, project_name)

    # Output to file or stdout
    if output:
        output_path = Path(output)
        output_path.write_text(summary_content)
        success(f"Summary written to: {output}")
    else:
        # Display to console
        if output_format == "markdown":
            # Render markdown nicely in terminal
            console.print(Markdown(summary_content))
        else:
            # For JSON and text, print directly
            print(summary_content)
