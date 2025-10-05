"""Cache management commands."""

import json
from pathlib import Path

import click
from rich.table import Table

from air.services.cache_manager import CacheManager
from air.services.filesystem import get_project_root
from air.utils.console import console, error, info, success


@click.group()
def cache() -> None:
    """Manage analysis cache."""
    pass


@cache.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text", help="Output format")
def status(format: str) -> None:
    """Show cache statistics.

    \b
    Examples:
      air cache status                  # Show cache stats
      air cache status --format=json    # JSON output
    """
    # Verify we're in an AIR project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=project_root / ".air" / "cache")

    # Get stats
    stats = cache_manager.get_stats()

    if format == "json":
        # JSON output
        console.print(json.dumps(stats.to_dict(), indent=2))
    else:
        # Rich table output
        table = Table(title="Cache Statistics", show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Entries", str(stats.total_entries))
        table.add_row("Cache Size", f"{stats.cache_size_mb:.2f} MB")
        table.add_row("Cache Hits", str(stats.hit_count))
        table.add_row("Cache Misses", str(stats.miss_count))
        table.add_row("Hit Rate", f"{stats.hit_rate:.1f}%")

        if stats.last_cleared:
            table.add_row("Last Cleared", stats.last_cleared.strftime("%Y-%m-%d %H:%M:%S"))
        else:
            table.add_row("Last Cleared", "Never")

        console.print(table)

        # Show interpretation
        if stats.total_entries == 0:
            info("\nCache is empty. Run 'air analyze' to populate cache.")
        elif stats.hit_rate >= 80:
            success(f"\n✨ Excellent hit rate ({stats.hit_rate:.1f}%)!")
        elif stats.hit_rate >= 50:
            info(f"\n✓ Good hit rate ({stats.hit_rate:.1f}%)")
        elif stats.hit_count + stats.miss_count > 0:
            info(f"\nHit rate: {stats.hit_rate:.1f}% - Cache is warming up")


@cache.command()
@click.confirmation_option(
    prompt="Are you sure you want to clear the cache? This cannot be undone."
)
def clear() -> None:
    """Clear all cached analysis results.

    \b
    Examples:
      air cache clear    # Clears all cached data (prompts for confirmation)
    """
    # Verify we're in an AIR project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=project_root / ".air" / "cache")

    # Get stats before clearing
    stats = cache_manager.get_stats()
    entries_before = stats.total_entries
    size_before = stats.cache_size_mb

    # Clear cache
    info("Clearing cache...")
    cache_manager.clear_all()

    success(f"Cache cleared: {entries_before} entries ({size_before:.2f} MB) removed")
