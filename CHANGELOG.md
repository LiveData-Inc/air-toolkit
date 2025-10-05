# Changelog

All notable changes to AIR Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.2.post1] - 2025-10-05

### Improved - Analysis Progress Indicator

- **Multi-Repo Analysis Progress** - Show "[X/Y] Analyzing: NAME" progress indicator
- Display current repo index and total count during multi-repo analysis
- Works with `air analyze --all`, `air analyze --gap`, and dependency-ordered analysis
- Improves UX by showing users exactly where they are in long analysis operations

### Planned Features (Design Phase)

**HTML Findings Report** - Comprehensive HTML report generation (Task 006)
- Rich HTML report with table of contents and detailed findings
- Summary table at top with clickable links to each finding
- Grouped by repository with detailed sections for each finding
- Severity color coding, location info, code context, and suggestions
- Command: `air findings --all --html [--output custom.html]`
- Single HTML file with embedded CSS for portability
- Responsive and print-friendly design

**External Library Exclusion** - Exclude vendor code from analysis (Task 007)
- Exclude external/vendor libraries by default for cleaner results
- 15x faster analysis, 98% less noise from vendor code
- Excludes: .venv, node_modules, vendor/, build/, dist/, etc.
- Command: `air analyze myapp --include-external` to opt-in to vendor analysis
- Automatic detection of common vendor directories across languages
- Performance: Analyze 250 files in 3s vs 15,000 files in 45s

## [0.6.2] - 2025-10-05

### Added - Shell Completion for Enhanced CLI Usability

**Tab Completion for All Shells** - Comprehensive shell completion for commands, options, and dynamic arguments

#### Completion Features

- **Dynamic Completion** - Tab complete resource names from air-config.json
- **Task ID Completion** - Complete task IDs from .air/tasks/ directory
- **Analyzer Focus** - Complete focus types: security, performance, quality, architecture, structure
- **Developer Resources** - Complete only developer resources for PR commands
- **Multi-Shell Support** - Works with bash, zsh, and fish shells

#### Commands Integration

Completion added to:
- `air analyze <TAB>` - Complete resource names
- `air analyze --focus=<TAB>` - Complete focus types (security, performance, etc.)
- `air analyze --gap=<TAB>` - Complete resource names for gap analysis
- `air task complete <TAB>` - Complete task IDs
- `air task status <TAB>` - Complete task IDs
- `air task archive <TAB>` - Complete task IDs (supports multiple)
- `air task restore <TAB>` - Complete task IDs (supports multiple)
- `air pr <TAB>` - Complete developer resource names only

#### New Command Group: `air completion`

- `air completion install [bash|zsh|fish]` - Install completion (auto-detects shell)
- `air completion uninstall [bash|zsh|fish]` - Uninstall completion
- `air completion show SHELL` - Display completion activation script

#### Installation

```bash
# Auto-detect and install
air completion install

# Install for specific shell
air completion install bash
air completion install zsh
air completion install fish

# Show what would be installed
air completion show bash
```

#### Technical Details

- Created `src/air/utils/completion.py` with 6 completion helper functions
- Uses Click 8.1+ native shell_complete parameter
- Reads air-config.json for dynamic resource completion
- Scans .air/tasks/ for task ID completion
- Auto-detects shell from $SHELL environment variable
- Adds completion to shell config files (~/.bashrc, ~/.zshrc, ~/.config/fish/completions/)

#### User Experience

```bash
air <TAB>                   # Shows: init, link, analyze, task, status...
air analyze <TAB>           # Shows: myapp, docs, shared-lib (from config)
air analyze --focus=<TAB>   # Shows: security, performance, quality...
air task status <TAB>       # Shows: 20251005-001, 20251005-002...
air pr <TAB>                # Shows: myapp (only developer resources)
```

## [0.6.1.post1] - 2025-10-05

### Fixed - Orphaned Repository Recovery

**Air Upgrade Enhancements** - Recover from missing or corrupted configuration

#### Bug Fixes

- **Missing Config Recovery** - `air upgrade` now creates air-config.json if missing instead of failing
- **Orphaned Repo Detection** - Detects symlinks in `repos/` directory that are not listed in air-config.json
- **Automatic Recovery** - `air upgrade --force` automatically adds orphaned repos back to config
- **Smart Classification** - Uses classifier to determine correct type and tech stack for recovered repos
- **Directory Name Fix** - Fixed `get_project_root()` to correctly detect `.air` directory (was incorrectly looking for `.ai`)

