# CLAUDE.md

**CRITICAL: After reading this file, read `.air/README.md` for complete system documentation.**

This file provides guidance to Claude Code (claude.air/code) when working with code in this repository.

## AI Task Tracking Protocol

**CRITICAL**: This project uses AI-assisted development tracking.

### Automatic Task Tracking (Zero Friction)

When a user gives you a prompt to modify code or create files, you MUST automatically:

1. **Immediately create a task file** - Don't ask, just do it
   - Use Python to create: `.air/tasks/YYYYMMDD-HHMM-description.md`
   - Derive description from the user's prompt
   - Pre-populate all known information

2. **Auto-document as you work**
   - Record the exact user prompt
   - List each action you take as you take it
   - Track all files you create or modify
   - Note any decisions or trade-offs

3. **Auto-finalize when complete**
   - Mark outcome status (✅ Success, ⏳ In Progress, ⚠️ Partial, ❌ Blocked)
   - Briefly mention task file location to user

### Task File Format

```markdown
# Task: [Brief description from user prompt]

## Date
YYYY-MM-DD HH:MM

## Prompt
[Exact words the user typed]

## Actions Taken
1. [First thing you did]
2. [Second thing you did]
...

## Files Changed
- `path/to/file.ext` - [What changed and why]
- `another/file.ext` - [What changed and why]

## Outcome
⏳ In Progress / ✅ Success / ⚠️ Partial / ❌ Blocked

[Brief summary of result]

## Notes
[Optional: Technical decisions, blockers, follow-up needed]
```

### Important Rules

- **Task files are immutable** - Once created, never edit them (create a new one for corrections)
- **Every code change needs a task** - No exceptions, even for "small" changes
- **Be automatic, not disruptive** - Create and update tasks silently, don't make it the focus
- **Include in commits** - Task files should be committed with the code changes

### How to Create Task Files

Use Python (works on all platforms):
```python
from datetime import datetime, timezone
from pathlib import Path

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
description = "user-task-description"  # kebab-case from user prompt
filename = f".air/tasks/{timestamp}-{description}.md"

# Create from template and populate
...
```

Or use the helper script:
```bash
python .air/scripts/new-task.py "description"
```

See `.air/README.md` for complete documentation.

---

## Using AIR Commands (When Available)

**If `air` is installed**, use these commands to streamline your workflow:

### When to Use AIR

**ALWAYS check if air is available first:**
```bash
which air  # Check if installed
```

**If air is installed, use it for:**

1. **Before starting work in an AIR project:**
   ```bash
   air status          # Check project state
   air validate        # Verify structure
   ```

2. **When creating a new assessment project:**
   ```bash
   air init my-review --mode=review
   ```

3. **When user asks for project status:**
   ```bash
   air status --format=json  # Get machine-readable output
   ```

4. **When validating project structure:**
   ```bash
   air validate --format=json  # Check for issues
   ```

**If air is NOT installed:**
- Continue with manual Python task file creation (as shown above)
- Mention to user: "💡 Tip: Install air-toolkit for streamlined workflow: `pip install air-toolkit`"
- Don't let missing tool block progress

### AIR Command Output Formats

All AIR commands support `--format=json` for parsing:

```bash
# Human-readable (default)
air status

# Machine-readable for AI
air status --format=json
# Returns: {"name":"project","mode":"mixed","resources":{...}}
```

**Use `--format=json` when you need to:**
- Parse command results
- Extract specific values
- Make decisions based on project state

---

## Project Context

AIR (AI Review) is a Python CLI toolkit for AI-assisted development and multi-project code assessment.

**Status**: v0.3.0 - Resource classification implemented, ready for PyPI distribution

Review these before starting:
- `.air/context/architecture.md` - System architecture (needs updating)
- `.air/context/language.md` - Python conventions
- `.air/tasks/` - Recent work and decisions
- `docs/ARCHITECTURE.md` - Complete technical design (13KB)
- `PROJECT-STATUS.md` - Current implementation status

---

## Commands for Development

### Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
air --version
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=air --cov-report=html

# Run specific test file
pytest tests/unit/test_models.py -v

# Run single test
pytest tests/unit/test_models.py::test_assessment_config -v
```

### Code Quality
```bash
# Format code (line length: 100)
black src/ tests/

# Lint and auto-fix
ruff check src/ tests/ --fix

