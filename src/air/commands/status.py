"""Show AIR project status."""

import click
from rich.console import Console
from rich.table import Table

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
def status(resource_type: str, contributions: bool) -> None:
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
    """
    console.print("[bold]AIR Project Status[/bold]\n")

    # TODO: Implement status display
    # - Read .assess-config.json
    # - Count linked resources
    # - List analysis documents
    # - Show contribution tracking if requested

    # Example table
    table = Table(title="Linked Resources")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Status", style="green")

    # TODO: Populate from actual data
    table.add_row("service-a", "review", "✓ linked")

    console.print(table)
