"""Code review command for AIR toolkit."""

import json
import subprocess
from pathlib import Path
from typing import Any

import click
from rich.console import Console

from air.services.filesystem import get_config_path, get_project_root
from air.utils.console import error, info

console = Console()


def get_git_diff(base: str | None, pr: bool, files: tuple[str, ...]) -> dict[str, Any]:
    """Get git diff information.

    Args:
        base: Base branch to compare against
        pr: Whether reviewing a PR branch
        files: Specific files to review

    Returns:
        Dict with diff information
    """
    try:
        # Determine what to diff
        if files:
            # Specific files (both staged and unstaged)
            cmd = ["git", "diff", "--"] + list(files)
        elif pr:
            # PR branch vs base
            if not base:
                # Try to detect base branch
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD@{upstream}"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0:
                    base = result.stdout.strip().split("/")[0]  # origin/main -> main
                else:
                    base = "main"

            cmd = ["git", "diff", base, "HEAD"]
        else:
            # Uncommitted changes (both staged and unstaged)
            cmd = ["git", "diff"]

        # Get diff
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return {"error": "Failed to get git diff", "stderr": result.stderr}

        diff_output = result.stdout

        # Get file stats
        stat_cmd = cmd + ["--stat"]
        stat_result = subprocess.run(stat_cmd, capture_output=True, text=True)

        # Parse stats
        files_changed = 0
        insertions = 0
        deletions = 0

        if stat_result.returncode == 0:
            for line in stat_result.stdout.split("\n"):
                if "file" in line and "changed" in line:
                    parts = line.split(",")
                    for part in parts:
                        if "file" in part:
                            files_changed = int(part.split()[0])
                        elif "insertion" in part:
                            insertions = int(part.split()[0])
                        elif "deletion" in part:
                            deletions = int(part.split()[0])

        # Get list of changed files
        files_cmd = ["git", "diff", "--name-status"] + cmd[2:]
        files_result = subprocess.run(files_cmd, capture_output=True, text=True)

        changed_files = []
        if files_result.returncode == 0:
            for line in files_result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        status, filepath = parts
                        changed_files.append({
                            "path": filepath,
                            "status": status,
                        })

        return {
            "diff": diff_output,
            "stats": {
                "files_changed": files_changed,
                "insertions": insertions,
                "deletions": deletions,
            },
            "files": changed_files,
        }

    except Exception as e:
        return {"error": str(e)}


def get_air_context() -> dict[str, Any]:
    """Get AIR project context if available.

    Returns:
        Dict with AIR context or empty dict
    """
    project_root = get_project_root()
    if not project_root:
        return {}

    context = {
        "project_root": str(project_root),
        "config_exists": get_config_path(project_root).exists(),
    }

    # Load config if available
    config_path = get_config_path(project_root)
    if config_path.exists():
        try:
            with open(config_path) as f:
                config_data = json.load(f)
                context["project_name"] = config_data.get("name")
                context["project_mode"] = config_data.get("mode")

                # Count resources
                resources = config_data.get("resources", {})
                context["resource_count"] = (
                    len(resources.get("review", [])) +
                    len(resources.get("develop", []))
                )
        except Exception:
            pass

    # Get recent tasks
    tasks_dir = project_root / ".air" / "tasks"
    if tasks_dir.exists():
        task_files = sorted(
            tasks_dir.glob("*.md"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:5]

        context["recent_tasks"] = [
            {
                "file": str(f.relative_to(project_root)),
                "name": f.stem,
            }
            for f in task_files
        ]

    # Check for coding standards
    context_dir = project_root / ".air" / "context"
    if context_dir.exists():
        standards = list(context_dir.glob("*.md"))
        context["standards"] = [
            str(s.relative_to(project_root))
            for s in standards
        ]

    return context


@click.command()
@click.option(
    "--base",
    default=None,
    help="Base branch to compare against (default: main)",
)
@click.option(
    "--pr",
    is_flag=True,
    help="Review current PR branch against base",
)
@click.option(
    "--format",
    type=click.Choice(["json", "markdown"]),
    default="json",
    help="Output format",
)
@click.argument("files", nargs=-1, type=click.Path())
def review(base: str | None, pr: bool, format: str, files: tuple[str, ...]) -> None:
    """Generate code review context from git changes.

    \b
    Examples:
      air review                              # Review uncommitted changes
      air review --pr                         # Review current PR branch
      air review --base=develop --pr          # Review PR against develop
      air review src/api/routes.py            # Review specific file
      air review --format=markdown            # Get markdown output

    The review context includes:
    - Git diff and file statistics
    - AIR project context (if available)
    - Recent task history
    - Coding standards

    Output is optimized for AI code review analysis.
    """
    # Check if we're in a git repository
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        error("Not a git repository", hint="Initialize git with 'git init'", exit_code=1)

    # Get git diff
    diff_data = get_git_diff(base, pr, files)

    if "error" in diff_data:
        error(
            f"Failed to get diff: {diff_data['error']}",
            hint="Check git status and try again",
            exit_code=1
        )

    # Get AIR context
    air_context = get_air_context()

    # Build review context
    review_context = {
        "mode": "pr-review" if pr else "local-review",
        "base_branch": base or "main",
        "changes": diff_data,
        "context": air_context,
        "metadata": {
            "air_version": "0.5.0",
        },
    }

    # Output
    if format == "json":
        console.print_json(data=review_context)
    else:
        # Markdown format
        console.print("# Code Review Context\n")

        console.print(f"**Mode:** {review_context['mode']}")
        console.print(f"**Base:** {review_context['base_branch']}\n")

        stats = diff_data.get("stats", {})
        console.print("## Changes\n")
        console.print(f"- Files changed: {stats.get('files_changed', 0)}")
        console.print(f"- Insertions: +{stats.get('insertions', 0)}")
        console.print(f"- Deletions: -{stats.get('deletions', 0)}\n")

        if diff_data.get("files"):
            console.print("## Files\n")
            for file_info in diff_data["files"]:
                console.print(f"- {file_info['status']} {file_info['path']}")
            console.print()

        if air_context:
            console.print("## AIR Project Context\n")
            if air_context.get("project_name"):
                console.print(f"- Project: {air_context['project_name']}")
            if air_context.get("resource_count"):
                console.print(f"- Linked resources: {air_context['resource_count']}")
            if air_context.get("recent_tasks"):
                console.print(f"- Recent tasks: {len(air_context['recent_tasks'])}")
            console.print()

        console.print("## Diff\n")
        console.print("```diff")
        console.print(diff_data.get("diff", "No changes"))
        console.print("```")
