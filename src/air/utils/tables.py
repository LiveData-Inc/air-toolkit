"""Shared table rendering utilities."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from air.core.models import Resource

console = Console()


def get_resource_status(resource: Resource, project_root: Path) -> str:
    """Get status indicator for a resource.

    Args:
        resource: The resource to check
        project_root: Project root directory

    Returns:
        Colored status string (e.g., "[green]✓ valid[/green]")
    """
    resource_path = Path(resource.path).expanduser()
    link_path = project_root / "repos" / resource.name

    if link_path.exists() and resource_path.exists():
        return "[green]✓ valid[/green]"
    elif link_path.exists() and not resource_path.exists():
        return "[red]✗ broken[/red]"
    else:
        return "[yellow]⚠ missing[/yellow]"


def render_resource_table(
    resources: list[Resource],
    project_root: Path,
    title: str,
    title_style: str = "cyan",
    name_style: str = "cyan",
) -> None:
    """Render a table of resources with status indicators.

    Args:
        resources: List of resources to display
        project_root: Project root directory
        title: Table title
        title_style: Color style for title
        name_style: Color style for name column
    """
    if not resources:
        return

    table = Table(title=title, style=title_style, show_header=True)
    table.add_column("Status", width=10)
    table.add_column("Name", style=name_style)
    table.add_column("Type", style="magenta")
    table.add_column("Path", style="dim")

    for resource in resources:
        status = get_resource_status(resource, project_root)
        table.add_row(
            status,
            resource.name,
            resource.type,
            resource.path,
        )

    console.print(table)
