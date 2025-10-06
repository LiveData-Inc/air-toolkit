"""View analysis findings."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.services.filesystem import get_project_root
from air.services.html_report_generator import generate_findings_html
from air.utils.console import error, info, success

console = Console()


def _get_severity_style(severity: str) -> tuple[str, str]:
    """Get emoji and style for severity level.

    Args:
        severity: Severity level

    Returns:
        Tuple of (emoji, style)
    """
    if severity in ["critical", "high"]:
        return "⚠️", "red"
    elif severity == "medium":
        return "⚡", "yellow"
    elif severity == "low":
        return "ℹ️", "blue"
    else:
        return "·", "dim"


def _show_summary_counts(findings_list: list) -> None:
    """Show summary counts at bottom of output.

    Args:
        findings_list: List of findings
    """
    critical_count = sum(1 for f in findings_list if f.get("severity") == "critical")
    high_count = sum(1 for f in findings_list if f.get("severity") == "high")
    medium_count = sum(1 for f in findings_list if f.get("severity") == "medium")
    low_count = sum(1 for f in findings_list if f.get("severity") == "low")

    console.print()
    console.print(
        f"[bold]Total:[/bold] {len(findings_list)} findings "
        f"([red]{critical_count + high_count} critical/high[/red], "
        f"[yellow]{medium_count} medium[/yellow], "
        f"[blue]{low_count} low[/blue])"
    )
    console.print()


def _show_summary(findings_list: list) -> None:
    """Show summary statistics view.

    Args:
        findings_list: List of findings
    """
    console.print()
    console.print("[bold cyan]Findings Summary[/bold cyan]")
    console.print()

    # Count by category
    by_category = {}
    for finding in findings_list:
        cat = finding.get("category", "unknown")
        by_category[cat] = by_category.get(cat, 0) + 1

    # Count by severity
    by_severity = {}
    for finding in findings_list:
        sev = finding.get("severity", "info")
        by_severity[sev] = by_severity.get(sev, 0) + 1

    # Count by source
    by_source = {}
    for finding in findings_list:
        src = finding.get("source", "unknown")
        by_source[src] = by_source.get(src, 0) + 1

    # Display totals
    console.print(f"[bold]Total Findings:[/bold] {len(findings_list)}")
    console.print()

    # Severity breakdown
    console.print("[bold]By Severity:[/bold]")
    for sev in ["critical", "high", "medium", "low", "info"]:
        count = by_severity.get(sev, 0)
        if count > 0:
            emoji, style = _get_severity_style(sev)
            console.print(f"  [{style}]{emoji} {sev.capitalize()}:[/{style}] {count}")
    console.print()

    # Category breakdown
    console.print("[bold]By Category:[/bold]")
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {cat}: {count}")
    console.print()

    # Source breakdown
    console.print("[bold]By Source:[/bold]")
    for src, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        console.print(f"  {src}: {count}")
    console.print()


def _show_details(findings_list: list) -> None:
    """Show detailed findings view.

    Args:
        findings_list: List of findings
    """
    console.print()
    console.print("[bold cyan]Detailed Findings[/bold cyan]")
    console.print()

    for i, finding in enumerate(findings_list, 1):
        # Header
        severity_val = finding.get("severity", "info")
        emoji, style = _get_severity_style(severity_val)

        console.print(f"[bold]{i}. [{style}]{emoji} {severity_val.upper()}[/{style}][/bold]")

        # Title
        title = finding.get("title", finding.get("type", "No title"))
        console.print(f"   [bold]{title}[/bold]")

        # Category and source
        category = finding.get("category", "unknown")
        source = finding.get("source", "unknown")
        console.print(f"   [dim]Category: {category} | Source: {source}[/dim]")

        # Location
        location = finding.get("location")
        line_number = finding.get("line_number")
        if location:
            if line_number:
                console.print(f"   [cyan]Location: {location}:{line_number}[/cyan]")
            else:
                console.print(f"   [cyan]Location: {location}[/cyan]")

        # Description
        description = finding.get("description", finding.get("reasoning", ""))
        if description:
            console.print(f"   {description}")

        # Suggestion
        suggestion = finding.get("suggestion")
        if suggestion:
            console.print(f"   [green]💡 Suggestion:[/green] {suggestion}")

        # Metadata
        metadata = finding.get("metadata")
        if metadata and isinstance(metadata, dict):
            details = ", ".join(f"{k}={v}" for k, v in metadata.items() if k != "match")
            if details:
                console.print(f"   [dim]Details: {details}[/dim]")

        console.print()

    _show_summary_counts(findings_list)


@click.command()
@click.option("--all", "all_findings", is_flag=True, help="Show findings from all analyses")
@click.option("--severity", help="Filter by severity (critical, high, medium, low)")
@click.option("--category", help="Filter by category (security, performance, quality, etc.)")
@click.option("--summary", is_flag=True, help="Show summary statistics only")
@click.option("--details", is_flag=True, help="Show detailed findings with location and suggestions")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
@click.option("--html", is_flag=True, help="Generate HTML report")
@click.option("--output", help="Output file path for HTML report (default: analysis/findings-report.html)")
def findings(
    all_findings: bool,
    severity: str | None,
    category: str | None,
    summary: bool,
    details: bool,
    output_format: str,
    html: bool,
    output: str | None,
) -> None:
    """View analysis findings.

    \b
    Examples:
      air findings --all                          # List all findings
      air findings --all --severity=high          # High severity only
      air findings --all --category=security      # Security findings only
      air findings --all --summary                # Summary statistics
      air findings --all --details                # Detailed view with locations
      air findings --all --format=json            # JSON output
      air findings --all --html                   # Generate HTML report
      air findings --all --html --output report.html  # Custom HTML output path
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

            # Handle both old format (array) and new format (object with findings array)
            if isinstance(findings_data, dict):
                # New format: {repository, classification, findings}
                repo_name = findings_data.get("repository", findings_file.stem.replace("-findings", ""))
                findings_array = findings_data.get("findings", [])
            else:
                # Old format: array of findings
                repo_name = findings_file.stem.replace("-findings", "")
                findings_array = findings_data

            for finding in findings_array:
                # Add source file info
                finding["source"] = repo_name
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

    # Filter by category if requested
    if category:
        all_findings_list = [
            f for f in all_findings_list
            if f.get("category", "").lower() == category.lower()
        ]

    # HTML output
    if html:
        if not all_findings_list:
            info("No findings to generate HTML report")
            return

        # Determine output path
        if output:
            html_path = Path(output)
        else:
            html_path = project_root / "analysis" / "findings-report.html"

        html_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate HTML report
        project_name = project_root.name
        generate_findings_html(all_findings_list, html_path, project_name)

        success(f"HTML report generated: {html_path}")
        info(f"Open in browser: file://{html_path.absolute()}")
        return

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
        if severity or category:
            info(f"No findings matching filters")
        else:
            info("No findings yet")
        return

    # Summary view
    if summary:
        _show_summary(all_findings_list)
        return

    # Details view
    if details:
        _show_details(all_findings_list)
        return

    # Default: Table view
    table = Table(title="[bold]Analysis Findings[/bold]", show_header=True)
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Severity", style="yellow")
    table.add_column("Category", style="green")
    table.add_column("Title/Description", style="white")

    for finding in all_findings_list:
        # Severity styling
        severity_val = finding.get("severity", "info")
        sev_emoji, sev_style = _get_severity_style(severity_val)

        # Get title or description
        title = finding.get("title", finding.get("reasoning", finding.get("type", "No title")))
        if len(title) > 60:
            title = title[:57] + "..."

        table.add_row(
            finding.get("source", "unknown"),
            f"[{sev_style}]{sev_emoji} {severity_val.capitalize()}[/{sev_style}]",
            finding.get("category", "unknown"),
            title,
        )

    console.print()
    console.print(table)

    # Summary counts
    _show_summary_counts(all_findings_list)
