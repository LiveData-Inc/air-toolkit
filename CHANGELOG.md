# Changelog

All notable changes to AIR Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1] - 2025-10-04

### Fixed

- **Critical packaging bug** - Templates not included in distribution
  - `air init` was failing with "Templates directory not found" error when installed via pip/pipx
  - Only directory structure created, no `air-config.json`, `README.md`, `CLAUDE.md`, or `.gitignore`
  - Root cause: Missing `[tool.setuptools.package-data]` in `pyproject.toml`
  - Fix: Added package-data configuration to include all template files
  - All template files now properly packaged in wheel distribution
  - Verified with fresh pipx installation

### Technical Details

The bug only appeared in packaged installations (pip/pipx), not in development mode (`pip install -e .`), which is why it wasn't caught during development. Template files need to be explicitly declared as package data in `pyproject.toml` for setuptools to include them in the distribution.

## [0.5.0] - 2025-10-04

### Added

- **`air review` command** - AI-powered code review integration
  - Generate review context from git changes
  - Review uncommitted changes: `air review`
  - Review PR branch: `air review --pr`
  - Review specific files: `air review src/file.py`
  - JSON output optimized for AI consumption
  - Markdown output for human readability
  - Includes git diff, file stats, and AIR project context

- **`air claude` command group** - AI assistant helper commands
  - `air claude context` - Get comprehensive project context for AI
  - Returns project status, recent tasks, linked resources, coding standards
  - JSON and markdown output formats
  - Optimized for AI parsing and decision-making

- **Claude Code Slash Commands** - Seamless workflow integration
  - `.claude/commands/air-review.md` - Code review workflow
  - `.claude/commands/air-begin.md` - Start AIR-tracked work session
  - `.claude/commands/air-done.md` - Complete and commit work
  - Enables `/air-review`, `/air-begin`, `/air-done` in Claude Code

- **Architecture Documentation** - Future roadmap
  - `docs/CODE-REVIEW.md` - AI-powered code review design (16-week plan)
  - `docs/MCP-SERVER.md` - Model Context Protocol integration (8-week plan)
  - Complete with API specs, data flows, implementation phases

### Changed

- **Version bumped to 0.5.0** - First code review release
- CLI now includes `review` and `claude` commands
- Project context available to AI assistants via structured APIs

### Testing

- **333 tests total** (was 325) - All passing ✅
- Added 8 new integration tests for review commands
- Test coverage for git operations, JSON parsing, error handling

### Documentation

- Added review command documentation
- Updated README.md with architecture docs links
- Task files for implementation tracking

### Use Cases

**Local Code Review:**
```bash
# Before committing
air review

# Claude Code analyzes changes with full context
/air-review
```

**AI-Assisted Development:**
```bash
# Get project context for AI
air claude context

# Start tracked work
/air-begin

# Complete and commit
/air-done
```

## [0.4.3] - 2025-10-04

### Added
- **`air validate --fix`** - Automatically recreate missing/broken symlinks
  - Recreates symlinks when source path still exists
  - Handles broken symlinks (removes and recreates)
  - Clear feedback showing what was fixed
  - Reports errors when source path doesn't exist
  - Perfect for cloning AIR projects and restoring links

- **Shell Tab Completion Support** - `air link add` now requires PATH as positional argument
  - `air link add ~/repos/myproject` - Use your shell's tab-completion! ⭐
  - PATH is required (running `air link add` without args shows help)
  - Still prompts interactively for name, relationship, and type if not provided
  - Much better UX than typing `--path` option
  - Removed ~40 lines of path prompting code

### Fixed
- **Broken Symlink Detection** - All commands now properly handle missing or broken symlinks
  - `air validate` now cross-references config with filesystem to detect missing resources
  - `air validate` detects when configured resources are missing from `repos/` directory
  - `air validate` detects when symlinks exist but target directories have been removed
  - `air link list` now shows status indicators: `✓ valid`, `✗ broken`, `⚠ missing`
  - `air status` now shows status indicators for all resources (consistent with link list)
  - `air classify` fails gracefully with helpful message if resource path not found
  - `air pr` fails gracefully with helpful message if resource path not found

