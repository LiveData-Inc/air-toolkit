"""Validate AIR project structure."""

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air.core.models import AirConfig
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
                    AirConfig(**config_data)
            except Exception as e:
                errors.append(f"Invalid config: {e}")
        else:
            errors.append("Missing air-config.json")

    # Check links in repos/ and contributions/ directories
    fixed = []
    if check_type in ["links", "all"]:
        # First, check that configured resources actually exist
        config_path = project_root / "air-config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config_data = json.load(f)
                    config = AirConfig(**config_data)

                    # Check all configured resources
                    for resource in config.get_all_resources():
                        # Check if symlink/directory exists in repos/
                        link_path = project_root / "repos" / resource.name
                        source_path = Path(resource.path).expanduser()

                        if not link_path.exists():
                            # Missing symlink - try to fix if --fix is enabled
                            if fix:
                                if source_path.exists():
                                    # Source exists, recreate symlink
                                    try:
                                        from air.services.filesystem import create_symlink
                                        create_symlink(source_path, link_path)
                                        fixed.append(f"Recreated symlink: repos/{resource.name}")
                                    except Exception as e:
                                        errors.append(
                                            f"Failed to recreate symlink repos/{resource.name}: {e}"
                                        )
                                else:
                                    errors.append(
                                        f"Cannot fix repos/{resource.name}: "
                                        f"source path does not exist: {source_path}"
                                    )
                            else:
                                errors.append(
                                    f"Missing resource: repos/{resource.name} "
                                    f"(configured in air-config.json but not found)"
                                )
                        elif link_path.is_symlink() and not is_symlink_valid(link_path):
                            # Broken symlink - try to fix if --fix is enabled
                            if fix:
                                if source_path.exists():
                                    # Remove broken symlink and recreate
                                    try:
                                        from air.services.filesystem import create_symlink
                                        link_path.unlink()
                                        create_symlink(source_path, link_path)
                                        fixed.append(f"Fixed broken symlink: repos/{resource.name}")
                                    except Exception as e:
                                        errors.append(
                                            f"Failed to fix broken symlink repos/{resource.name}: {e}"
                                        )
                                else:
                                    errors.append(
                                        f"Cannot fix repos/{resource.name}: "
                                        f"source path does not exist: {source_path}"
                                    )
                            else:
                                errors.append(f"Broken symlink: repos/{resource.name}")
            except Exception as e:
                errors.append(f"Failed to validate resources from config: {e}")

        # Then, check for unexpected/orphaned items in repos/ and contributions/
        for dir_name in ["repos", "contributions"]:
            resource_path = project_root / dir_name
            if resource_path.exists():
                for item in resource_path.iterdir():
                    if item.name == ".gitkeep":
                        continue
                    if item.is_symlink():
                        if not is_symlink_valid(item):
                            errors.append(f"Broken symlink: {dir_name}/{item.name}")
                    elif item.is_dir():
                        # Check if it's a git repository
                        if not (item / ".git").exists():
                            warnings.append(
                                f"Not a git repository: {dir_name}/{item.name}"
                            )

    # Output results
    if output_format == "json":
        result = {
            "success": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "fixed": fixed if fix else [],
            "project_root": str(project_root),
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if len(errors) == 0 else 3)
    else:
        # Human-readable output
        if fixed:
            table = Table(title="Fixed Issues", style="green")
            table.add_column("Action", style="green")
            for fix_msg in fixed:
                table.add_row(fix_msg)
            console.print(table)
            console.print()

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

        if not errors and not warnings and not fixed:
            success("Project structure is valid")
            sys.exit(0)
        elif not errors and fixed:
            print()
            success(f"Fixed {len(fixed)} issue(s)")
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
