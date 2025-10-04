"""Pull request generation service."""

import subprocess
from pathlib import Path
from typing import NamedTuple

from air.core.models import Resource
from air.services.task_parser import parse_task_file


class ChangeDetection(NamedTuple):
    """Result of change detection in contributions directory."""

    has_changes: bool
    changed_files: list[Path]
    contribution_dir: Path


class PRMetadata(NamedTuple):
    """Metadata for pull request creation."""

    title: str
    body: str
    branch_name: str
    related_tasks: list[str]


def detect_changes(contributions_dir: Path, resource_name: str) -> ChangeDetection:
    """Detect changes in contributions directory for resource.

    Args:
        contributions_dir: Path to contributions/ directory
        resource_name: Name of the resource

    Returns:
        ChangeDetection with status and file list
    """
    contribution_path = contributions_dir / resource_name

    if not contribution_path.exists():
        return ChangeDetection(
            has_changes=False, changed_files=[], contribution_dir=contribution_path
        )

    # Find all files in contribution directory (excluding hidden files)
    changed_files = []
    for file_path in contribution_path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            changed_files.append(file_path)

    return ChangeDetection(
        has_changes=len(changed_files) > 0,
        changed_files=changed_files,
        contribution_dir=contribution_path,
    )


def generate_pr_metadata(
    resource_name: str,
    tasks_dir: Path,
    custom_title: str | None = None,
    custom_body: str | None = None,
) -> PRMetadata:
    """Generate PR title and body from recent task files.

    Args:
        resource_name: Name of the resource
        tasks_dir: Path to .air/tasks directory
        custom_title: Optional custom title
        custom_body: Optional custom body

    Returns:
        PRMetadata with title, body, and branch name
    """
    # Use custom title/body if provided
    if custom_title and custom_body:
        branch_name = _sanitize_branch_name(custom_title)
        return PRMetadata(
            title=custom_title,
            body=custom_body,
            branch_name=branch_name,
            related_tasks=[],
        )

    # Parse recent task files
    task_files = sorted(tasks_dir.glob("*.md"), reverse=True)[:5]  # Last 5 tasks
    related_tasks = []
    task_summaries = []

    for task_file in task_files:
        try:
            task_info = parse_task_file(task_file)
            if task_info.title:
                task_summaries.append(f"- {task_info.title}")
                related_tasks.append(task_file.stem)
        except Exception:
            continue

    # Generate title
    if custom_title:
        title = custom_title
    else:
        title = f"Improvements to {resource_name}"

    # Generate body
    if custom_body:
        body = custom_body
    else:
        body_parts = [
            "## Summary",
            "",
            f"This PR contains improvements to {resource_name}.",
            "",
        ]

        if task_summaries:
            body_parts.extend(
                [
                    "## Related Work",
                    "",
                    *task_summaries,
                    "",
                ]
            )

        body_parts.extend(
            [
                "## Changes",
                "",
                "- Documentation improvements",
                "- Enhanced clarity and examples",
                "",
                "---",
                "",
                "🤖 Generated with [AIR Toolkit](https://github.com/LiveData-Inc/air-toolkit)",
            ]
        )

        body = "\n".join(body_parts)

    # Generate branch name
    branch_name = _sanitize_branch_name(title)

    return PRMetadata(
        title=title, body=body, branch_name=branch_name, related_tasks=related_tasks
    )


def _sanitize_branch_name(title: str) -> str:
    """Convert title to valid git branch name.

    Args:
        title: PR title

    Returns:
        Sanitized branch name
    """
    # Convert to lowercase, replace spaces with hyphens
    branch = title.lower().replace(" ", "-")

    # Remove special characters
    allowed_chars = set("abcdefghijklmnopqrstuvwxyz0123456789-_/")
    branch = "".join(c for c in branch if c in allowed_chars)

    # Remove consecutive hyphens
    while "--" in branch:
        branch = branch.replace("--", "-")

    # Trim hyphens from ends
    branch = branch.strip("-")

    # Limit length
    if len(branch) > 50:
        branch = branch[:50].rstrip("-")

    # Add prefix
    return f"air/{branch}"


def check_gh_cli_available() -> bool:
    """Check if gh CLI is installed and authenticated.

    Returns:
        True if gh is available and authenticated
    """
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def create_pr_with_gh(
    resource_path: Path,
    branch_name: str,
    title: str,
    body: str,
    draft: bool = False,
    base: str = "main",
) -> tuple[bool, str]:
    """Create pull request using gh CLI.

    Args:
        resource_path: Path to the git repository
        branch_name: Name of the branch
        title: PR title
        body: PR body
        draft: Create as draft PR
        base: Base branch (default: main)

    Returns:
        Tuple of (success, pr_url or error_message)
    """
    try:
        # Create PR with gh CLI
        cmd = [
            "gh",
            "pr",
            "create",
            "--title",
            title,
            "--body",
            body,
            "--base",
            base,
        ]

        if draft:
            cmd.append("--draft")

        result = subprocess.run(
            cmd, cwd=resource_path, capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            # Extract PR URL from output
            pr_url = result.stdout.strip()
            return True, pr_url
        else:
            return False, result.stderr.strip()

    except subprocess.TimeoutExpired:
        return False, "Timeout creating PR"
    except Exception as e:
        return False, str(e)


def copy_contributions_to_resource(
    contribution_dir: Path, resource_path: Path, changed_files: list[Path]
) -> list[Path]:
    """Copy contribution files to resource repository.

    Args:
        contribution_dir: Path to contributions/{resource}
        resource_path: Path to resource repository
        changed_files: List of files to copy

    Returns:
        List of copied file paths relative to resource root
    """
    import shutil

    copied_files = []

    for file_path in changed_files:
        # Get relative path from contribution dir
        rel_path = file_path.relative_to(contribution_dir)

        # Target path in resource
        target_path = resource_path / rel_path

        # Create parent directories
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(file_path, target_path)
        copied_files.append(rel_path)

    return copied_files


def git_create_branch_and_commit(
    resource_path: Path, branch_name: str, commit_message: str, files: list[Path]
) -> tuple[bool, str]:
    """Create git branch and commit changes.

    Args:
        resource_path: Path to git repository
        branch_name: Name of branch to create
        commit_message: Commit message
        files: List of files to add (relative paths)

    Returns:
        Tuple of (success, error_message)
    """
    try:
        # Create and checkout branch
        result = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=resource_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False, f"Failed to create branch: {result.stderr}"

        # Add files
        for file_path in files:
            result = subprocess.run(
                ["git", "add", str(file_path)],
                cwd=resource_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False, f"Failed to add file {file_path}: {result.stderr}"

        # Commit
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=resource_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return False, f"Failed to commit: {result.stderr}"

        # Push branch
        result = subprocess.run(
            ["git", "push", "-u", "origin", branch_name],
            cwd=resource_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return False, f"Failed to push: {result.stderr}"

        return True, ""

    except subprocess.TimeoutExpired:
        return False, "Timeout during git operations"
    except Exception as e:
        return False, str(e)


def is_git_repository(path: Path) -> bool:
    """Check if path is a git repository.

    Args:
        path: Path to check

    Returns:
        True if path is a git repository
    """
    git_dir = path / ".git"
    return git_dir.exists() and git_dir.is_dir()
