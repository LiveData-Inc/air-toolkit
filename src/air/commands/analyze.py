"""Analyze repositories using AI agents."""

import json
import sys
import time
import traceback
from pathlib import Path

import click

from air.core.models import AirConfig
from air.services.agent_manager import (
    AnalysisOrchestrator,
    generate_agent_id,
    reconstruct_analyzer_result,
    spawn_background_agent,
    update_agent_status,
)
from air.services.analyzers import (
    ArchitectureAnalyzer,
    CodeStructureAnalyzer,
    PerformanceAnalyzer,
    QualityAnalyzer,
    SecurityAnalyzer,
)
from air.services.cache_manager import CacheManager
from air.services.classifier import classify_resource
from air.services.dependency_graph import (
    build_dependency_graph,
    detect_dependency_gaps,
    filter_repos_with_dependencies,
    topological_sort,
)
from air.services.filesystem import get_project_root, load_config
from air.utils.completion import complete_analyzer_focus, complete_resource_names
from air.utils.console import error, info, success, warn


@click.command()
@click.argument("resource", required=False, shell_complete=complete_resource_names)
@click.option("--all", "analyze_all", is_flag=True, help="Analyze all linked repos")
@click.option("--no-order", is_flag=True, help="Disable dependency-ordered analysis (parallel)")
@click.option("--deps-only", is_flag=True, help="Only analyze repos with dependencies")
@click.option("--gap", help="Gap analysis for this library vs dependents", shell_complete=complete_resource_names)
@click.option("--no-deps", is_flag=True, help="Skip dependency checking")
@click.option("--background", is_flag=True, help="Run in background")
@click.option("--id", "agent_id", help="Agent identifier (for background mode)")
@click.option("--focus", help="Analysis focus area (security, architecture, performance)", shell_complete=complete_analyzer_focus)
@click.option("--no-cache", is_flag=True, help="Force fresh analysis (skip cache)")
@click.option("--clear-cache", is_flag=True, help="Clear cache before analysis")
@click.option("--include-external", is_flag=True, help="Include external/vendor libraries in analysis")
@click.option("--parallel", is_flag=True, help="Run analyzers in parallel (faster)")
@click.option("--workers", type=int, default=None, help="Number of parallel workers (default: CPU count)")
def analyze(
    resource: str | None,
    analyze_all: bool,
    no_order: bool,
    deps_only: bool,
    gap: str | None,
    no_deps: bool,
    background: bool,
    agent_id: str | None,
    focus: str | None,
    no_cache: bool,
    clear_cache: bool,
    include_external: bool,
    parallel: bool,
    workers: int | None,
) -> None:
    """Analyze repositories with intelligent defaults.

    \b
    Single Repo (checks dependencies by default):
      air analyze myapp                       # Checks dependencies
      air analyze myapp --no-deps             # Skip dependency checking
      air analyze myapp --focus=security

    \b
    Multi-Repo (dependency order by default):
      air analyze --all                       # Analyzes in dependency order
      air analyze --all --no-order            # Parallel analysis
      air analyze --all --deps-only           # Skip isolated repos
      air analyze --gap shared-utils          # Gap analysis

    \b
    Background:
      air analyze myapp --background --id=security-analysis
    """
    # Verify we're in an AIR project
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    # Load config
    config = load_config(project_root)

    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=project_root / ".air" / "cache")

    # Clear cache if requested
    if clear_cache:
        info("Clearing analysis cache...")
        cache_manager.clear_all()
        success("Cache cleared")

    # Multi-repo analysis modes
    if analyze_all:
        # Default: respect dependencies (unless --no-order specified)
        respect_deps = not no_order
        _analyze_multi_repo(
            config=config,
            respect_deps=respect_deps,
            deps_only=deps_only,
            focus=focus,
            background=background,
            cache_manager=cache_manager,
            no_cache=no_cache,
            include_external=include_external,
            parallel=parallel,
            max_workers=workers,
        )
        return

    if gap:
        _analyze_gap(config=config, library_name=gap, focus=focus, include_external=include_external)
        return

    # Single repo analysis - resolve resource name or path
    if not resource:
        error("Resource name or path required", exit_code=1)

    resource_path = _resolve_resource(config, resource)

    # Default: check dependencies (unless --no-deps specified)
    check_deps = not no_deps

    # Run single repo analysis
    _analyze_single_repo(
        resource_path=resource_path,
        focus=focus,
        background=background,
        agent_id=agent_id,
        project_root=project_root,
        check_deps=check_deps,
        config=config if check_deps else None,
        cache_manager=cache_manager,
        no_cache=no_cache,
        include_external=include_external,
        parallel=parallel,
        max_workers=workers,
    )


