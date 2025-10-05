"""Dependency graph building and analysis for multi-repo projects."""

from pathlib import Path

from air.core.models import AirConfig
from air.services.dependency_detector import (
    detect_dependencies,
    detect_package_name,
    get_dependency_version,
)


def build_dependency_graph(config: AirConfig) -> dict[str, set[str]]:
    """Build graph of dependencies between linked repos.

    Args:
        config: AIR project configuration

    Returns:
        {repo_name: set of repo names it depends on}
    """
    graph = {}

    # Get all linked repos and their package names
    repo_packages = {}  # {package_name: repo_name}

    for resource in config.get_all_resources():
        repo_path = Path(resource.path).expanduser()

        # Detect what this repo provides (its package name)
        package_name = detect_package_name(repo_path)
        if package_name:
            repo_packages[package_name] = resource.name

    # For each repo, check if it depends on other linked repos
    for resource in config.get_all_resources():
        repo_path = Path(resource.path).expanduser()
        deps = detect_dependencies(repo_path)

        # Find which linked repos this depends on
        linked_deps = set()
        for dep in deps:
            if dep in repo_packages:
                linked_deps.add(repo_packages[dep])

        graph[resource.name] = linked_deps

    return graph


def topological_sort(graph: dict[str, set[str]]) -> list[list[str]]:
    """Sort repos by dependency order, return levels for parallel execution.

    Args:
        graph: Dependency graph from build_dependency_graph

    Returns:
        List of lists - each inner list can be analyzed in parallel

    Raises:
        ValueError: If circular dependency detected
    """
    # Calculate in-degree (how many repos depend on each repo)
    in_degree = {node: 0 for node in graph}
    for node, deps in graph.items():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1

    # Process by levels
    levels = []
    remaining = set(graph.keys())

    while remaining:
        # Find nodes with no dependencies (in-degree = 0)
        level = [node for node in remaining if in_degree[node] == 0]
        if not level:
            # Circular dependency!
            raise ValueError(f"Circular dependency detected in: {remaining}")

        levels.append(level)

        # Remove this level and update in-degrees
        for node in level:
            remaining.remove(node)
            for dep_node in graph.get(node, set()):
                in_degree[dep_node] -= 1

    return levels


def filter_repos_with_dependencies(graph: dict[str, set[str]]) -> dict[str, set[str]]:
    """Filter to only repos that have dependencies OR are depended upon.

    Args:
        graph: Dependency graph

    Returns:
        Filtered graph with only relevant repos
    """
    relevant = set()

    for repo, deps in graph.items():
        if deps:  # Has dependencies
            relevant.add(repo)
            relevant.update(deps)  # Include what it depends on

    # Filter graph
    return {k: v for k, v in graph.items() if k in relevant}


def detect_dependency_gaps(
    config: AirConfig,
    graph: dict[str, set[str]],
) -> list[dict]:
    """Detect version mismatches and gaps between dependencies.

    Args:
        config: AIR project configuration
        graph: Dependency graph

    Returns:
        List of gap findings (version mismatches, missing features, etc.)
    """
    gaps = []

    # Create repo lookup
    repos_by_name = {r.name: r for r in config.get_all_resources()}

    for repo_name, deps in graph.items():
        if not deps:
            continue

        repo_path = Path(repos_by_name[repo_name].path).expanduser()

        for dep_repo_name in deps:
            dep_repo_path = Path(repos_by_name[dep_repo_name].path).expanduser()

            # Detect package name of dependency
            dep_package_name = detect_package_name(dep_repo_path)
            if not dep_package_name:
                continue

            # Get version being used
            used_version = get_dependency_version(repo_path, dep_package_name)
            if not used_version:
                continue

            # Get available version from the dependency repo itself
            # (This is a simplified check - could be enhanced to read package metadata)
            available_version = _get_repo_version(dep_repo_path)

            if available_version and used_version != available_version:
                gaps.append({
                    "type": "version_mismatch",
                    "repo": repo_name,
                    "dependency": dep_repo_name,
                    "package": dep_package_name,
                    "used_version": used_version,
                    "available_version": available_version,
                    "severity": "medium",
                    "message": f"{repo_name} uses {dep_package_name}@{used_version} but {available_version} is available",
                })

    return gaps


def _get_repo_version(repo_path: Path) -> str | None:
    """Get version number from repository package metadata.

    Args:
        repo_path: Path to repository

    Returns:
        Version string or None
    """
    # Try Python pyproject.toml
    if (repo_path / "pyproject.toml").exists():
        try:
            content = (repo_path / "pyproject.toml").read_text()
            import re
            match = re.search(r'^version\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception:
            pass

    # Try JavaScript package.json
    if (repo_path / "package.json").exists():
        try:
            import json
            data = json.loads((repo_path / "package.json").read_text())
            return data.get("version")
        except Exception:
            pass

    return None
