"""Upgrade existing AIR projects to latest version."""

import json
import shutil
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from air import __version__
from air.services.filesystem import get_project_root
from air.utils.console import error, info, success, warn

console = Console()


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be upgraded without making changes")
@click.option("--force", is_flag=True, help="Overwrite existing files (use with caution)")
@click.option("--backup/--no-backup", default=True, help="Create backup before upgrading")
def upgrade(dry_run: bool, force: bool, backup: bool) -> None:
    """Upgrade AIR project to latest version.

    \b
    Safely upgrades your existing AIR project with:
    - New scripts (scripts/daily-analysis.sh)
    - New directories (.air/agents/, .air/shared/)
    - Updated templates
    - New configuration fields

    \b
    Examples:
      air upgrade                    # Preview changes
      air upgrade --dry-run          # Same as above (safe by default)
      air upgrade --force            # Apply changes
      air upgrade --force --no-backup  # Apply without backup (risky!)
    """
    project_root = get_project_root()
    if not project_root:
        error(
            "Not in an AIR project",
            hint="Run 'air init' to create a project or 'cd' to project directory",
            exit_code=1,
        )

    console.print()
    console.print("[bold cyan]AIR Project Upgrade[/bold cyan]")
    console.print()

    # Load current project config
    config_file = project_root / "air-config.json"
    if not config_file.exists():
        error("air-config.json not found", exit_code=1)

    config_data = json.loads(config_file.read_text())
    project_version = config_data.get("version", "1.0.0")  # Legacy projects have no version
    current_air_version = __version__

    info(f"Project version: {project_version}")
    info(f"AIR version: {current_air_version}")
    console.print()

    # Collect upgrade actions
    actions = []

    # 1. Check for missing directories
    missing_dirs = _check_directories(project_root)
    for dir_path, description in missing_dirs:
        actions.append(("create_dir", dir_path, description))

    # 2. Check for missing scripts
    missing_scripts = _check_scripts(project_root)
    for script_path, description in missing_scripts:
        actions.append(("create_file", script_path, description))

    # 3. Check for outdated templates
    outdated_templates = _check_templates(project_root, force)
    for template_path, description in outdated_templates:
        actions.append(("update_file", template_path, description))

    # 4. Check config schema
    config_updates = _check_config_schema(config_data)
    if config_updates:
        actions.append(("update_config", config_file, f"Add {len(config_updates)} new fields"))

    # Show upgrade plan
    if not actions:
        success("✓ Project is up to date! No upgrades needed.")
        return

    table = Table(title=f"[bold]Upgrade Plan ({len(actions)} actions)[/bold]", show_header=True)
    table.add_column("Action", style="cyan", width=12)
    table.add_column("Path", style="yellow")
    table.add_column("Description", style="white")

    for action_type, path, description in actions:
        action_icon = {
            "create_dir": "📁 Create",
            "create_file": "📄 Create",
            "update_file": "🔄 Update",
            "update_config": "⚙️  Update",
        }.get(action_type, action_type)

        rel_path = str(Path(path).relative_to(project_root)) if project_root in Path(path).parents else str(path)
        table.add_row(action_icon, rel_path, description)

    console.print(table)
    console.print()

    if dry_run or not force:
        warn("Dry run mode - no changes made")
        console.print()
        console.print("[dim]To apply changes, run:[/dim]")
        console.print("[cyan]  air upgrade --force[/cyan]")
        console.print()
        return

    # Apply changes
    if backup:
        _create_backup(project_root)

    for action_type, path, description in actions:
        try:
            if action_type == "create_dir":
                Path(path).mkdir(parents=True, exist_ok=True)
                success(f"✓ Created {Path(path).relative_to(project_root)}")

            elif action_type == "create_file":
                _create_file(path, project_root)
                success(f"✓ Created {Path(path).relative_to(project_root)}")

            elif action_type == "update_file":
                _update_file(path, project_root)
                success(f"✓ Updated {Path(path).relative_to(project_root)}")

            elif action_type == "update_config":
                _update_config(path, config_updates)
                success(f"✓ Updated air-config.json")

        except Exception as e:
            error(f"Failed to {action_type} {path}: {e}")

    console.print()
    success(f"✓ Upgrade complete! Project upgraded to AIR v{current_air_version}")
    console.print()


