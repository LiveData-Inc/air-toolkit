"""Manage AI task files."""

import click
from rich.console import Console

console = Console()


@click.group()
def task() -> None:
    """Manage AI task files.

    Create, list, and manage task files in .ai/tasks/
    """
    pass


@task.command("new")
@click.argument("description")
@click.option(
    "--prompt",
    help="User prompt that triggered this task",
)
def task_new(description: str, prompt: str | None) -> None:
    """Create new task file.

    \b
    Examples:
      air task new "implement feature X"
      air task new "fix bug Y" --prompt "Fix the login issue"
    """
    console.print(f"[blue]ℹ[/blue] Creating task: {description}")

    # TODO: Implement task creation
    # - Generate timestamp filename: YYYYMMDD-HHMM-description.md
    # - Use template from .ai/templates/
    # - Populate with description and prompt
    # - Write to .ai/tasks/

    console.print("[green]✓[/green] Task file created: .ai/tasks/20251003-1200-implement-feature-x.md")


@task.command("list")
@click.option(
    "--status",
    type=click.Choice(["all", "in-progress", "success", "blocked"]),
    default="all",
    help="Filter by task status",
)
def task_list(status: str) -> None:
    """List all task files.

    \b
    Examples:
      air task list
      air task list --status=in-progress
    """
    console.print("[bold]AI Tasks[/bold]\n")

    # TODO: Implement task listing
    # - Read .ai/tasks/*.md
    # - Parse status from each file
    # - Filter by status if specified
    # - Display in table or list format

    console.print("  • 20251003-1200-implement-feature-x.md [green]✓ Success[/green]")
    console.print("  • 20251003-1315-fix-bug-y.md [yellow]⏳ In Progress[/yellow]")


@task.command("complete")
@click.argument("task_id")
def task_complete(task_id: str) -> None:
    """Mark task as complete.

    \b
    Examples:
      air task complete 20251003-1200
    """
    console.print(f"[blue]ℹ[/blue] Marking task complete: {task_id}")

    # TODO: Implement task completion
    # - Find task file by ID prefix
    # - Update outcome to ✅ Success
    # - Optionally update timestamp

    console.print("[green]✓[/green] Task marked as complete")
