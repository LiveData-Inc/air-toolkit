"""Template rendering service for AIR toolkit."""

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from air.utils.console import error


def get_template_path() -> Path:
    """Get the path to the templates directory.

    Returns:
        Path to templates directory
    """
    # Get path to templates in package
    try:
        # Try to get templates module
        import air

        air_package = Path(air.__file__).parent
        templates_path = air_package / "templates"

        if not templates_path.exists():
            error(
                f"Templates directory not found at {templates_path}",
                hint="Ensure air-toolkit is properly installed",
                exit_code=2,
            )

        return templates_path
    except (ImportError, AttributeError, TypeError) as e:
        error(
            f"Failed to locate templates directory: {e}",
            hint="Ensure air-toolkit is properly installed",
            exit_code=2,
        )


def render_template(template_name: str, context: dict[str, Any]) -> str:
    """Render a Jinja2 template with given context.

    Args:
        template_name: Template filename (e.g., "assessment/README.md.j2")
        context: Template context variables

    Returns:
        Rendered template content

    Raises:
        SystemExit: If template not found or rendering fails
    """
    template_dir = get_template_path()

    try:
        env = Environment(
            loader=FileSystemLoader(template_dir),
            trim_blocks=True,
            lstrip_blocks=True,
        )
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        error(
            f"Failed to render template {template_name}: {e}",
            hint="Check template syntax and context variables",
            exit_code=2,
        )


def render_assessment_templates(
    project_name: str,
    mode: str,
    created: datetime,
    goals: list[str] | None = None,
) -> dict[str, str]:
    """Render all assessment project templates.

    Args:
        project_name: Name of the project
        mode: Project mode (review, collaborate, mixed)
        created: Creation timestamp
        goals: Optional list of project goals

    Returns:
        Dictionary mapping filenames to rendered content
    """
    context = {
        "name": project_name,
        "mode": mode,
        "created": created.strftime("%Y-%m-%d"),
        "goals": goals or [],
    }

    templates = {
        "README.md": render_template("assessment/README.md.j2", context),
        "CLAUDE.md": render_template("assessment/CLAUDE.md.j2", context),
        ".gitignore": render_template("assessment/gitignore.j2", context),
    }

    return templates


def render_ai_templates() -> dict[str, str]:
    """Render AI task tracking templates.

    Returns:
        Dictionary mapping filenames to rendered content
    """
    templates = {
        ".air/README.md": render_template("ai/README.md.j2", {}),
    }

    return templates


def create_config_file(
    project_name: str,
    mode: str,
    created: datetime,
    goals: list[str] | None = None,
) -> str:
    """Create air-config.json content.

    Args:
        project_name: Name of the project
        mode: Project mode (review, collaborate, mixed)
        created: Creation timestamp
        goals: Optional list of project goals

    Returns:
        JSON configuration content
    """
    import json

    config = {
        "version": "2.0.0",
        "name": project_name,
        "mode": mode,
        "created": created.isoformat(),
        "resources": {"review": [], "develop": []},
        "goals": goals or [],
    }

    return json.dumps(config, indent=2) + "\n"


def get_context_template(context_type: str) -> str:
    """Get a context file template.

    Args:
        context_type: Type of context (architecture, language)

    Returns:
        Template content for context file
    """
    templates = {
        "architecture": """# Architecture

## System Overview

[Describe the high-level architecture]

## Key Components

[List and describe major components]

## Design Patterns

[Document important patterns and decisions]

## Data Flow

[Explain how data flows through the system]

## External Dependencies

[List third-party services, APIs, databases]

## Architectural Decisions

[Document significant choices and rationale]
""",
        "language": """# Code Conventions

## Language-Specific Rules

[Document language conventions - Python, TypeScript, etc.]

## Naming Conventions

- Files: snake_case
- Functions: snake_case
- Classes: PascalCase
- Constants: UPPER_SNAKE_CASE

## Common Patterns

[Document common patterns used in this project]

## Tools

- Formatter: [e.g., black, prettier]
- Linter: [e.g., ruff, eslint]
- Type checker: [e.g., mypy, tsc]

## Testing

[Document testing approach and conventions]
""",
    }

    return templates.get(context_type, "")


def create_claude_commands(project_dir: Path) -> bool:
    """Create Claude Code slash command files in .claude/commands/.

    Args:
        project_dir: Root directory of the project

    Returns:
        True if commands were created successfully, False otherwise
    """
    import importlib.resources
    from air.services.filesystem import create_directory, create_file
    from air.utils.console import info, warn

    # Create .claude/commands directory
    commands_dir = project_dir / ".claude" / "commands"
    create_directory(commands_dir)

    # List of slash command files to copy
    command_files = [
        "air-analyze.md",
        "air-findings.md",
        "air-link.md",
        "air-review.md",
        "air-status.md",
        "air-summary.md",
        "air-task-complete.md",
        "air-task.md",
        "air-validate.md",
    ]

    # Copy each command file from templates
    try:
        for command_file in command_files:
            # Read from embedded templates
            try:
                template_content = importlib.resources.read_text(
                    "air.templates.claude_commands", command_file
                )
            except FileNotFoundError:
                # Fallback: try reading from source directory during development
                template_path = get_template_path() / "claude_commands" / command_file
                if template_path.exists():
                    template_content = template_path.read_text()
                else:
                    warn(f"Claude command template not found: {command_file}")
                    continue

            # Write to project
            command_path = commands_dir / command_file
            create_file(command_path, template_content, overwrite=True)

        info("Created Claude Code slash commands in .claude/commands/")
        return True
    except Exception as e:
        warn(f"Could not create Claude commands: {e}")
        return False
