"""Validate AIR project structure."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.core.models import AssessmentConfig
from air.services.filesystem import get_project_root, is_symlink_valid, validate_project_structure
from air.utils.console import error, info, success, warn

console = Console()


@click.command()
@click.option(
    "--type",
    "check_type",
    type=click.Choice(["structure", "links", "config", "all"]),
    default="all",
    help="Type of validation to perform",
)
@click.option(
    "--fix",
    is_flag=True,
    help="Attempt to fix issues automatically",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["human", "json"]),
    default="human",
    help="Output format",
)
def validate(check_type: str, fix: bool, output_format: str) -> None:
    """Validate AIR project structure.

    \b
    Checks:
      - Directory structure (review/, collaborate/, analysis/, etc.)
      - Symlinks and clones validity
      - Configuration file (air-config.json)
      - Repository accessibility

    \b
    Examples:
      air validate
      air validate --type=links
      air validate --fix
      air validate --format=json
    """
    # Find project root
    project_root = get_project_root()
    if project_root is None:
        if output_format == "json":
            print(json.dumps({"success": False, "error": "Not an AIR project"}))
        else:
            error(
                "Not an AIR project",
                hint="Run 'air init' to create a new AIR project",
                exit_code=1,
            )

    if output_format == "human":
        info("Validating project structure...")

    errors = []
    warnings = []

    # Check structure
    if check_type in ["structure", "all"]:
        config_path = project_root / "air-config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)
                    mode = config_data.get("mode", "mixed")
                    structure_errors = validate_project_structure(project_root, mode)
                    errors.extend(structure_errors)
            except Exception as e:
                errors.append(f"Failed to read config: {e}")
        else:
            errors.append("Missing air-config.json")

    # Check config
    if check_type in ["config", "all"]:
        config_path = project_root / "air-config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)
                    # Validate against Pydantic model
                    AssessmentConfig(**config_data)
            except Exception as e:
                errors.append(f"Invalid config: {e}")
        else:
            errors.append("Missing air-config.json")

    # Check links
    if check_type in ["links", "all"]:
        for resource_dir in ["review", "collaborate"]:
            resource_path = project_root / resource_dir
            if resource_path.exists():
                for item in resource_path.iterdir():
                    if item.name == ".gitkeep":
                        continue
                    if item.is_symlink():
                        if not is_symlink_valid(item):
                            errors.append(f"Broken symlink: {resource_dir}/{item.name}")
                    elif item.is_dir():
                        # Check if it's a git repository
                        if not (item / ".git").exists():
                            warnings.append(
                                f"Not a git repository: {resource_dir}/{item.name}"
                            )

    # Output results
    if output_format == "json":
        result = {
            "success": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "project_root": str(project_root),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if len(errors) == 0 else 3)
    else:
        # Human-readable output
        if errors:
            table = Table(title="Validation Errors", style="red")
            table.add_column("Issue", style="red")
            for err in errors:
                table.add_row(err)
            console.print(table)

        if warnings:
            table = Table(title="Warnings", style="yellow")
            table.add_column("Warning", style="yellow")
            for wrn in warnings:
                table.add_row(wrn)
            console.print(table)

        if not errors and not warnings:
            success("Project structure is valid")
            sys.exit(0)
        elif errors:
            print()
            error(
                f"Validation failed with {len(errors)} error(s)",
                hint="Run 'air validate --fix' to attempt automatic fixes" if fix is False else None,
                exit_code=3,
            )
        else:
            print()
            warn(f"Validation completed with {len(warnings)} warning(s)")
            sys.exit(0)
