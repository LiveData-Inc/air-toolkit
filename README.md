# AIR - AI Review & Development Toolkit

**AIR** = **AI Review** - A unified toolkit for AI-assisted development and multi-project code assessment.

## Overview

AIR provides two complementary capabilities:

1. **Multi-Project Assessment**: Create structured review projects to analyze and compare multiple codebases
2. **AI Task Tracking**: Automatic task file generation and tracking for AI-assisted development

## Installation

### From Source (Development)

```bash
cd air-toolkit
pip install -e .
```

### From PyPI (Future)

```bash
pip install air-toolkit
# or for isolated installation
pipx install air-toolkit
```

## Quick Start

### Complete Workflow (v0.2.0)

```bash
# 1. Initialize project
air init my-assessment --mode=mixed

cd my-assessment

# 2. Link repositories
air link add service-a:~/repos/service-a --review
air link add docs:~/repos/docs --collaborate --type=documentation

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

### Core Workflow (v0.2.0) ✅
- **Project Initialization** (`air init`)
  - Create new projects or initialize in existing directories
  - Support for review, collaborate, or mixed modes
  - Automatic directory structure and template generation

- **Repository Linking** (`air link`)
  - Link resources with NAME:PATH format
  - Review-only (read-only) or collaborative modes
  - Resource types: implementation, documentation, library, service
  - Symlink-based (no copying)
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

### Task Archive System ✅
- Archive tasks by ID, date, or all tasks
- Organization strategies: by-month, by-quarter, flat
- Task restoration from archive
- Archive statistics and reporting

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

### Core Commands (v0.2.0)

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
air task list [OPTIONS]              # List tasks
  --all                              # Include archived
  --archived                         # Only archived
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

# Validation & Status
air validate [--format=json]         # Validate project
air status [--format=json]           # Show project status
```

### Coming Soon

```bash
air classify                         # Auto-classify resources
air pr [resource]                    # Create pull request
air task complete ID                 # Mark task complete
```

## License

MIT

## Based On

This toolkit evolved from the AA-ingest-review project, combining:
- Multi-project assessment patterns
- AI-assisted task tracking system
- Structured documentation approach
