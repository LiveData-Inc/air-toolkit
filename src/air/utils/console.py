"""Rich console utilities for AIR toolkit."""

import sys
from typing import NoReturn

from rich.console import Console

# Global console instance
console = Console()


def info(message: str) -> None:
    """Print info message.

    Args:
        message: Message to print
    """
    console.print(f"[blue]ℹ[/blue] {message}")


def success(message: str) -> None:
    """Print success message.

    Args:
        message: Message to print
    """
    console.print(f"[green]✓[/green] {message}")


def warn(message: str) -> None:
    """Print warning message.

    Args:
        message: Message to print
    """
    console.print(f"[yellow]⚠[/yellow] {message}")


def error(message: str, hint: str | None = None, exit_code: int = 1) -> NoReturn:
    """Print error message and exit.

    Args:
        message: Error message to print
        hint: Optional hint for resolving the error
        exit_code: Exit code (default: 1)
    """
    console.print(f"[red]✗[/red] {message}")
    if hint:
        console.print(f"[dim]💡 Hint: {hint}[/dim]")
    sys.exit(exit_code)
