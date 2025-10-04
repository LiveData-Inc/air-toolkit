"""Create pull request for collaborative resource."""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.core.models import AssessmentConfig, ResourceRelationship
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
    project_root = get_project_root()
    if project_root is None:
        console.print("[red]✗[/red] Not in an AIR project")
        console.print("[dim]💡 Hint: Run 'air init' to create a project[/dim]")
        sys.exit(1)

    # Load config
    config_path = project_root / "air-config.json"
    try:
        with open(config_path) as f:
            config = AssessmentConfig.model_validate_json(f.read())
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
        console.print(f"[red]✗[/red] Resource '{resource}' not found")
        sys.exit(1)

    # Validate resource is collaborative
    if target_resource.relationship != ResourceRelationship.CONTRIBUTOR:
        console.print(f"[red]✗[/red] Resource '{resource}' is not a collaborative resource")
        console.print("[dim]💡 Hint: Use --collaborate when adding resource[/dim]")
        sys.exit(1)

    # Check resource is a git repository
    resource_path = Path(target_resource.path)
    if not is_git_repository(resource_path):
        console.print(f"[red]✗[/red] Resource '{resource}' is not a git repository")
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
        console.print("[red]✗[/red] GitHub CLI (gh) is not installed or not authenticated")
        console.print("[dim]💡 Install: brew install gh && gh auth login[/dim]")
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

    # Copy contributions
    console.print("\n[blue]ℹ[/blue] Copying contributions...")
    try:
        copied_files = copy_contributions_to_resource(
            changes.contribution_dir, resource_path, changes.changed_files
        )
        console.print(f"[green]✓[/green] Copied {len(copied_files)} files")
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to copy files: {e}")
        sys.exit(1)

    # Create branch and commit
    console.print("[blue]ℹ[/blue] Creating branch and committing...")
    success, error = git_create_branch_and_commit(
        resource_path, pr_metadata.branch_name, pr_metadata.title, copied_files
    )
    if not success:
        console.print(f"[red]✗[/red] Git operation failed: {error}")
        sys.exit(1)
    console.print(f"[green]✓[/green] Committed changes to {pr_metadata.branch_name}")

    # Create PR
    console.print("[blue]ℹ[/blue] Creating pull request...")
    success, result = create_pr_with_gh(
        resource_path, pr_metadata.branch_name, pr_metadata.title, pr_metadata.body, draft, base
    )

    if success:
        console.print(f"[green]✓[/green] Pull request created successfully!")
        console.print(f"\n[bold]{result}[/bold]")
    else:
        console.print(f"[red]✗[/red] Failed to create PR: {result}")
        sys.exit(1)


def _list_collaborative_resources(project_root: Path, config: AssessmentConfig) -> None:
    """List collaborative resources with contribution status."""
    # Get collaborative resources
    collab_resources = [
        r for r in config.get_all_resources() if r.relationship == ResourceRelationship.CONTRIBUTOR
    ]

    if not collab_resources:
        console.print("[yellow]⚠[/yellow] No collaborative resources found")
        console.print("[dim]💡 Add with: air link add NAME:PATH --collaborate[/dim]")
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
