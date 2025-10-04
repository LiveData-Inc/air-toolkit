"""Progress indicators for long-running operations."""

from contextlib import contextmanager
from typing import Any, Iterator

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()


@contextmanager
def progress_spinner(description: str) -> Iterator[None]:
    """Context manager for spinner progress indicator.

    Args:
        description: Description of the operation

    Yields:
        None

    Example:
        with progress_spinner("Copying files..."):
            # Do work
            pass
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description, total=None)
        yield


@contextmanager
def progress_bar(description: str, total: int) -> Iterator[Any]:
    """Context manager for progress bar with known total.

    Args:
        description: Description of the operation
        total: Total number of steps

    Yields:
        Progress task that can be advanced

    Example:
        with progress_bar("Processing files", total=100) as task:
            for i in range(100):
                task.advance(1)
    """
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task(description, total=total)

        class ProgressTask:
            """Helper class to advance progress."""

            def advance(self, amount: float = 1.0) -> None:
                progress.advance(task_id, amount)

            def update(self, completed: float) -> None:
                progress.update(task_id, completed=completed)

        yield ProgressTask()


class ProgressTracker:
    """Track progress for multi-step operations."""

    def __init__(self, description: str, total_steps: int):
        """Initialize progress tracker.

        Args:
            description: Description of the operation
            total_steps: Total number of steps
        """
        self.description = description
        self.total_steps = total_steps
        self.current_step = 0
        self._progress: Progress | None = None
        self._task_id: TaskID | None = None

    def __enter__(self) -> "ProgressTracker":
        """Start progress tracking."""
        self._progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            console=console,
        )
        self._progress.__enter__()
        self._task_id = self._progress.add_task(self.description, total=self.total_steps)
        return self

    def __exit__(self, *args: Any) -> None:
        """Stop progress tracking."""
        if self._progress:
            self._progress.__exit__(*args)

    def step(self, description: str | None = None) -> None:
        """Advance progress by one step.

        Args:
            description: Optional description for current step
        """
        if self._progress and self._task_id is not None:
            self.current_step += 1
            if description:
                self._progress.update(
                    self._task_id,
                    completed=self.current_step,
                    description=f"{self.description}: {description}",
                )
            else:
                self._progress.advance(self._task_id, 1)

    def update_description(self, description: str) -> None:
        """Update progress description.

        Args:
            description: New description
        """
        if self._progress and self._task_id is not None:
            self._progress.update(self._task_id, description=description)


def show_status(message: str, status: str = "info") -> None:
    """Show a status message with appropriate formatting.

    Args:
        message: Status message
        status: Status type (info, success, warning, error)
    """
    icons = {
        "info": "[blue]ℹ[/blue]",
        "success": "[green]✓[/green]",
        "warning": "[yellow]⚠[/yellow]",
        "error": "[red]✗[/red]",
    }

    icon = icons.get(status, "[blue]ℹ[/blue]")
    console.print(f"{icon} {message}")
