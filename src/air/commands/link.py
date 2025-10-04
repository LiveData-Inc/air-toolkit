"""Link repositories to assessment project."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.core.models import AirConfig, Resource, ResourceRelationship, ResourceType
from air.services.filesystem import create_symlink, get_project_root
from air.utils.console import error, info, success, warn

console = Console()


def parse_name_path(name_path: str) -> tuple[str, str]:
    """Parse NAME:PATH format.

    Args:
        name_path: String in format "name:path"

    Returns:
        Tuple of (name, path)

    Raises:
        SystemExit: If format is invalid
    """
    if ":" not in name_path:
        error(
            f"Invalid format: {name_path}",
            hint="Use NAME:PATH format, e.g., service-a:~/repos/service-a",
            exit_code=1,
        )

    parts = name_path.split(":", 1)
    name = parts[0].strip()
    path = parts[1].strip()

    if not name or not path:
        error(
            f"Invalid format: {name_path}",
            hint="Both name and path must be non-empty",
            exit_code=1,
        )

    return name, path


def load_config(project_root: Path) -> AirConfig:
    """Load project configuration.

    Args:
        project_root: Project root directory

    Returns:
        Loaded configuration

    Raises:
        SystemExit: If config cannot be loaded
    """
    config_path = project_root / "air-config.json"

    if not config_path.exists():
        error(
            "Configuration file not found",
            hint="Run 'air init' to create a project",
            exit_code=1,
        )

    try:
        with open(config_path) as f:
            config_data = json.load(f)
        return AirConfig(**config_data)
    except Exception as e:
        error(
            f"Failed to load configuration: {e}",
            hint="Check air-config.json syntax",
            exit_code=2,
        )


def save_config(project_root: Path, config: AirConfig) -> None:
    """Save project configuration.

    Args:
        project_root: Project root directory
        config: Configuration to save

    Raises:
        SystemExit: If config cannot be saved
    """
    config_path = project_root / "air-config.json"

    try:
        with open(config_path, "w") as f:
            # Use model_dump for Pydantic v2
            json.dump(config.model_dump(mode="json"), f, indent=2, default=str)
            f.write("\n")  # Add trailing newline
    except Exception as e:
        error(
            f"Failed to save configuration: {e}",
            hint="Check file permissions",
            exit_code=2,
        )


@click.group()
def link() -> None:
    """Link repositories to assessment project.

    Manage resources linked to this AIR assessment project.
    """
    pass


@link.command("add")
@click.argument("name_path")
@click.option(
    "--review",
    "is_review",
    is_flag=True,
    help="Link as review-only resource",
)
@click.option(
    "--develop",
    "is_develop",
    is_flag=True,
    help="Link as collaborative resource",
)
@click.option(
    "--type",
    "resource_type",
    type=click.Choice(["implementation", "documentation", "library", "service"]),
    default="implementation",
    help="Resource type",
)
def link_add(
    name_path: str, is_review: bool, is_develop: bool, resource_type: str
) -> None:
    """Add a linked resource.

    \b
    Examples:
      air link add service-a:~/repos/service-a --review
      air link add docs:~/repos/docs --develop
      air link add api:~/repos/api --review --type=service
    """
    # Validate project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    # Determine mode
    if is_review and is_develop:
        error(
            "Cannot specify both --review and --develop",
            hint="Choose one mode for the resource",
            exit_code=1,
        )

    if not is_review and not is_develop:
        # Default to review mode
        is_review = True
        info("Defaulting to review mode (read-only)")

    category = "review" if is_review else "develop"
    relationship = (
        ResourceRelationship.REVIEW_ONLY
        if is_review
        else ResourceRelationship.DEVELOPER
    )

    # Parse name and path
    name, path_str = parse_name_path(name_path)

    # Expand and validate path
    source_path = Path(path_str).expanduser().resolve()

    if not source_path.exists():
        error(
            f"Path does not exist: {source_path}",
            hint="Check the path is correct and accessible",
            exit_code=1,
        )

    if not source_path.is_dir():
        error(
            f"Path is not a directory: {source_path}",
            hint="Resources must be directories",
            exit_code=1,
        )

    # Load configuration
    config = load_config(project_root)

    # Check if resource already exists
    existing = config.find_resource(name)
    if existing:
        error(
            f"Resource '{name}' already linked",
            hint="Use a different name or remove the existing resource first",
            exit_code=1,
        )

    # Create symlink in repos/ directory
    # Note: Both review and develop resources go in repos/
    # The difference is the relationship (REVIEW_ONLY vs DEVELOPER)
    link_dir = project_root / "repos"
    link_path = link_dir / name

    if link_path.exists():
        error(
            f"Path already exists: {link_path}",
            hint="Remove existing file/link first",
            exit_code=1,
        )

    info(f"Creating symlink: repos/{name} -> {source_path}")
    create_symlink(source_path, link_path)

    # Create resource entry
    resource = Resource(
        name=name,
        path=str(source_path),
        type=ResourceType(resource_type),
        relationship=relationship,
        clone=False,
    )

    # Add to configuration
    config.add_resource(resource, category)
    save_config(project_root, config)

    success(f"Linked {category} resource: {name}")


@link.command("list")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def link_list(output_format: str) -> None:
    """List linked resources.

    \b
    Examples:
      air link list
      air link list --format=json
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    config = load_config(project_root)

    if output_format == "json":
        result = {
            "review": [
                {
                    "name": r.name,
                    "path": r.path,
                    "type": r.type,
                    "relationship": r.relationship,
                }
                for r in config.resources.get("review", [])
            ],
            "develop": [
                {
                    "name": r.name,
                    "path": r.path,
                    "type": r.type,
                    "relationship": r.relationship,
                }
                for r in config.resources.get("develop", [])
            ],
        }
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    review_resources = config.resources.get("review", [])
    collab_resources = config.resources.get("develop", [])

    if not review_resources and not collab_resources:
        info("No resources linked")
        console.print("\n[dim]Use 'air link add' to link resources[/dim]")
        return

    if review_resources:
        console.print("\n[bold]Review Resources (Read-Only)[/bold]\n")
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Path")

        for resource in review_resources:
            table.add_row(resource.name, resource.type, resource.path)

        console.print(table)

    if collab_resources:
        console.print("\n[bold]Collaborative Resources[/bold]\n")
        table = Table(show_header=True)
        table.add_column("Name")
        table.add_column("Type")
        table.add_column("Path")

        for resource in collab_resources:
            table.add_row(resource.name, resource.type, resource.path)

        console.print(table)

    total = len(review_resources) + len(collab_resources)
    console.print(f"\n[dim]Total: {total} resources[/dim]")


