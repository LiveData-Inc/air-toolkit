# AIR Toolkit - Quick Start (v0.6.2)

Get started with AIR in 5 minutes - complete workflow with advanced code analysis!

## Installation

```bash
# Install from PyPI (recommended)
pip install air-toolkit

# Or with pipx for isolated installation
pipx install air-toolkit

# Verify installation
air --version
```

### Development Installation

```bash
# Clone repository
git clone https://github.com/LiveData-Inc/air-toolkit.git
cd air-toolkit

# Install in development mode
pip install -e .
```

## Create Your First Project

```bash
# Create a new assessment project
air init my-review --mode=mixed

# Change to project directory
cd my-review

# Link a repository to review
air link add ~/repos/myapp --name myapp --review

# Create your first task
air task new "analyze architecture"

# Run deep code analysis
air analyze repos/myapp

# Validate project structure
air validate

# Check status
air status
```

You now have a complete AIR project:

```
my-review/
├── air-config.json      # Project configuration
├── README.md            # Project overview
├── CLAUDE.md            # AI assistant instructions
├── .air/                # Task tracking & agent coordination
│   ├── tasks/           # Task files (YYYYMMDD-NNN-HHMM format)
│   ├── agents/          # Background agents (v0.6.0)
│   └── context/         # Project context
├── repos/               # All linked repositories (symlinks)
├── analysis/            # Your analysis documents
│   ├── reviews/         # Code reviews
│   └── dependency-graph.json  # Multi-repo dependencies
└── scripts/             # Helper scripts
```

## Quick Commands (v0.6.0)

### Repository Linking
```bash
air link add PATH [OPTIONS]             # Link repository (fast, non-interactive)
air link add ~/repos/service            # Uses folder name, auto-detects type
air link add ~/repos/service --name myservice --review
air link add ~/docs --name docs --develop --type=documentation
air link add ~/repos/lib -i             # Interactive mode
air link list                           # List resources with status
air link remove NAME                    # Remove resource
air link remove -i                      # Interactive removal (numbered list)
```

### Code Analysis (v0.6.0)
```bash
air analyze repos/myapp                 # Comprehensive analysis (all analyzers)
air analyze repos/myapp --focus=security  # Security-focused
air analyze --all                       # Analyze all repos (dependency order)
air analyze --gap library-name          # Gap analysis
air analyze repos/myapp --background --id=analysis-1  # Background mode
air wait --all                          # Wait for background agents
air findings --all                      # Aggregate findings
air status --agents                     # View agent status
```

### Analysis Caching (v0.6.1)
```bash
air cache status                        # Show cache statistics
air cache status --format=json          # JSON output
air cache clear                         # Clear all cached data
air analyze repos/myapp --no-cache      # Force fresh analysis
air analyze repos/myapp --clear-cache   # Clear cache, then analyze
```

### External Library Exclusion (v0.6.2)
```bash
# By default, excludes .venv, node_modules, vendor/, build/, etc.
air analyze repos/myapp                 # Analyzes only your code (fast!)
air analyze repos/myapp --include-external  # Include vendor libraries

# Clear cache to rerun with new exclusion defaults
air cache clear
air analyze repos/myapp                 # Much faster, 98% less noise
```

### HTML Findings Report (v0.6.2)
```bash
air findings --all --html               # Generate rich HTML report
air findings --all --html --output custom-report.html
air findings --all --severity=critical --html  # Filtered HTML report
# Opens: analysis/findings-report.html (by default)
```

### Shell Completion (v0.6.2)
```bash
# Enable tab completion for your shell
air completion install                  # Auto-detects bash/zsh/fish
air completion install bash             # Specific shell
air completion show zsh                 # View completion script
air completion uninstall                # Remove completion
```

### Task Management
```bash
air task new "DESCRIPTION"              # Create task
air task new "fix bug" --prompt "Fix login issue"
air task status ID                      # View task details
air task status ID --format=json        # JSON output
air task complete ID                    # Mark task complete
air task complete ID --notes "All tests passing"
air task list                           # List active tasks
air task list --status=success          # Filter by status
air task list --sort=title              # Sort by title
air task list --search=auth             # Search tasks
air task list --all                     # Include archived
air task archive --all                  # Archive all tasks
air task restore ID                     # Restore task
```

### Summary Generation
```bash
air summary                             # Rich markdown to terminal
air summary --format=json               # JSON for AI
air summary --output=REPORT.md          # Save to file
air summary --since=2025-10-01          # Recent tasks only
```

### Check Status
```bash
air status                  # View project info
air status --format=json    # JSON output for AI
air validate                # Check project structure
```

## Common Workflows

### Review Workflow (Analyze Code)

1. **Create review project:**
   ```bash
   air init code-review --mode=review
   cd code-review
   ```

2. **Link resources:**
   ```bash
   air link add ~/repos/target-project --name target --review
   air link add ~/repos/comparison-project --name comparison --review
   ```

3. **Run deep analysis:**
   ```bash
   # Analyze all repos in dependency order
   air analyze --all

   # Or specific repo with focused analysis
   air analyze repos/target --focus=security
   ```

4. **Create task and document findings:**
   ```bash
   air task new "security audit" --prompt "Review security findings from analysis"
   # Review findings in analysis/reviews/target-findings.json
   # Write summary to analysis/reviews/security-audit.md
   ```

5. **Generate summary:**
   ```bash
   air summary --output=ANALYSIS-REPORT.md
   ```

6. **Archive tasks:**
   ```bash
   air task archive --all
   ```

### Development Workflow (Contribute)