def _resolve_resource(config: AirConfig, resource: str) -> Path:
    """Resolve resource name or path to absolute path.

    Args:
        config: AIR project configuration
        resource: Resource name or path

    Returns:
        Resolved absolute path

    Raises:
        SystemExit: If resource not found
    """
    # Try as resource name first
    for r in config.get_all_resources():
        if r.name == resource:
            return Path(r.path).expanduser().resolve()

    # Try as path
    path = Path(resource).expanduser()
    if path.exists():
        return path.resolve()

    error(f"Resource not found: {resource}", exit_code=1)


def _get_analyzer_list(focus: str | None) -> list[str]:
    """Get list of analyzer names based on focus.

    Args:
        focus: Analysis focus area or None for all

    Returns:
        List of analyzer names
    """
    if focus == "security":
        return ["security"]
    elif focus == "performance":
        return ["performance"]
    elif focus == "architecture":
        return ["architecture"]
    elif focus == "quality":
        return ["quality"]
    elif not focus:
        # All analyzers
        return ["security", "performance", "architecture", "quality", "code_structure"]
    else:
        return []


def _analyze_single_repo(
    resource_path: Path,
    focus: str | None,
    background: bool,
    agent_id: str | None,
    project_root: Path,
    check_deps: bool = False,
    config: AirConfig | None = None,
    cache_manager: CacheManager | None = None,
    no_cache: bool = False,
    current_index: int | None = None,
    total_count: int | None = None,
    include_external: bool = False,
    parallel: bool = False,
    max_workers: int | None = None,
) -> None:
    """Analyze a single repository.

    Args:
        resource_path: Path to repository
        focus: Analysis focus area
        background: Run in background
        agent_id: Agent identifier
        project_root: AIR project root
        check_deps: Check for dependency issues
        config: AIR config (if checking deps)
        cache_manager: Cache manager instance
        no_cache: Skip cache lookup/storage
        current_index: Current repo index (for progress display)
        total_count: Total repos to analyze (for progress display)
    """
    if background:
        # Spawn background agent
        if not agent_id:
            agent_id = generate_agent_id("analyze")

        spawn_background_agent(
            agent_id=agent_id,
            command="analyze",
            args={"focus": focus} if focus else {},
            resource_path=str(resource_path),
        )
        return

    # Run analysis
    try:
        # Start timing
        analysis_start = time.time()

        # Show progress indicator if we have index/count
        if current_index is not None and total_count is not None:
            # Add separator between repos (except for first one)
            if current_index > 1:
                info("")
                info("─" * 60)
                info("")
            info(f"[{current_index}/{total_count}] Analyzing: {resource_path}")
        else:
            info(f"Analyzing: {resource_path}")

        if focus:
            info(f"Focus area: {focus}")

        # Always start with classification
        classification_start = time.time()
        result = classify_resource(resource_path)
        classification_time = time.time() - classification_start

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
        analyzer_times = {}

        if parallel:
            # PARALLEL EXECUTION using subprocess orchestrator
            analyzer_names = _get_analyzer_list(focus)

            with AnalysisOrchestrator(max_workers=max_workers) as orchestrator:
                results = orchestrator.analyze_parallel(
                    repo_paths=[resource_path],
                    analyzers=analyzer_names,
                    include_external=include_external,
                )

            # Process results from parallel execution
            for result_dict in results.get(str(resource_path), []):
                if result_dict.get("success"):
                    # Extract timing
                    analyzer_name = result_dict.get("analyzer")
                    analyzer_times[analyzer_name] = result_dict.get("elapsed_time", 0)

                    # Reconstruct result and add findings
                    analyzer_result = reconstruct_analyzer_result(result_dict)
                    if analyzer_result:
                        # Add summary
                        all_findings.append({
                            "category": analyzer_result.analyzer_name,
                            "severity": "info",
                            "type": "summary",
                            "summary": analyzer_result.summary,
                        })

                        # Add individual findings
                        for finding in analyzer_result.findings:
                            all_findings.append(finding.to_dict())

        else:
            # SEQUENTIAL EXECUTION (original code path)
            analyzers = []

            if focus == "security" or not focus:
                analyzers.append(SecurityAnalyzer(resource_path, include_external=include_external))

            if focus == "performance" or not focus:
                analyzers.append(PerformanceAnalyzer(resource_path, include_external=include_external))

            if focus == "architecture" or not focus:
                analyzers.append(ArchitectureAnalyzer(resource_path, include_external=include_external))

            if focus == "quality" or not focus:
                analyzers.append(QualityAnalyzer(resource_path, include_external=include_external))

            if not focus:  # Always run structure analysis when no focus
                analyzers.append(CodeStructureAnalyzer(resource_path, include_external=include_external))

            # Run analyzers and collect findings
            for analyzer in analyzers:
                analyzer_result = None
                analyzer_start = time.time()

                # Check cache first (unless --no-cache or no cache_manager)
                if not no_cache and cache_manager:
                    # Create a marker file representing the whole repo
                    # (We cache at repo level, not file level for now)
                    repo_marker = resource_path / ".git" if (resource_path / ".git").exists() else resource_path
                    cached_result = cache_manager.get_cached_analysis(
                        resource_path, repo_marker, analyzer.name
                    )

                    if cached_result:
                        info(f"{analyzer.name} analysis (cached)...")
                        analyzer_result = cached_result

                # Run analysis if not cached
                if not analyzer_result:
                    info(f"Running {analyzer.name} analysis...")
                    analyzer_result = analyzer.analyze()

                    # Cache the result (unless --no-cache or no cache_manager)
                    if not no_cache and cache_manager:
                        repo_marker = resource_path / ".git" if (resource_path / ".git").exists() else resource_path
                        cache_manager.set_cached_analysis(resource_path, repo_marker, analyzer_result)

                analyzer_times[analyzer.name] = time.time() - analyzer_start

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

        # Check for dependency issues if requested
        deps_time = 0
        if check_deps and config:
            deps_start = time.time()
            info("Checking dependencies...")
            graph = build_dependency_graph(config)
            gaps = detect_dependency_gaps(config, graph)
            if gaps:
                warn(f"Found {len(gaps)} dependency issues")
                all_findings.extend(gaps)
            deps_time = time.time() - deps_start

        # Save findings to analysis directory
        analysis_dir = project_root / "analysis" / "reviews"
        analysis_dir.mkdir(parents=True, exist_ok=True)

        findings_file = analysis_dir / f"{resource_path.name}-findings.json"
        findings_file.write_text(json.dumps(all_findings, indent=2))

        # Calculate total time
        total_time = time.time() - analysis_start

        # Display timing information (skip if parallel - already shown in progress)
        if not parallel:
            info("")
            info("⏱️  Analysis Timing:")
            info(f"  Classification: {classification_time:.2f}s")
            for analyzer_name, analyzer_time in analyzer_times.items():
                info(f"  {analyzer_name}: {analyzer_time:.2f}s")
            if deps_time > 0:
                info(f"  Dependencies: {deps_time:.2f}s")
            info(f"  Total: {total_time:.2f}s")
            info("")

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