@link.command("remove")
@click.argument("name")
@click.option(
    "--keep-link",
    is_flag=True,
    help="Keep symlink, only remove from config",
)
def link_remove(name: str, keep_link: bool) -> None:
    """Remove a linked resource.

    \b
    Examples:
      air link remove service-a
      air link remove docs --keep-link
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    config = load_config(project_root)

    # Find resource
    resource = config.find_resource(name)
    if not resource:
        error(
            f"Resource not found: {name}",
            hint="Use 'air link list' to see available resources",
            exit_code=1,
        )

    # Determine category
    category = None
    for cat in ["review", "develop"]:
        if resource in config.resources.get(cat, []):
            category = cat
            break

    if not category:
        error(
            f"Resource '{name}' not in configuration",
            hint="Configuration may be corrupted",
            exit_code=2,
        )

    # Remove symlink from repos/ directory
    link_path = project_root / "repos" / name
    if link_path.exists() or link_path.is_symlink():
        if not keep_link:
            info(f"Removing symlink: repos/{name}")
            link_path.unlink()
        else:
            warn(f"Keeping symlink: repos/{name}")

    # Remove from configuration
    config.resources[category] = [
        r for r in config.resources[category] if r.name != name
    ]
    save_config(project_root, config)

    success(f"Removed resource: {name}")
