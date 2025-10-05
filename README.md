# AIR - AI Review & Development Toolkit

**AIR** = **AI Review** - A unified toolkit for AI-assisted development and multi-project code assessment.

## Overview

AIR provides two complementary capabilities:

1. **Multi-Project Assessment**: Create structured review projects to analyze and compare multiple codebases
2. **AI Task Tracking**: Automatic task file generation and tracking for AI-assisted development

## Installation

### From PyPI (Recommended)

```bash
pip install air-toolkit
# or for isolated installation
pipx install air-toolkit
```

### From Source (Development)

```bash
cd air-toolkit
pip install -e .
```

## Quick Start

### Complete Workflow (v0.6.0)

```bash
# 1. Initialize project
air init my-assessment --mode=mixed

cd my-assessment

# 2. Link repositories (PATH required, use shell tab completion!)
air link add ~/repos/service-a --name service-a --review
air link add ~/repos/docs --name docs --develop --type=documentation

# Or just provide PATH and answer prompts interactively
air link add ~/repos/service-a

# List linked resources
air link list

# 3. Create tasks as you work
air task new "analyze service architecture"
air task new "review authentication flow" --prompt "Focus on OAuth implementation"

# 4. Generate summaries
air summary                          # Rich markdown to terminal
air summary --format=json            # JSON for AI consumption
air summary --output=REPORT.md       # Save to file
air summary --since=2025-10-01       # Recent tasks only

# 5. Check status
air status
air validate
```

### Initialize in Existing Project

```bash
# Initialize AIR in current directory
cd ~/my-existing-project
air init

# Now use task tracking
air task new "refactor auth module"
air task list
air summary
```

## Features

### Core Workflow (v0.6.0) ✅
- **Project Initialization** (`air init`)
  - Create new projects or initialize in existing directories
  - Support for review, develop, or mixed modes
  - Automatic directory structure and template generation

- **Repository Linking** (`air link`)
  - Interactive and non-interactive modes
  - Review-only (read-only) or developer modes
  - Resource types: library, documentation, service
  - Auto-classification with technology stack detection
  - Symlink-based (no copying)
  - All linked repos go in `repos/` directory
  - List and manage linked resources with status indicators

- **Task Tracking** (`air task new`)
  - Timestamped task files: YYYYMMDD-HHMM-description.md
  - Standard markdown template with sections
  - Custom prompts support
  - Safe filename generation

- **Summary Generation** (`air summary`)
  - Multiple formats: markdown, JSON, text
  - Statistics: total tasks, success/blocked counts, files touched
  - Date filtering with --since
  - File or stdout output
  - Rich terminal rendering

- **Project Validation** (`air validate`)
  - Check directory structure
  - Validate symlinks and configuration
  - Report issues with helpful hints

- **Status Reporting** (`air status`)
  - View project information
  - Count resources and tasks
  - JSON output for automation

### Complete Task Lifecycle (v0.2.2) ✅
- **Task Status** (`air task status`) - View detailed task information
- **Enhanced Task List** (`air task list`) - Filter, sort, and search tasks
- **Task Completion** (`air task complete`) - Mark tasks as complete
- **Task Archive System** - Archive, restore, and manage task history

### Resource Classification (v0.3.0) ✅

- **Auto-Classify Resources** (`air classify`) - Automatic resource type detection
- Detects 11 programming languages (Python, JavaScript, Go, Rust, etc.)
- Detects 10 major frameworks (Django, React, Rails, Spring, etc.)
- Classifies as: implementation, documentation, library, or service
- Confidence scoring and verbose output
- Updates air-config.json automatically

### Deep Code Analysis (v0.6.0) ✅

- **Comprehensive Code Analysis** (`air analyze`) - AI-powered deep code analysis
- **5 Specialized Analyzers:**
  - SecurityAnalyzer - 14 security pattern types (secrets, SQL injection, weak crypto, etc.)
  - PerformanceAnalyzer - 7 performance anti-patterns (N+1 queries, nested loops, etc.)
  - CodeStructureAnalyzer - Repository structure analysis
  - ArchitectureAnalyzer - Dependency and pattern detection
  - QualityAnalyzer - Code quality metrics
- Focused analysis: `--focus=security|performance|architecture|quality`
- Severity levels: critical, high, medium, low, info
- Structured JSON output for AI consumption

### Dependency-Aware Multi-Repo Analysis (v0.6.0) ✅

- **Intelligent Multi-Repo Analysis** (`air analyze --all`)
- Analyzes repositories in dependency order (libraries before services)
- Dependency graph generation and topological sorting
- Gap analysis: `air analyze --gap LIBRARY`
- Version mismatch detection across repositories
- Pluggable dependency detectors (Python, JavaScript, Go)
- Support for package manifests and code imports

### Agent Coordination (v0.6.0) ✅

- **Parallel Analysis** (`air analyze --background`)
- Spawn multiple background agents for concurrent analysis
- Wait for completion: `air wait --all`
- Aggregate findings: `air findings --all`
- Cross-platform process management
- Rich status display with progress tracking

### Analysis Caching (v0.6.1) ✅

- **Intelligent Caching** - Massive performance improvements on repeat analysis
- Hash-based cache invalidation (SHA256 content hashing)
- Automatic caching for all 5 analyzers
- Cache statistics: `air cache status`
- Clear cache: `air cache clear`
- Force fresh analysis: `air analyze --no-cache`
- **Performance**: ~100x faster on cache hits
- **Hit Rate**: 80%+ in typical workflows
- Version-aware cache invalidation

### Shell Completion (v0.6.2) ✅

