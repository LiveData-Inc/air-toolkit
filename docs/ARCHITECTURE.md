# AIR Toolkit - Architecture

**Version:** 0.3.1
**Last Updated:** 2025-10-04

## 1. System Architecture

### 1.1 High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                     CLI Entry Point                      │
│                    (air command)                         │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Command Router (Click)                  │
│  ┌──────────────┬──────────────┬────────────────────┐  │
│  │  Assessment  │  Task Track  │    Utilities       │  │
│  │   Commands   │   Commands   │    Commands        │  │
│  └──────────────┴──────────────┴────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         ▼           ▼           ▼
┌────────────┐ ┌──────────┐ ┌──────────┐
│ Assessment │ │   Task   │ │  Config  │
│   Engine   │ │  Manager │ │  Manager │
└────────────┘ └──────────┘ └──────────┘
      │              │             │
      ▼              ▼             ▼
┌─────────────────────────────────────────┐
│          Core Services Layer             │
│  ┌───────┬──────┬────────┬───────────┐ │
│  │  Git  │ File │ Template│ Validator │ │
│  │Service│System│ Engine  │  Service  │ │
│  └───────┴──────┴────────┴───────────┘ │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│         External Dependencies            │
│  • Git repositories                      │
│  • File system (symlinks, files)        │
│  • GitHub API (via gh CLI)              │
└─────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

**CLI Layer**
- Parse command-line arguments
- Route to appropriate command handler
- Handle errors and user feedback
- Rich terminal output

**Command Layer**
- Implement specific commands
- Validate inputs
- Orchestrate core services
- Format and display results

**Core Services**
- **GitService**: Git operations (clone, branch, commit, push)
- **FileSystem**: File/directory operations, symlinks
- **TemplateEngine**: Load and render templates
- **ValidatorService**: Validate projects, configs, resources

**Business Logic**
- **AssessmentEngine**: Project creation, resource linking
- **TaskManager**: Task file CRUD operations
- **ConfigManager**: Read/write configuration files

## 2. Directory Structure

```
air-toolkit/
├── src/
│   └── air/
│       ├── __init__.py
│       ├── cli.py              # Main CLI entry point
│       │
│       ├── commands/           # Command implementations
│       │   ├── __init__.py
│       │   ├── init.py         # air init
│       │   ├── link.py         # air link
│       │   ├── validate.py     # air validate
│       │   ├── status.py       # air status
│       │   ├── classify.py     # air classify
│       │   ├── pr.py           # air pr
│       │   ├── task.py         # air task
│       │   ├── track.py        # air track
│       │   └── summary.py      # air summary
│       │
│       ├── core/               # Core business logic
│       │   ├── __init__.py
│       │   ├── assessment.py   # Assessment engine
│       │   ├── tasks.py        # Task management
│       │   ├── config.py       # Config management
│       │   └── models.py       # Data models (Pydantic)
│       │
│       ├── services/           # Infrastructure services
│       │   ├── __init__.py
│       │   ├── git.py          # Git operations
│       │   ├── filesystem.py   # File operations
│       │   ├── templates.py    # Template rendering
│       │   └── validator.py    # Validation logic
│       │
│       ├── templates/          # Embedded templates
│       │   ├── assessment/     # Assessment project templates
│       │   │   ├── README.md.j2
│       │   │   ├── CLAUDE.md.j2
│       │   │   └── .gitignore.j2
│       │   └── ai/             # .ai folder templates
│       │       ├── README.md.j2
│       │       ├── task.md.j2
│       │       └── context/
│       │           ├── architecture.md.j2
│       │           └── language.md.j2
│       │
│       └── utils/              # Utilities
│           ├── __init__.py
│           ├── console.py      # Rich console helpers
│           ├── dates.py        # Date/time utilities
│           └── paths.py        # Path manipulation
│
├── tests/                      # Test suite
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── docs/                       # Documentation
│   ├── SPECIFICATION.md
│   ├── ARCHITECTURE.md (this file)
│   ├── DEVELOPMENT.md
│   └── COMMANDS.md
│
├── examples/                   # Example projects
│   ├── review-only/
│   ├── collaborative/
│   └── mixed/
│
├── pyproject.toml              # Package configuration
├── README.md
└── LICENSE
```

## 3. Data Models

### 3.1 Core Models (Pydantic)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import StrEnum
from typing import Literal


class ProjectMode(StrEnum):
    """Assessment project mode."""
    REVIEW = "review"
    DEVELOP = "develop"
    MIXED = "mixed"


