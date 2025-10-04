"""Analyze repositories using AI agents."""

import json
import sys
import traceback
from pathlib import Path

import click

from air.services.agent_manager import generate_agent_id, spawn_background_agent, update_agent_status
from air.services.analyzers import (
    ArchitectureAnalyzer,
    CodeStructureAnalyzer,
    PerformanceAnalyzer,
    QualityAnalyzer,
    SecurityAnalyzer,
)
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

    # Run analysis
    try:
        info(f"Analyzing: {resource}")

        if focus:
            info(f"Focus area: {focus}")

        # Always start with classification
        result = classify_resource(resource)

        info(f"Type: {result.resource_type.value}")
        if result.technology_stack:
            info(f"Technology: {result.technology_stack}")
        if result.detected_languages:
            info(f"Languages: {', '.join(result.detected_languages)}")
        if result.detected_frameworks:
            info(f"Frameworks: {', '.join(result.detected_frameworks)}")
        info(f"Confidence: {result.confidence:.0%}")

        # Gather findings from classification
        all_findings = [
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

        # Run deep analysis based on focus
        analyzers = []

        if focus == "security" or not focus:
            analyzers.append(SecurityAnalyzer(resource))

        if focus == "performance" or not focus:
            analyzers.append(PerformanceAnalyzer(resource))

        if focus == "architecture" or not focus:
            analyzers.append(ArchitectureAnalyzer(resource))

        if focus == "quality" or not focus:
            analyzers.append(QualityAnalyzer(resource))

        if not focus:  # Always run structure analysis when no focus
            analyzers.append(CodeStructureAnalyzer(resource))

        # Run analyzers and collect findings
        for analyzer in analyzers:
            info(f"Running {analyzer.name} analysis...")
            analyzer_result = analyzer.analyze()

            # Add summary to findings
            all_findings.append(
                {
                    "category": analyzer.name,
                    "severity": "info",
                    "type": "summary",
                    "summary": analyzer_result.summary,
                }
            )

            # Add individual findings
            for finding in analyzer_result.findings:
                all_findings.append(finding.to_dict())

            # Show summary
            if analyzer_result.summary:
                summary_items = [f"{k}: {v}" for k, v in analyzer_result.summary.items()]
                info(f"{analyzer.name}: {', '.join(summary_items[:3])}")

        # Count findings by severity
        severity_counts = {}
        for finding in all_findings:
            sev = finding.get("severity", "info")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        info(
            f"Total findings: {len(all_findings)} "
            f"(critical: {severity_counts.get('critical', 0)}, "
            f"high: {severity_counts.get('high', 0)}, "
            f"medium: {severity_counts.get('medium', 0)})"
        )

        # Save findings to analysis directory
        analysis_dir = project_root / "analysis" / "reviews"
        analysis_dir.mkdir(parents=True, exist_ok=True)

        findings_file = analysis_dir / f"{resource.name}-findings.json"
        findings_file.write_text(json.dumps(all_findings, indent=2))

        success(f"Analysis complete: {findings_file}")

        # Update agent status if running as background agent
        if agent_id:
            update_agent_status(agent_id, "complete")

    except Exception as e:
        error_msg = f"Analysis failed: {e}"
        error(error_msg)

        # Update agent status if running as background agent
        if agent_id:
            update_agent_status(agent_id, "failed", error=str(e), traceback=traceback.format_exc())

        sys.exit(1)
