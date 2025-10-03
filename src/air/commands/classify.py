"""Classify resources by type."""

import click
from rich.console import Console

console = Console()


@click.command()
@click.option(
    "--verbose",
    is_flag=True,
    help="Show detailed classification information",
)
@click.option(
    "--update",
    is_flag=True,
    help="Update .assess-config.json with classifications",
)
def classify(verbose: bool, update: bool) -> None:
    """Classify resources by type.

    Analyzes linked resources and classifies them as:
      - Review-only: Implementation projects owned by other teams
      - Collaborative: Documentation we can contribute to

    \b
    Examples:
      air classify
      air classify --verbose
      air classify --update
    """
    console.print("[blue]ℹ[/blue] Classifying resources...")

    # TODO: Implement classification
    # - Detect git repos vs symlinks
    # - Check file types (code vs docs)
    # - Interactive prompts for ambiguous cases
    # - Update config if --update

    console.print("\n[bold]Review-Only Resources:[/bold]")
    console.print("  • service-a (implementation)")

    console.print("\n[bold]Collaborative Resources:[/bold]")
    console.print("  • architecture-docs (documentation)")
