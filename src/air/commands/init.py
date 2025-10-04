"""Initialize new AIR assessment project."""

from datetime import datetime
from pathlib import Path

import click

from air.core.models import ProjectMode, ProjectStructure
from air.services.filesystem import create_directory, create_file, get_project_root
from air.services.templates import (
    create_config_file,
    get_context_template,
    render_ai_templates,
    render_assessment_templates,
)
from air.utils.console import error, info, success, warn


@click.command()
@click.argument("name", default=None, required=False)
@click.option(
    "--mode",
    type=click.Choice(["review", "collaborate", "mixed"]),
    default="mixed",
    help="Project mode: review-only, collaborative, or mixed",
)
@click.option(
    "--track/--no-track",
    default=True,
    help="Initialize .air/ task tracking",
)
@click.option(
    "--create-dir",
    is_flag=True,
    help="Create new directory (when NAME is provided)",
)
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Interactive mode with prompts",
)
def init(name: str | None, mode: str, track: bool, create_dir: bool, interactive: bool) -> None:
    """Initialize AIR assessment project.

    \b
    Usage:
      air init                        # Initialize in current directory
      air init --create-dir my-proj   # Create directory and initialize
      air init my-proj                # Same as --create-dir (backward compat)

    \b
    Examples:
      air init                              # Current directory, mixed mode
      air init --mode=review                # Current directory, review mode
      air init --create-dir review-proj     # Create new directory
      air init my-review --mode=review      # Backward compatible
    """
    # Interactive mode
    if interactive:
        return _init_interactive()

    # Determine behavior based on arguments
    if name is None:
        # No name: initialize in current directory
        project_dir = Path.cwd()
        project_name = project_dir.name
        creating_new_dir = False
    else:
        # Name provided: backward compatibility (create directory by default)
        # unless user explicitly wants current directory with "."
        if name == ".":
            project_dir = Path.cwd()
            project_name = project_dir.name
            creating_new_dir = False
        else:
            # Create new directory (backward compatible behavior)
            project_dir = Path.cwd() / name
            project_name = name
            creating_new_dir = True

    # Override if --create-dir flag is set
    if create_dir and name is None:
        error(
            "Must provide NAME when using --create-dir",
            hint="Try: air init --create-dir my-project",
            exit_code=1,
        )

    # Show what we're doing
    if creating_new_dir:
        info(f"Creating AIR project: {project_name}")
        info(f"Directory: {project_dir}")
    else:
        info(f"Initializing AIR in current directory: {project_name}")

    info(f"Mode: {mode}")

    # Check if already in an AIR project (unless initializing current dir)
    existing_root = get_project_root()
    if existing_root is not None:
        if existing_root == project_dir.resolve():
            error(
                "This directory is already an AIR project",
                hint="AIR project already initialized here",
                exit_code=1,
            )
        elif not creating_new_dir:
            error(
                f"Already in an AIR project: {existing_root}",
                hint="Create new project in a different directory with --create-dir",
                exit_code=1,
            )

    # Check if directory exists and has content
    if project_dir.exists():
        if creating_new_dir:
            # Creating new directory - should be empty
            if any(project_dir.iterdir()):
                error(
                    f"Directory not empty: {project_dir}",
                    hint="Use an empty directory or specify a different name",
                    exit_code=1,
                )
        else:
            # Initializing in existing directory - warn if has files
            existing_files = list(project_dir.iterdir())
            if existing_files:
                # Filter out hidden files/dirs for count
                visible_files = [f for f in existing_files if not f.name.startswith(".")]
                if visible_files:
                    warn(
                        f"Initializing AIR in directory with {len(visible_files)} existing files"
                    )
                    info("AIR files will be added alongside existing content")

    # Create project directory if needed
    if not project_dir.exists():
        create_directory(project_dir)

    # Get expected structure for mode
    project_mode = ProjectMode(mode)
    structure = ProjectStructure.for_mode(project_mode)

    # Create directories
    info("Creating directory structure...")
    for directory in structure.directories:
        dir_path = project_dir / directory
        create_directory(dir_path)

        # Create .gitkeep for resource directories
        if directory in ["review", "collaborate"]:
            gitkeep = dir_path / ".gitkeep"
            create_file(gitkeep, "", overwrite=True)

    # Render and create template files
    info("Generating project files...")
    created = datetime.now()

    # Assessment templates
    assessment_files = render_assessment_templates(project_name, mode, created)
    for filename, content in assessment_files.items():
        file_path = project_dir / filename
        create_file(file_path, content, overwrite=True)

    # Config file
    config_content = create_config_file(project_name, mode, created)
    config_path = project_dir / "air-config.json"
    create_file(config_path, config_content, overwrite=True)

    # AI tracking templates
    if track:
        ai_files = render_ai_templates()
        for filename, content in ai_files.items():
            file_path = project_dir / filename
            create_file(file_path, content, overwrite=True)

        # Create context files
        for context_type in ["architecture", "language"]:
            context_content = get_context_template(context_type)
            context_path = project_dir / f".air/context/{context_type}.md"
            create_file(context_path, context_content, overwrite=True)

        # Create templates directory
        templates_dir = project_dir / ".air/templates"
        create_directory(templates_dir)

    if creating_new_dir:
        success(f"Project created successfully: {project_dir}")
    else:
        success(f"AIR initialized in: {project_dir}")

    # Show next steps
    print()  # Blank line
    info("Next steps:")
    if creating_new_dir:
        print(f"  cd {name}")

    if mode in ["review", "mixed"]:
        print("  air link --review service-a:~/repos/service-a")
    if mode in ["collaborate", "mixed"]:
        print("  air link --collaborate docs:~/repos/docs")

    print("  air validate")
    print("  air status")


