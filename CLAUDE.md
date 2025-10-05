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
from datetime import datetime
from pathlib import Path

# IMPORTANT: Use LOCAL time, not UTC, for proper chronological sorting
# New format: YYYYMMDD-NNN-HHMM-description.md

# Get next ordinal for today
tasks_dir = Path(".air/tasks")
date_prefix = datetime.now().strftime("%Y%m%d")
existing = list(tasks_dir.glob(f"{date_prefix}-*.md"))
ordinal = len(existing) + 1

# Format with ordinal
date_str = datetime.now().strftime("%Y%m%d")
time_str = datetime.now().strftime("%H%M")
timestamp = f"{date_str}-{ordinal:03d}-{time_str}"

description = "user-task-description"  # kebab-case from user prompt
filename = f".air/tasks/{timestamp}-{description}.md"

# Create from template and populate
...
```

**Legacy format (still valid):**
```python
# YYYYMMDD-HHMM-description.md
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
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

**Status**: v0.6.0 - Production-ready with deep analysis, dependency-aware multi-repo analysis, and agent coordination

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
├── cli.py              # Click-based CLI entry point ✅
├── commands/           # Command implementations (11 command groups) ✅
│   ├── init.py        # Create assessment projects ✅
│   ├── link.py        # Link repositories ✅
│   ├── validate.py    # Validate structure ✅
│   ├── status.py      # Show project status ✅
│   ├── classify.py    # Auto-classify resources ✅
│   ├── pr.py          # Create pull requests ✅
│   ├── task.py        # Task management (new/list/complete/archive) ✅
│   ├── summary.py     # Generate summaries ✅
│   ├── review.py      # Code review context ✅
│   ├── analyze.py     # Deep code analysis ✅
│   └── agent.py       # Agent coordination (wait/findings) ✅
├── core/              # Business logic ✅
│   ├── models.py      # Pydantic data models ✅
│   └── enums.py       # StrEnum definitions ✅
├── services/          # Infrastructure ✅
│   ├── filesystem.py  # File operations ✅
│   ├── templates.py   # Jinja2 rendering ✅
│   ├── validator.py   # Validation logic ✅
│   ├── git.py         # Git operations ✅
│   ├── classifier.py  # Resource classification ✅
│   ├── pr_generator.py # PR creation ✅
│   ├── task_parser.py # Task parsing ✅
│   ├── summary_generator.py # Summaries ✅
│   ├── task_archive.py # Archiving ✅
│   ├── agent_manager.py # Agent coordination ✅
│   ├── analyzers/     # Code analyzers (5 types) ✅
│   └── detectors/     # Dependency detectors ✅
├── utils/             # Helpers ✅
│   ├── console.py     # Rich console output ✅
│   ├── dates.py       # Date/time formatting ✅
│   ├── paths.py       # Path manipulation ✅
│   ├── tables.py      # Table rendering ✅
│   ├── errors.py      # Error handling ✅
│   └── progress.py    # Progress indicators ✅
└── templates/         # Jinja2 templates (embedded) ✅
```

### Data Models (Pydantic)
Key models in `src/air/core/models.py`:
- `AirConfig`: Project configuration (air-config.json) - formerly AssessmentConfig
- `Resource`: Linked repository metadata with technology stack
- `Contribution`: Proposed code changes
- `TaskFile`: Parsed task file metadata
- `ProjectStructure`: Expected directory structure
- `ClassificationResult`: Resource classification data
- `AnalysisResult`: Code analysis findings
- `DependencyResult`: Dependency detection data

Enums (all use StrEnum in `src/air/core/enums.py`):
- `ProjectMode`: review, develop, mixed (formerly collaborate → develop)
- `ResourceType`: library, documentation, service (simplified from implementation → library)
- `ResourceRelationship`: REVIEW_ONLY, DEVELOPER (formerly CONTRIBUTOR → DEVELOPER)
- `ContributionStatus`: proposed, draft, submitted, merged
- `TaskOutcome`: in-progress, success, partial, blocked
- `AnalysisFocus`: security, performance, architecture, quality, all
- `Severity`: critical, high, medium, low, info
- `DependencyType`: PACKAGE, IMPORT, API

### AIR Project Structure
Created by `air init`:
```
project-name/
├── air-config.json        # AirConfig (JSON)
├── README.md              # Project overview
├── CLAUDE.md              # AI guidance
├── .gitignore
├── .air/                   # Task tracking & agent coordination
│   ├── tasks/            # YYYYMMDD-NNN-HHMM-description.md (ordinal-based)
│   ├── agents/           # Background agent metadata (v0.6.0)
│   │   └── {agent-id}/   # Per-agent directory with metadata.json, logs
│   ├── context/          # Architecture, conventions
│   └── templates/        # Task templates
├── repos/                # All linked repos (symlinks) - formerly review/collaborate
├── analysis/             # Analysis outputs
│   ├── reviews/          # Review analysis (formerly assessments)
│   ├── improvements/     # Improvement proposals
│   └── dependency-graph.json # Multi-repo dependency graph (v0.6.0)
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
- jinja2 >=3.1.0 (template rendering)
- psutil >=5.9.0 (cross-platform process management)