def _check_directories(project_root: Path) -> list[tuple[Path, str]]:
    """Check for missing directories.

    Returns:
        List of (path, description) tuples
    """
    missing = []

    required_dirs = [
        (project_root / ".air" / "agents", "Background agent metadata"),
        (project_root / ".air" / "shared", "Shared state between agents"),
        (project_root / "scripts", "Automation scripts"),
        (project_root / "analysis" / "reviews", "Analysis findings"),
    ]

    for dir_path, description in required_dirs:
        if not dir_path.exists():
            missing.append((dir_path, description))

    return missing


def _check_scripts(project_root: Path) -> list[tuple[Path, str]]:
    """Check for missing scripts.

    Returns:
        List of (path, description) tuples
    """
    missing = []

    scripts = [
        (project_root / "scripts" / "daily-analysis.sh", "Daily analysis automation"),
        (project_root / "scripts" / "README.md", "Scripts documentation"),
    ]

    for script_path, description in scripts:
        if not script_path.exists():
            missing.append((script_path, description))

    return missing


def _check_templates(project_root: Path, force: bool) -> list[tuple[Path, str]]:
    """Check for outdated templates.

    Returns:
        List of (path, description) tuples
    """
    outdated = []

    # Only update templates if --force specified
    # (we don't want to overwrite user customizations)
    if not force:
        return outdated

    templates_dir = project_root / ".air" / "templates"
    if templates_dir.exists():
        # Could compare checksums/versions here
        # For now, we skip template updates unless explicitly forced
        pass

    return outdated


def _check_config_schema(config_data: dict) -> dict:
    """Check for missing config fields.

    Returns:
        Dict of field_name: default_value to add
    """
    updates = {}

    # Check for missing version field (legacy projects)
    if "version" not in config_data:
        updates["version"] = "2.0.0"

    return updates


def _create_backup(project_root: Path) -> None:
    """Create backup of project before upgrading."""
    from datetime import datetime

    backup_name = f".air-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    backup_path = project_root / backup_name

    info(f"Creating backup: {backup_name}")

    # Backup critical files
    files_to_backup = [
        "air-config.json",
        ".air/tasks",
        ".air/context",
        ".air/templates",
    ]

    backup_path.mkdir(exist_ok=True)

    for file_path in files_to_backup:
        source = project_root / file_path
        if source.exists():
            dest = backup_path / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            if source.is_dir():
                shutil.copytree(source, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(source, dest)

    success(f"✓ Backup created: {backup_name}")


def _create_file(file_path: Path, project_root: Path) -> None:
    """Create a new file from template or embedded content."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Special handling for specific files
    if file_path.name == "daily-analysis.sh":
        # Copy from air-toolkit repo if available, otherwise download from GitHub
        toolkit_script = Path(__file__).parent.parent.parent.parent / "scripts" / "daily-analysis.sh"

        if toolkit_script.exists():
            # Development mode - copy from repo
            script_content = toolkit_script.read_text()
        else:
            # Packaged mode - download from GitHub
            import urllib.request
            url = "https://raw.githubusercontent.com/LiveData-Inc/air-toolkit/main/scripts/daily-analysis.sh"
            try:
                with urllib.request.urlopen(url) as response:
                    script_content = response.read().decode('utf-8')
            except Exception as e:
                error(f"Failed to download daily-analysis.sh: {e}", exit_code=1)

        file_path.write_text(script_content)
        file_path.chmod(0o755)  # Make executable

    elif file_path.name == "README.md" and file_path.parent.name == "scripts":
        toolkit_readme = Path(__file__).parent.parent.parent.parent / "scripts" / "README.md"

        if toolkit_readme.exists():
            readme_content = toolkit_readme.read_text()
        else:
            import urllib.request
            url = "https://raw.githubusercontent.com/LiveData-Inc/air-toolkit/main/scripts/README.md"
            try:
                with urllib.request.urlopen(url) as response:
                    readme_content = response.read().decode('utf-8')
            except Exception:
                readme_content = "# Scripts\n\nSee https://github.com/LiveData-Inc/air-toolkit/tree/main/scripts\n"

        file_path.write_text(readme_content)

    else:
        # Generic file creation
        file_path.touch()


def _update_file(file_path: Path, project_root: Path) -> None:
    """Update an existing file (with backup)."""
    if file_path.exists():
        backup_path = file_path.with_suffix(file_path.suffix + ".bak")
        shutil.copy2(file_path, backup_path)

    _create_file(file_path, project_root)


def _update_config(config_path: Path, updates: dict) -> None:
    """Update air-config.json with new fields."""
    config_data = json.loads(config_path.read_text())

    # Add new fields
    for key, value in updates.items():
        if key not in config_data:
            config_data[key] = value

    # Write back
    config_path.write_text(json.dumps(config_data, indent=2))