- **Classifier Improvements** - Fixed Flask false positives and added CDK/Lambda detection
  - Removed `app.py` from Flask detection (too generic, conflicted with FastAPI/CDK)
  - Fixed framework detection to search in requirements.txt/pyproject.toml properly
  - Added CDK and Lambda framework detection (cdk.json, mangum, app.py combinations)
  - Added proper capitalization (FastAPI, JavaScript, Next.js, PHP, C#)
  - Multi-framework stacks now supported (e.g., `Python/FastAPI/Lambda`)
  - AWS CDK Lambda projects now correctly identified

### Changed
- **Enhanced UX** - Better visibility and consistency
  - Status column added to `air link list` output (shows `✓ valid`, `✗ broken`, `⚠ missing`)
  - Status column added to `air status` resource tables (consistent formatting)
  - Status column width increased to 10 chars (prevents text wrapping)
  - Clear error messages guide users to run `air validate` when paths are missing
  - `air validate --fix` displays "Fixed Issues" table with green checkmarks
  - `air init` shows usage pattern and complete examples in "Next steps"

- **Code Quality** - Refactored duplicate code
  - Created `src/air/utils/tables.py` with shared resource table rendering
  - Both `air link list` and `air status` use same rendering function
  - Removed ~80 lines of duplicate table rendering code
  - Consistent column widths across all commands

- **Breaking Changes** - Removed deprecated NAME:PATH format
  - `air link add` no longer accepts `--path` option (use positional PATH argument)
  - Removed deprecated NAME:PATH format completely (e.g., `service-a:~/repos/service-a`)
  - All documentation updated to show new syntax
  - All hint messages updated

### Testing
- **333 tests total** (was 318) - All passing ✅
  - Added 2 new integration tests for symlink validation
  - Added 2 new integration tests for --fix functionality
  - Added 11 new unit tests for validate fix logic
  - Updated 7 tests to use positional PATH argument

### Use Cases

**Scenario 1: Manually Removed Symlink**
When a user manually removes a symlink, `air validate` detects it and `air validate --fix` recreates it.

**Scenario 2: Cloning AIR Projects**
Clone an AIR project from GitHub, run `air validate --fix`, and all symlinks are automatically restored
(assuming the source repositories exist on the new machine).

**Scenario 3: Broken Symlinks**
When target directories are moved/removed, `air validate` detects broken symlinks. If the source paths
are updated in config, `air validate --fix` removes broken symlinks and creates new ones.

## [0.4.2] - 2025-10-04

### Breaking Changes
- **Resource Type Simplification** - Renamed `implementation` → `library`
  - All code repositories now classified as `library` (simpler, clearer)
  - Only 3 types remain: `library`, `documentation`, `service`
  - Tests updated: 318 passing ✅

### Added
- **Technology Stack Field** - New `technology_stack` field on all resources
  - Captures language + framework (e.g., "Python/FastAPI", "TypeScript/React")
  - Auto-populated during classification
  - Displayed in confirmation panel and listings
  - Stored in `air-config.json`

- **Auto-Classification Now Default** - Changed from opt-in to opt-out
  - Interactive prompt now defaults to YES for auto-classify
  - Shows detected stack in output (e.g., "library (Python/Django)")
  - Can still skip classification if desired

### Changed
- **Classifier Updates:**
  - Returns `technology_stack` in ClassificationResult
  - Helper function `_generate_technology_stack()` creates stack strings
  - All code repos default to `library` type
  - Service detection unchanged (requires deployment configs)
  - Documentation detection unchanged (>70% doc files)

- **Link Command:**
  - Default type changed from `implementation` to `library`
  - Auto-classification prompt defaults to True (was False)
  - Displays technology stack in confirmation panel
  - Non-interactive mode sets `technology_stack=None`

### Documentation
- Updated all docs to use `library` instead of `implementation`
- COMMANDS.md reflects new 3-type system
- ARCHITECTURE.md updated with correct ResourceType enum
- SPECIFICATION.md examples updated

### Migration
Existing configs with `"type": "implementation"` will need manual update to `"type": "library"`.
The system still accepts it but it's deprecated.

### Future (v0.4.3+)
- User suggested: `mixed` type for monorepos with multiple projects
- User suggested: Path autocomplete and command history (up/down arrows)

## [0.4.1] - 2025-10-04

### Added
- **Interactive Link Command** - `air link add` is now interactive by default
  - Guided prompts for path, name, relationship, and type
  - Smart defaults: folder name for resource name, review mode, implementation type
  - Path validation with retry loops for invalid paths
  - Name uniqueness validation
  - Optional auto-classification (opt-in) for resource type detection
  - Confirmation panel showing summary before creating link
  - Partial argument support - provide some args, prompted for rest

### Changed
- **air link add** command signature updated:
  - `--path` and `--name` now explicit options (no longer NAME:PATH)
  - `--review` is now the default relationship (no flag needed for review mode)
  - `--type` is now optional (defaults to "implementation" if not specified)
  - Interactive mode triggers when path or name missing
  - Minimal usage: `air link add --path PATH --name NAME` (uses review + implementation defaults)

### Deprecated
- **NAME:PATH format** - Shows deprecation warning, will be removed in v0.5.0
  - Old: `air link add service-a:~/repos/service-a --review`
  - New: `air link add --path ~/repos/service-a --name service-a --review`

### Documentation
- Updated COMMANDS.md with comprehensive interactive link documentation
- Added examples for interactive and non-interactive usage
- Documented all interactive features and prompts

### Testing
- **318 tests total** - All passing ✅
- Updated 7 link command integration tests for new format
- Added test for default review behavior
- Tests cover interactive detection, deprecation warnings, defaults, and validation

## [0.4.0] - 2025-10-04

### Breaking Changes

**Nomenclature & Architecture Refactoring** - Major clarity improvements with breaking changes:

- **Mode Rename**: `collaborate` → `develop`
  - More intuitive: you're developing/building, not "collaborating"
  - Clearer distinction from review mode

- **Relationship Rename**: `CONTRIBUTOR` → `DEVELOPER`
  - Better reflects active development role
  - Consistent with "develop" mode terminology

- **Model Rename**: `AssessmentConfig` → `AirConfig`
  - More generic, works for all modes (review/develop/mixed)
  - "Assessment" only applies to review activities

- **Directory Changes**:
  - `review/` → `repos/` - All linked repositories now in `repos/`
  - `analysis/assessments/` → `analysis/reviews/` - Perfect parallelism: review repos, write reviews
  - Removed `develop/` directory concept (was confusing in develop mode)

### Architecture Clarification

**REVIEW Mode** - Assessment project structure:
```
project/
├── repos/                 # Symlinks to external code (review-only)
├── analysis/
│   └── reviews/          # Your written reviews
└── .air/                 # Task tracking
```

**DEVELOP Mode** - Regular development with tracking:
```
project/
├── src/                  # Your code (standard structure)
├── tests/                # Your tests
├── docs/                 # Your docs
└── .air/                 # Task tracking (only special directory)
```

**MIXED Mode** - Both assessment and development:
```
project/
├── repos/                # External repos (review-only + developer)
├── analysis/
│   └── reviews/         # Reviews of external repos
├── contributions/       # Prepared PRs for developer repos
├── src/                 # Your code
├── tests/               # Your tests
└── .air/                # Task tracking
```

### Migration Guide

**For existing projects:**

1. **Update mode in air-config.json**: Change `"mode": "collaborate"` to `"mode": "develop"`
2. **Update relationship**: Change `"relationship": "contributor"` to `"relationship": "developer"`
3. **Rename directories**:
   - `mv review/ repos/` (if exists)
   - `mv analysis/assessments/ analysis/reviews/` (if exists)
4. **Update resources in air-config.json**: Change `"collaborate": []` to `"develop": []`
5. **Re-run**: `air validate` to verify new structure

### Changed

- All commands now use `--develop` instead of `--collaborate`
- All linked repos (both REVIEW_ONLY and DEVELOPER) symlinked to `repos/`
- Templates updated for new directory structure
- Documentation updated throughout

### Testing

- **317 tests total** - All passing ✅
- Updated 9 test files for new nomenclature
- All integration tests updated for new structure

## [0.3.2] - 2025-10-04

### Added
- **Enhanced Error Messages** - Helpful error messages with suggestions
  - New error classes with context and hints
  - Similar name suggestions using Levenshtein distance
  - Documentation links for complex errors
  - Rich formatted error display
  - Error classes: ProjectNotFoundError, ConfigurationError, ResourceNotFoundError, PathError, GitError, GitHubCLIError, TaskError, ValidationError

- **Progress Indicators** - Visual feedback for long operations
  - Progress bars with elapsed time
  - Progress tracking for multi-step workflows
  - Spinner indicators for indeterminate operations
  - Status messages with icons
  - Applied to PR workflow (4-step process)

- **Interactive Init Mode** - Guided project setup
  - `air init --interactive` or `air init -i`
  - Interactive prompts for all options
  - Project name, mode, and goals
  - Configuration preview before creation
  - Support for adding project goals interactively

### Infrastructure
- New utilities module: `src/air/utils/errors.py`
  - Centralized error handling with AirError base class
  - Levenshtein distance algorithm for name suggestions
  - Rich-formatted error display
- New utilities module: `src/air/utils/progress.py`
  - Progress indicators and status messages
  - Context managers for progress tracking
  - ProgressTracker class for multi-step operations

### Changed
- Updated `air pr` command to use enhanced error messages and progress tracking
- Error messages now include actionable suggestions and hints
- Long operations show progress feedback

### Testing
- **314 tests total** (was 278) - All passing ✅
- Added 36 new tests for error handling and progress utilities

## [0.3.1] - 2025-10-04

### Added
- **`air pr`** - Create pull requests for collaborative resources
  - Automatic change detection in `contributions/{resource}/` directory
  - Auto-generated PR titles and descriptions from recent task files
  - Custom PR title and body via `--title` and `--body` options
  - Draft PR support with `--draft` flag
  - Custom base branch via `--base` option (default: main)
  - Dry-run mode to preview changes without creating PR
  - List collaborative resources with contribution status (when no resource specified)
  - Integration with GitHub CLI (`gh pr create`)
  - Automatic branch creation with `air/{sanitized-title}` naming
  - File copying from contributions to resource repository
  - Git operations: branch creation, commit, push
  - PR metadata generation from last 5 task files
  - Branch name sanitization (lowercase, hyphens, 50 char limit)
  - 30 unit tests for pr_generator service
  - 9 integration tests for pr command

### Infrastructure
- New service module: `src/air/services/pr_generator.py`
  - `detect_changes()` - Detect files in contributions directory
  - `generate_pr_metadata()` - Generate PR title/body from tasks
  - `create_pr_with_gh()` - Create PR via gh CLI
  - `copy_contributions_to_resource()` - Copy files to target repo
  - `git_create_branch_and_commit()` - Git operations
  - `check_gh_cli_available()` - Verify gh CLI setup
  - `is_git_repository()` - Validate git repos
  - `_sanitize_branch_name()` - Clean branch names

### Testing
- **276 tests total** (was 237) - All passing ✅
- Added 39 new tests (30 unit + 9 integration)

### Documentation
- Updated COMMANDS.md with comprehensive `air pr` documentation
- Added examples for all PR workflow scenarios
- Documented auto-generated PR metadata format
- Added gh CLI installation and authentication instructions

## [0.3.0] - 2025-10-04

### Added
- **`air classify`** - Auto-classify resources by analyzing repository structure
  - Detects programming languages (Python, JavaScript, Go, Rust, Java, Ruby, PHP, etc.)
  - Detects frameworks (Django, React, Vue, Angular, Express, Rails, Spring, etc.)
  - Classifies resource type: implementation, documentation, library, service
  - Provides confidence scores for classifications
  - Verbose mode shows detection details (languages, frameworks, reasoning)
  - `--update` flag to update air-config.json with detected types
  - Support for specific resource classification by name
  - JSON output format for automation
  - 24 unit tests + 8 integration tests

### Changed
- Resource classification is now automated (previously manual)
- Classification algorithm uses file pattern matching and content analysis
- Detection patterns for major languages and frameworks

### Testing
- **237 tests total** (was 205) - All passing ✅
- Added 32 new tests (24 unit + 8 integration)

## [0.2.3] - 2025-10-04

### Changed
- **Package Distribution** - Ready for PyPI publishing
  - Built wheel and source distributions
  - Verified with twine check
  - Ready for `pip install air-toolkit`

### Infrastructure
- Distribution artifacts generated and validated
- PyPI-compliant package structure

## [0.2.2] - 2025-10-04

### Added
- **`air task status`** - View detailed task information
  - Show task title, date, prompt, actions, files, outcome, and notes
  - JSON and human-readable output formats
  - Searches both active and archived tasks
  - Rich terminal display with status emojis
  - 7 unit tests + 7 integration tests

- **Enhanced `air task list`** - Advanced filtering and sorting
  - Filter by status: `--status=success|in-progress|blocked|partial`
  - Sort by field: `--sort=date|title|status`
  - Search by keyword: `--search=TERM` (searches title and prompt)
  - Combined filters work together
  - Enhanced JSON output with task details
  - Rich display with status emojis for each task
  - 5 integration tests

### Changed
- Task list display now shows status emoji and title for each task
- JSON output includes task title, status, and date fields

### Testing
- **205 tests total** (was 186) - All passing ✅
- Added 19 new tests (7 unit + 12 integration)

## [0.2.1] - 2025-10-03

### Added
- **`air task complete`** - Mark tasks as complete
  - Update task outcome to ✅ Success from any status
  - `--notes` option to add completion notes
  - Partial task ID matching support
  - Preserves all existing task content and sections
  - 9 unit tests + 7 integration tests

### Fixed
- Template trailing newline after `## Notes` section for proper pattern matching
- Timezone handling in `test_summary_since_filter` test

### Testing
- **186 tests total** - All passing ✅

## [0.2.0] - 2025-10-03

### Added

**Core Workflow Complete** - Full AI-assisted development workflow now functional

#### Commands
- **`air init`** - Enhanced project initialization
  - Support for existing projects with `air init` (no args)
  - `--create-dir` flag for explicit directory creation
  - `--mode` option: review, collaborate, or mixed (default)
  - Smart warnings for non-empty directories
  - Full test coverage with 9 integration tests

- **`air link`** - Repository linking system
  - `air link add NAME:PATH` - Link resources with --review or --collaborate
  - `air link list` - Display linked resources (human/JSON formats)
  - `air link remove NAME` - Unlink resources with optional --keep-link
  - Resource types: implementation, documentation, library, service
  - Symlink-based linking (no copying)
  - 27 new tests (14 unit + 13 integration)

- **`air task new`** - Task tracking
  - `air task new DESCRIPTION` - Create timestamped task files
  - `--prompt` option for custom prompt text
  - Timestamped filenames: YYYYMMDD-HHMM-description.md
  - Markdown template with standard sections
  - Safe filename generation with special character handling
  - 15 new tests (8 unit + 7 integration)

- **`air summary`** - Summary generation
  - `air summary` - Generate project summaries from task files
  - `--format` option: markdown (default), json, text
  - `--output FILE` - Save to file instead of stdout
  - `--since DATE` - Filter tasks by date (YYYY-MM-DD)
  - Rich markdown rendering in terminal
  - Statistics: total tasks, success/blocked counts, files touched
  - 21 new tests (13 unit + 8 integration)

- **`air task archive`** - Task archiving system
  - Archive tasks by ID, date, or all tasks
  - `--strategy` option: by-month, by-quarter, flat
  - `--dry-run` for preview
  - Task restoration with `air task restore`
  - Archive statistics with `air task archive-status`

#### Services
- **task_parser.py** - Parse task markdown files with regex
- **summary_generator.py** - Generate summaries in multiple formats
- **task_archive.py** - Archive and restore task files
- Enhanced **filesystem.py** - Symlink support and validation
- Enhanced **templates.py** - Task template rendering

#### Templates
- **task.md.j2** - Standard task file template

### Changed
- Renamed `.ai` folder to `.air` for brand consistency
- Enhanced `safe_filename()` to handle multiple consecutive spaces
- Improved error messages with helpful hints throughout
- JSON output modes now suppress extra console output

### Fixed
- Multiple space handling in filenames (test   spaces → test-spaces)
- JSON output formatting in summary command
- Path expansion in resource linking

### Testing
- **170 tests total** (up from 110)
- 11 test files
- ~100 unit tests
- ~70 integration tests
- All tests passing ✅

### Documentation
- Added comprehensive command documentation
- Task file format standardization
- Updated PROJECT-STATUS.md with completed features

## [0.1.0] - 2025-10-03

### Added
- Initial release with Phase 1 core functionality
- **`air init`** - Project initialization
- **`air validate`** - Structure validation
- **`air status`** - Project status display
- **`air task list`** - List task files
- Complete Python package structure
- Click-based CLI framework
- Pydantic data models
- Rich console output
- Comprehensive test suite (110 tests)
- Full documentation (68KB across 5 docs)

### Infrastructure
- Python 3.10+ support
- setuptools-based packaging
- pytest test framework
- black + ruff for code quality
- mypy for type checking

[0.2.0]: https://github.com/LiveData-Inc/air-toolkit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/LiveData-Inc/air-toolkit/releases/tag/v0.1.0
