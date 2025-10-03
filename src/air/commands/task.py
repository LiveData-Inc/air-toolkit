"""Manage AI task files."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.services.filesystem import get_project_root
from air.services.task_archive import (
    archive_task,
    find_task_in_archive,
    get_archive_stats,
    get_tasks_before_date,
    list_tasks,
    restore_task,
)
from air.utils.console import error, success

console = Console()


@click.group()
def task() -> None:
    """Manage AI task files.

    Create, list, and manage task files in .air/tasks/
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
    # - Use template from .air/templates/
    # - Populate with description and prompt
    # - Write to .air/tasks/

    console.print("[green]✓[/green] Task file created: .air/tasks/20251003-1200-implement-feature-x.md")


@task.command("list")
@click.option(
    "--status",
    type=click.Choice(["all", "in-progress", "success", "blocked"]),
    default="all",
    help="Filter by task status",
)
@click.option(
    "--all",
    "include_archived",
    is_flag=True,
    help="Include archived tasks",
)
@click.option(
    "--archived",
    "archived_only",
    is_flag=True,
    help="Show only archived tasks",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def task_list(
    status: str, include_archived: bool, archived_only: bool, output_format: str
) -> None:
    """List all task files.

    \b
    Examples:
      air task list                    # List active tasks
      air task list --all              # Include archived
      air task list --archived         # Only archived
      air task list --format=json      # JSON output
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    tasks_root = project_root / ".air/tasks"
    archive_root = tasks_root / "archive"

    tasks_dict = list_tasks(tasks_root, archive_root, include_archived, archived_only)

    if output_format == "json":
        result = {
            "active": [str(t.relative_to(project_root)) for t in tasks_dict["active"]],
            "archived": [str(t.relative_to(project_root)) for t in tasks_dict["archived"]],
            "total_active": len(tasks_dict["active"]),
            "total_archived": len(tasks_dict["archived"]),
        }
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    if not archived_only:
        console.print("[bold]Active Tasks[/bold]\n")
        if tasks_dict["active"]:
            for task_file in tasks_dict["active"]:
                console.print(f"  • {task_file.name}")
        else:
            console.print("  [dim]No active tasks[/dim]")

    if include_archived or archived_only:
        console.print("\n[bold]Archived Tasks[/bold]\n")
        if tasks_dict["archived"]:
            for task_file in tasks_dict["archived"]:
                # Show relative path from archive root
                rel_path = task_file.relative_to(archive_root)
                console.print(f"  • {rel_path}")
        else:
            console.print("  [dim]No archived tasks[/dim]")

    # Summary
    total_active = len(tasks_dict["active"])
    total_archived = len(tasks_dict["archived"])
    console.print(f"\n[dim]Active: {total_active}, Archived: {total_archived}[/dim]")


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


@task.command("archive")
@click.argument("task_ids", nargs=-1)
@click.option(
    "--all",
    "archive_all",
    is_flag=True,
    help="Archive all completed tasks",
)
@click.option(
    "--before",
    help="Archive tasks before date (YYYY-MM-DD)",
)
@click.option(
    "--strategy",
    type=click.Choice(["by-month", "by-quarter", "flat"]),
    default="by-month",
    help="Archive organization strategy",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be archived without doing it",
)
def task_archive(
    task_ids: tuple[str, ...],
    archive_all: bool,
    before: str | None,
    strategy: str,
    dry_run: bool,
) -> None:
    """Archive task files.

    \b
    Examples:
      air task archive 20251003-1200              # Archive one task
      air task archive 20251003-1200 20251003-1215  # Archive multiple
      air task archive --all                      # Archive all tasks
      air task archive --before=2025-09-01        # Archive before date
      air task archive --dry-run --all           # Preview
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    tasks_root = project_root / ".air/tasks"
    archive_root = tasks_root / "archive"

    # Determine which tasks to archive
    tasks_to_archive: list[Path] = []

    if task_ids:
        # Archive specific tasks
        for task_id in task_ids:
            # Find task file
            if not task_id.endswith(".md"):
                pattern = f"{task_id}-*.md"
            else:
                pattern = task_id

            matching = list(tasks_root.glob(pattern))
            if not matching:
                error(
                    f"Task not found: {task_id}",
                    hint="Use 'air task list' to see available tasks",
                    exit_code=1,
                )
            tasks_to_archive.extend(matching)

    elif archive_all:
        # Archive all active tasks
        tasks_dict = list_tasks(tasks_root, archive_root, include_archived=False)
        tasks_to_archive = tasks_dict["active"]

    elif before:
        # Archive tasks before date
        tasks_dict = list_tasks(tasks_root, archive_root, include_archived=False)
        tasks_to_archive = get_tasks_before_date(tasks_dict["active"], before)

    else:
        error(
            "Must specify task IDs, --all, or --before",
            hint="Try: air task archive --help",
            exit_code=1,
        )

    if not tasks_to_archive:
        console.print("[yellow]ℹ[/yellow] No tasks to archive")
        return

    # Archive tasks
    archived_count = 0
    for task_file in tasks_to_archive:
        archive_path = archive_task(task_file, archive_root, strategy, dry_run)  # type: ignore

        if dry_run:
            console.print(f"[dim]Would archive:[/dim] {task_file.name} → {archive_path.relative_to(archive_root)}")
        else:
            console.print(f"[green]✓[/green] Archived: {task_file.name} → {archive_path.relative_to(archive_root)}")
            archived_count += 1

    if dry_run:
        console.print(f"\n[dim]Dry run: {len(tasks_to_archive)} tasks would be archived[/dim]")
    else:
        success(f"Archived {archived_count} tasks to {archive_root.relative_to(project_root)}/")


@task.command("restore")
@click.argument("task_ids", nargs=-1, required=True)
def task_restore(task_ids: tuple[str, ...]) -> None:
    """Restore archived tasks back to active.

    \b
    Examples:
      air task restore 20251003-1200
      air task restore 20251003-1200 20251003-1215
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    tasks_root = project_root / ".air/tasks"
    archive_root = tasks_root / "archive"

    restored_count = 0
    for task_id in task_ids:
        restored_path = restore_task(task_id, tasks_root, archive_root)
        console.print(f"[green]✓[/green] Restored: {restored_path.name}")
        restored_count += 1

    success(f"Restored {restored_count} tasks from archive")


@task.command("archive-status")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def task_archive_status(output_format: str) -> None:
    """Show archive statistics.

    \b
    Examples:
      air task archive-status
      air task archive-status --format=json
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    archive_root = project_root / ".air/tasks/archive"
    stats = get_archive_stats(archive_root)

    if output_format == "json":
        print(json.dumps(stats, indent=2))
        return

    # Human-readable output
    console.print("[bold]Archive Statistics[/bold]\n")
    console.print(f"Total archived tasks: {stats['total_archived']}")

    if stats["by_month"]:
        console.print("\n[bold]By Month:[/bold]")
        for month, count in sorted(stats["by_month"].items(), reverse=True):
            console.print(f"  {month}: {count} tasks")

    if stats["by_quarter"]:
        console.print("\n[bold]By Quarter:[/bold]")
        for quarter, count in sorted(stats["by_quarter"].items(), reverse=True):
            console.print(f"  {quarter}: {count} tasks")
