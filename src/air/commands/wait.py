"""Wait for background agents to complete."""

import json
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.live import Live
from rich.table import Table

from air.services.agent_manager import list_agents
from air.utils.console import info, success

console = Console()


@click.command()
@click.option("--agents", help="Comma-separated agent IDs to wait for")
@click.option("--all", "wait_all", is_flag=True, help="Wait for all running agents")
@click.option("--timeout", type=int, help="Timeout in seconds")
@click.option("--interval", type=int, default=5, help="Check interval in seconds (default: 5)")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def wait(
    agents: str | None,
    wait_all: bool,
    timeout: int | None,
    interval: int,
    output_format: str,
) -> None:
    """Wait for background agents to complete.

    \b
    Examples:
      air wait --all
      air wait --agents worker-1,worker-2
      air wait --all --timeout=300
    """
    if not agents and not wait_all:
        console.print("[red]Error: Specify --agents or --all[/red]")
        sys.exit(1)

    # Parse agent IDs if specified
    agent_ids = set(agents.split(",")) if agents else None

    # Track elapsed time
    elapsed = 0
    start_time = time.time()

    if output_format == "human":
        info("Waiting for agents to complete...")
        if timeout:
            info(f"Timeout: {timeout}s")

    try:
        while True:
            # Get current agent list
            agent_list = list_agents()

            # Filter to agents we're waiting for
            if agent_ids:
                waiting_for = [a for a in agent_list if a["id"] in agent_ids]
            else:
                waiting_for = agent_list

            # Check if any are still running
            running = [a for a in waiting_for if a.get("status") == "running"]

            if not running:
                # All done!
                if output_format == "json":
                    result = {
                        "success": True,
                        "message": "All agents complete",
                        "elapsed": elapsed,
                        "agents": waiting_for,
                    }
                    print(json.dumps(result, indent=2))
                else:
                    success(f"All agents complete (elapsed: {elapsed}s)")

                    # Show final status
                    complete = sum(1 for a in waiting_for if a.get("status") == "complete")
                    failed = sum(1 for a in waiting_for if a.get("status") == "failed")

                    if failed > 0:
                        console.print(f"\n[yellow]⚠️  {failed} agent(s) failed[/yellow]")
                        sys.exit(1)
                    else:
                        console.print(f"\n[green]✓ {complete} agent(s) completed successfully[/green]")

                sys.exit(0)

            # Check timeout
            if timeout and elapsed >= timeout:
                if output_format == "json":
                    result = {
                        "success": False,
                        "error": "Timeout exceeded",
                        "elapsed": elapsed,
                        "still_running": [a["id"] for a in running],
                    }
                    print(json.dumps(result, indent=2))
                else:
                    console.print(f"\n[red]✗ Timeout exceeded ({elapsed}s)[/red]")
                    console.print(f"[dim]Still running: {', '.join(a['id'] for a in running)}[/dim]")
                sys.exit(1)

            # Wait interval
            if output_format == "human":
                console.print(
                    f"[dim]Waiting for {len(running)} agent(s): "
                    f"{', '.join(a['id'] for a in running[:3])}"
                    f"{'...' if len(running) > 3 else ''}[/dim]",
                    end="\r",
                )

            time.sleep(interval)
            elapsed = int(time.time() - start_time)

    except KeyboardInterrupt:
        if output_format == "json":
            result = {"success": False, "error": "Interrupted by user", "elapsed": elapsed}
            print(json.dumps(result, indent=2))
        else:
            console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(130)
