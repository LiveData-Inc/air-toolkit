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

### Complete Workflow (v0.4.0)

```bash
# 1. Initialize project
air init my-assessment --mode=mixed

cd my-assessment

# 2. Link repositories
air link add service-a:~/repos/service-a --review
air link add docs:~/repos/docs --develop --type=documentation

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

### Core Workflow (v0.4.0) ✅
- **Project Initialization** (`air init`)
  - Create new projects or initialize in existing directories
  - Support for review, develop, or mixed modes
  - Automatic directory structure and template generation

- **Repository Linking** (`air link`)
  - Link resources with NAME:PATH format
  - Review-only (read-only) or developer modes
  - Resource types: implementation, documentation, library, service
  - Symlink-based (no copying)
  - All linked repos go in `repos/` directory
  - List and manage linked resources

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

### Core Commands (v0.3.1)

```bash
# Project Management
air init [NAME]                      # Create or initialize project
air init --mode=MODE                 # Initialize with specific mode
air init --create-dir NAME           # Explicit directory creation

# Repository Linking
air link add NAME:PATH [OPTIONS]     # Link repository
  --review                           # Link as review-only
  --collaborate                      # Link as collaborative
  --type TYPE                        # Resource type
air link list [--format=json]        # List linked resources
air link remove NAME [--keep-link]   # Remove resource

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
  --format json                      # JSON output
air task archive ID [OPTIONS]        # Archive tasks
  --all                              # Archive all
  --before DATE                      # Archive before date
  --strategy STRATEGY                # Organization strategy
air task restore ID                  # Restore archived task

# Summary & Reporting
air summary [OPTIONS]                # Generate summary
  --format FORMAT                    # markdown|json|text
  --output FILE                      # Save to file
  --since DATE                       # Filter by date

# Resource Classification
air classify [OPTIONS]               # Classify resources
  --verbose                          # Show detection details
  --update                           # Update air-config.json
  --format json                      # JSON output
air classify RESOURCE                # Classify specific resource

# Validation & Status
air validate [--format=json]         # Validate project
air status [--format=json]           # Show project status
```

### Coming Soon

```bash
air pr [resource]                    # Create pull request
```

## License

MIT

## Based On

This toolkit evolved from the AA-ingest-review project, combining:
- Multi-project assessment patterns
- AI-assisted task tracking system
- Structured documentation approach
