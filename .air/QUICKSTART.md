# AI Assistant Quick Start Guide

**Read this first! Also see: `CLAUDE.md` and `.air/README.md`**

## 🚨 Critical Rules - AUTOMATIC TRACKING

1. **AUTO-CREATE task files** when user requests code changes (don't ask, just do it)
2. **AUTO-POPULATE** with prompt, date, and structure immediately
3. **AUTO-UPDATE** as you work - add actions and files progressively
4. **UPDATE the same task file** throughout the work session - don't create duplicates
5. **Include task file in git commits**

**Goal**: ZERO FRICTION - tracking should be invisible to the user

## 📝 Task File Format

**Filename**: `YYYYMMDD-HHMM-description.md` in `.air/tasks/`

**Example**: `20250101-1430-add-user-authentication.md`

## 📋 Automatic Task Creation

**AI assistants should use the library mode:**
```python
import sys
sys.path.insert(0, '.air/scripts')
from new_task import create_task

# Silently create task file
task_file = create_task(
    description="brief description from user prompt",
    prompt="exact user prompt",
    silent=True
)

# Continue working, update task file as you progress
```

**Simplified task structure:**
```markdown
# Task: [Description]

## Date
YYYY-MM-DD HH:MM

## Prompt
[Exact user prompt]

## Actions Taken
1. [Action 1]
2. [Action 2]

## Files Changed
- `path/file.ext` - [What changed]

## Outcome
⏳ In Progress

[Brief summary]

## Notes
[Optional: decisions, blockers]
```

## 🔄 Workflow

1. **User gives prompt** → Create task file immediately
2. **Work on task** → Update task file as you go
3. **Complete task** → Finalize outcome
4. **Significant work?** → Update `AI_CHANGELOG.md`
5. **Commit** → Use `[AI: YYYYMMDD-HHMM]` in commit message

## 📂 Quick Context Check

Before starting work:
```bash
# Check recent tasks
python .air/scripts/list-tasks.py 5

# Read project context
cat .air/context/architecture.md
cat .air/context/language.md

# Check backlog
cat .air/tasks/TASKS.md

# Search for related work
python .air/scripts/search-tasks.py "authentication"
```

## ✅ Session Checklist

- [ ] Read this QUICKSTART.md
- [ ] Check `.air/tasks/` for recent work
- [ ] Review `.air/context/` files
- [ ] Create task file BEFORE coding
- [ ] Follow protocol for ALL changes

## 🔗 Git Commit Format

```bash
git commit -m "feat: add feature [AI: 20250101-1430]"
```

## ❌ Common Mistakes

- ❌ Creating multiple task files for the same work session
- ❌ Forgetting to create task file
- ❌ Not recording the exact prompt
- ❌ Missing file changes in documentation
- ❌ Skipping task file for "small" changes

## 🆘 If You Make a Mistake

Update the current task file to note the correction. If you've already marked a task complete and need to revisit it, create a new task file: `YYYYMMDD-HHMM-follow-up-to-YYYYMMDD-HHMM.md`

## 🛠️ Useful Commands

```bash
# Create new task
python .air/scripts/new-task.py "implement user login"

# List recent tasks
python .air/scripts/list-tasks.py 10

# Search tasks
python .air/scripts/search-tasks.py "database"

# View statistics
python .air/scripts/task-stats.py

# Validate all tasks
python .air/scripts/validate-tasks.py

# Archive old tasks
python .air/scripts/archive-tasks.py 2024-Q4
```

## 📚 Need More Info?

- **Full documentation**: `.air/README.md`
- **Task template**: `.air/templates/task-template.md`
- **Project patterns**: `.air/context/`
- **Change history**: `AI_CHANGELOG.md`

---

**Remember**: Task files capture your entire work session. Update them as you work, then mark complete when done.
