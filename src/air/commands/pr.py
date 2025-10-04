"""Create pull request for collaborative resource."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.core.models import AirConfig, ResourceRelationship
from air.services.filesystem import get_project_root
from air.services.pr_generator import (
    check_gh_cli_available,
    copy_contributions_to_resource,
    create_pr_with_gh,
    detect_changes,
    generate_pr_metadata,
    git_create_branch_and_commit,
    is_git_repository,
)
from air.utils.errors import (
    GitHubCLIError,
    ProjectNotFoundError,
    ResourceError,
    ResourceNotFoundError,
    display_error,
)
from air.utils.progress import ProgressTracker, show_status

console = Console()


@click.command()
@click.argument("resource", required=False)
@click.option(
    "--base",
    default="main",
    help="Base branch for PR (default: main)",
)
@click.option(
    "--title",
    help="Custom PR title",
)
@click.option(
    "--body",
    help="Custom PR body",
)
@click.option(
    "--draft",
    is_flag=True,
    help="Create as draft PR",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be done without doing it",
)
def pr(
    resource: str | None,
    base: str,
    title: str | None,
    body: str | None,
    draft: bool,
    dry_run: bool,
) -> None:
    """Create pull request for collaborative resource.

    Workflow:
      1. Detect changes in contributions/{resource}/
      2. Generate PR title and body from recent tasks
      3. Copy files to resource repository
      4. Create git branch and commit
      5. Push and create PR via gh CLI

    \b
    Examples:
      air pr docs                    # Create PR for docs resource
      air pr docs --draft            # Create draft PR
      air pr docs --title="Add API docs"
      air pr --dry-run               # See what would happen
    """
    # Get project root
    try:
        project_root = get_project_root()
        if project_root is None:
            raise ProjectNotFoundError(Path.cwd())
    except ProjectNotFoundError as e:
        display_error(e)
        sys.exit(1)

    # Load config
    config_path = project_root / "air-config.json"
    try:
        with open(config_path) as f:
            config = AirConfig.model_validate_json(f.read())
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load config: {e}")
        sys.exit(1)

    # If no resource specified, list collaborative resources with contributions
    if not resource:
        _list_collaborative_resources(project_root, config)
        return

    # Find resource
    target_resource = config.find_resource(resource)
    if not target_resource:
        all_resources = [r.name for r in config.get_all_resources()]
        error = ResourceNotFoundError(resource, all_resources)
        display_error(error)
        sys.exit(1)

    # Validate resource is collaborative
    if target_resource.relationship != ResourceRelationship.DEVELOPER:
        error = ResourceError(
            f"Resource '{resource}' is not a collaborative resource",
            resource_name=resource,
            suggestion="Use --develop flag when adding resource with 'air link add'",
        )
        display_error(error)
        sys.exit(1)

    # Check resource path exists
    resource_path = Path(target_resource.path)
    if not resource_path.exists():
        error = PathError(
            f"Resource path not found: {resource_path}",
            path=resource_path,
            suggestion="The symlink or directory may have been removed. Run 'air validate' to check project structure",
        )
        display_error(error)
        sys.exit(1)

    # Check resource is a git repository
    if not is_git_repository(resource_path):
        error = ResourceError(
            f"Resource '{resource}' is not a git repository",
            resource_name=resource,
            suggestion=f"Resource path must be a git repository: {resource_path}",
        )
        display_error(error)
        sys.exit(1)

    # Detect changes
    contributions_dir = project_root / "contributions"
    changes = detect_changes(contributions_dir, resource)

    if not changes.has_changes:
        console.print(f"[yellow]⚠[/yellow] No contributions found for '{resource}'")
        console.print(f"[dim]💡 Add files to: {contributions_dir / resource}/[/dim]")
        sys.exit(0)

    # Check gh CLI is available
    if not dry_run and not check_gh_cli_available():
        error = GitHubCLIError("GitHub CLI (gh) is not installed or not authenticated")
        display_error(error)
        sys.exit(1)

    # Generate PR metadata
    tasks_dir = project_root / ".air/tasks"
    pr_metadata = generate_pr_metadata(resource, tasks_dir, title, body)

    # Display what will be done
    if dry_run:
        console.print("[yellow]⚠[/yellow] Dry run mode - no changes will be made\n")

    console.print(f"[bold]Creating PR for: {resource}[/bold]\n")
    console.print(f"  Branch: [cyan]{pr_metadata.branch_name}[/cyan]")
    console.print(f"  Base: [cyan]{base}[/cyan]")
    console.print(f"  Title: {pr_metadata.title}")
    console.print(f"  Files: {len(changes.changed_files)}")
    console.print(f"  Draft: {'Yes' if draft else 'No'}")

    if dry_run:
        console.print("\n[dim]Files to be contributed:[/dim]")
        for file_path in changes.changed_files[:10]:
            rel_path = file_path.relative_to(changes.contribution_dir)
            console.print(f"  • {rel_path}")
        if len(changes.changed_files) > 10:
            console.print(f"  ... and {len(changes.changed_files) - 10} more")
        sys.exit(0)

    # Execute PR workflow with progress tracking
    console.print()
    with ProgressTracker("Creating pull request", total_steps=4) as progress:
        # Step 1: Copy contributions
        progress.step("Copying files to resource")
        try:
            copied_files = copy_contributions_to_resource(
                changes.contribution_dir, resource_path, changes.changed_files
            )
        except Exception as e:
            console.print(f"\n[red]✗[/red] Failed to copy files: {e}")
            sys.exit(1)

        # Step 2: Create branch
        progress.step("Creating git branch")
        success, error = git_create_branch_and_commit(
            resource_path, pr_metadata.branch_name, pr_metadata.title, copied_files
        )
        if not success:
            console.print(f"\n[red]✗[/red] Git operation failed: {error}")
            sys.exit(1)

        # Step 3: Push changes
        progress.step("Pushing to remote")
        # (push is part of git_create_branch_and_commit)

        # Step 4: Create PR
        progress.step("Creating pull request")
        success, result = create_pr_with_gh(
            resource_path, pr_metadata.branch_name, pr_metadata.title, pr_metadata.body, draft, base
        )

    console.print()
    if success:
        show_status("Pull request created successfully!", "success")
        console.print(f"\n[bold]{result}[/bold]")
    else:
        show_status(f"Failed to create PR: {result}", "error")
        sys.exit(1)


def _list_collaborative_resources(project_root: Path, config: AirConfig) -> None:
    """List collaborative resources with contribution status."""
    # Get collaborative resources
    collab_resources = [
        r for r in config.get_all_resources() if r.relationship == ResourceRelationship.DEVELOPER
    ]

    if not collab_resources:
        console.print("[yellow]⚠[/yellow] No collaborative resources found")
        console.print("[dim]💡 Add with: air link add --path PATH --name NAME --develop[/dim]")
        return

    console.print("[bold]Collaborative Resources:[/bold]\n")

    contributions_dir = project_root / "contributions"
    table = Table(show_header=True)
    table.add_column("Resource")
    table.add_column("Type")
    table.add_column("Contributions")
    table.add_column("Status")

    for res in collab_resources:
        changes = detect_changes(contributions_dir, res.name)
        status = "✓ Ready" if changes.has_changes else "○ No changes"
        file_count = len(changes.changed_files) if changes.has_changes else 0

        table.add_row(res.name, res.type, str(file_count), status)

    console.print(table)
    console.print("\n[dim]💡 Run 'air pr RESOURCE' to create a pull request[/dim]")
