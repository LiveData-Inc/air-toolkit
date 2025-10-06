# AI Development Tracking System

This `.air/` folder implements a comprehensive tracking system for AI-assisted development work.

## 🚀 Quick Start

**If you are an AI assistant working in this project:**

1. Read `CLAUDE.md` for automatic task tracking instructions
2. **Automatically create task files** as you work - don't ask, just do it
3. Review `.air/context/` files for project patterns
4. Check recent tasks in `.air/tasks/` for context
5. Document your work in task files as you progress

**The goal: ZERO FRICTION.** Task tracking should be invisible to the user.

## 📁 Structure

```
.air/
├── README.md                    # This file (system documentation)
├── QUICKSTART.md               # Quick reference for AI assistants
├── AI_CHANGELOG.md             # High-level summary of all AI work
├── context/                    # Project-specific context files
│   ├── architecture.md         # Architectural patterns and information
│   └── language.md             # Language-specific conventions
├── templates/                  # Templates for task files and other docs
│   └── task-template.md       # Task file template
├── scripts/                    # Helper scripts for task management
│   ├── new-task.py            # Create new task file (CLI & library)
│   ├── list-tasks.py          # List recent tasks
│   ├── search-tasks.py        # Search tasks by keyword
│   ├── task-stats.py          # Generate statistics
│   ├── validate-tasks.py      # Validate task files
│   └── archive-tasks.py       # Archive old tasks
└── tasks/                      # Individual task logs
    ├── TASKS.md               # Index/backlog of tasks
    ├── YYYYMMDD-HHMM-description.md  # Active tasks
    └── archive/               # Archived tasks (v0.6.3)
        └── YYYY-MM/          # Organized by year-month
```

## 📝 Task Logging Protocol

### Automatic Task Tracking (AI Assistants)

**AI assistants should automatically create and maintain task files** without user intervention:

1. **Auto-create on user request** - When user asks you to code something, silently create a task file first
2. **Auto-populate** - Fill in the prompt, date, and initial structure immediately
3. **Auto-update** - Add actions and files as you work
4. **Auto-finalize** - Mark outcome when complete

**Use the library mode:**
```python
# Add .air/scripts to path if needed
import sys
sys.path.insert(0, '.air/scripts')

from new_task import create_task

# Create task file
task_file = create_task(
    description="implement user authentication",
    prompt="Add JWT-based authentication to the API",
    silent=True  # Don't print output
)

# Update task file as you work...
```

### File Naming Convention
Task files use format: `YYYYMMDD-HHMM-description-with-hyphens.md`

Examples:
- `20250829-1430-setup-react-frontend.md` ✅
- `20250829-1515-add-authentication-system.md` ✅
- `20250830-0900-fix-database-connection.md` ✅

Bad examples:
- `update.md` ❌ (no timestamp)
- `20250829-authentication.md` ❌ (no time)
- `2025-08-29-1430-task.md` ❌ (wrong date format)

### Task File Template
Each task file MUST contain:

```markdown
# Task: [Brief Description]

## Date
YYYY-MM-DD HH:MM

## Prompt
```
[Exact user prompt that initiated this task]
```

## Context
[Any relevant context about why this task was needed]

## Actions Taken
- [ ] [Step-by-step list of actions]
- [ ] [Include file paths affected]
- [ ] [Note any decisions made]

## Files Changed
- `path/to/file1.ts` - Description of changes
- `path/to/file2.md` - Description of changes

## Testing
[How the changes were tested/verified]

## Outcome
⏳ In Progress | ✅ Success | ⚠️ Partial | ❌ Blocked

[Detailed outcome description]

## Notes
[Any additional observations or follow-up needed]
```

**Tip**: Use the template at `.air/templates/task-template.md` or run `python .air/scripts/new-task.py "description"` to quickly create new task files.

## ⚠️ Critical Rules

### For AI Assistants - YOU MUST:
1. **ALWAYS** create a task file when making code changes
2. **ALWAYS** record the exact user prompt verbatim
3. **ALWAYS** list all files modified or created
4. **NEVER** skip documentation even for small changes
5. **UPDATE the same task file** as work progresses - don't create duplicates
6. **UPDATE** AI_CHANGELOG.md after significant tasks

### Task File Updates
**CRITICAL**: Task files should be UPDATED as you work:
- Create the task file once at the start with timestamp
- Update that same file as you make progress
- Don't create new files with different timestamps for the same task
- The task file captures the entire work session, not just the start
- Only create a NEW task file for a genuinely separate/new user request

## 🔄 Workflow

