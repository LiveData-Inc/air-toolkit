# AIR Toolkit - Commands Reference

**Version:** 0.3.1
**Last Updated:** 2025-10-04

Complete reference for all AIR commands.

## Table of Contents

- [Global Options](#global-options)
- [Assessment Commands](#assessment-commands)
  - [air init](#air-init)
  - [air link](#air-link)
  - [air validate](#air-validate)
  - [air status](#air-status)
  - [air classify](#air-classify)
  - [air pr](#air-pr)
- [Task Tracking Commands](#task-tracking-commands)
  - [air task](#air-task)
  - [air track](#air-track)
  - [air summary](#air-summary)
- [Utility Commands](#utility-commands)
  - [air version](#air-version)

## Global Options

These options work with all commands:

```bash
air --version        # Show version and exit
air --help           # Show help message
```

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
  - `collaborate` - Collaborative mode
  - `mixed` - Both review and developer
- `--track / --no-track` - Initialize .air/ tracking (default: enabled)

#### Examples

```bash
# Create mixed-mode project (default)
air init my-review

# Create review-only project
air init service-review --mode=review

# Create developer project without tracking
air init docs --mode=collaborate --no-track

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
├── air-config.json
├── .gitignore
├── repos/
├── analysis/
│   └── assessments/
├── .air/
└── scripts/
```

**Collaborative Mode:**
```
project-name/
├── README.md
├── CLAUDE.md
├── air-config.json
├── .gitignore
├── collaborate/
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
├── air-config.json
├── .gitignore
├── repos/
├── collaborate/
├── analysis/
│   ├── SUMMARY.md
│   ├── assessments/
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

Link repositories to the assessment project. Interactive by default for easy setup.

#### Commands

##### air link add

Add a resource to the project.

**Usage:**

```bash
air link add [OPTIONS]
```

**Interactive Mode (default):**

When run without all required options, enters interactive mode with guided prompts:

```bash
# Interactive setup
air link add

# Partial arguments - will prompt for missing values
air link add --path ~/repos/service-a
air link add --name my-service --review
```

**Non-Interactive Mode:**

Provide all required options for scripting:

```bash
air link add --path PATH --name NAME --review|--develop [--type TYPE]
```

**Options:**

- `--path PATH` - Path to repository (required)
- `--name NAME` - Resource name/alias (required)
- `--review` - Link as review-only resource (read-only) **[default]**
- `--develop` - Link as developer resource (can contribute)
- `--type TYPE` - Resource type: `library`, `documentation`, `service` (default: `library`)

**Examples:**

```bash
# Fully interactive mode
air link add

# Path with shell tab-complete (prompts for name, type, etc) ⭐ RECOMMENDED
air link add ~/repos/mylib

# Minimal - uses defaults (review mode, library type)
air link add ~/repos/service-a --name service-a

# Explicit review resource with type
air link add ~/repos/service-a --name service-a --review --type library

# Develop resource
air link add ~/repos/architecture --name arch --develop --type documentation
```

**Usage:**

```bash
air link add [PATH] [OPTIONS]
```

**Interactive Features:**

1. **Path Validation** - Checks path exists and is a directory
2. **Name Suggestions** - Defaults to folder name, validates uniqueness
3. **Relationship Choice** - Review (read-only) or Develop (contribute)
4. **Auto-Classification** - Optional auto-detect of resource type
5. **Confirmation** - Review summary before creating link

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
air link remove NAME [--keep-link]
```

**Options:**

- `--keep-link` - Keep symlink, only remove from config

**Examples:**

```bash
# Remove resource and symlink
air link remove service-a

# Remove from config but keep symlink
air link remove service-a --keep-link
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
- Managed in `air-config.json`
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
- `air-config.json` present
- Mode-appropriate structure (repos/, collaborate/, etc.)

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
  ✓ air-config.json
  ✓ repos/
  ✓ analysis/assessments/

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
  - `collaborate` - Show only developer resources
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
- `--update` - Update `air-config.json` with classifications

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
    Analysis: analysis/assessments/service-a.md

  ✓ service-b (library)
    Reason: Service implementation
    Analysis: analysis/assessments/service-b.md

Collaborative (1):
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

Classify as (repos/collaborate)? collaborate
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
- `complete` - Mark task as complete

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

`air-config.json` - Project metadata and resource tracking

### Global Configuration (Future)

`~/.config/air/config.yaml` - Global settings

```yaml
github:
  default_org: "LiveData-Inc"

editor: "vim"
auto_open_tasks: true
```

## Shell Completion (Future)

```bash
# Bash
eval "$(_AIR_COMPLETE=bash_source air)"

# Zsh
eval "$(_AIR_COMPLETE=zsh_source air)"

# Fish
eval (env _AIR_COMPLETE=fish_source air)
```
