"""Rich console utilities for AIR toolkit."""

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


def error(message: str) -> None:
    """Print error message.

    Args:
        message: Message to print
    """
    console.print(f"[red]✗[/red] {message}", err=True)
