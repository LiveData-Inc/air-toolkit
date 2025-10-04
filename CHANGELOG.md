# Changelog

All notable changes to AIR Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