- **Tab Completion** - Complete commands, options, and dynamic arguments
- Multi-shell support: bash, zsh, and fish
- **Dynamic Completion**:
  - Resource names from air-config.json
  - Task IDs from .air/tasks/ directory
  - Analyzer focus types (security, performance, etc.)
  - Developer resources for PR commands
- Easy installation: `air completion install`
- Auto-detects shell from environment

### Pull Request Workflow (v0.3.1) ✅

- **Create Pull Requests** (`air pr`) - Automated PR creation for collaborative resources
- Auto-detect changes in `contributions/{resource}/` directory
- Auto-generate PR titles and descriptions from recent task files
- Custom PR options: `--title`, `--body`, `--draft`, `--base`
- GitHub CLI integration (`gh pr create`)
- Dry-run mode to preview changes
- List collaborative resources with contribution status
- Automatic branch creation and file copying

### Package Distribution (v0.2.3) ✅

- Available on PyPI for easy installation
- Built wheel and source distributions
- Cross-platform support (macOS, Linux, Windows)

## Documentation

- [Specification](docs/SPECIFICATION.md) - Complete feature specification
- [Architecture](docs/ARCHITECTURE.md) - System design and technical architecture
- [Development Guide](docs/DEVELOPMENT.md) - Contributing and development workflow
- [Commands Reference](docs/COMMANDS.md) - Complete command reference
- [Code Review](docs/CODE-REVIEW.md) - AI-powered code review design (future)
- [MCP Server](docs/MCP-SERVER.md) - Model Context Protocol integration (future)

## Project Structure

```
air-toolkit/
├── src/air/              # Package source
│   ├── cli.py           # Main CLI entry point
│   ├── commands/        # Command implementations
│   ├── core/            # Core functionality
│   └── templates/       # Project templates
├── tests/               # Test suite
├── docs/                # Documentation
└── examples/            # Example projects
```

## Command Overview

### Core Commands (v0.6.0)

```bash
# Project Management
air init [NAME]                      # Create or initialize project
air init --mode=MODE                 # Initialize with specific mode
air init --interactive               # Guided project setup

# Repository Linking
air link add PATH [OPTIONS]          # Link repository
  --name NAME                        # Resource name (optional, defaults to folder name)
  --review                           # Link as review-only (default)
  --develop                          # Link as collaborative/developer
  --type TYPE                        # Resource type (library/documentation/service)
  -i, --interactive                  # Interactive mode with prompts
air link list [--format=json]        # List linked resources
air link remove NAME [--keep-link]   # Remove resource
air link remove -i                   # Interactive removal with numbered list

# Code Analysis (v0.6.0)
air analyze REPO [OPTIONS]           # Analyze repository
  --focus AREA                       # Focus: security|performance|architecture|quality
  --background                       # Run in background
  --id NAME                          # Agent ID for background mode
  --no-cache                         # Force fresh analysis (skip cache)
  --clear-cache                      # Clear cache before analysis
air analyze --all [OPTIONS]          # Analyze all repos
  --no-order                         # Disable dependency ordering
  --deps-only                        # Only repos with dependencies
air analyze --gap LIBRARY            # Gap analysis for library and dependents

# Analysis Caching (v0.6.1)
air cache status                     # Show cache statistics
  --format json                      # JSON output
air cache clear                      # Clear all cached data

# Shell Completion (v0.6.2)
air completion install [SHELL]       # Install completion (auto-detects shell)
air completion uninstall [SHELL]     # Uninstall completion
air completion show SHELL            # Show completion script

# Agent Coordination (v0.6.0)
air wait --all                       # Wait for all agents to complete
air wait --agents ID1,ID2            # Wait for specific agents
  --timeout SECONDS                  # Timeout in seconds
air findings --all                   # Aggregate all findings
  --severity LEVEL                   # Filter: critical|high|medium|low
  --format json                      # JSON output
air status --agents                  # Show background agent status

# Code Review (v0.5.0)
air review [FILES]                   # Generate review context
  --pr                               # Review PR branch
  --format json                      # JSON output
air claude context                   # Get project context for AI

# Task Tracking
air task new DESCRIPTION             # Create task file
  --prompt TEXT                      # Custom prompt
air task status ID                   # Show task details
  --format json                      # JSON output
air task complete ID                 # Mark task as complete
  --notes TEXT                       # Add completion notes
air task list [OPTIONS]              # List tasks
  --all                              # Include archived
  --archived                         # Only archived
  --status STATUS                    # Filter by status
  --sort FIELD                       # Sort by date/title/status
  --search TERM                      # Search by keyword
air task archive ID [OPTIONS]        # Archive tasks

# Summary & Reporting
air summary [OPTIONS]                # Generate summary
  --format FORMAT                    # markdown|json|text
  --output FILE                      # Save to file
  --since DATE                       # Filter by date

# Resource Classification
air classify [OPTIONS]               # Classify resources
  --verbose                          # Show detection details
  --update                           # Update air-config.json
air classify RESOURCE                # Classify specific resource

# Pull Requests (v0.3.1)
air pr RESOURCE [OPTIONS]            # Create pull request
  --title TEXT                       # PR title
  --body TEXT                        # PR description
  --draft                            # Create as draft
  --dry-run                          # Preview without creating

# Validation & Status
air validate [--format=json]         # Validate project
air validate --fix                   # Auto-fix broken symlinks
air status [--format=json]           # Show project status
```

## License

MIT

## Based On

This toolkit evolved from the AA-ingest-review project, combining:
- Multi-project assessment patterns
- AI-assisted task tracking system
- Structured documentation approach
