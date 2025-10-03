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

### Create Assessment Project

```bash
# Create new assessment project
air init my-review

cd my-review

# Configure repositories to review
air link --review service-a:~/repos/service-a
air link --review service-b:~/repos/service-b

# Validate setup
air validate

# Check status
air status
```

### AI Task Tracking

```bash
# Initialize .air/ tracking in any project
cd ~/my-project
air track init

# Create task file
air task new "implement feature X"

# List tasks
air task list

# Generate summary
air summary
```

## Features

### Assessment Workflow
- **Project Initialization**: Create structured assessment projects
- **Repository Linking**: Symlink or clone repositories for review
- **Resource Classification**: Distinguish between review-only and collaborative resources
- **Validation**: Check project structure and links
- **Status Reporting**: View project status and progress
- **PR Creation**: Submit improvements to collaborative repositories

### Task Tracking
- **Automatic Task Files**: AI creates task files as work progresses
- **Structured Format**: Consistent markdown format with metadata
- **Context Management**: Track architecture, language conventions, decisions
- **Summary Generation**: Compile task summaries across projects

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

```bash
# Assessment commands
air init [name]          # Create assessment project
air link                 # Link repositories
air validate             # Validate project structure
air status               # Show project status
air classify             # Classify resource types
air pr [resource]        # Create pull request

# Task tracking commands
air track init           # Initialize .air/ tracking
air task new [desc]      # Create task file
air task list            # List all tasks
air summary              # Generate task summary

# Utility commands
air version              # Show version
air config               # Configure AIR settings
```

## License

MIT

## Based On

This toolkit evolved from the AA-ingest-review project, combining:
- Multi-project assessment patterns
- AI-assisted task tracking system
- Structured documentation approach
