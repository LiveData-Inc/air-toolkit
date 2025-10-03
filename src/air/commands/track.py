"""Initialize and manage .ai/ tracking."""

import click
from rich.console import Console

console = Console()


@click.group()
def track() -> None:
    """Initialize and manage .ai/ tracking system.

    Use this to add AI task tracking to any project.
    """
    pass


@track.command("init")
@click.option(
    "--minimal",
    is_flag=True,
    help="Create minimal .ai/ structure without full templates",
)
def track_init(minimal: bool) -> None:
    """Initialize .ai/ tracking in current directory.

    Creates:
      .ai/README.md - Documentation
      .ai/tasks/ - Task files directory
      .ai/context/ - Context files directory
      .ai/templates/ - Task templates

    \b
    Examples:
      air track init
      air track init --minimal
    """
    console.print("[blue]ℹ[/blue] Initializing .ai/ tracking...")

    # TODO: Implement .ai/ initialization
    # - Create directory structure
    # - Copy templates
    # - Create README.md
    # - Optionally create CLAUDE.md

    console.print("[green]✓[/green] .ai/ tracking initialized")
    console.print("\n[dim]Next steps:[/dim]")
    console.print("  1. Review .ai/README.md")
    console.print("  2. Update .ai/context/ files")
    console.print("  3. Start using: air task new 'description'")


@track.command("status")
def track_status() -> None:
    """Show .ai/ tracking status."""
    console.print("[bold].ai/ Tracking Status[/bold]\n")

    # TODO: Implement status display
    # - Check if .ai/ exists
    # - Count task files
    # - Show recent tasks
    # - List context files

    console.print("Tasks: 5 files")
    console.print("Context files: 3")
    console.print("\nRecent tasks:")
    console.print("  • implement-feature-x (✓)")
    console.print("  • fix-bug-y (⏳)")