def _analyze_multi_repo(
    config: AirConfig,
    respect_deps: bool,
    deps_only: bool,
    focus: str | None,
    background: bool,
    cache_manager: CacheManager | None = None,
    no_cache: bool = False,
    include_external: bool = False,
    parallel: bool = False,
    max_workers: int | None = None,
) -> None:
    """Analyze multiple repos with dependency awareness.

    Args:
        config: AIR project configuration
        respect_deps: Analyze in dependency order
        deps_only: Only analyze repos with dependencies
        focus: Analysis focus area
        background: Run analyses in background
        cache_manager: Cache manager instance
        no_cache: Skip cache lookup/storage
    """
    # Start total timing
    multi_repo_start = time.time()

    # Build dependency graph
    graph_start = time.time()
    info("Building dependency graph...")
    graph = build_dependency_graph(config)
    graph_time = time.time() - graph_start

    # Save graph as JSON
    project_root = get_project_root()
    graph_file = project_root / "analysis" / "dependency-graph.json"
    graph_file.parent.mkdir(parents=True, exist_ok=True)

    # Convert graph to serializable format
    graph_json = {repo: list(deps) for repo, deps in graph.items()}
    graph_file.write_text(json.dumps(graph_json, indent=2))
    info(f"Dependency graph saved: {graph_file}")

    # Filter if deps_only
    if deps_only:
        original_count = len(graph)
        graph = filter_repos_with_dependencies(graph)
        skipped = original_count - len(graph)
        if skipped:
            info(f"Skipping {skipped} isolated repos (--deps-only)")

    if not graph:
        info("No repos to analyze")
        return

    # Determine analysis order
    if respect_deps:
        try:
            levels = topological_sort(graph)
            info(f"Analysis order: {len(levels)} levels")
            for i, level in enumerate(levels, 1):
                info(f"  Level {i}: {', '.join(level)}")
        except ValueError as e:
            error(str(e), exit_code=1)
    else:
        # All in one level (parallel)
        levels = [list(graph.keys())]
        info(f"Analyzing {len(levels[0])} repos in parallel")

    # Count total repos for progress tracking
    total_repos = sum(len(level) for level in levels)
    current_repo = 0

    # Track timing for each level
    level_times = {}

    # Analyze by level
    for level_num, repos_in_level in enumerate(levels, 1):
        level_start = time.time()
        if respect_deps and len(levels) > 1:
            info(f"\nLevel {level_num}/{len(levels)}: {', '.join(repos_in_level)}")

        # Spawn agents for this level
        agent_ids = []
        for repo_name in repos_in_level:
            current_repo += 1
            agent_id = f"level-{level_num}-{repo_name}"

            # Find resource
            resource = next((r for r in config.get_all_resources() if r.name == repo_name), None)
            if not resource:
                warn(f"Resource not found: {repo_name}")
                continue

            resource_path = Path(resource.path).expanduser().resolve()

            if background:
                spawn_background_agent(
                    agent_id=agent_id,
                    command="analyze",
                    args={"focus": focus} if focus else {},
                    resource_path=str(resource_path),
                )
                agent_ids.append(agent_id)
            else:
                # Run synchronously (with optional parallel analyzers per repo)
                _analyze_single_repo(
                    resource_path=resource_path,
                    focus=focus,
                    background=False,
                    agent_id=None,
                    project_root=project_root,
                    check_deps=True,
                    config=config,
                    cache_manager=cache_manager,
                    no_cache=no_cache,
                    current_index=current_repo,
                    total_count=total_repos,
                    include_external=include_external,
                    parallel=parallel,
                    max_workers=max_workers,
                )

        # If background, wait for this level to complete before next
        if background and respect_deps and agent_ids:
            info(f"Waiting for level {level_num} to complete...")
            # TODO: Implement wait for agents
            # For now, just inform user
            info(f"Use 'air status --agents' to monitor progress")
            info(f"Agents: {', '.join(agent_ids)}")

        # Record level timing
        level_times[f"Level {level_num}"] = time.time() - level_start

    # Detect cross-repo dependency gaps
    gaps_start = time.time()
    info("\nChecking for dependency gaps...")
    gaps = detect_dependency_gaps(config, graph)
    gaps_time = time.time() - gaps_start
    if gaps:
        warn(f"Found {len(gaps)} dependency issues:")
        for gap in gaps:
            warn(f"  {gap['message']}")
    else:
        success("No dependency issues found")

    # Calculate total time and display timing summary
    total_time = time.time() - multi_repo_start

    info("")
    info("⏱️  Multi-Repo Analysis Timing:")
    info(f"  Dependency graph: {graph_time:.2f}s")
    for level_name, level_time in level_times.items():
        repo_count = len(levels[int(level_name.split()[1]) - 1])
        info(f"  {level_name} ({repo_count} repos): {level_time:.2f}s")
    info(f"  Dependency gap check: {gaps_time:.2f}s")
    info(f"  Total: {total_time:.2f}s")
    info(f"  Average per repo: {total_time / total_repos:.2f}s")
    info("")


