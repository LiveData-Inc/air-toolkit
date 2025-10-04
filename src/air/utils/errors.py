"""Enhanced error handling with helpful suggestions."""

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel

console = Console()


class AirError(Exception):
    """Base exception for AIR toolkit with enhanced error messages."""

    def __init__(
        self,
        message: str,
        hint: str | None = None,
        details: str | None = None,
        doc_link: str | None = None,
    ):
        """Initialize error with context.

        Args:
            message: Main error message
            hint: Helpful hint for fixing the error
            details: Additional error details
            doc_link: Link to relevant documentation
        """
        self.message = message
        self.hint = hint
        self.details = details
        self.doc_link = doc_link
        super().__init__(message)

    def display(self) -> None:
        """Display formatted error message with Rich."""
        lines = [f"[red]✗[/red] {self.message}"]

        if self.details:
            lines.append(f"\n[dim]{self.details}[/dim]")

        if self.hint:
            lines.append(f"\n[yellow]💡 Hint:[/yellow] {self.hint}")

        if self.doc_link:
            lines.append(f"\n[blue]📖 Docs:[/blue] {self.doc_link}")

        console.print("\n".join(lines))


class ProjectNotFoundError(AirError):
    """Raised when not in an AIR project."""

    def __init__(self, current_dir: Path | None = None):
        message = "Not in an AIR project"
        hint = "Run 'air init' to create a project or 'cd' to project directory"
        details = None
        if current_dir:
            details = f"Current directory: {current_dir}"

        super().__init__(message, hint=hint, details=details)


class ConfigurationError(AirError):
    """Raised when configuration is invalid."""

    def __init__(
        self,
        message: str,
        config_path: Path | None = None,
        fix_suggestion: str | None = None,
    ):
        hint = fix_suggestion or "Check air-config.json for syntax errors"
        details = None
        if config_path:
            details = f"Config file: {config_path}"

        super().__init__(
            message,
            hint=hint,
            details=details,
            doc_link="https://github.com/LiveData-Inc/air-toolkit/blob/main/docs/SPECIFICATION.md",
        )


class ResourceError(AirError):
    """Raised when resource operations fail."""

    def __init__(
        self, message: str, resource_name: str | None = None, suggestion: str | None = None
    ):
        hint = suggestion
        details = None
        if resource_name:
            details = f"Resource: {resource_name}"

        super().__init__(message, hint=hint, details=details)


class ResourceNotFoundError(ResourceError):
    """Raised when resource doesn't exist."""

    def __init__(self, resource_name: str, available_resources: list[str] | None = None):
        message = f"Resource '{resource_name}' not found"

        hint = "Run 'air link list' to see available resources"
        if available_resources and len(available_resources) > 0:
            # Find similar resource names for suggestions
            similar = _find_similar_names(resource_name, available_resources)
            if similar:
                hint = f"Did you mean: {', '.join(similar)}?"

        super().__init__(message, resource_name=resource_name, suggestion=hint)


class PathError(AirError):
    """Raised when path operations fail."""

    def __init__(self, message: str, path: Path, suggestion: str | None = None):
        hint = suggestion or f"Check that path exists and is accessible: {path}"
        super().__init__(message, hint=hint, details=f"Path: {path}")


class GitError(AirError):
    """Raised when git operations fail."""

    def __init__(self, message: str, suggestion: str | None = None, git_output: str | None = None):
        hint = suggestion or "Ensure git is installed and repository is valid"
        details = None
        if git_output:
            details = f"Git output: {git_output}"

        super().__init__(message, hint=hint, details=details)


class GitHubCLIError(AirError):
    """Raised when GitHub CLI operations fail."""

    def __init__(self, message: str, gh_output: str | None = None):
        hint = "Install: brew install gh && gh auth login"
        details = None
        if gh_output:
            details = f"Output: {gh_output}"

        super().__init__(
            message,
            hint=hint,
            details=details,
            doc_link="https://cli.github.com/manual/installation",
        )


class TaskError(AirError):
    """Raised when task operations fail."""

    def __init__(self, message: str, task_id: str | None = None, suggestion: str | None = None):
        hint = suggestion or "Run 'air task list' to see available tasks"
        details = None
        if task_id:
            details = f"Task ID: {task_id}"

        super().__init__(message, hint=hint, details=details)


class ValidationError(AirError):
    """Raised when validation fails."""

    def __init__(
        self, message: str, issues: list[str] | None = None, suggestion: str | None = None
    ):
        hint = suggestion or "Run 'air validate' for full validation report"
        details = None
        if issues:
            details = "Issues:\n" + "\n".join(f"  • {issue}" for issue in issues[:5])
            if len(issues) > 5:
                details += f"\n  ... and {len(issues) - 5} more"

        super().__init__(message, hint=hint, details=details)


def _find_similar_names(target: str, candidates: list[str], max_distance: int = 2) -> list[str]:
    """Find similar names using Levenshtein distance.

    Args:
        target: Target string to match
        candidates: List of candidate strings
        max_distance: Maximum edit distance for matches

    Returns:
        List of similar names sorted by similarity
    """
    similarities = []

    for candidate in candidates:
        distance = _levenshtein_distance(target.lower(), candidate.lower())
        if distance <= max_distance:
            similarities.append((distance, candidate))

    # Sort by distance, then alphabetically
    similarities.sort(key=lambda x: (x[0], x[1]))

    return [name for _, name in similarities[:3]]  # Return top 3 matches


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein distance between two strings.

    Args:
        s1: First string
        s2: Second string

    Returns:
        Edit distance between strings
    """
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            # Cost of insertions, deletions, or substitutions
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def display_error(error: Exception) -> None:
    """Display error with enhanced formatting.

    Args:
        error: Exception to display
    """
    if isinstance(error, AirError):
        error.display()
    else:
        console.print(f"[red]✗[/red] Unexpected error: {error}")
        console.print("[dim]Use --debug for full traceback[/dim]")
