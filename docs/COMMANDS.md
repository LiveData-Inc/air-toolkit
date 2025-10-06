# AIR Toolkit - Commands Reference

**Version:** 0.6.2.post2
**Last Updated:** 2025-10-05

Complete reference for all AIR commands.

## Table of Contents

- [Global Options](#global-options)
- [Claude Code Slash Commands](#claude-code-slash-commands) ⭐ NEW
- [Assessment Commands](#assessment-commands)
  - [air init](#air-init)
  - [air link](#air-link)
  - [air validate](#air-validate)
  - [air status](#air-status)
  - [air classify](#air-classify)
  - [air pr](#air-pr)
- [Code Review Commands](#code-review-commands)
  - [air review](#air-review)
  - [air claude](#air-claude)
- [Agent Coordination Commands](#agent-coordination-commands)
  - [air analyze](#air-analyze)
  - [air cache](#air-cache)
  - [air status --agents](#air-status---agents)
  - [air findings](#air-findings)
  - [air wait](#air-wait)
- [Task Tracking Commands](#task-tracking-commands)
  - [air task](#air-task)
  - [air track](#air-track)
  - [air summary](#air-summary)
- [Utility Commands](#utility-commands)
  - [air completion](#air-completion)
  - [air upgrade](#air-upgrade)
  - [air version](#air-version)

## Global Options

These options work with all commands:

```bash
air --version        # Show version and exit
air --help           # Show help message
```

---

## Claude Code Slash Commands

AIR provides **9 Claude Code-specific slash commands** for streamlined workflow. These commands are defined in `.claude/commands/` and only work in Claude Code's CLI interface.

**Available Slash Commands:**

| Command | Description | Equivalent Air Command |
|---------|-------------|------------------------|
| `/air-task` | Create and start new AIR task | Manual task file creation |
| `/air-link PATH` | Quickly link a repository | `air link add PATH` |
| `/air-analyze` | Run comprehensive analysis | `air analyze --all` |
| `/air-validate` | Validate project and auto-fix | `air validate --fix` |
| `/air-status` | Get project status for AI | `air status --format=json` |
| `/air-findings` | Generate HTML findings report | `air findings --all --html` |
| `/air-summary` | Generate work summary | `air summary --format=json` |
| `/air-review` | Generate code review context | `air review --format=json` |
| `/air-task-complete` | Complete current task and commit | `air task complete` + git commit |

**Usage Examples:**

```bash
# Start a new task (Claude Code only)
/air-task

# Quickly link a repository (Claude Code only)
/air-link ~/repos/myapp

# Run comprehensive analysis (Claude Code only)
/air-analyze

# Generate HTML report (Claude Code only)
/air-findings

# Complete work session (Claude Code only)
/air-task-complete
```

**Note:** For other AI assistants or manual CLI use, use the regular `air` commands shown in the "Equivalent Air Command" column.

---

## Assessment Commands

Commands for creating and managing multi-project assessment projects.

---

### air init

Create a new AIR assessment project.

#### Usage

```bash
air init [NAME] [OPTIONS]
```

#### Arguments

- `NAME` - Project name/directory (default: current directory `.`)

#### Options

- `--mode=MODE` - Project mode (default: `mixed`)
  - `review` - Review-only mode
  - `develop` - Development mode with tracking
  - `mixed` - Both review and developer
- `--track / --no-track` - Initialize .air/ tracking (default: enabled)

#### Examples

```bash
# Create mixed-mode project (default)
air init my-review

# Create review-only project
air init service-review --mode=review

# Create developer project without tracking
air init docs --mode=develop --no-track

# Initialize in current directory
air init
```

#### Output

Creates project structure:

**Review Mode:**
```
project-name/
├── README.md
├── CLAUDE.md
├── .air/air-config.json
├── .gitignore
├── repos/
├── analysis/
│   └── reviews/
├── .air/
└── scripts/
```

**Develop Mode:**
```
project-name/
├── README.md
├── CLAUDE.md
├── .air/air-config.json
├── .gitignore
├── repos/
├── analysis/
│   └── improvements/
├── contributions/
├── .air/
└── scripts/
```

**Mixed Mode:**
```
project-name/
├── README.md
├── CLAUDE.md
├── .air/air-config.json
├── .gitignore
├── repos/
├── analysis/
│   ├── SUMMARY.md
│   ├── reviews/
│   └── improvements/
├── contributions/
├── .air/
└── scripts/
```

#### Next Steps

After running `air init`:

1. Edit `README.md` with project goals
2. Configure repositories (see `air link`)
3. Validate structure: `air validate`
4. Start AI analysis session

---

### air link

Link repositories to the assessment project. Non-interactive by default for fast workflow.

#### Commands

##### air link add

Add a resource to the project.

**Usage:**

```bash
air link add PATH [OPTIONS]
```

**Non-Interactive Mode (default):**

Fast mode with smart defaults - no prompts:

```bash
# Fastest: use folder name, auto-detect type, review mode ⭐ RECOMMENDED
air link add ~/repos/my-service

# With custom name
air link add ~/repos/service-a --name my-service

# With explicit type
air link add ~/repos/service-a --type library

# Developer mode
air link add ~/repos/service-a --develop

# Fully explicit
air link add ~/repos/service-a --name my-service --review --type library
```

**Interactive Mode:**

Use `-i` flag for guided prompts and customization:

```bash
# Interactive setup with prompts
air link add ~/repos/service-a -i

# Interactive mode features:
# - Path validation and verification
# - Name suggestion with uniqueness check
# - Relationship choice (review/develop)
# - Auto-classification with opt-out
# - Confirmation summary
```

**Options:**

- `PATH` - Path to repository (required)
- `--name NAME` - Resource name/alias (default: folder name)
- `--review` - Link as review-only resource (read-only) **[default]**
- `--develop` - Link as developer resource (can contribute)
- `--type TYPE` - Resource type: `library`, `documentation`, `service` (default: auto-detect)
- `-i, --interactive` - Interactive mode with prompts

**Smart Defaults:**

1. **Name** - Uses folder name if not provided
2. **Type** - Auto-classifies by analyzing repository structure
3. **Relationship** - Defaults to `review` (read-only)

**Examples:**

```bash
# Quick link (folder name + auto-detect) ⭐ RECOMMENDED
air link add /path/to/my-repo

# Custom name
air link add /path/to/my-repo --name custom-name

# Developer mode with auto-detect
air link add /path/to/my-repo --develop

# Explicit type (skip auto-detection)
air link add /path/to/my-repo --type documentation

# Interactive mode for full customization
air link add /path/to/my-repo -i
```

**Auto-Classification:**

When `--type` is not provided, AIR analyzes the repository:
- Detects languages (Python, JavaScript, Go, etc.)
- Identifies frameworks (Django, React, FastAPI, etc.)
- Classifies as: `library`, `documentation`, or `service`
- Generates technology stack (e.g., "Python/FastAPI")

##### air link list

List all linked resources.

**Usage:**

```bash
air link list [--format FORMAT]
```

**Options:**

- `--format FORMAT` - Output format: `human` (default) or `json`

**Examples:**

```bash
# Human-readable table
air link list

# JSON output
air link list --format json
```

##### air link remove

Remove a linked resource.

**Usage:**

```bash
air link remove [NAME] [OPTIONS]
```

**Non-Interactive Mode:**

Provide resource name directly:

```bash
# Remove resource and symlink
air link remove service-a

# Remove from config but keep symlink
air link remove service-a --keep-link
```

**Interactive Mode:**

Use `-i` for numbered list selection:

```bash
# Select from numbered list
air link remove -i

# Shows:
# Linked Resources:
#
# #  Name         Type           Relationship  Path
# 1  service-a    library        review        /path/to/service-a
# 2  docs         documentation  review        /path/to/docs
# 3  my-api       service        develop       /path/to/my-api
#
# Select resource to remove (number or 'q' to quit) [q]: 2
# Remove resource: docs
# Confirm removal? [y/N]: y
# ✓ Removed resource: docs
```

**Options:**

- `NAME` - Resource name (required if not using `-i`)
- `-i, --interactive` - Interactive mode with numbered selection
- `--keep-link` - Keep symlink, only remove from config

**Examples:**

```bash
# Direct removal by name
air link remove service-a

# Remove but keep symlink
air link remove service-a --keep-link

# Interactive selection ⭐ RECOMMENDED
air link remove -i

# Interactive + keep symlink
air link remove -i --keep-link
```

#### Behavior

**Review Resources:**
- Always created as symlinks (read-only)
- Placed in `repos/` directory
- Original repository not modified
- Relationship: `REVIEW_ONLY`

**Developer Resources:**
- Created as symlinks
- Placed in `repos/` directory
- Can be modified (for contributing back)
- Relationship: `DEVELOPER`

**All Resources:**
- Stored in `repos/` directory
- Managed in `.air/air-config.json`
- Validated for uniqueness

#### Exit Codes

- `0` - Success
- `1` - Validation error or resource not found
- `2` - Configuration error

---

### air validate

Validate assessment project structure.

#### Usage

```bash
air validate [OPTIONS]
```

#### Options

- `--type=TYPE` - Validation type (default: `all`)
  - `structure` - Check directory structure
  - `links` - Check symlinks and clones
  - `config` - Validate configuration file
  - `all` - All checks
- `--fix` - Attempt to fix issues automatically

#### Examples

```bash
# Validate everything
air validate

# Check only symlinks
air validate --type=links

# Validate and attempt fixes
air validate --fix
```

#### Checks Performed

**Structure Check:**
- Required directories exist
- `.air/air-config.json` present
- Mode-appropriate structure (repos/, analysis/, contributions/, etc.)

**Links Check:**
- Symlinks point to valid locations
- Cloned repositories accessible
- No broken links

**Config Check:**
- JSON is valid
- Required fields present
- Resource paths match linked resources
- Mode matches directory structure

#### Output

```
[i] Validating project structure...

Structure:
  ✓ README.md
  ✓ .air/air-config.json
  ✓ repos/
  ✓ analysis/reviews/

Links:
  ✓ repos/service-a -> /Users/user/repos/service-a
  ✓ repos/service-b -> /Users/user/repos/service-b

Config:
  ✓ Valid JSON
  ✓ All resources defined
  ✓ Mode matches structure

[✓] Project structure is valid
```

#### Exit Codes

- `0` - Valid
- `3` - Validation errors found

---

### air status

Show assessment project status.

#### Usage

```bash
air status [OPTIONS]
```

#### Options

- `--type=TYPE` - Filter by type (default: `all`)
  - `review` - Show only review resources
  - `develop` - Show only developer resources
  - `all` - Show all resources
- `--contributions` - Show contribution tracking details

#### Examples

```bash
# Show all status
air status

# Show only review resources
air status --type=review

# Show with contribution details
air status --contributions
```

#### Output

```
AIR Project Status
==================

Project: my-review
Mode: mixed
Created: 2025-10-03

Review Resources (2):
  ✓ service-a (linked)
  ✓ service-b (linked)

Collaborative Resources (1):
  ✓ architecture (cloned)

Analysis Output:
  Assessments: 2 documents
  Improvements: 1 document

AI Tasks:
  Total: 5
  Completed: 3
  In Progress: 2
```

#### With --contributions

```
Contributions:
  architecture
    ✓ new-guide.md -> docs/guides/implementation-guide.md (proposed)
    ✓ Update ADR-2025.008 (draft)

Next Actions:
  1. Review contributions/architecture/
  2. Submit PR: air pr architecture
```

---

### air classify

Classify resources by type (review vs developer).

#### Usage

```bash
air classify [OPTIONS]
```

#### Options

- `--verbose` - Show detailed classification reasoning
- `--update` - Update `.air/air-config.json` with classifications

#### Examples

```bash
# Classify resources
air classify

# Show detailed reasoning
air classify --verbose

# Classify and update config
air classify --update
```

#### Classification Logic

**Review-Only Indicators:**
- Contains implementation code (`.py`, `.js`, `.java`, etc.)
- Service/application repository
- No write access
- Symlinked (not cloned)

**Collaborative Indicators:**
- Contains primarily documentation (`.md`, `.rst`)
- Architecture/design repository
- Write access available
- Cloned repository

#### Output

```
Resource Classification:

Review-Only (2):
  ✓ service-a (library)
    Reason: Contains Python implementation code
    Analysis: analysis/reviews/service-a.md

  ✓ service-b (library)
    Reason: Service implementation
    Analysis: analysis/reviews/service-b.md

Developer (1):
  ✓ architecture (documentation)
    Reason: Architecture documentation repository
    Analysis: analysis/improvements/gaps.md
    Contributions: 2 proposed

Workflow Status:
  Review: ✅ Complete (2/2 analyzed)
  Contribute: ⏳ Pending (1 needs PR)
```

#### Interactive Mode

For ambiguous resources:

```
Resource: shared-utils
Could be either review or developer.

Indicators:
  - Contains implementation code
  - Also contains extensive documentation
  - Has write access

Classify as (review/develop)? develop
```

---

### air pr

Create pull request for developer resource.

#### Usage

```bash
air pr [RESOURCE] [OPTIONS]
```

#### Arguments

- `RESOURCE` - Name of developer resource (optional - lists resources if omitted)

#### Options

- `--base=BRANCH` - Base branch for PR (default: `main`)
- `--title=TEXT` - Custom PR title (default: auto-generated from tasks)
- `--body=TEXT` - Custom PR body (default: auto-generated from tasks)
- `--draft` - Create as draft PR
- `--dry-run` - Show what would be done without making changes

#### Examples

```bash
# List developer resources with contribution status
air pr

# Create PR for resource (auto-generated title/body)
air pr docs

# Create PR with custom title and body
air pr docs --title="Add API documentation" --body="Comprehensive API guide"

# Create draft PR
air pr docs --draft

# Create PR against develop branch
air pr docs --base=develop

# Preview without creating PR
air pr docs --dry-run
```

#### Workflow

1. Detect changes in `contributions/{resource}/` directory
2. Generate PR title and body from recent task files
3. Copy files from contributions to resource repository
4. Create git branch and commit changes
5. Push branch to remote
6. Create pull request via `gh` CLI

#### Requirements

- GitHub CLI (`gh`) must be installed and authenticated
  - Install: `brew install gh` (macOS) or see [GitHub CLI docs](https://cli.github.com/)
  - Authenticate: `gh auth login`
- Resource must be a git repository
- Resource must be marked as developer (`--develop` flag when linking)
- Contributions must exist in `contributions/{resource}/` directory

#### Auto-Generated PR Metadata

When `--title` and `--body` are not provided, the PR metadata is automatically generated:

**Title:**
- Format: `Improvements to {resource}`

**Body:**
- Summary of improvements
- Related Work section (from last 5 task files)
- Changes section
- Footer with AIR Toolkit attribution

**Branch Name:**
- Format: `air/{sanitized-title}`
- Example: `air/improvements-to-docs`

#### Output

```
Creating PR for: docs

  Branch: air/improvements-to-docs
  Base: main
  Title: Improvements to docs
  Files: 3
  Draft: No

[i] Copying contributions...
[✓] Copied 3 files

[i] Creating branch and committing...
[✓] Committed changes to air/improvements-to-docs

[i] Creating pull request...
[✓] Pull request created successfully!

https://github.com/org/docs/pull/42
```

#### Dry Run Output

```
[⚠] Dry run mode - no changes will be made

Creating PR for: docs

  Branch: air/add-api-docs
  Base: main
  Title: Add API documentation
  Files: 5
  Draft: No

Files to be contributed:
  • README.md
  • api/endpoints.md
  • api/authentication.md
  • examples/quickstart.md
  • examples/advanced.md
```

#### Listing Collaborative Resources

When no resource is specified, shows all developer resources with contribution status:

```
Collaborative Resources:

┌──────────┬──────────────┬───────────────┬─────────────┐
│ Resource │ Type         │ Contributions │ Status      │
├──────────┼──────────────┼───────────────┼─────────────┤
│ docs     │ documentation│ 3             │ ✓ Ready     │
│ api      │ implementation│ 0             │ ○ No changes│
└──────────┴──────────────┴───────────────┴─────────────┘

💡 Run 'air pr RESOURCE' to create a pull request
```

---

## Code Review Commands

Commands for AI-powered code review and assistant integration.

---

### air review

Generate code review context from git changes.

#### Usage

```bash
air review [OPTIONS] [FILES]...
```

#### Options

- `--base TEXT` - Base branch to compare against (default: `main`)
- `--pr` - Review current PR branch against base
- `--format [json|markdown]` - Output format (default: `json`)

#### Arguments

- `FILES` - Specific files to review (optional)

#### Examples

```bash
# Review uncommitted changes
air review

# Review PR branch
air review --pr

# Review specific files
air review src/api/routes.py
```

#### Integration with Claude Code

Use the `/air-review` slash command in Claude Code.

---

### air claude

AI assistant helper commands for getting project context.

#### Subcommands

- `context` - Get comprehensive project context for AI assistants

#### Examples

```bash
# Get context in JSON (for AI)
air claude context

# Get context in markdown
air claude context --format=markdown
```

---

## Agent Coordination Commands

Commands for running parallel analyses and coordinating multiple AI agents (v0.6.0+).

---

### air analyze

Analyze a repository using AI-powered classification and insights.

**Usage:**

```bash
air analyze RESOURCE_PATH [OPTIONS]
```

**Options:**

- `--background` - Run analysis in background as an agent
- `--id TEXT` - Agent identifier (for background mode)
- `--focus TEXT` - Analysis focus area (security, architecture, performance)
- `--no-cache` - Force fresh analysis (skip cache lookup)
- `--clear-cache` - Clear cache before running analysis

**Examples:**

```bash
# Inline analysis (runs immediately)
air analyze repos/service-a

# Focused analysis
air analyze repos/service-a --focus=security

# Background analysis (spawn agent)
air analyze repos/service-a --background --id=security-analysis

# Multiple parallel analyses
air analyze repos/service-a --background --id=analysis-1
air analyze repos/service-b --background --id=analysis-2
air analyze repos/service-c --background --id=analysis-3

# Force fresh analysis (skip cache)
air analyze repos/service-a --no-cache

# Clear cache before analyzing
air analyze repos/service-a --clear-cache
```

**Output:**

- **Inline mode**: Displays classification results to terminal
- **Background mode**: Spawns detached agent, writes to `.air/agents/<id>/`

**Files Created:**

- `analysis/reviews/<resource>-findings.json` - Analysis findings
- `.air/agents/<id>/metadata.json` - Agent metadata (background only)
- `.air/agents/<id>/stdout.log` - Agent output (background only)

---

### air cache

Manage analysis cache for improved performance.

**Subcommands:**

#### air cache status

Display cache statistics including size, hit rate, and entry count.

**Usage:**

```bash
air cache status [--format=FORMAT]
```

**Options:**

- `--format=FORMAT` - Output format (text or json, default: text)

**Examples:**

```bash
# Show cache statistics
air cache status

# JSON output
air cache status --format=json
```

**Output:**

Text format displays a formatted table with:
- Total Entries - Number of cached analysis results
- Cache Size - Total size in MB
- Cache Hits - Number of successful cache retrievals
- Cache Misses - Number of cache misses (analysis ran)
- Hit Rate - Percentage of cache hits (higher is better)
- Last Cleared - When cache was last cleared

```
Cache Statistics
───────────────────────────────────
Metric          Value
───────────────────────────────────
Total Entries   15
Cache Size      2.34 MB
Cache Hits      45
Cache Misses    10
Hit Rate        81.8%
Last Cleared    2025-10-05 10:30:15
```

JSON format provides machine-readable output:

```json
{
  "total_entries": 15,
  "cache_size_mb": 2.34,
  "hit_count": 45,
  "miss_count": 10,
  "hit_rate": 81.8,
  "last_cleared": "2025-10-05T10:30:15"
}
```

**Performance Interpretation:**

- **80%+ hit rate**: Excellent - Cache is working optimally
- **50-80% hit rate**: Good - Cache is warming up
- **<50% hit rate**: Low - Many fresh analyses or frequent file changes

#### air cache clear

Clear all cached analysis results. Requires confirmation.

**Usage:**

```bash
air cache clear
```

**Examples:**

```bash
# Clear all cache (will prompt for confirmation)
air cache clear
```

**Confirmation Prompt:**

```
Are you sure you want to clear the cache? This cannot be undone. [y/N]:
```

**Output:**

```
[i] Clearing cache...
[✓] Cache cleared: 15 entries (2.34 MB) removed
```

**When to Clear Cache:**

- After AIR version upgrade (automatic, but can force)
- When analyzer logic changes significantly
- When troubleshooting unexpected analysis results
- When cache size grows too large
- When switching analysis focus areas

**Cache Behavior:**

- Cache stored in `.air/cache/` directory
- Organized by repository hash
- Separate cache files per analyzer (security, performance, etc.)
- Metadata tracks file hashes for invalidation
- Automatically invalidates when files change
- Automatically invalidates when AIR version changes

**Cache Flags on `air analyze`:**

```bash
# Force fresh analysis (skip cache)
air analyze repos/myapp --no-cache

# Clear cache before analyzing
air analyze repos/myapp --clear-cache

# Normal analysis (uses cache)
air analyze repos/myapp
```

---

### air status --agents

Show status of all background agents.

**Usage:**

```bash
air status --agents [--format=FORMAT]
```

**Options:**

- `--format` - Output format: human (default) or json

**Examples:**

```bash
# Human-readable table
air status --agents

# JSON format for scripts
air status --agents --format=json
```

**Output Example:**

```
Active Agents

Agent       Status     Started    Progress
analysis-1  ⏳ Running 5m ago     Analyzing database queries...
analysis-2  ✓ Complete 10m ago
analysis-3  ⏳ Running 2m ago     Reviewing security patterns...

Total: 3 agents (2 running, 1 complete, 0 failed)
```

---

### air findings

View and aggregate analysis findings from all agents.

**Usage:**

```bash
air findings [OPTIONS]
```

**Options:**

- `--all` - Show findings from all analyses (recommended)
- `--severity TEXT` - Filter by severity: high, medium, low
- `--format` - Output format: human (default) or json

**Examples:**

```bash
# View all findings
air findings --all

# High-severity findings only
air findings --all --severity=high

# JSON format for processing
air findings --all --format=json
```

**Output Example:**

```
Analysis Findings

Source       Severity  Category        Description
service-a    ⚠️  High   Security        No password hashing
service-a    ⚡ Medium Performance     Missing database index
service-b    ⚠️  High   Security        SQL injection risk
service-c    ℹ️  Low    Style           Long function detected

Total: 4 findings (2 high, 1 medium, 1 low)
```

---

### air wait

Wait for background agents to complete (v0.6.0+).

**Usage:**

```bash
air wait [OPTIONS]
```

**Options:**

- `--all` - Wait for all running agents
- `--agents TEXT` - Comma-separated agent IDs to wait for
- `--timeout INTEGER` - Timeout in seconds (optional)
- `--interval INTEGER` - Check interval in seconds (default: 5)
- `--format` - Output format: human (default) or json

**Examples:**

```bash
# Wait for all agents
air wait --all

# Wait for specific agents
air wait --agents analysis-1,analysis-2

# With timeout (exit after 300 seconds)
air wait --all --timeout=300

# JSON format for scripts
air wait --all --format=json

# Custom check interval (poll every 2 seconds)
air wait --all --interval=2
```

**Output:**

```
Waiting for agents to complete...
Timeout: None
All agents complete (elapsed: 45s)

✓ 3 agent(s) completed successfully
```

**JSON Output:**

```json
{
  "success": true,
  "message": "All agents complete",
  "elapsed": 45,
  "agents": [
    {
      "id": "analysis-1",
      "status": "complete",
      "started": "2025-10-04T16:00:00"
    }
  ]
}
```

**Behavior:**

- Blocks until all specified agents complete or timeout expires
- Auto-detects terminated processes
- Exits with code 0 on success, 1 on failure or timeout
- Shows failed agents if any fail during execution

**Use Case: Coordination Workflows**

The `air wait` command is designed for Claude to coordinate multi-agent workflows:

```bash
# Claude spawns workers
air analyze repos/service-a --background --id=worker-1
air analyze repos/service-b --background --id=worker-2
air analyze repos/service-c --background --id=worker-3

# Claude waits for all to complete
air wait --all

# Claude aggregates results
air findings --all
```

See [AGENT-COORDINATION.md](AGENT-COORDINATION.md) for workflow patterns.

---

## Task Tracking Commands

Commands for managing AI task files and tracking.

---

### air task

Manage AI task files.

#### Usage

```bash
air task SUBCOMMAND [OPTIONS]
```

#### Subcommands

- `new` - Create new task file
- `list` - List all task files
- `status` - Show task details
- `complete` - Mark task as complete
- `archive` - Archive task files
- `restore` - Restore archived tasks
- `archive-status` - Show archive statistics

---

#### air task new

Create new task file.

#### Usage

```bash
air task new DESCRIPTION [OPTIONS]
```

#### Arguments

- `DESCRIPTION` - Brief task description (kebab-case recommended)

#### Options

- `--prompt=TEXT` - User prompt that triggered this task

#### Examples

```bash
# Create task
air task new "implement feature X"

# With prompt
air task new "fix bug Y" --prompt "Fix the login redirect issue"
```

#### Output

Creates file: `.air/tasks/YYYYMMDD-HHMM-description.md`

```markdown
# Task: Implement feature X

## Date
2025-10-03 14:30

## Prompt
[To be filled by AI or user]

## Actions Taken
1. [Actions will be documented here]

## Files Changed
- [Files will be listed here]

## Outcome
⏳ In Progress

[Summary will be added when complete]

## Notes
[Optional notes]
```

---

#### air task list

List all task files.

#### Usage

```bash
air task list [OPTIONS]
```

#### Options

- `--status=STATUS` - Filter by status
  - `all` - All tasks (default)
  - `in-progress` - Only in-progress tasks
  - `success` - Only completed tasks
  - `blocked` - Only blocked tasks

#### Examples

```bash
# List all tasks
air task list

# List in-progress tasks
air task list --status=in-progress

# List completed tasks
air task list --status=success
```

#### Output

```
AI Tasks (5 total)

✅ 20251003-1200-implement-feature-x.md (Success)
   Prompt: Add user authentication
   Files: 3 changed
   Duration: 2h 15m

⏳ 20251003-1315-fix-bug-y.md (In Progress)
   Prompt: Fix login redirect issue
   Files: 1 changed

✅ 20251003-0945-refactor-services.md (Success)
   Prompt: Refactor service layer
   Files: 7 changed
   Duration: 4h 30m

⚠️ 20251002-1630-add-tests.md (Partial)
   Prompt: Add integration tests
   Files: 2 changed
   Note: Missing test data fixtures

❌ 20251002-1100-deploy-feature.md (Blocked)
   Prompt: Deploy to staging
   Note: Waiting for DevOps approval
```

---

#### air task complete

Mark task as complete.

#### Usage

```bash
air task complete TASK_ID
```

#### Arguments

- `TASK_ID` - Task identifier (timestamp or prefix)

#### Examples

```bash
# Full timestamp
air task complete 20251003-1200

# Prefix (if unique)
air task complete 20251003

# Partial match
air task complete 1003-1200
```

#### Output

```
[i] Marking task complete: 20251003-1200-implement-feature-x

[✓] Task marked as complete
```

Updates task file outcome to `✅ Success`.

---

#### air task status

Show detailed information about a task.

#### Usage

```bash
air task status TASK_ID [OPTIONS]
```

#### Arguments

- `TASK_ID` - Task identifier (timestamp or prefix)

#### Options

- `--format=FORMAT` - Output format (`human` or `json`)

#### Examples

```bash
# Show task details
air task status 20251003-1200

# JSON output
air task status 20251003-1200 --format=json
```

#### Output

Displays full task information including prompt, actions taken, files changed, outcome, and notes.

---

#### air task archive

Archive task files to `.air/tasks/archive/` organized by year and month.

#### Usage

```bash
air task archive [TASK_IDS...] [OPTIONS]
```

#### Arguments

- `TASK_IDS` - One or more task identifiers (optional if using flags)

#### Options

- `--all` - Archive all tasks
- `--before=DATE` - Archive tasks before date (YYYY-MM-DD)
- `--strategy=STRATEGY` - Archive organization strategy (default: `by-month`)
  - `by-month` - Organize as `.air/tasks/archive/YYYY-MM/`
  - `by-quarter` - Organize as `.air/tasks/archive/YYYY-QN/`
  - `flat` - No subdirectories
- `--dry-run` - Preview what would be archived

#### Examples

```bash
# Archive specific task
air task archive 20251003-1200

# Archive multiple tasks
air task archive 20251003-1200 20251003-1215

# Archive all tasks
air task archive --all

# Archive tasks before October 1, 2025
air task archive --before=2025-10-01

# Preview archiving
air task archive --all --dry-run

# Use quarterly organization
air task archive --all --strategy=by-quarter
```

#### Output

```
[✓] Archived: 20251003-1200-task.md → 2025-10/20251003-1200-task.md
Updated archive summary: .air/tasks/archive/ARCHIVE.md
[✓] Archived 1 tasks to .air/tasks/archive/
```

**Note:**
- Archiving helps reduce AI context window usage by moving completed tasks out of the active directory while maintaining full history.
- An `ARCHIVE.md` summary file is automatically generated/updated in the archive directory, providing an organized index of all archived tasks by time period.

---

#### air task restore

Restore archived tasks back to active tasks directory.

#### Usage

```bash
air task restore TASK_IDS...
```

#### Arguments

- `TASK_IDS` - One or more task identifiers to restore

#### Examples

```bash
# Restore single task
air task restore 20251003-1200

# Restore multiple tasks
air task restore 20251003-1200 20251003-1215
```

#### Output

```
[✓] Restored: 20251003-1200-task.md
Updated archive summary: .air/tasks/archive/ARCHIVE.md
[✓] Restored 1 tasks from archive
```

**Note:** The archive summary is automatically updated when tasks are restored.

---

#### air task archive-status

Show statistics about archived tasks.

#### Usage

```bash
air task archive-status [OPTIONS]
```

#### Options

- `--format=FORMAT` - Output format (`human` or `json`)

#### Examples

```bash
# Show archive statistics
air task archive-status

# JSON output
air task archive-status --format=json
```

#### Output

```
Archive Statistics

Total archived tasks: 47

By Month:
  2025-10: 12 tasks
  2025-09: 18 tasks
  2025-08: 17 tasks

By Quarter:
  2025-Q3: 35 tasks
  2025-Q2: 12 tasks
```

---

### air track

Initialize and manage .air/ tracking system.

#### Usage

```bash
air track SUBCOMMAND [OPTIONS]
```

#### Subcommands

- `init` - Initialize .air/ tracking
- `status` - Show tracking status

---

#### air track init

Initialize .air/ tracking in current directory.

#### Usage

```bash
air track init [OPTIONS]
```

#### Options

- `--minimal` - Create minimal structure (no full templates)

#### Examples

```bash
# Full initialization
air track init

# Minimal structure
air track init --minimal
```

#### Output

Creates `.air/` structure:

```
.air/
├── README.md              # Documentation
├── tasks/                 # Task files directory
├── context/               # Context files
│   ├── architecture.md
│   ├── language.md
│   └── decisions.md
└── templates/             # Task templates
    └── task.md
```

#### Output

```
[i] Initializing .air/ tracking...

Created:
  ✓ .air/README.md
  ✓ .air/tasks/
  ✓ .air/context/
  ✓ .air/templates/

[✓] .air/ tracking initialized

Next steps:
  1. Review .air/README.md
  2. Update .air/context/ files
  3. Start using: air task new 'description'
```

---

#### air track status

Show .air/ tracking status.

#### Usage

```bash
air track status
```

#### Examples

```bash
air track status
```

#### Output

```
.air/ Tracking Status
====================

Status: Initialized
Location: /Users/user/project/.ai

Tasks: 5 files
  ✅ Completed: 3
  ⏳ In Progress: 2
  ❌ Blocked: 0

Context files:
  ✓ architecture.md (2.5 KB)
  ✓ language.md (1.8 KB)
  ✓ decisions.md (3.2 KB)

Recent tasks:
  • 20251003-1315-fix-bug-y (⏳)
  • 20251003-1200-implement-feature-x (✅)
  • 20251003-0945-refactor-services (✅)
```

---

### air summary

Generate summary of AI task files.

#### Usage

```bash
air summary [OPTIONS]
```

#### Options

- `--output=FILE` - Write to file (default: stdout)
- `--format=FORMAT` - Output format
  - `markdown` - Markdown format (default)
  - `json` - JSON format
  - `text` - Plain text
- `--since=DATE` - Only tasks since date (YYYY-MM-DD)

#### Examples

```bash
# Generate summary to stdout
air summary

# Save to file
air summary --output=SUMMARY.md

# Generate since date
air summary --since=2025-10-01

# JSON format
air summary --format=json --output=tasks.json
```

#### Output (Markdown)

```markdown
# AI Task Summary

Generated: 2025-10-03 15:45

## Statistics

- Total Tasks: 5
- Completed: 3 (60%)
- In Progress: 2 (40%)
- Blocked: 0

## Tasks

### ✅ 20251003-1200-implement-feature-x

**Date:** 2025-10-03 12:00
**Prompt:** Add user authentication
**Duration:** 2h 15m
**Files Changed:** 3

- `src/auth/login.py` - Implemented login flow
- `src/auth/session.py` - Added session management
- `tests/test_auth.py` - Added authentication tests

**Outcome:** Success
Implemented complete authentication system with tests.

---

### ⏳ 20251003-1315-fix-bug-y

**Date:** 2025-10-03 13:15
**Prompt:** Fix login redirect issue
**Files Changed:** 1

- `src/auth/login.py` - Fixed redirect logic

**Outcome:** In Progress
Currently debugging edge case with social login.

---

[Additional tasks...]

## Summary

Completed 3 major tasks related to authentication system.
Currently working on bug fixes and edge cases.
```

#### Output (JSON)

```json
{
  "generated": "2025-10-03T15:45:00Z",
  "statistics": {
    "total": 5,
    "completed": 3,
    "in_progress": 2,
    "blocked": 0
  },
  "tasks": [
    {
      "filename": "20251003-1200-implement-feature-x.md",
      "timestamp": "2025-10-03T12:00:00Z",
      "description": "implement feature X",
      "prompt": "Add user authentication",
      "outcome": "success",
      "files_changed": {
        "src/auth/login.py": "Implemented login flow",
        "src/auth/session.py": "Added session management",
        "tests/test_auth.py": "Added authentication tests"
      }
    }
  ]
}
```

---

## Utility Commands

### air version

Show AIR version.

#### Usage

```bash
air version
# or
air --version
```

#### Output

```
air version 0.3.1
```

---

## Exit Codes

All AIR commands use consistent exit codes:

- `0` - Success
- `1` - User error or business logic error
- `2` - System error or unexpected error
- `3` - Validation failure (specific to `air validate`)

## Environment Variables

Future support for:

```bash
AIR_CONFIG_DIR=~/.config/air   # Configuration directory
AIR_EDITOR=vim                  # Preferred editor
AIR_COLOR=auto                  # Color output (auto|always|never)
```

## Configuration Files

### Project Configuration

`.air/air-config.json` - Project metadata and resource tracking

### Global Configuration (Future)

`~/.config/air/config.yaml` - Global settings

```yaml
github:
  default_org: "LiveData-Inc"

editor: "vim"
auto_open_tasks: true
```

## air completion

**Added in v0.6.2** - Manage shell completion for air commands.

Enable tab completion for commands, options, resource names, task IDs, and more.

### Usage

```bash
# Install completion (auto-detects shell)
air completion install

# Install for specific shell
air completion install bash
air completion install zsh
air completion install fish

# Show completion script
air completion show bash

# Uninstall completion
air completion uninstall
```

### Features

- **Auto-detection**: Detects shell from $SHELL environment variable
- **Dynamic completion**: Completes resource names, task IDs, analyzer focus types
- **Multi-shell support**: Works with bash, zsh, and fish
- **Easy installation**: Adds completion to shell config files automatically

### Examples

```bash
air <TAB>                   # Shows: init, link, analyze, task, status...
air analyze <TAB>           # Shows: myapp, docs, shared-lib (from config)
air analyze --focus=<TAB>   # Shows: security, performance, quality...
air task status <TAB>       # Shows: 20251005-001, 20251005-002...
air pr <TAB>                # Shows: myapp (only developer resources)
```

## External Library Exclusion (v0.6.2)

By default, `air analyze` excludes external/vendor libraries for faster, cleaner analysis.

### Default Exclusions

- Python: `.venv`, `venv`, `__pycache__`, `site-packages`
- JavaScript: `node_modules`, `bower_components`
- Go: `vendor`, `pkg/mod`
- Ruby: `vendor/bundle`, `.bundle`
- General: `.git`, `build`, `dist`, `target`

### Usage

```bash
# Default: Excludes vendor code (15x faster!)
air analyze myapp

# Include vendor libraries
air analyze myapp --include-external

# Clear cache to rerun with new defaults
air cache clear
air analyze myapp
```

## HTML Findings Report (v0.6.2)

Generate rich HTML reports from analysis findings.

### Usage

```bash
# Generate HTML report
air findings --all --html

# Custom output path
air findings --all --html --output custom-report.html

# Filtered report
air findings --all --severity=critical --html
```

### Features

- Executive summary with severity/category breakdowns
- Clickable table of contents
- Findings grouped by repository
- Severity color coding
- Responsive and print-friendly
- Single HTML file with embedded CSS