def _init_interactive() -> None:
    """Interactive project initialization with prompts."""
    from rich.console import Console
    from rich.prompt import Confirm, Prompt
    from rich.panel import Panel

    console = Console()

    # Welcome message
    console.print(Panel.fit(
        "[bold]AIR Toolkit - Interactive Setup[/bold]\n"
        "Let's create your AI Review & Development project!",
        border_style="blue"
    ))
    console.print()

    # Project name
    default_name = Path.cwd().name
    project_name = Prompt.ask(
        "[cyan]Project name[/cyan]",
        default=default_name
    )

    # Create new directory?
    if project_name != default_name:
        create_dir = Confirm.ask(
            f"Create new directory '{project_name}'?",
            default=True
        )
    else:
        create_dir = False
        console.print(f"[dim]✓ Using current directory: {Path.cwd()}[/dim]")
        console.print()

    # Project mode
    console.print("[cyan]Project mode:[/cyan]")
    console.print("  [bold]review[/bold] - Review existing code only")
    console.print("  [bold]collaborate[/bold] - Contribute changes back")
    console.print("  [bold]mixed[/bold] - Both review and collaboration")
    console.print()

    mode_choice = Prompt.ask(
        "Select mode",
        choices=["review", "collaborate", "mixed"],
        default="mixed"
    )

    # Task tracking
    track = Confirm.ask(
        "Enable task tracking (.air/ directory)?",
        default=True
    )

    # Project goals (optional)
    console.print()
    add_goals = Confirm.ask(
        "Would you like to add project goals?",
        default=False
    )

    goals = []
    if add_goals:
        console.print("[dim]Enter goals (one per line, empty line to finish):[/dim]")
        while True:
            goal = Prompt.ask(f"Goal {len(goals) + 1}", default="")
            if not goal:
                break
            goals.append(goal)

    # Confirmation
    console.print()
    console.print(Panel.fit(
        f"[bold]Configuration:[/bold]\n"
        f"Name: {project_name}\n"
        f"Mode: {mode_choice}\n"
        f"Tracking: {'Yes' if track else 'No'}\n"
        f"Goals: {len(goals)} goal(s)" +
        (f"\n  • " + "\n  • ".join(goals) if goals else ""),
        border_style="green",
        title="Review"
    ))
    console.print()

    if not Confirm.ask("Create project with these settings?", default=True):
        console.print("[yellow]✗[/yellow] Cancelled")
        return

    # Call init with collected parameters
    console.print()
    if create_dir:
        init.invoke(
            click.get_current_context(),
            name=project_name,
            mode=mode_choice,
            track=track,
            create_dir=True,
            interactive=False
        )
    else:
        init.invoke(
            click.get_current_context(),
            name=None,
            mode=mode_choice,
            track=track,
            create_dir=False,
            interactive=False
        )

    # Add goals to config if provided
    if goals:
        project_dir = Path.cwd() / project_name if create_dir else Path.cwd()
        config_path = project_dir / "air-config.json"

        import json
        with open(config_path) as f:
            config_data = json.load(f)

        config_data["goals"] = goals

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        info(f"Added {len(goals)} goal(s) to configuration")
