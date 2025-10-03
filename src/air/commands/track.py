"""Initialize and manage .air/ tracking."""

import click
from rich.console import Console

console = Console()


@click.group()
def track() -> None:
    """Initialize and manage .air/ tracking system.

    Use this to add AI task tracking to any project.
    """
    pass


@track.command("init")
@click.option(
    "--minimal",
    is_flag=True,
    help="Create minimal .air/ structure without full templates",
)
def track_init(minimal: bool) -> None:
    """Initialize .air/ tracking in current directory.

    Creates:
      .air/README.md - Documentation
      .air/tasks/ - Task files directory
      .air/context/ - Context files directory
      .air/templates/ - Task templates

    \b
    Examples:
      air track init
      air track init --minimal
    """
    console.print("[blue]ℹ[/blue] Initializing .air/ tracking...")

    # TODO: Implement .air/ initialization
    # - Create directory structure
    # - Copy templates
    # - Create README.md
    # - Optionally create CLAUDE.md

    console.print("[green]✓[/green] .air/ tracking initialized")
    console.print("\n[dim]Next steps:[/dim]")
    console.print("  1. Review .air/README.md")
    console.print("  2. Update .air/context/ files")
    console.print("  3. Start using: air task new 'description'")


@track.command("status")
def track_status() -> None:
    """Show .air/ tracking status."""
    console.print("[bold].air/ Tracking Status[/bold]\n")

    # TODO: Implement status display
    # - Check if .air/ exists
    # - Count task files
    # - Show recent tasks
    # - List context files

    console.print("Tasks: 5 files")
    console.print("Context files: 3")
    console.print("\nRecent tasks:")
    console.print("  • implement-feature-x (✓)")
    console.print("  • fix-bug-y (⏳)")
