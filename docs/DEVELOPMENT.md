# AIR Toolkit - Development Guide

**Version:** 0.1.0
**Last Updated:** 2025-10-03

## 1. Getting Started

### 1.1 Prerequisites

**Required:**
- Python 3.10 or higher
- Git 2.30+
- pip or pipx

**Recommended:**
- GitHub CLI (`gh`) - for PR functionality
- Virtual environment tool (venv, virtualenv, or conda)

### 1.2 Initial Setup

```bash
# Clone repository
git clone https://github.com/LiveData-Inc/air-toolkit.git
cd air-toolkit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
air --version
```

### 1.3 Verify Setup

```bash
# Run tests
pytest

# Check code formatting
black --check src/

# Run linter
ruff check src/

# Type checking
mypy src/
```

## 2. Development Workflow

### 2.1 Making Changes

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes:**
   - Edit code in `src/air/`
   - Add tests in `tests/`
   - Update documentation if needed

3. **Test changes:**
   ```bash
   # Run specific test
   pytest tests/unit/test_commands.py -v

   # Run all tests with coverage
   pytest --cov=air --cov-report=html

   # View coverage report
   open htmlcov/index.html
   ```

4. **Format and lint:**
   ```bash
   # Format code
   black src/ tests/

   # Check with ruff
   ruff check src/ tests/ --fix

   # Type check
   mypy src/
   ```

5. **Commit:**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

6. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   gh pr create
   ```

### 2.2 Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(commands): add air classify command
fix(git): handle repositories without remotes
docs(readme): update installation instructions
test(core): add tests for AssessmentConfig
```

## 3. Project Structure

### 3.1 Source Code Organization

```
src/air/
├── cli.py              # Entry point, command routing
├── commands/           # Command implementations
│   └── *.py           # One file per command/group
├── core/              # Business logic
│   ├── assessment.py  # Assessment project logic
│   ├── tasks.py       # Task management
│   ├── config.py      # Configuration management
│   └── models.py      # Pydantic models
├── services/          # Infrastructure services
│   ├── git.py         # Git operations
│   ├── filesystem.py  # File operations
│   ├── templates.py   # Template rendering
│   └── validator.py   # Validation
├── templates/         # Jinja2 templates
│   ├── assessment/    # Assessment project templates
│   └── ai/           # .ai folder templates
└── utils/            # Utilities
    ├── console.py     # Rich console helpers
    ├── dates.py       # Date/time utilities
    └── paths.py       # Path helpers
```

### 3.2 Adding a New Command

**Step 1: Create command module**

Create `src/air/commands/yourcommand.py`:

```python
"""Your command description."""

import click
from rich.console import Console

console = Console()


@click.command()
@click.argument("arg1")
@click.option("--flag", is_flag=True, help="Flag description")
def yourcommand(arg1: str, flag: bool) -> None:
    """Command help text.

    \b
    Examples:
      air yourcommand value
      air yourcommand value --flag
    """
    console.print(f"[blue]ℹ[/blue] Running yourcommand with {arg1}")

    # Implementation here

    console.print("[green]✓[/green] Success")
```

**Step 2: Register in `__init__.py`**

Edit `src/air/commands/__init__.py`:

```python
from . import yourcommand

__all__ = [
    # ... existing commands
    "yourcommand",
]
```

**Step 3: Add to CLI**

Edit `src/air/cli.py`:

```python
from air.commands import yourcommand

# In main() function:
main.add_command(yourcommand.yourcommand)
```

**Step 4: Add tests**

Create `tests/unit/test_commands/test_yourcommand.py`:

```python
from click.testing import CliRunner
from air.cli import main


def test_yourcommand():
    runner = CliRunner()
    result = runner.invoke(main, ["yourcommand", "value"])
    assert result.exit_code == 0
    assert "Success" in result.output
```

**Step 5: Update documentation**

Add to `docs/COMMANDS.md`

### 3.3 Adding a Core Service

Create `src/air/services/yourservice.py`:

```python
"""Your service description."""

from typing import Protocol


class YourServiceProtocol(Protocol):
    """Protocol defining service interface."""

    def do_something(self, arg: str) -> bool:
        """Do something."""
        ...


class YourService:
    """Implementation of your service."""

    def __init__(self) -> None:
        """Initialize service."""
        pass

    def do_something(self, arg: str) -> bool:
        """Do something.

        Args:
            arg: Description

        Returns:
            True if successful

        Raises:
            YourServiceError: If operation fails
        """
        # Implementation
        return True
```