### Starting a Task
1. User provides a prompt
2. IMMEDIATELY create file: `.air/tasks/YYYYMMDD-HHMM-task-description.md`
3. Record the prompt exactly as given
4. Document actions as you perform them
5. List all files as you change them

**Quick command**: `python .air/scripts/new-task.py "task description"`

### During the Task
- Update the task file as you work
- Include failed attempts and why they failed
- Document decisions and trade-offs
- Note any blockers or issues

### Completing a Task
1. Finalize the task file with outcomes
2. Update `AI_CHANGELOG.md` with summary (if significant)
3. Ensure task file is complete before moving on
4. Include task file in any git commits

### Multi-Session Tasks
For tasks spanning multiple sessions:
- Create new task file per session
- Reference previous task: "Continues work from 20250829-1430..."
- Link related tasks in Notes section
- Consider tracking in TASKS.md for coordination

### Correcting Errors During Work
If you need to correct errors while working on a task:
1. Update the current task file to note the correction
2. Document what was wrong and the fix in "Actions Taken"
3. If task is already marked complete, create new task: `YYYYMMDD-HHMM-follow-up-to-YYYYMMDD-HHMM.md`
4. **Never delete task files**

## 🔗 Git Integration

### Commit Messages
When committing code with AI assistance:
```bash
git add .
git commit -m "feat: add user authentication [AI: 20250829-1430]"
```

The `[AI: YYYYMMDD-HHMM]` reference links the commit to the task file.

### Benefits
1. **Traceability**: Every change linked to prompt and reasoning
2. **Knowledge Transfer**: Future AI sessions have complete context
3. **Debugging**: Can trace back why specific decisions were made
4. **Learning**: Review what worked and what didn't
5. **Audit Trail**: Complete record of AI involvement

## 📊 Maintaining AI_CHANGELOG.md

### Structure
```markdown
# AI Development Changelog - [PROJECT_NAME]

## Overview
Total AI-assisted tasks: X
Files modified: X
Last updated: YYYY-MM-DD

## [YYYY-MM-DD] - Session Summary
### Major Changes
- Feature: Description [AI: YYYYMMDD-HHMM]
- Refactor: Description [AI: YYYYMMDD-HHMM]

### Decisions Made
- Decision with rationale

### Patterns Discovered
- Pattern or learning

### Metrics
- X files created/modified
- X tests added
- X bugs fixed
```

Update the changelog after completing significant tasks or at session end.

## 🔍 Quick Reference Commands

### Find Recent Work
```bash
# Last 10 tasks
python .air/scripts/list-tasks.py 10

# Tasks from today
ls .air/tasks/$(date +%Y%m%d)*.md
```

### Search by Topic
```bash
# Find tasks about authentication
python .air/scripts/search-tasks.py "authentication"

# Search all content
grep -r "database migration" .air/tasks/
```

### View Task Timeline
```bash
# Preview all tasks
for f in .air/tasks/202*.md; do
  echo "=== $f ===";
  head -5 "$f";
  echo;
done
```

### Statistics
```bash
# View task statistics
python .air/scripts/task-stats.py

# Count tasks by day
ls .air/tasks/ | cut -d- -f1 | sort | uniq -c

# Count total tasks
ls .air/tasks/202*.md | wc -l
```

### Finding Information
To understand project history:
1. Read `QUICKSTART.md` for immediate overview
2. Read `AI_CHANGELOG.md` for high-level summary
3. List recent tasks: `.air/scripts/list-tasks.sh 20`
4. Search for specific work: `python .air/scripts/search-tasks.py "keyword"`
5. Review context files in `.air/context/` for patterns

## 📦 Archive Strategy (v0.6.3+)

AIR toolkit includes automated task archiving to reduce AI context window usage.

### Using `air task archive`

```bash
# Archive specific tasks
air task archive 20251003-1200

# Archive all tasks
air task archive --all

# Archive tasks before a date
air task archive --before=2025-10-01

# Preview what would be archived
air task archive --all --dry-run

# Use different organization strategy
air task archive --all --strategy=by-quarter
```

### Archive Structure

Tasks are organized by default in year-month folders:
```
.air/tasks/archive/
├── ARCHIVE.md            # Auto-generated summary of all archived tasks
├── 2025-10/
│   ├── 20251003-001-1200-task.md
│   └── 20251003-002-1430-another-task.md
├── 2025-09/
└── 2025-08/
```

The `ARCHIVE.md` file is automatically generated and updated whenever tasks are archived or restored. It provides:
- Table of contents with links to each time period
- Summary of all archived tasks organized by month/quarter
- Task titles, dates, statuses, and prompts
- Quick navigation to understand project history without reading individual files

### Archive Strategies

