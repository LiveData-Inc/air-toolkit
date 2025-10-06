"""Classify resources by type."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.core.models import AirConfig, Resource, ResourceType
from air.services.classifier import classify_resource
from air.services.filesystem import get_config_path, get_project_root

console = Console()


@click.command()
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed classification information",
)
@click.option(
    "--update",
    "-u",
    is_flag=True,
    help="Update air-config.json with detected resource types",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
@click.argument("resource_name", required=False)
def classify(
    verbose: bool, update: bool, output_format: str, resource_name: str | None
) -> None:
    """Classify resources by type.

    Analyzes linked resources and classifies them by detecting:
      - Programming languages (Python, JavaScript, Go, etc.)
      - Frameworks (Django, React, Spring, etc.)
      - Resource type (library, documentation, service)

    \b
    Examples:
      air classify                    # Classify all resources
      air classify myapp              # Classify specific resource
      air classify --verbose          # Show detection details
      air classify --update           # Update air-config.json with results
      air classify --format=json      # JSON output
    """
    # Get project root
    project_root = get_project_root()
    if project_root is None:
        console.print("[red]✗[/red] Not in an AIR project")
        console.print("[dim]💡 Hint: Run 'air init' to create a project[/dim]")
        sys.exit(1)

    # Load config
    config_path = get_config_path(project_root)
    try:
        with open(config_path) as f:
            config = AirConfig.model_validate_json(f.read())
    except Exception as e:
        console.print(f"[red]✗[/red] Failed to load config: {e}")
        sys.exit(1)

    # Get resources to classify
    resources = config.get_all_resources()
    if not resources:
        if output_format == "json":
            print(json.dumps({"resources": [], "message": "No linked resources"}))
        else:
            console.print("[yellow]⚠[/yellow] No linked resources to classify")
            console.print("[dim]💡 Hint: Run 'air link add' to link resources[/dim]")
        sys.exit(0)

    # Filter by resource name if specified
    if resource_name:
        resource = config.find_resource(resource_name)
        if not resource:
            console.print(f"[red]✗[/red] Resource '{resource_name}' not found")
            sys.exit(1)
        resources = [resource]

    # Classify each resource
    results = []
    updated_count = 0

    for resource in resources:
        resource_path = Path(resource.path)

        # Check if resource path exists
        if not resource_path.exists():
            console.print(
                f"[red]✗[/red] Resource '{resource.name}' path not found: {resource_path}"
            )
            console.print(
                f"[dim]💡 Hint: The symlink or directory may have been removed. "
                f"Run 'air validate' to check project structure[/dim]"
            )
            sys.exit(1)

        result = classify_resource(resource_path)

        results.append(
            {
                "name": resource.name,
                "path": str(resource.path),
                "current_type": resource.type,
                "detected_type": result.resource_type,
                "confidence": result.confidence,
                "languages": result.detected_languages,
                "frameworks": result.detected_frameworks,
                "reasoning": result.reasoning,
                "updated": False,
            }
        )

        # Update if requested and type changed
        if update and resource.type != result.resource_type:
            resource.type = result.resource_type
            updated_count += 1
            results[-1]["updated"] = True

    # Save updated config if changes were made
    if update and updated_count > 0:
        try:
            with open(config_path, "w") as f:
                f.write(config.model_dump_json(indent=2))
                f.write("\n")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to update config: {e}")
            sys.exit(1)

    # Output results
    if output_format == "json":
        output = {
            "total": len(results),
            "updated": updated_count if update else 0,
            "resources": results,
        }
        print(json.dumps(output, indent=2))
    else:
        _display_results(results, verbose, update, updated_count)


def _display_results(
    results: list[dict], verbose: bool, update: bool, updated_count: int
) -> None:
    """Display classification results in human-readable format."""
    console.print(f"\n[bold]Classified {len(results)} resource(s)[/bold]\n")

    for result in results:
        # Status emoji
        if result["confidence"] >= 0.8:
            confidence_emoji = "✅"
        elif result["confidence"] >= 0.5:
            confidence_emoji = "⚠️"
        else:
            confidence_emoji = "❓"

        # Type changed indicator
        type_changed = result["current_type"] != result["detected_type"]
        change_indicator = " [yellow]→ CHANGED[/yellow]" if result.get("updated") else ""

        console.print(f"{confidence_emoji} [bold]{result['name']}[/bold]{change_indicator}")

        if type_changed and not result.get("updated"):
            console.print(
                f"   Current: [dim]{result['current_type']}[/dim] → Detected: [cyan]{result['detected_type']}[/cyan]"
            )
        else:
            console.print(f"   Type: [cyan]{result['detected_type']}[/cyan]")

        console.print(f"   Confidence: {result['confidence']:.0%}")

        if verbose:
            if result["languages"]:
                console.print(f"   Languages: {', '.join(result['languages'])}")
            if result["frameworks"]:
                console.print(f"   Frameworks: {', '.join(result['frameworks'])}")
            console.print(f"   Reasoning: {result['reasoning']}")
            console.print(f"   Path: [dim]{result['path']}[/dim]")

        console.print()

    if update:
        if updated_count > 0:
            console.print(
                f"[green]✓[/green] Updated {updated_count} resource type(s) in air-config.json"
            )
        else:
            console.print("[dim]No changes needed - all types already correct[/dim]")
    elif any(r["current_type"] != r["detected_type"] for r in results):
        console.print(
            "[dim]💡 Run with --update to apply detected types to air-config.json[/dim]"
        )