### 3.4 Adding a Template

Create template file in `src/air/templates/`:

```jinja2
{# src/air/templates/assessment/README.md.j2 #}
# {{ project_name }}

Created: {{ created_date }}
Mode: {{ mode }}

## Goals

{% for goal in goals %}
{{ loop.index }}. {{ goal }}
{% endfor %}

## Setup

Run `air validate` to check project structure.
```

Load and render in code:

```python
from air.services.templates import TemplateEngine

engine = TemplateEngine()
content = engine.render(
    "assessment/README.md.j2",
    project_name="my-project",
    created_date="2025-10-03",
    mode="mixed",
    goals=["Goal 1", "Goal 2"]
)
```

## 4. Testing

### 4.1 Test Organization

```
tests/
├── unit/                      # Unit tests (fast, isolated)
│   ├── test_commands/        # Command tests
│   ├── test_core/            # Core logic tests
│   ├── test_services/        # Service tests
│   └── test_models.py        # Model tests
│
├── integration/              # Integration tests (slower)
│   ├── test_init_workflow.py
│   ├── test_link_workflow.py
│   └── test_pr_workflow.py
│
└── fixtures/                 # Test data
    ├── sample_configs/
    │   └── valid_config.json
    ├── sample_repos/
    └── sample_tasks/
```

### 4.2 Writing Tests

**Unit Test Example:**

```python
import pytest
from air.core.config import ConfigManager
from air.core.models import AssessmentConfig, ProjectMode


def test_load_config(tmp_path):
    """Test loading configuration file."""
    # Arrange
    config_path = tmp_path / ".assess-config.json"
    config_data = {
        "version": "2.0.0",
        "name": "test-project",
        "mode": "mixed",
        "created": "2025-10-03T10:00:00Z",
        "resources": {"review": [], "collaborate": []},
        "goals": []
    }
    config_path.write_text(json.dumps(config_data))

    manager = ConfigManager(tmp_path)

    # Act
    config = manager.load()

    # Assert
    assert config.name == "test-project"
    assert config.mode == ProjectMode.MIXED
```

**Integration Test Example:**

```python
from click.testing import CliRunner
from air.cli import main
import json


def test_init_and_validate_workflow(tmp_path):
    """Test complete init -> validate workflow."""
    runner = CliRunner()

    with runner.isolated_filesystem(temp_dir=tmp_path):
        # Initialize project
        result = runner.invoke(main, ["init", "test-project"])
        assert result.exit_code == 0

        # Validate created project
        result = runner.invoke(main, ["validate"],
                             cwd="test-project")
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
```

**Testing Commands:**

```python
from click.testing import CliRunner
from air.cli import main


def test_command_with_options():
    """Test command with various options."""
    runner = CliRunner()

    # Test with flag
    result = runner.invoke(main, ["yourcommand", "arg", "--flag"])
    assert result.exit_code == 0

    # Test without flag
    result = runner.invoke(main, ["yourcommand", "arg"])
    assert result.exit_code == 0
```

### 4.3 Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_commands/test_init.py

# Run specific test function
pytest tests/unit/test_commands/test_init.py::test_init_creates_structure

# Run with coverage
pytest --cov=air --cov-report=html

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Run tests matching pattern
pytest -k "test_init"
```

### 4.4 Test Coverage Goals

- Overall coverage: > 80%
- Critical paths: > 95%
- New code: 100% (enforce in PR review)

## 5. Code Quality

### 5.1 Formatting with Black

```bash
# Format all code
black src/ tests/

# Check without modifying
black --check src/

# Format specific file
black src/air/commands/init.py
```

**Configuration** (in `pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']
```

### 5.2 Linting with Ruff

```bash
# Check all code
ruff check src/ tests/

# Fix auto-fixable issues
ruff check src/ tests/ --fix

# Check specific file
ruff check src/air/cli.py
```

**Configuration** (in `pyproject.toml`):
```toml
[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "N", "W"]
```

### 5.3 Type Checking with mypy

```bash
# Check all code
mypy src/

