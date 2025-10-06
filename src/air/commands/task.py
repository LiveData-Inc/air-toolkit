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
    update_archive_summary,
)
from air.utils.completion import complete_task_ids
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
    from datetime import datetime, timezone
    from air.services.templates import render_template
    from air.utils.console import info
    from air.utils.dates import format_timestamp
    from air.utils.paths import safe_filename

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

    # Generate filename with ordinal (new format)
    from air.utils.dates import get_next_ordinal

    ordinal = get_next_ordinal(tasks_dir)
    timestamp = format_timestamp(ordinal=ordinal)
    safe_desc = safe_filename(description)
    filename = f"{timestamp}-{safe_desc}.md"
    task_path = tasks_dir / filename

    # Check if file already exists
    if task_path.exists():
        error(
            f"Task file already exists: {filename}",
            hint="Wait a minute or use a different description",
            exit_code=1,
        )

    # Prepare template context
    now = datetime.now(timezone.utc)
    context = {
        "title": description.capitalize(),
        "date": now.strftime("%Y-%m-%d %H:%M UTC"),
        "prompt": prompt or description,
        "description": f"Working on: {description}",
    }

    # Render template
    content = render_template("ai/task.md.j2", context)

    # Write task file
    task_path.write_text(content)

    info(f"Task file created: .air/tasks/{filename}")
    success(f"Task: {description}")


