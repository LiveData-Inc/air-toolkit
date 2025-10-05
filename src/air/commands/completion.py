"""Manage shell completion."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console

from air.utils.console import error, info, success, warn

console = Console()


@click.group()
def completion() -> None:
    """Manage shell completion for air CLI.

    Enable tab completion for commands, options, resource names, task IDs, etc.
    """
    pass


@completion.command("install")
@click.argument(
    "shell",
    type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
    required=False,
)
def completion_install(shell: str | None) -> None:
    """Install shell completion.

    \b
    Supports:
      - bash: Adds completion to ~/.bashrc
      - zsh: Adds completion to ~/.zshrc
      - fish: Creates completion file in ~/.config/fish/completions/

    \b
    Examples:
      air completion install bash    # Install for bash
      air completion install zsh     # Install for zsh
      air completion install         # Auto-detect shell
    """
    # Auto-detect shell if not specified
    if not shell:
        detected_shell = detect_shell()
        if not detected_shell:
            error(
                "Could not detect shell",
                hint="Please specify shell explicitly: bash, zsh, or fish",
                exit_code=1,
            )
        shell = detected_shell
        info(f"Auto-detected shell: {shell}")

    shell = shell.lower()

    # Get appropriate completion script
    if shell == "bash":
        _install_bash_completion()
    elif shell == "zsh":
        _install_zsh_completion()
    elif shell == "fish":
        _install_fish_completion()
    else:
        error(f"Unsupported shell: {shell}", exit_code=1)


@completion.command("uninstall")
@click.argument(
    "shell",
    type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
    required=False,
)
def completion_uninstall(shell: str | None) -> None:
    """Uninstall shell completion.

    \b
    Examples:
      air completion uninstall bash  # Uninstall from bash
      air completion uninstall       # Auto-detect shell
    """
    # Auto-detect shell if not specified
    if not shell:
        detected_shell = detect_shell()
        if not detected_shell:
            error(
                "Could not detect shell",
                hint="Please specify shell explicitly: bash, zsh, or fish",
                exit_code=1,
            )
        shell = detected_shell
        info(f"Auto-detected shell: {shell}")

    shell = shell.lower()

    if shell == "bash":
        _uninstall_bash_completion()
    elif shell == "zsh":
        _uninstall_zsh_completion()
    elif shell == "fish":
        _uninstall_fish_completion()
    else:
        error(f"Unsupported shell: {shell}", exit_code=1)


@completion.command("show")
@click.argument(
    "shell",
    type=click.Choice(["bash", "zsh", "fish"], case_sensitive=False),
)
def completion_show(shell: str) -> None:
    """Show completion script for shell.

    Prints the completion activation command that would be added to your shell config.

    \b
    Examples:
      air completion show bash
      air completion show zsh
    """
    shell = shell.lower()

    if shell == "bash":
        script = 'eval "$(_AIR_COMPLETE=bash_source air)"'
    elif shell == "zsh":
        script = 'eval "$(_AIR_COMPLETE=zsh_source air)"'
    elif shell == "fish":
        script = 'eval (env _AIR_COMPLETE=fish_source air)'
    else:
        error(f"Unsupported shell: {shell}", exit_code=1)
        return

    console.print(f"[bold]{shell} completion:[/bold]")
    console.print(f"  {script}")


def detect_shell() -> str | None:
    """Auto-detect the current shell.

    Returns:
        Shell name (bash, zsh, fish) or None if cannot detect
    """
    shell_env = os.environ.get("SHELL", "")

    if "bash" in shell_env:
        return "bash"
    elif "zsh" in shell_env:
        return "zsh"
    elif "fish" in shell_env:
        return "fish"

    return None


def _install_bash_completion() -> None:
    """Install bash completion to ~/.bashrc."""
    bashrc = Path.home() / ".bashrc"
    completion_line = 'eval "$(_AIR_COMPLETE=bash_source air)"'
    marker = "# air-toolkit completion"

    if not bashrc.exists():
        error(
            "~/.bashrc not found",
            hint="Create ~/.bashrc or install completion manually",
            exit_code=1,
        )

    # Check if already installed
    content = bashrc.read_text()
    if marker in content or completion_line in content:
        warn("Completion already installed in ~/.bashrc")
        return

    # Append completion
    with bashrc.open("a") as f:
        f.write(f"\n{marker}\n{completion_line}\n")

    success("Bash completion installed to ~/.bashrc")
    info("Run 'source ~/.bashrc' or restart your shell to activate")


def _install_zsh_completion() -> None:
    """Install zsh completion to ~/.zshrc."""
    zshrc = Path.home() / ".zshrc"
    completion_line = 'eval "$(_AIR_COMPLETE=zsh_source air)"'
    marker = "# air-toolkit completion"

    if not zshrc.exists():
        error(
            "~/.zshrc not found",
            hint="Create ~/.zshrc or install completion manually",
            exit_code=1,
        )

    # Check if already installed
    content = zshrc.read_text()
    if marker in content or completion_line in content:
        warn("Completion already installed in ~/.zshrc")
        return

    # Append completion
    with zshrc.open("a") as f:
        f.write(f"\n{marker}\n{completion_line}\n")

    success("Zsh completion installed to ~/.zshrc")
    info("Run 'source ~/.zshrc' or restart your shell to activate")


def _install_fish_completion() -> None:
    """Install fish completion to ~/.config/fish/completions/."""
    completions_dir = Path.home() / ".config/fish/completions"
    completions_file = completions_dir / "air.fish"
    completion_script = "env _AIR_COMPLETE=fish_source air | source"

    # Create directory if it doesn't exist
    if not completions_dir.exists():
        completions_dir.mkdir(parents=True, exist_ok=True)

    # Check if already installed
    if completions_file.exists():
        content = completions_file.read_text()
        if completion_script in content:
            warn(f"Completion already installed in {completions_file}")
            return

    # Write completion file
    completions_file.write_text(completion_script + "\n")

    success(f"Fish completion installed to {completions_file}")
    info("Restart your fish shell to activate")


def _uninstall_bash_completion() -> None:
    """Uninstall bash completion from ~/.bashrc."""
    bashrc = Path.home() / ".bashrc"
    marker = "# air-toolkit completion"
    completion_line = 'eval "$(_AIR_COMPLETE=bash_source air)"'

    if not bashrc.exists():
        warn("~/.bashrc not found, nothing to uninstall")
        return

    # Read and filter out completion lines
    lines = bashrc.read_text().splitlines()
    filtered_lines = []
    skip_next = False

    for line in lines:
        if marker in line:
            skip_next = True
            continue
        if skip_next and completion_line in line:
            skip_next = False
            continue
        filtered_lines.append(line)

    # Also handle case where marker isn't present but completion line is
    filtered_lines = [l for l in filtered_lines if completion_line not in l]

    # Write back
    bashrc.write_text("\n".join(filtered_lines) + "\n")
    success("Bash completion uninstalled from ~/.bashrc")


def _uninstall_zsh_completion() -> None:
    """Uninstall zsh completion from ~/.zshrc."""
    zshrc = Path.home() / ".zshrc"
    marker = "# air-toolkit completion"
    completion_line = 'eval "$(_AIR_COMPLETE=zsh_source air)"'

    if not zshrc.exists():
        warn("~/.zshrc not found, nothing to uninstall")
        return

    # Read and filter out completion lines
    lines = zshrc.read_text().splitlines()
    filtered_lines = []
    skip_next = False

    for line in lines:
        if marker in line:
            skip_next = True
            continue
        if skip_next and completion_line in line:
            skip_next = False
            continue
        filtered_lines.append(line)

    # Also handle case where marker isn't present but completion line is
    filtered_lines = [l for l in filtered_lines if completion_line not in l]

    # Write back
    zshrc.write_text("\n".join(filtered_lines) + "\n")
    success("Zsh completion uninstalled from ~/.zshrc")


def _uninstall_fish_completion() -> None:
    """Uninstall fish completion from ~/.config/fish/completions/."""
    completions_file = Path.home() / ".config/fish/completions/air.fish"

    if not completions_file.exists():
        warn("Fish completion not installed, nothing to uninstall")
        return

    completions_file.unlink()
    success(f"Fish completion uninstalled from {completions_file}")
