# AIR Toolkit - Quick Start (v0.2.0)

Get started with AIR in 5 minutes - complete workflow now available!

## Installation

```bash
# Clone repository
git clone https://github.com/LiveData-Inc/air-toolkit.git
cd air-toolkit

# Install in development mode
pip install -e .

# Verify installation
air --version
```

## Create Your First Project

```bash
# Create a new assessment project
air init my-review --mode=mixed

# Change to project directory
cd my-review

# Link a repository to review
air link add myapp:~/repos/myapp --review

# Create your first task
air task new "analyze architecture"

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
├── .air/                # Task tracking
│   ├── tasks/           # Task files go here
│   └── context/         # Project context
├── review/              # Linked resources (symlinks)
├── analysis/            # Your analysis documents
└── scripts/             # Helper scripts
```

## Quick Commands (v0.2.0)

### Repository Linking
```bash
air link add NAME:PATH [OPTIONS]        # Link repository
air link add service:~/repos/service --review
air link add docs:~/docs --collaborate --type=documentation
air link list                           # List resources
air link remove NAME                    # Remove resource
```

### Task Management
```bash
air task new "DESCRIPTION"              # Create task
air task new "fix bug" --prompt "Fix login issue"
air task list                           # List active tasks
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
   air link add target:~/repos/target-project --review
   air link add comparison:~/repos/comparison-project --review
   ```

3. **Create task:**
   ```bash
   air task new "analyze architecture" --prompt "Compare service architectures"
   ```

4. **Analyze and document:**
   - Read code in `review/target/`
   - Write analysis to `analysis/assessments/target.md`
   - Create comparison documents

5. **Generate summary:**
   ```bash
   air summary --output=ANALYSIS-REPORT.md
   ```

6. **Archive tasks:**
   ```bash
   air task archive --all
   ```

### Collaborate Workflow (Contribute)

1. **Create collaborative project:**
   ```bash
   air init docs-improve --mode=collaborate
   cd docs-improve
   ```

2. **Link documentation repositories:**
   ```bash
   air link add docs:~/repos/docs-project --collaborate --type=documentation
   ```

3. **Create task:**
   ```bash
   air task new "improve API documentation" --prompt "Add missing examples"
   ```

4. **Create contributions:**
   - Review docs in `collaborate/docs/`
   - Place improved docs in `contributions/docs/`
   - Follow original structure

5. **Generate report:**
   ```bash
   air summary --output=IMPROVEMENTS.md
   ```

6. **Submit** (coming soon: `air pr`):
   ```bash
   # Manual PR for now
   cd collaborate/docs
   git checkout -b improve-docs
   # Copy contributions, commit, push
   gh pr create
   ```

## AI Assistant Integration

If you're using **Claude Code** or similar AI assistants:

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
- **Directories**: `review/`, `analysis/assessments/`
- **Use case**: Compare implementations, identify patterns

### Collaborate Mode
```bash
air init project --mode=collaborate
```
- **Purpose**: Contribute improvements
- **Directories**: `collaborate/`, `contributions/`
- **Use case**: Documentation improvements, code contributions

### Mixed Mode (Default)
```bash
air init project --mode=mixed
# or simply:
air init project
```
- **Purpose**: Both review and collaborate
- **Directories**: All of the above
- **Use case**: Complex assessments with some contributions

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

## Quick Reference (v0.2.0)

| Command | Description |
|---------|-------------|
| `air init [NAME]` | Create or initialize project |
| `air link add NAME:PATH` | Link repository |
| `air link list` | List linked resources |
| `air task new DESC` | Create task file |
| `air task list` | List active tasks |
| `air summary` | Generate summary |
| `air validate` | Validate project structure |
| `air status` | Show project status |
| `air task archive --all` | Archive all tasks |
| `air task restore <id>` | Restore archived task |

---

**Ready to dive deeper?** Check out the [full documentation](docs/README.md) or try creating your first assessment project!