#### Recovery Features

- Scans `repos/` directory for valid symlinks
- Compares with resources listed in air-config.json
- Identifies orphaned repositories (symlinks without config entries)
- Classifies each orphaned repo using the classifier
- Adds recovered repos to config with review-only relationship (safe default)
- Preserves technology stack and resource type information
- Handles broken symlinks gracefully (skips them)

#### Use Cases

- **Corrupted Config** - Recover when air-config.json is manually edited incorrectly
- **Missing Config** - Bootstrap configuration from existing directory structure
- **Partial Migration** - Recover repos after moving/copying AIR project
- **Manual Cleanup** - Fix config after manually removing repo entries

#### Example Output

```
AIR Project Upgrade

Project version: 2.0.0
AIR version: 0.6.1

Upgrade Plan (1 action)
────────────────────────────────────────────────
Action       Path              Description
────────────────────────────────────────────────
🔗 Recover   air-config.json   Recover 2 orphaned repo(s)
────────────────────────────────────────────────

Dry run mode - no changes made

To apply changes, run:
  air upgrade --force
```

#### Technical Details

- Added `_check_orphaned_repos()` to detect orphaned symlinks
- Added `_recover_orphaned_repos()` to add them back to config
- Creates air-config.json if completely missing
- Uses classifier to determine resource type and technology stack
- Defaults to review-only relationship for safety
- 3 new integration tests for orphaned repo scenarios

## [0.6.1] - 2025-10-05

### Added - Analysis Caching for Massive Performance Improvements

**Intelligent Caching System** - Dramatically improves analysis performance on repeat runs

#### Cache Features

- **Hash-Based Invalidation** - SHA256 content hashing automatically invalidates cache when files change
- **Automatic Caching** - All analyzers check cache before running analysis
- **Version Awareness** - Cache automatically invalidates when AIR version changes
- **Repository-Level Caching** - Caches results for all 5 analyzers per repository
- **Hit/Miss Tracking** - Tracks cache hits, misses, and calculates hit rate
- **Cache Statistics** - View cache size, entry count, and performance metrics

#### New Commands

- `air cache status` - Display cache statistics with hit rate and size
- `air cache status --format=json` - Machine-readable cache stats
- `air cache clear` - Clear all cached analysis results

#### New Flags

- `air analyze --no-cache` - Force fresh analysis, skip cache lookup
- `air analyze --clear-cache` - Clear cache before running analysis

#### Performance Impact

- **Cache Hit**: ~100x faster (skips entire analysis)
- **Typical Hit Rate**: 80%+ in normal workflows
- **Cache Storage**: `.air/cache/` with per-repo subdirectories
- **Automatic Management**: No manual intervention needed

#### Technical Details

- SHA256 hashing for content-based invalidation
- Separate cache files per analyzer per repository
- Metadata tracking with timestamps and version info
- Cross-platform compatibility (macOS, Linux, Windows)
- 18 new unit tests for cache manager

## [0.6.0] - 2025-10-04

### Added - Enhanced Analysis Depth & Dependency-Aware Multi-Repo Analysis

**Deep Code Analysis** - Five specialized analyzers with Strategy pattern architecture

#### New Analyzers

- **SecurityAnalyzer** - Detects security vulnerabilities (14 pattern types)
  - Hardcoded secrets and API keys (Bearer tokens, SSH keys, passwords)
  - SQL injection risks
  - Weak cryptography (MD5, SHA1, DES)
  - Use of eval/exec
  - Debug mode enabled
  - Insecure deserialization
  - Shell injection risks
  - Missing security headers
  - Config files not in .gitignore
  - **NEW:** Path traversal vulnerabilities
  - **NEW:** Command injection (os.popen, commands.getoutput)
  - **NEW:** XML External Entity (XXE) attacks
  - **NEW:** CSRF protection missing on POST endpoints
  - **NEW:** LDAP injection
  - **NEW:** Regular Expression DoS (ReDoS)
  - **NEW:** Cryptographically weak random (random vs secrets module)

