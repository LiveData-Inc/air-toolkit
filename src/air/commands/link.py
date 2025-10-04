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


def _interactive_link_add(
    project_root: Path,
    config: AirConfig,
    path: str | None,
    name: str | None,
    is_review: bool,
    is_develop: bool,
    resource_type: str | None,
) -> None:
    """Interactive mode for adding a linked resource."""
    from rich.console import Console
    from rich.prompt import Prompt, Confirm
    from rich.panel import Panel

    console = Console()

    console.print(Panel.fit(
        "[bold]Link Repository to AIR Project[/bold]\n"
        "Interactive setup - press Enter to accept defaults",
        border_style="blue"
    ))
    console.print()

    # Step 1: Path prompt
    if not path:
        while True:
            path = Prompt.ask("[cyan]Path to repository[/cyan]")
            if not path:
                console.print("[red]✗[/red] Path is required")
                continue

            # Expand and validate
            source_path = Path(path).expanduser().resolve()
            if not source_path.exists():
                console.print(f"[red]✗[/red] Path does not exist: {source_path}")
                continue
            if not source_path.is_dir():
                console.print(f"[red]✗[/red] Not a directory: {source_path}")
                continue

            break
    else:
        source_path = Path(path).expanduser().resolve()

    # Step 2: Name prompt (with default from folder name)
    suggested_name = source_path.name
    if not name:
        while True:
            resource_name = Prompt.ask(
                f"[cyan]Resource name[/cyan]",
                default=suggested_name
            )

            # Check uniqueness
            existing = config.find_resource(resource_name)
            if existing:
                console.print(f"[red]✗[/red] Resource '{resource_name}' already exists. Choose a different name.")
                suggested_name = f"{source_path.name}-2"  # Suggest alternative
                continue

            break
    else:
        resource_name = name
        # Validate uniqueness
        existing = config.find_resource(resource_name)
        if existing:
            error(
                f"Resource '{resource_name}' already linked",
                hint="Use a different name",
                exit_code=1,
            )

    # Step 3: Relationship prompt
    if not is_review and not is_develop:
        console.print()
        console.print("[cyan]Relationship:[/cyan]")
        console.print("  [bold]review[/bold] - Read-only (for assessment)")
        console.print("  [bold]develop[/bold] - Contribute back (for development)")
        console.print()

        relationship_choice = Prompt.ask(
            "Select relationship",
            choices=["review", "develop"],
            default="review"
        )
        is_review = relationship_choice == "review"
        is_develop = relationship_choice == "develop"

    category = "review" if is_review else "develop"
    relationship = (
        ResourceRelationship.REVIEW_ONLY
        if is_review
        else ResourceRelationship.DEVELOPER
    )

    # Step 4: Auto-detect type?
    if not resource_type:
        console.print()
        auto_detect = Confirm.ask(
            "[cyan]Auto-detect resource type?[/cyan]",
            default=False
        )

        if auto_detect:
            # Import classifier
            from air.services.classifier import classify_resource

            console.print("🔍 Analyzing repository...")
            try:
                result = classify_resource(source_path)
                console.print(
                    f"✓ Detected: [bold]{result.resource_type}[/bold] "
                    f"(confidence: {result.confidence:.0%})"
                )
                if result.detected_languages:
                    console.print(f"  Languages: {', '.join(result.detected_languages)}")
                if result.detected_frameworks:
                    console.print(f"  Frameworks: {', '.join(result.detected_frameworks)}")

                use_detected = Confirm.ask(
                    f"Use detected type '{result.resource_type}'?",
                    default=True
                )

                if use_detected:
                    resource_type = result.resource_type
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Classification failed: {e}")

        # Manual selection if not detected or rejected
        if not resource_type:
            console.print()
            resource_type = Prompt.ask(
                "[cyan]Resource type[/cyan]",
                choices=["implementation", "documentation", "library", "service"],
                default="implementation"
            )

    # Step 5: Confirmation
    console.print()
    console.print(Panel.fit(
        f"[bold]📋 Review Configuration:[/bold]\n\n"
        f"  Name:         [cyan]{resource_name}[/cyan]\n"
        f"  Path:         {source_path}\n"
        f"  Relationship: [cyan]{category}[/cyan] ({'read-only' if is_review else 'contribute'})\n"
        f"  Type:         [cyan]{resource_type}[/cyan]",
        border_style="green",
        title="Confirmation"
    ))
    console.print()

    if not Confirm.ask("Link this resource?", default=True):
        console.print("[yellow]✗[/yellow] Cancelled")
        return

    # Create the link
    link_dir = project_root / "repos"
    link_path = link_dir / resource_name

    if link_path.exists():
        error(
            f"Path already exists: {link_path}",
            hint="Remove existing file/link first",
            exit_code=1,
        )

    info(f"Creating symlink: repos/{resource_name} -> {source_path}")
    create_symlink(source_path, link_path)

    # Create resource entry
    resource = Resource(
        name=resource_name,
        path=str(source_path),
        type=ResourceType(resource_type),
        relationship=relationship,
        clone=False,
    )

    # Add to configuration
    config.add_resource(resource, category)
    save_config(project_root, config)

    success(f"✓ Linked {category} resource: {resource_name}")


