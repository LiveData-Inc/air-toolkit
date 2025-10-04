"""Analyze repositories using AI agents."""

import json
from pathlib import Path

import click

from air.services.agent_manager import generate_agent_id, spawn_background_agent
from air.services.classifier import classify_resource
from air.services.filesystem import get_project_root
from air.utils.console import error, info, success


@click.command()
@click.argument("resource_path", type=click.Path(exists=True))
@click.option("--background", is_flag=True, help="Run in background")
@click.option("--id", "agent_id", help="Agent identifier (for background mode)")
@click.option("--focus", help="Analysis focus area (security, architecture, performance)")
def analyze(
    resource_path: str, background: bool, agent_id: str | None, focus: str | None
) -> None:
    """Analyze a repository.

    \b
    Examples:
      air analyze repos/service-a
      air analyze repos/service-a --focus=security
      air analyze repos/service-a --background --id=security-analysis
    """
    # Verify we're in an AIR project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    resource = Path(resource_path).resolve()

    if background:
        # Spawn background agent
        if not agent_id:
            agent_id = generate_agent_id("analyze")

        spawn_background_agent(
            agent_id=agent_id,
            command="analyze",
            args={"focus": focus} if focus else {},
            resource_path=str(resource),
        )
        return

    # Run analysis inline (for MVP: just classification)
    info(f"Analyzing: {resource}")

    if focus:
        info(f"Focus area: {focus}")

    # Classify the resource
    result = classify_resource(resource)

    info(f"Type: {result.resource_type.value}")
    if result.technology_stack:
        info(f"Technology: {result.technology_stack}")
    if result.detected_languages:
        info(f"Languages: {', '.join(result.detected_languages)}")
    if result.detected_frameworks:
        info(f"Frameworks: {', '.join(result.detected_frameworks)}")
    info(f"Confidence: {result.confidence:.0%}")

    # Write findings (simple for MVP)
    findings = [
        {
            "category": "classification",
            "severity": "info",
            "type": result.resource_type.value,
            "technology_stack": result.technology_stack,
            "confidence": result.confidence,
            "languages": result.detected_languages,
            "frameworks": result.detected_frameworks,
            "reasoning": result.reasoning,
        }
    ]

    # Save findings to analysis directory
    analysis_dir = project_root / "analysis" / "reviews"
    analysis_dir.mkdir(parents=True, exist_ok=True)

    findings_file = analysis_dir / f"{resource.name}-findings.json"
    findings_file.write_text(json.dumps(findings, indent=2))

    success(f"Analysis complete: {findings_file}")