**Dev:**
- pytest >=7.0.0, pytest-cov >=4.0.0
- black >=23.0.0, ruff >=0.1.0, mypy >=1.0.0

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

**Core Commands (v0.1.0-v0.4.0):**
- ✅ `air init` - Project initialization (interactive and non-interactive)
- ✅ `air link` - Repository linking with auto-classification
- ✅ `air validate` - Structure validation with auto-fix
- ✅ `air status` - Project status and agent tracking
- ✅ `air task new/list/status/complete/archive` - Complete task lifecycle
- ✅ `air summary` - Summary generation (markdown/JSON/text)

**Advanced Features (v0.3.0-v0.6.0):**
- ✅ `air classify` - Auto-classify resources with tech stack detection
- ✅ `air pr` - Pull request creation with GitHub CLI integration
- ✅ `air review` - Code review context generation
- ✅ `air analyze` - Deep code analysis (5 specialized analyzers)
- ✅ `air analyze --all` - Dependency-aware multi-repo analysis
- ✅ `air wait` - Agent coordination and waiting
- ✅ `air findings` - Aggregate analysis findings

**Services & Infrastructure:**
- ✅ Filesystem operations with symlink support
- ✅ Template system (Jinja2) with embedded templates
- ✅ Validator with auto-fix capabilities
- ✅ Git operations (GitPython)
- ✅ Resource classifier (11+ languages, 10+ frameworks)
- ✅ PR generator with GitHub CLI integration
- ✅ Task parser and archiving system
- ✅ Summary generator (multiple formats)
- ✅ 5 specialized analyzers (Security, Performance, Quality, Architecture, Structure)
- ✅ Pluggable dependency detectors (Python, JavaScript, Go)
- ✅ Agent manager with cross-platform process tracking

**Testing:**
- ✅ 372 tests total (all passing)
- ✅ ~200 unit tests
- ✅ ~172 integration tests
- ✅ >80% code coverage achieved
- ✅ Comprehensive test suite for all features

**Distribution:**
- ✅ PyPI publishing (v0.6.0 available)
- ✅ Cross-platform support (macOS, Linux, Windows)
- ✅ Proper package structure with embedded templates

### Future Enhancements (v0.7.0+)

**Analysis Improvements:**
- Additional language support (Java, Ruby, PHP, Rust, C#)
- Custom analyzer plugins
- Analysis caching for faster re-runs
- Incremental analysis (only changed files)

**Agent Coordination:**
- Shared findings database (SQLite)
- Automated spawning with `air spawn` command
- Parallel execution pipeline with dependencies
- Resource management (token budgets, rate limits)

**Integration:**
- MCP (Model Context Protocol) server implementation
- GitHub Actions integration
- VS Code extension
- Web UI for analysis results

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
- an important goal for air is to make the planning steps and implementation tasks explicit, and part of the github history, rather than hidden in teh claude-specific files under the user's $HOME folder.