@click.group()
def link() -> None:
    """Link repositories to assessment project.

    Manage resources linked to this AIR assessment project.
    """
    pass


@link.command("add")
@click.argument("name_path", required=False)
@click.option("--path", help="Path to repository")
@click.option("--name", help="Resource name (alias)")
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
    help="Link as developer resource",
)
@click.option(
    "--type",
    "resource_type",
    type=click.Choice(["implementation", "documentation", "library", "service"]),
    help="Resource type",
)
def link_add(
    name_path: str | None,
    path: str | None,
    name: str | None,
    is_review: bool,
    is_develop: bool,
    resource_type: str | None,
) -> None:
    """Add a linked resource.

    Interactive by default. Provide all options for non-interactive use.

    \b
    Examples:
      air link add                                    # Interactive mode
      air link add --path ~/repos/service-a --review  # Semi-interactive
      air link add --path ~/repos/service-a --name service-a --review --type service  # Non-interactive

      # Deprecated (still works, will be removed in v0.5.0):
      air link add service-a:~/repos/service-a --review
    """
    # Validate project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    # Load configuration early for validation
    config = load_config(project_root)

    # Handle deprecated NAME:PATH format
    if name_path and ":" in name_path:
        warn("⚠️  NAME:PATH format is deprecated and will be removed in v0.5.0")
        warn("   Use: air link add --path PATH --name NAME")
        parsed_name, parsed_path = parse_name_path(name_path)
        # Override with parsed values if not provided via options
        if not path:
            path = parsed_path
        if not name:
            name = parsed_name

    # Default to review mode if neither flag specified
    if not is_review and not is_develop:
        is_review = True

    # Detect if we need interactive mode
    # We need interactive if missing path OR name
    # Note: relationship defaults to review, resource_type defaults to "implementation"
    needs_interactive = not all([path, name])

    if needs_interactive:
        # Enter interactive mode
        return _interactive_link_add(
            project_root, config, path, name, is_review, is_develop, resource_type
        )

    # Non-interactive mode: validate all required args
    if not path:
        error("--path is required in non-interactive mode", exit_code=1)
    if not name:
        error("--name is required in non-interactive mode", exit_code=1)

    # Determine mode
    if is_review and is_develop:
        error(
            "Cannot specify both --review and --develop",
            hint="Choose one mode for the resource",
            exit_code=1,
        )

    # Note: is_review is already set to True as default above if neither flag was specified
    category = "review" if is_review else "develop"
    relationship = (
        ResourceRelationship.REVIEW_ONLY
        if is_review
        else ResourceRelationship.DEVELOPER
    )

    # Use provided values
    path_str = path
    resource_name = name
    res_type = resource_type or "implementation"

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

    # Check if resource already exists
    existing = config.find_resource(resource_name)
    if existing:
        error(
            f"Resource '{resource_name}' already linked",
            hint="Use a different name or remove the existing resource first",
            exit_code=1,
        )

    # Create symlink in repos/ directory
    # Note: Both review and develop resources go in repos/
    # The difference is the relationship (REVIEW_ONLY vs DEVELOPER)
    link_dir = project_root / "repos"
    link_path = link_dir / resource_name

    if link_path.exists():
        error(
            f"Path already exists: {link_path}",
            hint="Remove existing file/link first",
            exit_code=1,
        )

    info(f"Creating symlink: repos/{resource_name} -> {source_path}")
    create_symlink(source_path, link_path)

    # Create resource entry
    resource = Resource(
        name=resource_name,
        path=str(source_path),
        type=ResourceType(res_type),
        relationship=relationship,
        clone=False,
    )

    # Add to configuration
    config.add_resource(resource, category)
    save_config(project_root, config)

    success(f"Linked {category} resource: {resource_name}")


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