1. **Create development project:**
   ```bash
   air init docs-improve --mode=develop
   cd docs-improve
   ```

2. **Link documentation repositories:**
   ```bash
   air link add ~/repos/docs-project --name docs --develop --type=documentation
   ```

3. **Create task:**
   ```bash
   air task new "improve API documentation" --prompt "Add missing examples"
   ```

4. **Create contributions:**
   - Review docs in `repos/docs/`
   - Place improved docs in `contributions/docs/`
   - Follow original structure

5. **Generate report:**
   ```bash
   air summary --output=IMPROVEMENTS.md
   ```

6. **Submit pull request:**
   ```bash
   # Use air pr command
   air pr docs --title "Improve API documentation" --body "Added examples and clarified usage"
   ```

## AI Assistant Integration

If you're using **Claude Code** or similar AI assistants:

### Claude Code Slash Commands (v0.6.2)

AIR includes **9 Claude Code-specific slash commands** for streamlined workflow:

```bash
/air-task          # Create and start new AIR task
/air-link PATH     # Quickly link repository
/air-analyze       # Run comprehensive analysis (air analyze --all)
/air-validate      # Validate project and auto-fix (air validate --fix)
/air-status        # Get project status (air status --format=json)
/air-findings      # Generate HTML findings report
/air-summary       # Generate work summary (air summary --format=json)
/air-review        # Generate code review context
/air-task-complete # Complete current task and commit changes
```

**Note:** These slash commands only work in Claude Code (`.claude/commands/`). For other AI assistants or manual use, use the regular `air` commands.

### Check if AIR is available
```bash
which air
```

### Use AIR commands when available
```bash
# Check project status
air status --format=json

# Validate structure
air validate --format=json

# List tasks
air task list --format=json
```

### Task tracking is automatic
AI assistants following the CLAUDE.md instructions will:
- Create task files for every piece of work
- Update with outcomes
- Archive when appropriate

## Project Modes

### Review Mode
```bash
air init project --mode=review
```
- **Purpose**: Analyze codebases (READ-ONLY)
- **Directories**: `repos/`, `analysis/reviews/`
- **Use case**: Compare implementations, identify patterns, security analysis

### Develop Mode
```bash
air init project --mode=develop
```
- **Purpose**: AI-assisted development with task tracking
- **Directories**: Standard project structure with `.air/` tracking
- **Use case**: Regular development with automatic task tracking

### Mixed Mode (Default)
```bash
air init project --mode=mixed
# or simply:
air init project
```
- **Purpose**: Both review and development
- **Directories**: All of the above
- **Use case**: Complex assessments with contributions to linked repos

## Task Archiving

Keep `.air/tasks/` organized:

```bash
# Archive tasks older than 30 days
air task archive --before=2025-09-01

# Archive all tasks (preview first)
air task archive --all --dry-run
air task archive --all

# View archive statistics
air task archive-status

# Restore if needed
air task restore 20251003-1430
```

Archived tasks move to `.air/tasks/archive/YYYY-MM/` and remain accessible with `air task list --all`.

## JSON Output

All status commands support `--format=json` for AI parsing:

```bash
air status --format=json
air validate --format=json
air task list --format=json
air task archive-status --format=json
```

## Next Steps

- **Read full docs**: See `docs/` directory
  - `COMMANDS.md` - Complete command reference
  - `SPECIFICATION.md` - Feature specifications
  - `AI-INTEGRATION.md` - AI assistant integration guide
  - `TASK-ARCHIVE-DESIGN.md` - Task archiving details

- **Example project**: Try the workflows above with a real repository

- **AI integration**: Use with Claude Code or similar AI assistants

- **Contribute**: See `DEVELOPMENT.md` for contributing guidelines

## Getting Help

```bash
# Command help
air --help
air init --help
air task --help

# Documentation
cat docs/COMMANDS.md

# Report issues
https://github.com/LiveData-Inc/air-toolkit/issues
```

## Quick Reference (v0.6.2)

| Command | Description |
|---------|-------------|
| `air init [NAME]` | Create or initialize project |
| `air link add PATH` | Link repository (auto-detects name/type) |
| `air link add PATH -i` | Interactive linking |
| `air link list` | List linked resources with status + writable column |
| `air analyze REPO` | Comprehensive code analysis (excludes vendor code) |
| `air analyze REPO --include-external` | Include .venv, node_modules, etc. |
| `air analyze --all` | Analyze all repos (dependency order, shows progress) |
| `air analyze --gap LIB` | Gap analysis |
| `air analyze --no-cache` | Force fresh analysis (skip cache) |
| `air cache status` | Show cache statistics |
| `air cache clear` | Clear all cached data |
| `air completion install` | Enable shell tab completion |
| `air findings --all` | Aggregate analysis findings |
| `air findings --all --html` | Generate rich HTML report |
| `air wait --all` | Wait for background agents |
| `air status --agents` | View background agent status |
| `air review` | Generate code review context |
| `air pr RESOURCE` | Create pull request |
| `air task new DESC` | Create task file |
| `air task status <id>` | View task details |
| `air task complete <id>` | Mark task as complete |
| `air task list` | List active tasks |
| `air task list --status=success` | Filter by status |
| `air task list --search=TERM` | Search tasks |
| `air summary` | Generate summary |
| `air validate` | Validate project structure |
| `air validate --fix` | Auto-fix broken symlinks |
| `air status` | Show project status (includes writable column) |
| `air classify` | Auto-classify resources |
| `air task archive --all` | Archive all tasks |

---

**Ready to dive deeper?** Check out the [full documentation](docs/README.md) or try creating your first assessment project!
