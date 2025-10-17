# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AIR (AI Review)** is a Python CLI toolkit for AI-assisted development and multi-project code assessment. It provides:
1. **Multi-Project Assessment**: Structured review projects to analyze multiple codebases
2. **AI Task Tracking**: Automatic task file generation and tracking for AI-assisted development

**Current Status**: v0.6.3 - Production-ready with deep analysis, dependency-aware multi-repo analysis, and agent coordination

## Essential Development Commands

### Setup & Installation
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
air --version
```

### Pre-Commit Workflow (CRITICAL)
**ALWAYS run these commands before committing:**
```bash
# Required checks
poetry run pytest          # All tests must pass
poetry run ruff check      # Linting must pass

# Optional but recommended
poetry run black src/ tests/           # Format code
poetry run mypy src/                   # Type checking
```

### Testing
```bash
# Run all tests (required before commit)
pytest

# Run with coverage
pytest --cov=air --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v

# Run single test
pytest tests/unit/test_models.py::test_air_config -v

# Run only unit or integration tests
pytest -m unit
pytest -m integration
```

### Building
```bash
# Build package for distribution
python -m build

# To publish (internal)
poetry build && poetry publish -r ld
```

## Architecture Overview

### Layered Architecture
```
CLI Layer (Click)
    ↓
Command Layer (commands/)
    ↓
Core Services (services/)
    ↓
Data Models (core/models.py, Pydantic)
```

### Key Components

**CLI Entry (`src/air/cli.py`)**
- Click-based command router
- 16 command groups registered

**Commands (`src/air/commands/`)**
- Each file implements one command group (e.g., `init.py`, `link.py`, `task.py`)
- Commands orchestrate services and handle user interaction
- Use Rich console for output

**Core Services (`src/air/services/`)**
- `filesystem.py` - File operations, symlinks
- `git.py` - Git operations via GitPython
- `templates.py` - Jinja2 template rendering
- `validator.py` - Project structure validation
- `classifier.py` - Technology stack detection
- `pr_generator.py` - GitHub PR creation
- `task_parser.py` - Task file parsing
- `analyzers/` - 5 specialized code analyzers (Security, Performance, Quality, Architecture, Structure)
- `detectors/` - Dependency detection (Python, JavaScript, Go)

**Data Models (`src/air/core/models.py`)**
- All models use Pydantic v2 for validation
- `AirConfig` - Project configuration (.air/air-config.json)
- `Resource` - Linked repository metadata
- `TaskFile` - Parsed task file metadata
- All enums use `StrEnum` (not deprecated `(str, Enum)` pattern)

**Utilities (`src/air/utils/`)**
- `console.py` - Rich console helpers (`info()`, `success()`, `warn()`, `error()`)
- `dates.py` - Date/time formatting
- `paths.py` - Path manipulation
- `errors.py` - Custom exception classes

### Project Structure Created by AIR
When `air init` creates a project, it generates:
```
project-name/
├── .air/
│   ├── air-config.json      # AirConfig model
│   ├── tasks/               # Task tracking (YYYYMMDD-NNN-HHMM-description.md)
│   │   └── archive/         # Archived tasks (YYYY-MM/)
│   ├── agents/              # Background agent metadata
│   ├── context/             # Architecture, conventions
│   └── templates/           # Task templates
├── repos/                   # Linked repositories (symlinks)
├── analysis/                # Analysis outputs
└── contributions/           # Staged contributions
```

## Code Conventions

### Python Style (Enforced)
- **Python version**: 3.10+ (use `str | None`, not `Optional[str]`)
- **Line length**: 100 characters
- **Type hints**: Required for all functions (mypy strict mode)
- **Enums**: Use `StrEnum` from `enum` module
- **Paths**: Use `pathlib.Path`, never string concatenation
- **Formatting**: Black (run before commit)
- **Linting**: Ruff (run before commit)
- **Docstrings**: Google style for public APIs

### Key Patterns

**Error Handling:**
```python
from air.utils.errors import AirError, ConfigError, ValidationError

# Raise custom errors with helpful messages
raise ConfigError(
    "Invalid configuration file",
    hint="Run 'air validate --fix' to repair"
)
```

**Console Output:**
```python
from air.utils.console import info, success, warn, error

info("Processing...")
success("Project created successfully")
warn("Resource not found")
error("Failed to validate", exit_code=1)  # Exits process
```

**Path Handling:**
```python
from pathlib import Path
from air.utils.paths import expand_path

# Always expand ~ in user paths
path = expand_path("~/repos/project")  # Returns absolute Path
```

**Template Rendering:**
```python
from air.services.templates import TemplateService