# Check specific module
mypy src/air/core/

# Show error codes
mypy src/ --show-error-codes
```

**Configuration** (in `pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### 5.4 Pre-commit Hooks

Install pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.9.1
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## 6. Documentation

### 6.1 Code Documentation

**Module docstrings:**
```python
"""Brief module description.

Longer description if needed.
"""
```

**Class docstrings:**
```python
class YourClass:
    """Brief class description.

    Attributes:
        attr1: Description of attr1
        attr2: Description of attr2
    """
```

**Function docstrings (Google style):**
```python
def your_function(arg1: str, arg2: int) -> bool:
    """Brief function description.

    Longer description if needed.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When arg1 is invalid

    Examples:
        >>> your_function("test", 42)
        True
    """
```

### 6.2 User Documentation

Update these files when adding features:

- `README.md` - Overview and quick start
- `docs/SPECIFICATION.md` - Feature specifications
- `docs/COMMANDS.md` - Command reference
- `docs/ARCHITECTURE.md` - Architecture decisions

### 6.3 Changelog

Update `CHANGELOG.md` for every PR:

```markdown
## [Unreleased]

### Added
- New `air classify` command for resource classification

### Changed
- Improved validation error messages

### Fixed
- Fix symlink validation on Windows
```

## 7. Release Process

### 7.1 Version Bumping

1. Update version in `pyproject.toml`
2. Update `src/air/__init__.py`
3. Update `CHANGELOG.md` (move Unreleased to version)
4. Commit: `git commit -m "chore: bump version to X.Y.Z"`
5. Tag: `git tag vX.Y.Z`
6. Push: `git push && git push --tags`

### 7.2 Building Package

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Check built package
twine check dist/*

# Upload to TestPyPI (for testing)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

### 7.3 GitHub Release

```bash
# Create release via gh CLI
gh release create vX.Y.Z \
  --title "Version X.Y.Z" \
  --notes "See CHANGELOG.md for details" \
  dist/*
```

## 8. Debugging

### 8.1 Interactive Debugging

```python
# Add breakpoint in code
breakpoint()

# Or use pdb
import pdb; pdb.set_trace()
```

### 8.2 Verbose Mode (Future)

Add `--debug` flag:

```python
@click.group()
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.pass_context
def main(ctx, debug):
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug

    if debug:
        logging.basicConfig(level=logging.DEBUG)
```

### 8.3 Testing CLI Interactively

```bash
# Use CliRunner in interactive Python
python
>>> from click.testing import CliRunner
>>> from air.cli import main
>>> runner = CliRunner()
>>> result = runner.invoke(main, ["init", "test"])
>>> print(result.output)
```

## 9. Common Tasks

### 9.1 Adding a New Dependency

```bash
# Add to pyproject.toml dependencies
# Then reinstall
pip install -e ".[dev]"
```

### 9.2 Updating Dependencies

```bash
# Update all dependencies
pip install --upgrade -e ".[dev]"

# Update specific package
pip install --upgrade rich
```

### 9.3 Regenerating Requirements

```bash
# Export current environment (if needed)
pip freeze > requirements-freeze.txt
```

## 10. Troubleshooting

### 10.1 Import Errors

```bash
# Reinstall in editable mode
pip install -e .
```

### 10.2 Test Failures

```bash
# Run with verbose output
pytest -vv

# Show print statements
pytest -s

# Drop into debugger on failure
pytest --pdb
```

### 10.3 Type Checking Errors

```bash
# Generate mypy report
mypy src/ --html-report mypy-report
open mypy-report/index.html
```

## 11. Resources

### 11.1 Python Resources

- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Docstring Conventions (PEP 257)](https://peps.python.org/pep-0257/)

### 11.2 Tool Documentation

- [Click](https://click.palletsprojects.com/)
- [Rich](https://rich.readthedocs.io/)
- [Pydantic](https://docs.pydantic.dev/)
- [pytest](https://docs.pytest.org/)
- [Black](https://black.readthedocs.io/)
- [Ruff](https://beta.ruff.rs/docs/)

### 11.3 Project Documentation

- [Specification](SPECIFICATION.md)
- [Architecture](ARCHITECTURE.md)
- [Commands Reference](COMMANDS.md)