- **by-month** (default): `.air/tasks/archive/YYYY-MM/`
- **by-quarter**: `.air/tasks/archive/YYYY-QN/`
- **flat**: `.air/tasks/archive/` (no subdirectories)

### Restoring Tasks

```bash
# Restore archived tasks back to active
air task restore 20251003-1200
```

### Archive Statistics

```bash
# View archive stats
air task archive-status

# JSON output
air task archive-status --format=json
```

### Best Practices

1. **Archive regularly** - Keep active tasks under 50-100 files
2. **Archive completed tasks** - Move finished work out of AI context
3. **Keep archives in git** - Maintain complete history
4. **Use `--all` flag** - Bulk archive when needed
5. **Preview first** - Use `--dry-run` to see what will be archived

## 🎯 Project Customization

### For Human Developers
After installing this `.air/` folder to your project:

1. Update `AI_CHANGELOG.md` header with project name
2. Customize `.air/context/architecture.md` with your architecture
3. Apply language profile with `ai-init overlay --lang <language>` or customize `.air/context/language.md`
4. Ensure AI assistant reads this README

### Organizing Context Files

**`.air/context/architecture.md`** - Document:
- Architectural patterns (hexagonal, layered, etc.)
- Key design decisions
- System boundaries and integration points
- Technology choices and rationale

**`.air/context/language.md`** - Document:
- Language-specific syntax patterns
- Naming conventions for your language
- Standard library usage
- Type system guidelines
- Testing conventions

## 🤖 For AI Assistants: Your Checklist

Every time you start work in this project:
- [ ] Read `.air/QUICKSTART.md` for quick orientation
- [ ] Check recent tasks in `.air/tasks/` for context
- [ ] Review `.air/context/` files for project patterns
- [ ] Create your task file BEFORE starting work
- [ ] Follow the protocol WITHOUT exceptions

## 💬 Coaching Your AI Assistant

### Why Reminders Are Important
AI assistants may not automatically discover or follow the `.air/` folder instructions. You should periodically remind them to check and follow the tracking protocol, especially:
- At the start of a new session
- When switching between major tasks
- If the AI seems to skip documentation
- When working with a different AI assistant

### Example Prompts to Guide Your AI

#### Initial Session Setup
- "Please read `.air/QUICKSTART.md` and follow the tracking protocol"
- "Before starting, review `.air/README.md` and create appropriate task files"
- "Check the `.air/` folder for our AI development tracking system"

#### During Development
- "Make sure you're creating task files in `.air/tasks/` as you work"
- "Don't forget to document this in a task file per the `.air/` protocol"
- "Please update the AI_CHANGELOG.md with this significant change"

#### Review and Compliance
- "Review instructions in `.air/README.md` and ensure all task files are complete"
- "Check that you've been following the `.air/` tracking protocol"
- "Verify all changed files are listed in the task file"

#### Specific Corrections
- "You need to create a task file for this work - see `.air/README.md`"
- "The task file should include the exact prompt I gave you"
- "Update the current task file as you work - don't create duplicates"
- "If you need to revisit completed work, create a follow-up task"

### Signs Your AI Needs a Reminder
- Not creating task files before making changes
- Forgetting to document file modifications
- Skipping the prompt recording
- Modifying existing task files
- Not updating AI_CHANGELOG.md for major work
- Not referencing past task files for context

### Best Practices
1. **Start each session** with: "Please check `.air/QUICKSTART.md` for our tracking protocol"
2. **Be explicit** about following the system - don't assume the AI knows
3. **Correct immediately** if the AI skips documentation
4. **Reference specific files** like `.air/README.md` rather than general instructions
5. **Verify compliance** by checking `.air/tasks/` for new task files
6. **Point to examples** from past task files when explaining patterns

## 📚 TASKS.md Purpose

The `.air/tasks/TASKS.md` file serves as:
- **Index** of all tasks (automatically or manually maintained)
- **Backlog** of planned work
- **Quick Reference** for finding related tasks
- **Status Tracking** for multi-part initiatives

Example structure:
```markdown
# Task Index

## In Progress
- [ ] 20250101-1200-implement-feature-x.md - User authentication

## Completed
- [x] 20241231-1500-setup-project.md - Initial project setup
- [x] 20241231-1600-configure-cicd.md - CI/CD pipeline

## Backlog
- [ ] Implement password reset flow
- [ ] Add OAuth providers
- [ ] Setup monitoring

## Related Tasks
- Authentication: 20250101-1200, 20250102-0900
- Database: 20250101-1400, 20250102-1000
```

---

**Remember**: This system creates a permanent record of AI-assisted development. Treat it with the same care as source code. These files become invaluable for debugging, knowledge transfer, and understanding project evolution over time.