@task.command("list")
@click.option(
    "--status",
    type=click.Choice(["all", "in-progress", "success", "blocked", "partial"]),
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
@click.option(
    "--sort",
    type=click.Choice(["date", "title", "status"]),
    default="date",
    help="Sort tasks by field",
)
@click.option(
    "--search",
    help="Search tasks by keyword (title or prompt)",
)
def task_list(
    status: str,
    include_archived: bool,
    archived_only: bool,
    output_format: str,
    sort: str,
    search: str | None,
) -> None:
    """List all task files.

    \b
    Examples:
      air task list                           # List active tasks
      air task list --all                     # Include archived
      air task list --archived                # Only archived
      air task list --status=success          # Only completed tasks
      air task list --sort=title              # Sort by title
      air task list --search=authentication   # Search for keyword
      air task list --format=json             # JSON output
    """
    from air.services.task_parser import parse_task_file

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

    # Collect all tasks with parsed info for filtering/sorting
    task_items = []
    for task_file in tasks_dict["active"]:
        try:
            task_info = parse_task_file(task_file)
            task_items.append({"file": task_file, "info": task_info, "archived": False})
        except Exception:
            # Skip files that can't be parsed
            pass

    for task_file in tasks_dict["archived"]:
        try:
            task_info = parse_task_file(task_file)
            task_items.append({"file": task_file, "info": task_info, "archived": True})
        except Exception:
            pass

    # Filter by status
    if status != "all":
        status_map = {
            "in-progress": "in_progress",
            "success": "success",
            "blocked": "blocked",
            "partial": "partial",
        }
        filter_status = status_map.get(status, status)
        task_items = [t for t in task_items if t["info"].outcome == filter_status]

    # Search by keyword
    if search:
        search_lower = search.lower()
        task_items = [
            t for t in task_items
            if (search_lower in (t["info"].title or "").lower()) or
               (search_lower in (t["info"].prompt or "").lower())
        ]

    # Sort tasks
    if sort == "title":
        task_items.sort(key=lambda t: (t["info"].title or "").lower())
    elif sort == "status":
        task_items.sort(key=lambda t: t["info"].outcome or "")
    else:  # date (default)
        task_items.sort(key=lambda t: t["info"].timestamp or t["file"].name, reverse=True)

    # Separate active and archived for display
    active_items = [t for t in task_items if not t["archived"]]
    archived_items = [t for t in task_items if t["archived"]]

    if output_format == "json":
        result = {
            "active": [
                {
                    "filename": str(t["file"].relative_to(project_root)),
                    "title": t["info"].title,
                    "status": t["info"].outcome,
                    "date": t["info"].date,
                }
                for t in active_items
            ],
            "archived": [
                {
                    "filename": str(t["file"].relative_to(project_root)),
                    "title": t["info"].title,
                    "status": t["info"].outcome,
                    "date": t["info"].date,
                }
                for t in archived_items
            ],
            "total_active": len(active_items),
            "total_archived": len(archived_items),
        }
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    status_emoji = {
        "success": "✅",
        "in_progress": "⏳",
        "partial": "⚠️",
        "blocked": "🚫",
    }

    if not archived_only:
        console.print("[bold]Active Tasks[/bold]\n")
        if active_items:
            for task_item in active_items:
                emoji = status_emoji.get(task_item["info"].outcome or "in_progress", "❓")
                console.print(f"  {emoji} {task_item['file'].name} - {task_item['info'].title}")
        else:
            console.print("  [dim]No active tasks[/dim]")

    if include_archived or archived_only:
        console.print("\n[bold]Archived Tasks[/bold]\n")
        if archived_items:
            for task_item in archived_items:
                emoji = status_emoji.get(task_item["info"].outcome or "in_progress", "❓")
                rel_path = task_item["file"].relative_to(archive_root)
                console.print(f"  {emoji} {rel_path} - {task_item['info'].title}")
        else:
            console.print("  [dim]No archived tasks[/dim]")

    # Summary
    console.print(f"\n[dim]Active: {len(active_items)}, Archived: {len(archived_items)}[/dim]")


@task.command("complete")
@click.argument("task_id", shell_complete=complete_task_ids)
@click.option(
    "--notes",
    help="Optional completion notes to add",
)
def task_complete(task_id: str, notes: str | None) -> None:
    """Mark task as complete.

    \b
    Examples:
      air task complete 20251003-1200
      air task complete 20251003-1200 --notes "Fixed authentication bug"
    """
    from air.utils.console import info

    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    tasks_root = project_root / ".air/tasks"

    # Find task file by ID prefix
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

    if len(matching) > 1:
        error(
            f"Multiple tasks match '{task_id}'",
            hint=f"Be more specific. Matches: {', '.join(t.name for t in matching)}",
            exit_code=1,
        )

    task_file = matching[0]

    # Read current content
    content = task_file.read_text()

    # Update outcome section
    import re

    # Find the outcome section and update it - match the line after ## Outcome
    # Preserve whatever comes after the outcome line
    outcome_pattern = r"(## Outcome\n)([^\n]+)(.*)"

    if re.search(outcome_pattern, content, re.DOTALL):
        # Replace existing outcome, keeping everything after it
        new_content = re.sub(
            outcome_pattern,
            r"\1✅ Success\3",
            content,
            count=1,
            flags=re.DOTALL
        )
    else:
        # No outcome section found - shouldn't happen with templates but handle it
        error(
            "Task file is missing Outcome section",
            hint="Check task file format",
            exit_code=1,
        )

    # Optionally append notes to Notes section if provided
    if notes:
        # Pattern to match Notes section - handles empty section or section with content
        notes_pattern = r"(## Notes\s*\n)(.*?)($)"
        match = re.search(notes_pattern, new_content, re.DOTALL)

        if match:
            existing_notes = match.group(2).strip()
            if existing_notes:
                updated_notes = f"{existing_notes}\n\n**Completed:** {notes}\n"
            else:
                updated_notes = f"**Completed:** {notes}\n"

            new_content = re.sub(
                notes_pattern,
                rf"\1{updated_notes}",
                new_content,
                count=1
            )

    # Write updated content
    task_file.write_text(new_content)

    info(f"Updated task file: .air/tasks/{task_file.name}")
    success(f"Task marked as complete: {task_id}")


@task.command("status")
@click.argument("task_id", shell_complete=complete_task_ids)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def task_status(task_id: str, output_format: str) -> None:
    """Show task details.

    \b
    Examples:
      air task status 20251003-1200
      air task status 20251003-1200 --format=json
    """
    from air.services.task_parser import parse_task_file
    from air.utils.console import info

    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    tasks_root = project_root / ".air/tasks"
    archive_root = tasks_root / "archive"

    # Find task file by ID prefix - check active first, then archive
    if not task_id.endswith(".md"):
        pattern = f"{task_id}-*.md"
    else:
        pattern = task_id

    # Search in active tasks
    matching = list(tasks_root.glob(pattern))

    # If not found in active, search archive
    if not matching:
        matching = list(archive_root.rglob(pattern))
        if matching:
            info(f"Task found in archive: {matching[0].relative_to(archive_root)}")

    if not matching:
        error(
            f"Task not found: {task_id}",
            hint="Use 'air task list --all' to see all tasks",
            exit_code=1,
        )

    if len(matching) > 1:
        error(
            f"Multiple tasks match '{task_id}'",
            hint=f"Be more specific. Matches: {', '.join(t.name for t in matching)}",
            exit_code=1,
        )

    task_file = matching[0]

    # Parse task file
    task_info = parse_task_file(task_file)

    if output_format == "json":
        # JSON output
        output = {
            "filename": task_info.filename,
            "title": task_info.title,
            "date": task_info.date,
            "prompt": task_info.prompt,
            "actions": task_info.actions,
            "files_changed": task_info.files_changed,
            "outcome": task_info.outcome,
            "notes": task_info.notes,
            "timestamp": task_info.timestamp.isoformat() if task_info.timestamp else None,
        }
        print(json.dumps(output, indent=2))
    else:
        # Human-readable output
        from rich.markdown import Markdown
        from rich.panel import Panel

        # Determine status emoji
        status_emoji = {
            "success": "✅",
            "in_progress": "⏳",
            "partial": "⚠️",
            "blocked": "🚫",
        }.get(task_info.outcome or "in_progress", "❓")

        # Build display
        console.print()
        console.print(Panel(
            f"[bold]{task_info.title}[/bold]",
            title=f"{status_emoji} Task Status",
            border_style="blue",
        ))
        console.print()

        # Metadata
        console.print(f"[dim]File:[/dim] {task_info.filename}")
        if task_info.date:
            console.print(f"[dim]Date:[/dim] {task_info.date}")
        if task_info.timestamp:
            console.print(f"[dim]ID:[/dim] {task_info.timestamp.strftime('%Y%m%d-%H%M')}")
        console.print()

        # Prompt
        if task_info.prompt:
            console.print("[bold]Prompt[/bold]")
            console.print(f"  {task_info.prompt}")
            console.print()

        # Actions
        if task_info.actions and any(a.strip() and a.strip() not in ["1.", "-"] for a in task_info.actions):
            console.print("[bold]Actions Taken[/bold]")
            for action in task_info.actions:
                if action.strip() and action.strip() not in ["1.", "-"]:
                    console.print(f"  • {action}")
            console.print()

        # Files Changed
        if task_info.files_changed and any(f.strip() and f.strip() != "-" for f in task_info.files_changed):
            console.print("[bold]Files Changed[/bold]")
            for file in task_info.files_changed:
                if file.strip() and file.strip() != "-":
                    console.print(f"  • {file}")
            console.print()

        # Outcome
        console.print(f"[bold]Outcome:[/bold] {status_emoji} {task_info.outcome or 'In Progress'}")
        console.print()

        # Notes
        if task_info.notes and task_info.notes.strip():
            console.print("[bold]Notes[/bold]")
            console.print(Markdown(task_info.notes))
            console.print()


@task.command("archive")
@click.argument("task_ids", nargs=-1, shell_complete=complete_task_ids)
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
        # Update archive summary
        update_archive_summary(archive_root)
        console.print(f"[dim]Updated archive summary: {(archive_root / 'ARCHIVE.md').relative_to(project_root)}[/dim]")
        success(f"Archived {archived_count} tasks to {archive_root.relative_to(project_root)}/")


@task.command("restore")
@click.argument("task_ids", nargs=-1, required=True, shell_complete=complete_task_ids)
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

    # Update archive summary after restoration
    if restored_count > 0:
        update_archive_summary(archive_root)
        console.print(f"[dim]Updated archive summary: {(archive_root / 'ARCHIVE.md').relative_to(project_root)}[/dim]")

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