template_service = TemplateService()
content = template_service.render(
    "assessment/README.md.j2",
    {"name": "project", "mode": "review"}
)
```

## Critical Implementation Details

### Configuration Management
- Configuration stored in `.air/air-config.json`
- Validates against `AirConfig` Pydantic model
- Path fields automatically expand `~` via `expand_path()` validator
- Version field for future migration support

### Task File Naming
Two supported formats:
- **New format** (v0.6.0+): `YYYYMMDD-NNN-HHMM-description.md` (ordinal for multiple tasks per day)
- **Legacy format**: `YYYYMMDD-HHMM-description.md`

Task files track AI-assisted development work and should be committed with code changes.

### Resource Linking
- Resources symlinked to `repos/` directory (no copying)
- Support for review-only (read-only) and developer (writable) modes
- Technology stack auto-detection via `ClassificationService`
- All paths support shell expansion (`~`)

### Testing CLI Commands
Use Click's `CliRunner` for testing commands:
```python
from click.testing import CliRunner
from air.cli import main

def test_init_command():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["init", "test-project"])
        assert result.exit_code == 0
```

### Template Embedding
Templates embedded using `importlib.resources`:
```python
from importlib.resources import files
template_data = files("air.templates").joinpath("path/to/template.j2")
```

## Common Development Workflows

### Adding a New Command
1. Create `src/air/commands/mycommand.py`
2. Define Click command with `@click.command()`
3. Add to `src/air/cli.py`: `from air.commands import mycommand` and `main.add_command(mycommand.mycommand)`
4. Add tests in `tests/unit/test_mycommand.py` and `tests/integration/test_mycommand.py`
5. Run `poetry run pytest` before committing

### Adding a New Service
1. Create `src/air/services/myservice.py`
2. Define service class with clear public API
3. Add unit tests in `tests/unit/test_myservice.py`
4. Use from command layer

### Adding a New Pydantic Model
1. Add to `src/air/core/models.py`
2. Use `StrEnum` for enum fields
3. Add validators for path expansion if needed
4. Add tests in `tests/unit/test_models.py`

## Important Context Files

Before starting work, review:
- `docs/ARCHITECTURE.md` - Complete technical design (13KB, most comprehensive)
- `.air/tasks/` - Recent work and decisions (read latest 5-10 tasks)
- `README.md` - User-facing documentation and command reference
- This file (CLAUDE.md) - Development guidance

**Note**: `.air/context/architecture.md` and `.air/context/language.md` are templates generated by `air init`, not AIR toolkit architecture docs.

## Key Dependencies

**Core:**
- click >=8.1.0 - CLI framework
- rich >=13.0.0 - Terminal UI
- pydantic >=2.0.0 - Data validation (v2 syntax required)
- gitpython >=3.1.0 - Git operations (not shell commands)
- jinja2 >=3.1.0 - Template rendering
- psutil >=5.9.0 - Process management

**Dev:**
- pytest >=7.0.0 - Testing framework
- pytest-cov >=4.0.0 - Coverage reporting
- black >=23.0.0 - Code formatting
- ruff >=0.1.0 - Linting
- mypy >=1.0.0 - Type checking

## Package Distribution

AIR is published to PyPI. Build process:
```bash
# Standard build
python -m build

# Internal publish (LiveData)
poetry build && poetry publish -r ld
```

## AI Task Tracking Protocol (For Working in AIR Projects)

When working in a project that **uses** AIR (not the AIR toolkit itself), follow the automatic task tracking protocol documented in `.air/README.md` of that project:

1. Create task files automatically: `.air/tasks/YYYYMMDD-NNN-HHMM-description.md`
2. Record exact user prompt
3. Update task file as you work
4. Mark outcome when complete
5. Include task file in commits

**This protocol applies when working in AIR-managed projects, not when developing AIR toolkit itself.**

## Development Principles

1. **Use Poetry for dependency management** - Never use pip directly for package management
2. **Run tests before every commit** - `poetry run pytest && poetry run ruff check`
3. **Type hints are required** - Mypy strict mode enforced
4. **Use Pydantic v2 syntax** - Not v1
5. **Git operations via GitPython** - Not shell commands
6. **Cross-platform support** - Test on macOS, Linux, Windows
7. **Templates are embedded** - Use importlib.resources
8. **Rich console for output** - Use helper functions from `air.utils.console`
9. **Error messages must be actionable** - Include hints for resolution
10. **Never use Mermaid for docs** - User preference specified in global CLAUDE.md

## Test Coverage

- **372 tests total** (all passing)
- ~200 unit tests
- ~172 integration tests
- >80% code coverage
- Markers: `@pytest.mark.unit`, `@pytest.mark.integration`
