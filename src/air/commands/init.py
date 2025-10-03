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
from air.utils.console import error, info, success


@click.command()
@click.argument("name", default=".", required=False)
@click.option(
    "--mode",
    type=click.Choice(["review", "collaborate", "mixed"]),
    default="mixed",
    help="Project mode: review-only, collaborative, or mixed",
)
@click.option(
    "--track/--no-track",
    default=True,
    help="Initialize .ai/ task tracking",
)
def init(name: str, mode: str, track: bool) -> None:
    """Create new AIR assessment project.

    \b
    Examples:
      air init my-review              # Create mixed-mode project
      air init review --mode=review   # Review-only mode
      air init docs --mode=collaborate --no-track
    """
    # Determine project directory
    if name == ".":
        project_dir = Path.cwd()
        project_name = project_dir.name
    else:
        project_dir = Path.cwd() / name
        project_name = name

    info(f"Creating AIR project: {project_name}")
    info(f"Mode: {mode}")

    # Check if already in an AIR project
    if get_project_root() is not None:
        error(
            "Already in an AIR project",
            hint="Create new project in a different directory",
            exit_code=1,
        )

    # Check if directory exists and has content
    if project_dir.exists():
        if name != "." and any(project_dir.iterdir()):
            error(
                f"Directory not empty: {project_dir}",
                hint="Use an empty directory or specify a new name",
                exit_code=1,
            )

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
            context_path = project_dir / f".ai/context/{context_type}.md"
            create_file(context_path, context_content, overwrite=True)

        # Create templates directory
        templates_dir = project_dir / ".ai/templates"
        create_directory(templates_dir)

    success(f"Project created successfully: {project_dir}")

    # Show next steps
    print()  # Blank line
    info("Next steps:")
    if name != ".":
        print(f"  cd {name}")

    if mode in ["review", "mixed"]:
        print("  air link --review service-a:~/repos/service-a")
    if mode in ["collaborate", "mixed"]:
        print("  air link --collaborate docs:~/repos/docs")

    print("  air validate")
    print("  air status")