def _analyze_gap(
    config: AirConfig,
    library_name: str,
    focus: str | None,
    include_external: bool = False,
) -> None:
    """Perform gap analysis for a library vs its dependents.

    Args:
        config: AIR project configuration
        library_name: Name of library to analyze
        focus: Analysis focus area
    """
    info(f"Gap analysis: {library_name}")

    # Find library resource
    library_resource = next((r for r in config.get_all_resources() if r.name == library_name), None)
    if not library_resource:
        error(f"Library not found: {library_name}", exit_code=1)

    # Build dependency graph
    graph = build_dependency_graph(config)

    # Find dependents
    dependents = [repo for repo, deps in graph.items() if library_name in deps]
    if not dependents:
        info(f"No repos depend on {library_name}")
        return

    info(f"Dependents: {', '.join(dependents)}")

    # Calculate total for progress tracking (library + dependents)
    total_repos = 1 + len(dependents)
    current_repo = 0

    # Analyze library
    project_root = get_project_root()
    library_path = Path(library_resource.path).expanduser().resolve()

    current_repo += 1
    info(f"\nAnalyzing library: {library_name}")
    _analyze_single_repo(
        resource_path=library_path,
        focus=focus,
        background=False,
        agent_id=None,
        project_root=project_root,
        check_deps=False,
        config=None,
        current_index=current_repo,
        total_count=total_repos,
        include_external=include_external,
    )

    # Analyze dependents
    for dependent_name in dependents:
        current_repo += 1
        dependent_resource = next((r for r in config.get_all_resources() if r.name == dependent_name), None)
        if not dependent_resource:
            continue

        dependent_path = Path(dependent_resource.path).expanduser().resolve()

        info(f"\nAnalyzing dependent: {dependent_name}")
        _analyze_single_repo(
            resource_path=dependent_path,
            focus=focus,
            background=False,
            agent_id=None,
            project_root=project_root,
            check_deps=True,
            config=config,
            current_index=current_repo,
            total_count=total_repos,
            include_external=include_external,
        )

    # Show gaps
    info("\n" + "="*60)
    info("Gap Analysis Summary")
    info("="*60)

    gaps = detect_dependency_gaps(config, graph)
    library_gaps = [g for g in gaps if library_name in (g.get('dependency'), g.get('repo'))]

    if library_gaps:
        warn(f"\nFound {len(library_gaps)} issues:")
        for gap in library_gaps:
            warn(f"  {gap['message']}")
    else:
        success("\nNo dependency issues found")
