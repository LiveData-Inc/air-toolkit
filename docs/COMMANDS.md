# AIR Toolkit - Commands Reference

**Version:** 0.1.0
**Last Updated:** 2025-10-03

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
  - `mixed` - Both review and collaborative
- `--track / --no-track` - Initialize .ai/ tracking (default: enabled)

#### Examples

```bash
# Create mixed-mode project (default)
air init my-review

# Create review-only project
air init service-review --mode=review

# Create collaborative project without tracking
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
├── .assess-config.json
├── .gitignore
├── review/
├── analysis/
│   └── assessments/
├── .ai/
└── scripts/
```

**Collaborative Mode:**
```
project-name/
├── README.md
├── CLAUDE.md
├── .assess-config.json
├── .gitignore
├── collaborate/
├── analysis/
│   └── improvements/
├── contributions/
├── .ai/
└── scripts/
```

**Mixed Mode:**
```
project-name/
├── README.md
├── CLAUDE.md
├── .assess-config.json
├── .gitignore
├── review/
├── collaborate/
├── analysis/
│   ├── SUMMARY.md
│   ├── assessments/
│   └── improvements/
├── contributions/
├── .ai/
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

Link repositories to the assessment project.

#### Usage

```bash
air link [OPTIONS]
```

#### Options

- `--review NAME:PATH` - Add review-only resource (repeatable)
- `--collaborate NAME:PATH` - Add collaborative resource (repeatable)
- `--clone` - Clone instead of symlink (for `--collaborate`)

If no options provided, reads from `repos-to-link.txt`.

#### Examples

```bash
# Link review-only repositories
air link --review service-a:~/repos/service-a
air link --review service-b:~/repos/service-b

# Link collaborative repository
air link --collaborate arch:~/repos/architecture

# Clone collaborative repository
air link --collaborate arch:~/repos/architecture --clone

# Link multiple at once
air link \
  --review service-a:~/repos/service-a \
  --review service-b:~/repos/service-b \
  --collaborate arch:~/repos/arch --clone

# Read from configuration file
air link
```

#### Configuration File

Create `repos-to-link.txt`:

```
# Review-only resources (symlinked)
review:service-a:~/repos/service-a
review:service-b:~/repos/service-b
review:change-lib:~/repos/change-command-lib

# Collaborative resources (cloned or symlinked)
collaborate:architecture:~/repos/cloud-native-architecture
```

#### Behavior

**Review Resources:**
- Always created as symlinks (read-only)
- Placed in `review/` directory
- Original repository not modified

**Collaborative Resources:**
- Default: symlink
- With `--clone`: git clone
- Placed in `collaborate/` directory
- Can be modified and committed

#### Exit Codes

- `0` - All resources linked successfully
- `1` - Some resources failed to link
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
- `.assess-config.json` present
- Mode-appropriate structure (review/, collaborate/, etc.)

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
  ✓ .assess-config.json
  ✓ review/
  ✓ analysis/assessments/

Links:
  ✓ review/service-a -> /Users/user/repos/service-a
  ✓ review/service-b -> /Users/user/repos/service-b

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
  - `collaborate` - Show only collaborative resources
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

Classify resources by type (review vs collaborative).

#### Usage

```bash
air classify [OPTIONS]
```

#### Options

- `--verbose` - Show detailed classification reasoning
- `--update` - Update `.assess-config.json` with classifications

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
  ✓ service-a (implementation)
    Reason: Contains Python implementation code
    Analysis: analysis/assessments/service-a.md

  ✓ service-b (implementation)
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
Could be either review or collaborative.

Indicators:
  - Contains implementation code
  - Also contains extensive documentation
  - Has write access

Classify as (review/collaborate)? collaborate
```

---

### air pr

Create pull request for collaborative resource.

#### Usage

```bash
air pr [RESOURCE] [OPTIONS]
```

#### Arguments

- `RESOURCE` - Name of collaborative resource (optional)

#### Options

- `--branch=NAME` - Branch name (default: auto-generated)
- `--message=TEXT` - Commit message
- `--draft` - Create as draft PR
- `--dry-run` - Show what would be done

#### Examples

```bash
# Create PR for resource
air pr architecture

# Specify branch name
air pr architecture --branch=add-integration-guide

# Create draft PR
air pr architecture --draft

# Preview without creating
air pr architecture --dry-run

# List resources with pending contributions
air pr
```

#### Workflow

1. Validate resource is collaborative type
2. Check `contributions/[resource]/` has content
3. Create git branch
4. Copy contribution files to target locations
5. Commit changes
6. Push branch to remote
7. Create PR via `gh` CLI

#### Requirements

- GitHub CLI (`gh`) must be installed and authenticated
- Resource must be a git clone (not symlink)
- Contributions exist in `contributions/[resource]/`
- Remote repository must be accessible

#### Output

```
[i] Creating PR for: architecture

Found contributions:
  • new-guide.md -> docs/guides/implementation-guide.md
  • Update ADR-2025.008

Creating branch: add-integration-guide
Copying contribution files...
Committing changes...
Pushing to remote...
Creating pull request...

[✓] PR created successfully
  https://github.com/org/architecture/pull/123
```

#### Dry Run Output

```
[⚠] Dry run mode - no changes will be made

Would create PR with:
  Branch: add-integration-guide
  Files:
    • contributions/architecture/new-guide.md
      -> docs/guides/implementation-guide.md
  Commit message:
    Add implementation guide from assessment
  PR title:
    Add integration implementation guide
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

Creates file: `.ai/tasks/YYYYMMDD-HHMM-description.md`

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

Initialize and manage .ai/ tracking system.

#### Usage

```bash
air track SUBCOMMAND [OPTIONS]
```

#### Subcommands

- `init` - Initialize .ai/ tracking
- `status` - Show tracking status

---

#### air track init

Initialize .ai/ tracking in current directory.

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

Creates `.ai/` structure:

```
.ai/
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
[i] Initializing .ai/ tracking...

Created:
  ✓ .ai/README.md
  ✓ .ai/tasks/
  ✓ .ai/context/
  ✓ .ai/templates/

[✓] .ai/ tracking initialized

Next steps:
  1. Review .ai/README.md
  2. Update .ai/context/ files
  3. Start using: air task new 'description'
```

---

#### air track status

Show .ai/ tracking status.

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
.ai/ Tracking Status
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
air version 0.1.0
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

`.assess-config.json` - Project metadata and resource tracking

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
