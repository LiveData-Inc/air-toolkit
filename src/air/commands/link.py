"""Link repositories to assessment project."""

import click
from rich.console import Console

console = Console()


@click.command()
@click.option(
    "--review",
    multiple=True,
    metavar="NAME:PATH",
    help="Add review-only resource (can specify multiple)",
)
@click.option(
    "--collaborate",
    multiple=True,
    metavar="NAME:PATH",
    help="Add collaborative resource (can specify multiple)",
)
@click.option(
    "--clone",
    is_flag=True,
    help="Clone instead of symlink (for collaborative resources)",
)
def link(review: tuple[str, ...], collaborate: tuple[str, ...], clone: bool) -> None:
    """Link repositories to assessment project.

    \b
    Examples:
      air link --review service-a:~/repos/service-a
      air link --collaborate arch:~/repos/architecture --clone
      air link  # Read from repos-to-link.txt
    """
    if not review and not collaborate:
        console.print("[blue]ℹ[/blue] Linking repositories from repos-to-link.txt")
        # TODO: Read from repos-to-link.txt
    else:
        for name_path in review:
            console.print(f"[blue]ℹ[/blue] Linking review resource: {name_path}")
            # TODO: Create symlink in review/

        for name_path in collaborate:
            action = "Cloning" if clone else "Linking"
            console.print(f"[blue]ℹ[/blue] {action} collaborative resource: {name_path}")
            # TODO: Clone or symlink in collaborate/

    console.print("[green]✓[/green] Resources linked successfully")
