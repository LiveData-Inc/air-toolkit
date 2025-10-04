"""View analysis findings."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.services.filesystem import get_project_root
from air.utils.console import error, info

console = Console()


@click.command()
@click.option("--all", "all_findings", is_flag=True, help="Show findings from all analyses")
@click.option("--severity", help="Filter by severity (high, medium, low)")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def findings(all_findings: bool, severity: str | None, output_format: str) -> None:
    """View analysis findings.

    \b
    Examples:
      air findings --all
      air findings --all --severity=high
      air findings --all --format=json
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    # Load findings from analysis directory
    analysis_dir = project_root / "analysis" / "reviews"
    if not analysis_dir.exists():
        if output_format == "json":
            print(json.dumps({"success": True, "findings": [], "count": 0}))
        else:
            info("No findings yet")
            console.print("\n[dim]Use 'air analyze' to generate findings[/dim]\n")
        return

    # Collect all findings
    all_findings_list = []

    for findings_file in analysis_dir.glob("*-findings.json"):
        try:
            findings_data = json.loads(findings_file.read_text())
            for finding in findings_data:
                # Add source file info
                finding["source"] = findings_file.stem.replace("-findings", "")
                all_findings_list.append(finding)
        except json.JSONDecodeError:
            # Skip corrupted files
            continue

    # Filter by severity if requested
    if severity:
        all_findings_list = [
            f for f in all_findings_list
            if f.get("severity", "").lower() == severity.lower()
        ]

    if output_format == "json":
        result = {
            "success": True,
            "findings": all_findings_list,
            "count": len(all_findings_list),
        }
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    if not all_findings_list:
        if severity:
            info(f"No findings with severity: {severity}")
        else:
            info("No findings yet")
        return

    # Create table
    table = Table(title="[bold]Analysis Findings[/bold]", show_header=True)
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Severity", style="yellow")
    table.add_column("Category", style="green")
    table.add_column("Description", style="white")

    for finding in all_findings_list:
        # Severity styling
        severity_val = finding.get("severity", "info")
        if severity_val == "high":
            sev_style = "red"
            sev_emoji = "⚠️"
        elif severity_val == "medium":
            sev_style = "yellow"
            sev_emoji = "⚡"
        elif severity_val == "low":
            sev_style = "blue"
            sev_emoji = "ℹ️"
        else:
            sev_style = "dim"
            sev_emoji = "·"

        # Get description
        desc = finding.get("reasoning", finding.get("type", "No description"))
        if len(desc) > 60:
            desc = desc[:57] + "..."

        table.add_row(
            finding.get("source", "unknown"),
            f"[{sev_style}]{sev_emoji} {severity_val.capitalize()}[/{sev_style}]",
            finding.get("category", "unknown"),
            desc,
        )

    console.print()
    console.print(table)

    # Summary
    high_count = sum(1 for f in all_findings_list if f.get("severity") == "high")
    medium_count = sum(1 for f in all_findings_list if f.get("severity") == "medium")
    low_count = sum(1 for f in all_findings_list if f.get("severity") == "low")

    console.print()
    console.print(
        f"[bold]Total:[/bold] {len(all_findings_list)} findings "
        f"([red]{high_count} high[/red], "
        f"[yellow]{medium_count} medium[/yellow], "
        f"[blue]{low_count} low[/blue])"
    )
    console.print()
