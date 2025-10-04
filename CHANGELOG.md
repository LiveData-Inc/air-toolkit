# Changelog

All notable changes to AIR Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