- **PerformanceAnalyzer** - Detects performance anti-patterns (7 pattern types)
  - N+1 query detection (Django ORM)
  - Nested loops (O(n²) complexity)
  - Inefficient string concatenation in loops
  - List comprehension opportunities
  - Missing pagination on queries
  - React component memoization issues
  - forEach+push → map opportunities

- **CodeStructureAnalyzer** - Analyzes repository structure
  - File and line counts
  - Language detection and distribution
  - Large file detection (>500 lines)
  - Missing test/docs directories

- **ArchitectureAnalyzer** - Analyzes architecture and dependencies
  - Dependency analysis (pinned vs unpinned)
  - Circular import detection
  - Architectural pattern detection (API, models, services)

- **QualityAnalyzer** - Detects code quality issues
  - Long functions (>100 lines)
  - Too many parameters (>5)
  - Excessive comments
  - Missing docstrings
  - Missing README
  - Low test coverage

#### Dependency Detection - Strategy Pattern Architecture

**Pluggable dependency detectors** for extensible multi-language support:

- **Package Detectors** (manifest files)
  - `PythonRequirementsDetector` - requirements.txt
  - `PythonPyprojectDetector` - pyproject.toml
  - `JavaScriptPackageJsonDetector` - package.json
  - `GoModDetector` - go.mod

- **Import Detectors** (code-level)
  - `PythonImportDetector` - `import` and `from` statements
  - `JavaScriptImportDetector` - `import` and `require()`
  - `GoImportDetector` - Go `import` blocks

- **API Detectors** (service-to-service) - Stub for future implementation

**3 Dependency Types:**
- `PACKAGE` - Declared in manifest files
- `IMPORT` - Actual code imports
- `API` - HTTP/REST calls (future)

#### Multi-Repo Dependency-Aware Analysis

- **`air analyze --all`** - Analyze all linked repos
  - **Default:** Analyzes in dependency order (libraries before services)
  - Builds dependency graph from project files
  - Topological sort for correct analysis order
  - Saves dependency graph to `analysis/dependency-graph.json`
  - Parallel analysis where possible (repos at same dependency level)

- **`air analyze --all --no-order`** - Disable dependency ordering (parallel)

- **`air analyze --all --deps-only`** - Only analyze repos with dependencies

- **`air analyze --gap <library>`** - Gap analysis
  - Analyzes library and all dependent services
  - Detects version mismatches
  - Identifies missing features and deprecated API usage

- **`air analyze <repo>`** - Single repo analysis
  - **Default:** Checks dependencies in project context
  - Detects dependency gaps and version issues

- **`air analyze <repo> --no-deps`** - Skip dependency checking

#### Enhanced Analysis Command

- `air analyze` now runs comprehensive deep analysis with **intelligent defaults**
- Focus flag controls which analyzers run:
  - `--focus=security` - Security issues only
  - `--focus=performance` - Performance issues only
  - `--focus=architecture` - Architecture analysis only
  - `--focus=quality` - Quality issues only
  - No flag - All analyzers (comprehensive)
- Findings include severity levels (critical/high/medium/low/info)
- Results saved as structured JSON with metadata
- Resource name resolution: `air analyze myapp` (consistent with `air pr`)

### Testing

- **372 tests total** (was 356) - All passing ✅
- Added 16 new tests:
  - 14 analyzer tests (security, performance, quality, architecture, structure)
  - 2 dependency detection tests
  - Multi-repo analysis integration tests

### Impact

**Security coverage:**
- Was: 9 security pattern types
- Now: 14 security pattern types (+55%)

**Performance analysis:**
- NEW: 7 types of performance issues detected
- Covers Python and JavaScript/TypeScript/React

**Analysis depth:**
- Before: Basic classification only (tech stack, languages)
- After: Multi-dimensional (security + performance + quality + architecture + structure + dependencies)
- Findings per repo: 10-70+ actionable items (was ~1)

**Multi-repo capabilities:**
- Dependency graph building across linked repos
- Topological sort for proper analysis order
- Gap detection between library versions
- Intelligent defaults (dependency order by default)

### Architecture