class ResourceType(StrEnum):
    """Type of linked resource."""
    LIBRARY = "library"
    DOCUMENTATION = "documentation"
    SERVICE = "service"


class ResourceRelationship(StrEnum):
    """Relationship to resource."""
    REVIEW_ONLY = "review-only"
    CONTRIBUTOR = "contributor"


class ContributionStatus(StrEnum):
    """Status of a contribution."""
    PROPOSED = "proposed"
    DRAFT = "draft"
    SUBMITTED = "submitted"
    MERGED = "merged"


class Contribution(BaseModel):
    """Proposed contribution to collaborative resource."""
    source: str  # Path in contributions/
    target: str  # Target path in resource
    status: ContributionStatus
    pr_url: str | None = None


class Resource(BaseModel):
    """Linked resource (review or collaborative)."""
    name: str
    path: str
    type: ResourceType
    relationship: ResourceRelationship
    clone: bool = False
    outputs: list[str] = Field(default_factory=list)
    contributions: list[Contribution] = Field(default_factory=list)


class AirConfig(BaseModel):
    """Project configuration (.air/air-config.json)."""
    version: str = "2.0.0"
    name: str
    mode: ProjectMode
    created: datetime
    resources: dict[str, list[Resource]] = Field(
        default_factory=lambda: {"review": [], "develop": []}
    )
    goals: list[str] = Field(default_factory=list)


class TaskOutcome(StrEnum):
    """Task completion status."""
    IN_PROGRESS = "in-progress"
    SUCCESS = "success"
    PARTIAL = "partial"
    BLOCKED = "blocked"


class TaskFile(BaseModel):
    """Parsed task file."""
    filename: str
    timestamp: datetime
    description: str
    prompt: str | None
    actions: list[str]
    files_changed: dict[str, str]  # path -> description
    outcome: TaskOutcome
    notes: str | None
```

### 3.2 Configuration Schema

**`.air/air-config.json`:**
```json
{
  "$schema": "https://air-toolkit.dev/schemas/assess-config.schema.json",
  "version": "2.0.0",
  "name": "project-name",
  "mode": "review|develop|mixed",
  "created": "2025-10-03T10:42:00Z",
  "resources": {
    "review": [...],
    "develop": [...]
  },
  "goals": [...]
}
```

## 4. Key Design Decisions

### 4.1 CLI Framework: Click

**Why Click:**
- Industry standard for Python CLIs
- Excellent documentation
- Built-in help generation
- Easy nested command groups
- Parameter validation

**Alternatives Considered:**
- Typer: Too opinionated, less flexible
- argparse: Too low-level, more boilerplate
- docopt: Less maintainable

### 4.2 Terminal UI: Rich

**Why Rich:**
- Beautiful, modern terminal output
- Tables, panels, progress bars
- Syntax highlighting
- Cross-platform

**Features Used:**
- Console for colored output
- Tables for status display
- Panels for important messages
- Markdown rendering (for help text)

### 4.3 Data Validation: Pydantic

**Why Pydantic:**
- Runtime type checking
- JSON schema generation
- Clear error messages
- V2 performance improvements

**Use Cases:**
- Validate `.air/air-config.json`
- Parse task file metadata
- Ensure data integrity

### 4.4 Templating: Jinja2

**Why Jinja2:**
- Standard Python templating
- Powerful but not complex
- Good for file generation

**Use Cases:**
- Generate README.md, CLAUDE.md
- Create task file templates
- Render configuration files

### 4.5 Git Operations: GitPython

**Why GitPython:**
- Pythonic interface to git
- Cross-platform
- No shell dependencies

**Use Cases:**
- Clone repositories
- Create branches
- Commit and push
- Check repository status

### 4.6 File Embedment: importlib.resources

**Why:**
- Templates packaged with tool
- No external dependencies
- Works with zip distribution

**Alternative Considered:**
- External template directory: Breaks pip install
- pkg_resources: Deprecated

## 5. Error Handling

### 5.1 Error Categories

**User Errors:**
- Invalid command arguments
- Missing required files
- Invalid configuration

**System Errors:**
- File I/O errors
- Git operation failures
- Network errors (GitHub API)

**Business Logic Errors:**
- Invalid project state
- Resource conflicts
- Validation failures

### 5.2 Error Handling Strategy

```python
from rich.console import Console
from typing import NoReturn
import sys

console = Console()


class AirError(Exception):
    """Base exception for AIR toolkit."""
    def __init__(self, message: str, hint: str | None = None):
        self.message = message
        self.hint = hint
        super().__init__(message)


class ConfigError(AirError):
    """Configuration file error."""
    pass


class ValidationError(AirError):
    """Project validation error."""
    pass


