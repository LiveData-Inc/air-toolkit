"""Link repositories to assessment project."""

import json
from pathlib import Path

import click
from rich.console import Console

from air.core.models import AirConfig, Resource, ResourceRelationship, ResourceType
from air.services.filesystem import create_symlink, get_project_root
from air.utils.console import error, info, success, warn
from air.utils.tables import render_resource_table

console = Console()


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

    # Step 2: Relationship prompt
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

    # Step 3: Auto-classify (opt-out, default: YES)
    tech_stack = None
    if not resource_type:
        console.print()
        auto_detect = Confirm.ask(
            "[cyan]Auto-classify resource?[/cyan]",
            default=True  # Changed to opt-out
        )

        if auto_detect:
            # Import classifier
            from air.services.classifier import classify_resource

            console.print("🔍 Analyzing repository...")
            try:
                result = classify_resource(source_path)
                tech_stack = result.technology_stack
                console.print(
                    f"✓ Detected: [bold]{result.resource_type}[/bold]"
                    + (f" ({result.technology_stack})" if result.technology_stack else "")
                    + f" (confidence: {result.confidence:.0%})"
                )
                if result.detected_languages:
                    console.print(f"  Languages: {', '.join(result.detected_languages)}")
                if result.detected_frameworks:
                    console.print(f"  Frameworks: {', '.join(result.detected_frameworks)}")

                use_detected = Confirm.ask(
                    f"Use detected classification?",
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
                choices=["library", "documentation", "service"],
                default="library"  # Changed default from "implementation"
            )

    # Step 4: Confirmation
    console.print()
    tech_display = f" ({tech_stack})" if tech_stack else ""
    console.print(Panel.fit(
        f"[bold]📋 Review Configuration:[/bold]\n\n"
        f"  Name:         [cyan]{resource_name}[/cyan]\n"
        f"  Path:         {source_path}\n"
        f"  Relationship: [cyan]{category}[/cyan] ({'read-only' if is_review else 'contribute'})\n"
        f"  Type:         [cyan]{resource_type}{tech_display}[/cyan]",
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
        technology_stack=tech_stack,
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
@click.argument("path", required=True, type=click.Path(exists=False))
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
    type=click.Choice(["library", "documentation", "service"]),
    help="Resource type",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Interactive mode - prompt for all options",
)
def link_add(
    path: str,
    name: str | None,
    is_review: bool,
    is_develop: bool,
    resource_type: str | None,
    interactive: bool,
) -> None:
    """Add a linked resource.

    By default, links immediately without prompting. Use -i for interactive mode.

    \b
    Examples:
      air link add ~/repos/service-a                    # Fast: uses folder name, auto-detects type
      air link add ~/repos/service-a -i                 # Interactive: prompts for all options
      air link add ~/repos/service-a --name my-service  # Custom name, auto-detects type
      air link add ~/repos/service-a --name service --review --type library  # Explicit values
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

    # Default to review mode if neither flag specified
    if not is_review and not is_develop:
        is_review = True

    # Determine if we should use interactive mode
    # Interactive if: -i flag OR no name provided AND no other args
    if interactive:
        # User explicitly requested interactive mode
        return _interactive_link_add(
            project_root, config, path, name, is_review, is_develop, resource_type
        )

    # Non-interactive mode: validate path and use defaults/provided values
    source_path = Path(path).expanduser().resolve()

    if not source_path.exists():
        error(
            f"Path does not exist: {path}",
            hint="Provide a valid directory path",
            exit_code=1,
        )

    if not source_path.is_dir():
        error(
            f"Path is not a directory: {path}",
            hint="Resource must be a directory",
            exit_code=1,
        )

    # If no name provided, use folder name as default
    resource_name = name or source_path.name

    # Determine mode
    if is_review and is_develop:
        error(
            "Cannot specify both --review and --develop",
            hint="Choose one mode for the resource",
            exit_code=1,
        )

    category = "review" if is_review else "develop"
    relationship = (
        ResourceRelationship.REVIEW_ONLY
        if is_review
        else ResourceRelationship.DEVELOPER
    )

    # Auto-classify if no type provided
    tech_stack = None
    if not resource_type:
        from air.services.classifier import classify_resource

        info("Auto-detecting resource type...")
        result = classify_resource(source_path)
        resource_type = result.resource_type.value
        tech_stack = result.technology_stack
        info(f"Detected: {resource_type} ({tech_stack})")

    res_type = resource_type

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
        technology_stack=tech_stack,  # From auto-classification
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
        console.print()
        render_resource_table(
            review_resources,
            project_root,
            title="Review Resources (Read-Only)",
            title_style="cyan",
            name_style="cyan",
        )

    if collab_resources:
        console.print()
        render_resource_table(
            collab_resources,
            project_root,
            title="Collaborative Resources",
            title_style="green",
            name_style="green",
        )

    total = len(review_resources) + len(collab_resources)
    console.print(f"\n[dim]Total: {total} resources[/dim]")


def _remove_resource(
    project_root: Path,
    config: AirConfig,
    resource_name: str,
    keep_link: bool,
) -> None:
    """Remove a resource from the project.

    Args:
        project_root: Project root directory
        config: Project configuration
        resource_name: Name of resource to remove
        keep_link: Whether to keep the symlink
    """
    # Find resource
    resource = config.find_resource(resource_name)
    if not resource:
        error(
            f"Resource not found: {resource_name}",
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
            f"Resource '{resource_name}' not in configuration",
            hint="Configuration may be corrupted",
            exit_code=2,
        )

    # Remove symlink from repos/ directory
    link_path = project_root / "repos" / resource_name
    if link_path.exists() or link_path.is_symlink():
        if not keep_link:
            info(f"Removing symlink: repos/{resource_name}")
            link_path.unlink()
        else:
            warn(f"Keeping symlink: repos/{resource_name}")

    # Remove from configuration
    config.resources[category] = [
        r for r in config.resources[category] if r.name != resource_name
    ]
    save_config(project_root, config)

    success(f"Removed resource: {resource_name}")


@link.command("remove")
@click.argument("name", required=False)
@click.option(
    "--keep-link",
    is_flag=True,
    help="Keep symlink, only remove from config",
)
@click.option(
    "-i",
    "--interactive",
    is_flag=True,
    help="Interactive mode - select from numbered list",
)
@click.pass_context
def link_remove(ctx: click.Context, name: str | None, keep_link: bool, interactive: bool) -> None:
    """Remove a linked resource.

    \b
    Examples:
      air link remove service-a              # Remove by name
      air link remove docs --keep-link       # Remove but keep symlink
      air link remove -i                     # Interactive selection
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    config = load_config(project_root)

    # Interactive mode
    if interactive:
        from rich.prompt import Prompt, Confirm
        from rich.table import Table

        # Get all resources
        all_resources = []
        for category in ["review", "develop"]:
            for resource in config.resources.get(category, []):
                all_resources.append((category, resource))

        if not all_resources:
            info("No resources linked")
            console.print("\n[dim]Use 'air link add' to link resources[/dim]")
            return

        # Display numbered list
        console.print("\n[bold]Linked Resources:[/bold]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=4)
        table.add_column("Name", style="cyan")
        table.add_column("Type", style="yellow")
        table.add_column("Relationship", style="green")
        table.add_column("Path", style="dim")

        for i, (category, resource) in enumerate(all_resources, 1):
            relationship = "review" if category == "review" else "develop"
            table.add_row(
                str(i),
                resource.name,
                resource.type.value,
                relationship,
                resource.path,
            )

        console.print(table)
        console.print()

        # Get selection
        try:
            selection = Prompt.ask(
                "[cyan]Select resource to remove (number or 'q' to quit)[/cyan]",
                default="q"
            )

            if selection.lower() == "q":
                console.print("[yellow]✗[/yellow] Cancelled")
                return

            idx = int(selection) - 1
            if idx < 0 or idx >= len(all_resources):
                error("Invalid selection", exit_code=1)

            category, resource = all_resources[idx]

            # Confirm removal
            console.print(f"\n[yellow]⚠[/yellow]  Remove resource: [bold]{resource.name}[/bold]")
            console.print(f"   Type: {resource.type.value}")
            console.print(f"   Path: {resource.path}\n")

            if not Confirm.ask("Confirm removal?", default=False):
                console.print("[yellow]✗[/yellow] Cancelled")
                return

            # Remove the resource
            _remove_resource(project_root, config, resource.name, keep_link)

        except ValueError:
            error("Invalid input - must be a number", exit_code=1)
        except KeyboardInterrupt:
            console.print("\n[yellow]✗[/yellow] Cancelled")
            return

    else:
        # Non-interactive mode - name required
        if not name:
            console.print("[red]Error:[/red] Missing argument 'NAME'.\n")
            console.print(ctx.get_help())
            ctx.exit(1)

        _remove_resource(project_root, config, name, keep_link)