**Strategy Pattern Benefits:**
- Easy to add new languages (Java, Ruby, PHP, Rust, C#)
- Each detector is independent and testable
- Type-safe filtering by dependency type
- Users can register custom detectors

**Example - Adding Rust support:**
```python
from air.services.detectors import DependencyDetectorStrategy, DependencyResult
from air.services.dependency_detector import register_detector

class RustCargoDetector(DependencyDetectorStrategy):
    @property
    def name(self) -> str:
        return "Rust Cargo.toml"

    def can_detect(self, repo_path: Path) -> bool:
        return (repo_path / "Cargo.toml").exists()

    def detect(self, repo_path: Path) -> DependencyResult:
        # Parse Cargo.toml
        ...

register_detector(RustCargoDetector())
```

### Added - Agent Coordination System (MVP)

**Parallel Analysis Tracking** - Run multiple analyses concurrently and aggregate results

#### New Commands

- **`air analyze`** - Analyze repositories with AI-powered insights
  - Inline mode: `air analyze repos/service-a`
  - Background mode: `air analyze repos/service-a --background --id=analysis-1`
  - Focus areas: `--focus=security|architecture|performance`
  - Generates findings in `analysis/reviews/<resource>-findings.json`
  - Agents auto-update status on completion

- **`air status --agents`** - View all background agent status
  - Shows agent ID, status, start time, and progress
  - Human-readable table and JSON formats
  - Auto-detects terminated processes and updates status
  - Example: `air status --agents`

- **`air findings --all`** - Aggregate findings from all analyses
  - Filter by severity: `--severity=high|medium|low`
  - JSON and table output formats
  - Example: `air findings --all --severity=high`

- **`air wait`** - Wait for background agents to complete
  - Blocks until agents finish (no polling needed)
  - `--all` flag to wait for all agents
  - `--agents` flag for specific agent IDs
  - `--timeout` to prevent indefinite waiting
  - Example: `air wait --all`

#### New Infrastructure

- **`.air/agents/` directory** - One subdirectory per background agent
  - `metadata.json` - Agent configuration and status
  - `stdout.log` - Agent output stream
  - `stderr.log` - Agent error stream

- **`.air/shared/` directory** - Shared state between agents (reserved for future use)

#### New Services

- **`agent_manager.py`** - Agent lifecycle management
  - Spawn background agents as detached subprocesses
  - Track agent status (running, complete, failed)
  - Load agent metadata and progress
  - List all agents with sorting
  - **Cross-platform process checking** using psutil
  - Auto-detect terminated processes and update status
  - Determine success/failure from stderr content

#### Utilities

- **`format_relative_time()`** - Display timestamps as "5m ago", "2h ago", etc.

### Testing

- **356 tests total** (was 337) - All passing ✅
- Added 7 agent coordination integration tests:
  - `test_analyze_command_inline` - Inline analysis
  - `test_analyze_command_background` - Background agent spawning
  - `test_status_agents_command` - Agent status display
  - `test_status_agents_json_format` - JSON output
  - `test_findings_command` - Findings aggregation
  - `test_findings_json_format` - JSON findings
  - `test_multiple_parallel_analyses` - Parallel execution
- Added 12 `air wait` command tests:
  - Basic wait functionality (--all, --agents flags)
  - JSON output format
  - Timeout handling
  - Integration with background agents
  - Failed agent detection
  - Sequential wait workflows

### Documentation

- **New:** `docs/AGENT-COORDINATION.md` - Complete guide to agent coordination patterns
- **New:** `docs/examples/CLAUDE-WORKFLOW-GAP-ANALYSIS.md` - Step-by-step gap analysis workflow
- **New:** `docs/examples/claude-gap-analysis-pattern.md` - Claude-native coordination
- **New:** `docs/examples/director-gap-analysis.md` - Conceptual director pattern
- **New:** `docs/tutorials/parallel-analysis-quickstart.md` - Hands-on tutorial
- Updated `docs/COMMANDS.md` with Agent Coordination Commands section
- Added documentation for `air analyze`, `air status --agents`, `air findings`, `air wait`
- Updated version to 0.6.0

### Use Cases

**Parallel Repository Analysis:**
```bash
# Spawn 3 background agents
air analyze repos/service-a --background --id=analysis-1
air analyze repos/service-b --background --id=analysis-2
air analyze repos/service-c --background --id=analysis-3

# Wait for all to complete
air wait --all

# View combined findings
air findings --all
```

**Focused Security Review:**
```bash
# Run security-focused analysis
air analyze repos/api-service --background --id=security-review --focus=security

# Wait for completion
air wait --agents security-review

# Check findings
air findings --all --severity=high
```

**Library-Service Gap Analysis:**
```bash
# Spawn workers to analyze library and service
air analyze repos/library --background --id=lib-current --focus=capabilities
air analyze repos/library-roadmap --background --id=lib-future --focus=roadmap
air analyze repos/service --background --id=service-needs --focus=requirements

# Wait for analysis to complete
air wait --all

# Claude aggregates findings and creates gap analysis
air findings --all --format=json
# Creates: analysis/gap-analysis.md, analysis/integration-plan.md
```

### Technical Details

- Background agents run as detached subprocesses (start_new_session=True)
- Agent metadata stored in JSON for easy querying
- Findings aggregated from multiple JSON files
- Cross-platform process management via psutil
- Agent status auto-updates when processes terminate
- `air wait` provides blocking coordination primitive

### Bug Fixes

- **Agent status bug**: Fixed agents showing as "running" after process termination
  - `air status --agents` now uses psutil to check if PIDs are alive
  - Auto-updates status to "complete" or "failed" based on stderr
  - Works cross-platform (macOS, Linux, Windows)
- **Agent completion**: Background agents now update their own status on exit
  - Success: status="complete"
  - Failure: status="failed" with error details

### Dependencies

- Added `psutil>=5.9.0` for cross-platform process management
- Process management via Python subprocess module (simple, cross-platform)

### Future Enhancements (v0.6.x)

See `.air/tasks/20251004-1520-mvp-parallel-analysis-tracking.md` for roadmap:
- M1: Automated spawning with `air spawn` command
- M2: Shared findings database (SQLite)
- M3: Parallel execution pipeline with dependencies
- M4: Resource management (token budgets, rate limits)
- M5: Advanced features (retry, GitHub integration, templates)

---

## [0.5.11] - 2025-10-04

### Changed

- **`air link add` now non-interactive by default** - Fast workflow with smart defaults
  - Uses folder name as default resource name (no `--name` required)
  - Auto-classifies repository type (no `--type` required)
  - Defaults to review mode (read-only)
  - Creates link immediately without prompting
  - Example: `air link add ~/repos/my-service` (instant, no prompts)

### Added

- **`-i, --interactive` flag for `air link add`** - Opt-in interactive mode
  - Guided prompts for all options
  - Path validation and verification
  - Name suggestion with uniqueness check
  - Relationship choice (review/develop)
  - Auto-classification with opt-out
  - Confirmation summary before creating link
  - Example: `air link add ~/repos/my-service -i`

- **`-i, --interactive` flag for `air link remove`** - Numbered list selection
  - Displays all linked resources in numbered table
  - Select resource by number (1, 2, 3, etc.)
  - Shows name, type, relationship, and path for each resource
  - Confirmation prompt before removal
  - Graceful cancellation with 'q' or Ctrl+C
  - Example: `air link remove -i`
  - Direct removal still works: `air link remove NAME`

### Testing

- **337 tests total** (was 333) - All passing ✅
- Added 4 new integration tests:
  - `test_link_add_auto_classify` - Auto-classification without --type
  - `test_link_add_folder_name_default` - Folder name as default name
  - `test_link_add_fully_automatic` - Both defaults (no --name, no --type)
  - `test_link_remove_no_name_without_interactive` - Usage display when no args
- All existing tests remain compatible (use explicit args)

### Documentation

- Updated `docs/COMMANDS.md` with new behavior for both commands
- Added `-i` flag documentation and examples for `link add` and `link remove`
- Documented smart defaults (name, type, relationship) for `link add`
- Documented interactive numbered selection for `link remove`
- Added auto-classification documentation

### Migration Guide

**Before (v0.5.1 and earlier):**
```bash
# Would prompt interactively
air link add ~/repos/my-service
```

**After (v0.5.11):**
```bash
# Instant, no prompts (uses folder name, auto-detects type)
air link add ~/repos/my-service

# For interactive mode, use -i flag
air link add ~/repos/my-service -i
```

This change makes the common case (quick linking with sensible defaults) much faster, while preserving full customization via the `-i` flag.

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