class GitError(AirError):
    """Git operation error."""
    pass


def handle_error(error: Exception) -> NoReturn:
    """Centralized error handler."""
    if isinstance(error, AirError):
        console.print(f"[red]✗[/red] {error.message}")
        if error.hint:
            console.print(f"[dim]💡 {error.hint}[/dim]")
        sys.exit(1)
    else:
        console.print(f"[red]✗[/red] Unexpected error: {error}")
        console.print("[dim]Use --debug for full traceback[/dim]")
        sys.exit(2)
```

### 5.3 Exit Codes

- `0`: Success
- `1`: User/business logic error
- `2`: System/unexpected error
- `3`: Validation failure (air validate)

## 6. Testing Strategy

### 6.1 Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_commands.py
│   ├── test_core/
│   │   ├── test_assessment.py
│   │   ├── test_tasks.py
│   │   └── test_config.py
│   ├── test_services/
│   │   ├── test_git.py
│   │   ├── test_filesystem.py
│   │   └── test_validator.py
│   └── test_models.py
│
├── integration/            # Integration tests
│   ├── test_init_workflow.py
│   ├── test_link_workflow.py
│   └── test_pr_workflow.py
│
└── fixtures/               # Test data
    ├── sample_configs/
    ├── sample_repos/
    └── sample_tasks/
```

### 6.2 Test Coverage Goals

- Unit tests: > 80%
- Integration tests: Key workflows
- Command tests: All commands

### 6.3 Testing Tools

- **pytest**: Test framework
- **pytest-cov**: Coverage reporting
- **pytest-mock**: Mocking
- **Click testing**: `CliRunner` for command testing

## 7. Security Considerations

### 7.1 File System Access

- Validate all paths before operations
- Prevent directory traversal attacks
- Check permissions before write operations
- Symlink validation (no cycles)

### 7.2 Git Operations

- Validate remote URLs
- Use SSH keys or tokens (never passwords in code)
- Confirm destructive operations (force push)

### 7.3 Configuration Files

- Validate JSON schema
- Sanitize user inputs
- Don't store secrets in config
- Support environment variables for sensitive data

## 8. Performance Considerations

### 8.1 File Operations

- Use async I/O for large file operations (future)
- Stream large files instead of loading into memory
- Cache file system checks

### 8.2 Git Operations

- Shallow clones when possible
- Parallel operations for multiple repos (future)
- Cache git status checks

### 8.3 Template Rendering

- Preload templates at startup
- Cache compiled templates

## 9. Extensibility

### 9.1 Plugin System (Future)

```python
# Plugin interface
class AirPlugin:
    """Base class for AIR plugins."""

    def register_commands(self, cli: click.Group) -> None:
        """Register custom commands."""
        pass

    def on_project_init(self, config: AirConfig) -> None:
        """Hook: project initialization."""
        pass

    def on_resource_linked(self, resource: Resource) -> None:
        """Hook: resource linked."""
        pass
```

### 9.2 Custom Templates

- User templates in `~/.config/air/templates/`
- Override default templates
- Template marketplace (future)

### 9.3 Custom Validators

- Register custom validation rules
- Project-specific validators
- Team standards enforcement

## 10. Deployment

### 10.1 Package Distribution

**PyPI Release Process:**
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run tests: `pytest`
4. Build: `python -m build`
5. Upload: `twine upload dist/*`

### 10.2 CI/CD Pipeline

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -e ".[dev]"
      - run: pytest --cov
```

### 10.3 Release Strategy

- Semantic versioning (MAJOR.MINOR.PATCH)
- Maintain CHANGELOG.md
- GitHub releases with notes
- Tag releases in git

## 11. Migration Path

### 11.1 From Bash Script

AA-ingest-review uses bash `create-tool-now.sh`. Migration:

1. Keep bash script for backwards compatibility
2. Recommend Python version in README
3. Provide migration guide
4. Eventually deprecate bash version

### 11.2 From v1.0 to v2.0

When adding new features:

1. Maintain backwards compatibility
2. Provide migration command: `air migrate`
3. Auto-detect old project structure
4. Interactive upgrade prompts

## 12. Future Architectural Improvements

### 12.1 Async Operations

- Use `asyncio` for concurrent operations
- Parallel git clones
- Parallel validation checks

### 12.2 Web API

- REST API for team collaboration
- Shared assessment projects
- Web dashboard

### 12.3 Database Backend

- SQLite for project metadata
- Query and filter projects
- Historical tracking

## 13. References

- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [GitPython Documentation](https://gitpython.readthedocs.io/)