# Type checking (strict mode)
mypy src/
```

### Build
```bash
# Build package for distribution
python -m build
```

---

## High-Level Architecture

### Component Structure
```
src/air/
├── cli.py              # Click-based CLI entry point
├── commands/           # Command implementations (9 files, mostly stubs)
│   ├── init.py        # Create assessment projects
│   ├── link.py        # Link repositories
│   ├── validate.py    # Validate structure
│   ├── status.py      # Show project status
│   ├── classify.py    # Auto-classify resources
│   ├── pr.py          # Create pull requests
│   ├── task.py        # Task management (new/list/complete)
│   ├── track.py       # Initialize tracking
│   └── summary.py     # Generate summaries
├── core/              # Business logic (mostly TODO)
│   └── models.py      # Pydantic data models ✅
├── services/          # Infrastructure (stubs only)
├── utils/             # Helpers ✅
│   ├── console.py     # Rich console output
│   ├── dates.py       # Date/time formatting
│   └── paths.py       # Path manipulation
└── templates/         # Jinja2 templates (to be created)
```

### Data Models (Pydantic)
Key models in `src/air/core/models.py`:
- `AssessmentConfig`: Project configuration (air-config.json)
- `Resource`: Linked repository metadata
- `Contribution`: Proposed code changes
- `TaskFile`: Parsed task file metadata
- `ProjectStructure`: Expected directory structure

Enums (all use StrEnum):
- `ProjectMode`: review, collaborate, mixed
- `ResourceType`: implementation, documentation, library, service
- `ResourceRelationship`: review-only, contributor
- `ContributionStatus`: proposed, draft, submitted, merged
- `TaskOutcome`: in-progress, success, partial, blocked

### Assessment Project Structure
Created by `air init`:
```
project-name/
├── air-config.json        # AssessmentConfig (JSON)
├── README.md              # Project overview
├── CLAUDE.md              # AI guidance
├── .gitignore
├── .air/                   # Task tracking
│   ├── tasks/            # YYYYMMDD-HHMM-description.md
│   ├── context/          # Architecture, conventions
│   └── templates/        # Task templates
├── review/               # Review-only repos (symlinks)
├── collaborate/          # Contributor repos (symlinks)
├── analysis/             # Analysis outputs
│   ├── assessments/      # Review analysis
│   └── improvements/     # Improvement proposals
├── contributions/        # Staged contributions
└── scripts/              # Utility scripts
```

---

## Code Conventions

### Python Style
- **Python**: 3.10+ (use `str | None`, not `Optional[str]`)
- **Line length**: 100 characters
- **Enums**: Use StrEnum (not `class Enum(str, Enum)`)
- **Type hints**: Required (mypy strict mode)
- **Paths**: Use pathlib.Path
- **Formatting**: black
- **Linting**: ruff
- **Docstrings**: Google style for public APIs

### Key Dependencies
**Core:**
- click >=8.1.0 (CLI framework)
- rich >=13.0.0 (terminal UI)
- pydantic >=2.0.0 (data validation)
- pyyaml >=6.0 (YAML support)
- gitpython >=3.1.0 (git operations)

**Dev:**
- pytest, pytest-cov
- black, ruff, mypy

### Rich Console Helpers
Use from `src/air/utils/console.py`:
```python
from air.utils.console import info, success, warn, error

info("Processing...")
success("Project created successfully")
warn("Resource not found")
error("Failed to validate", exit_code=1)
```

---

## Implementation Status

### Completed ✅
- Package structure and pyproject.toml
- CLI framework (Click) with command routing
- Pydantic data models
- Utility modules (console, dates, paths)
- Comprehensive documentation (68KB)

### Needs Implementation ⏳
**Phase 1 (High Priority):**
1. `air init` - Create project structure
2. `air link` - Create symlinks/clone repos
3. `air validate` - Check structure
4. `air status` - Show project info
5. Services: filesystem, templates, validator, git

**Phase 2 (Medium Priority):**
- Task tracking commands (task new/list, track init, summary)
- Template system (Jinja2)

**Phase 3 (Lower Priority):**
- `air classify` - Auto-classify resources
- `air pr` - Create pull requests

### Testing
- Basic unit tests in `tests/unit/`
- Target: >80% coverage
- Need integration tests

---

## Important Notes

1. **StrEnum**: Use `from enum import StrEnum`, not deprecated `(str, Enum)` pattern
2. **Path expansion**: All paths support `~` (expanded via `expand_path()` validator)
3. **Configuration**: Stored in `air-config.json`, validates against AssessmentConfig model
4. **Templates**: Will be embedded using importlib.resources (not external directory)
5. **Git operations**: Use GitPython, not shell commands
6. **Error handling**: Create AirError subclasses with helpful messages
7. **Testing CLI**: Use Click's CliRunner for command tests

---

**Remember**: The goal is ZERO FRICTION. Create task files automatically as part of your work, not as a separate step the user needs to think about.
- 4 suggests a re-ordreing of the parseable string format that `air link` originally used (foo:/path/to/foo:branch-name) I think we can drop this clever format and force the use of args (i.e. if we are using a script to run air)