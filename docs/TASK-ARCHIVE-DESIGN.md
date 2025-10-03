# Task Archive Enhancement - Design Proposal

**Date:** 2025-10-03
**Status:** Proposal

## Overview

Enable archiving of completed task files to maintain a clean, manageable `.air/tasks/` directory while preserving historical task data for reference.

## Problem Statement

Over time, `.air/tasks/` accumulates many completed task files, making it difficult to:
- Quickly scan recent/active tasks
- Navigate the task directory
- Maintain focus on current work

**Current structure after one day:**
```
.air/tasks/
├── 20251003-1234-create-development-plan-phase1.md
├── 20251003-1236-design-air-as-claude-tool.md
├── 20251003-1244-rename-config-file-to-air-config.md
├── 20251003-1255-implement-phase1-core-commands.md
├── 20251003-1313-write-comprehensive-tests-phase1.md
├── 20251003-1319-consolidate-pytest-config-to-pyproject.md
└── 20251003-1323-design-task-archive-enhancement.md
```

After months: 100+ files in one directory.

## Goals

1. **Keep recent tasks visible** - Easy to see what's been worked on recently
2. **Preserve history** - Archive, don't delete completed tasks
3. **Flexible organization** - Support multiple archive strategies
4. **Simple workflow** - Easy CLI commands for archiving
5. **AI-friendly** - Clear guidelines for when/how AI should archive

## Proposed CLI Commands

### Core Commands

```bash
# Archive specific tasks
air task archive <task-id>                    # Archive single task
air task archive <task-id> <task-id> ...      # Archive multiple tasks
air task archive --all                        # Archive all completed tasks
air task archive --before=2025-09-01          # Archive tasks before date
air task archive --older-than=30d             # Archive tasks older than 30 days

# List tasks
air task list                                 # List current (non-archived) tasks
air task list --all                           # Include archived tasks
air task list --archived                      # Only archived tasks
air task list --since=2025-10-01              # Tasks since date

# Search tasks
air task search "keyword"                     # Search current tasks
air task search "keyword" --all               # Search all (including archived)

# Restore from archive
air task restore <task-id>                    # Move task back to current
air task restore --pattern="*-implement-*"    # Restore matching tasks

# View archive structure
air task archive-status                       # Show archive statistics
```

### Extended Options

```bash
# Archive with organization
air task archive --by-month                   # Organize by month (default)
air task archive --by-quarter                 # Organize by quarter
air task archive --flat                       # Single archive/ folder

# Summary integration
air summary                                   # Only current tasks
air summary --all                             # Include archived
air summary --month=2025-10                   # Specific month
```

## Archive Structure Options

### Option A: Flat Archive (Simple)

```
.air/tasks/
├── archive/
│   ├── 20250901-1430-old-task-1.md
│   ├── 20250902-0900-old-task-2.md
│   └── ...
├── 20251003-1234-current-task-1.md
└── 20251003-1430-current-task-2.md
```

**Pros:** Simple, easy to implement
**Cons:** Archive directory grows unbounded

### Option B: By Month (Recommended)

```
.air/tasks/
├── archive/
│   ├── 2025-09/
│   │   ├── 20250901-1430-task-1.md
│   │   └── 20250915-0900-task-2.md
│   └── 2025-08/
│       └── 20250815-1200-task-3.md
├── 20251003-1234-current-task-1.md
└── 20251003-1430-current-task-2.md
```

**Pros:** Chronologically organized, bounded directory sizes
**Cons:** Slightly more complex

### Option C: By Quarter (Alternative)

```
.air/tasks/
├── archive/
│   ├── 2025-Q3/
│   │   ├── 20250901-1430-task-1.md
│   │   └── 20250915-0900-task-2.md
│   └── 2025-Q2/
│       └── 20250615-1200-task-3.md
├── 20251003-1234-current-task-1.md
└── 20251003-1430-current-task-2.md
```

**Pros:** Lower directory count for long-running projects
**Cons:** Less granular than by-month

**Recommendation: Option B (By Month)** - Best balance of organization and simplicity

## Archiving Strategies

### 1. Manual Archiving (Phase 1)

**User/AI explicitly archives tasks:**
```bash
# At end of sprint/milestone
air task archive --before=2025-09-30

# Archive completed tasks periodically
air task archive --all --status=completed
```

**When to archive (suggested guidelines):**
- End of sprint/milestone
- Monthly cleanup
- When task count exceeds threshold (e.g., 20 files)
- Before starting major new work

### 2. Automatic Archiving (Phase 2 - Future)

**Auto-archive based on rules:**
```bash
# Configure auto-archive rules
air config set task.auto_archive true
air config set task.auto_archive_days 30
air config set task.auto_archive_on_summary true
```

**Auto-archive triggers:**
- When running `air summary` (if configured)
- When task count exceeds threshold
- On a schedule (if running in CI/CD)

## Implementation Plan

### Phase 1: Core Functionality

**Commands to implement:**
1. `air task archive <task-id>` - Archive specific task(s)
2. `air task archive --all` - Archive all completed tasks
3. `air task archive --before=<date>` - Archive by date
4. `air task list` - List current tasks (exclude archived)
5. `air task list --all` - Include archived tasks
6. `air task restore <task-id>` - Restore from archive

**Implementation tasks:**
1. Update `src/air/commands/task.py` with archive subcommands
2. Create `src/air/services/task_archive.py` service
3. Implement by-month organization as default
4. Update `air summary` to exclude archived by default
5. Add tests for archive operations
6. Update documentation (CLAUDE.md templates)

**File structure:**
```python
# src/air/services/task_archive.py
def archive_task(task_file: Path, archive_root: Path, strategy: str = "by-month")
def list_tasks(include_archived: bool = False, archived_only: bool = False)
def restore_task(task_id: str, tasks_root: Path)
def get_archive_path(task_file: Path, strategy: str) -> Path
```

### Phase 2: Enhanced Features

1. Task search across archives
2. Archive statistics and reporting
3. Automatic archiving based on rules
4. Archive by quarter/year options
5. Bulk operations (archive by pattern)

### Phase 3: Advanced Features

1. Task metadata index for fast searching
2. Archive compression (tar.gz old archives)
3. Export tasks to other formats
4. Task analytics and visualization

## CLI Command Semantics

### Consistent Patterns

All task archive commands follow this pattern:
```
air task <action> [selector] [options]
```

**Actions:**
- `archive` - Move to archive
- `restore` - Move from archive back to current
- `list` - Show tasks
- `search` - Find tasks by content

**Selectors:**
- `<task-id>` - Specific task (e.g., `20251003-1430`)
- `--all` - All tasks (matching criteria)
- `--before=<date>` - Tasks before date
- `--older-than=<duration>` - Tasks older than duration
- `--status=<status>` - Tasks with specific status

**Options:**
- `--by-month` / `--by-quarter` / `--flat` - Archive organization
- `--dry-run` - Preview without making changes
- `--verbose` - Show detailed output

### Examples

```bash
# Basic archiving
air task archive 20251003-1234
air task archive 20251003-1234 20251003-1236

# Archive all completed tasks
air task archive --all --status=completed

# Archive old tasks
air task archive --before=2025-09-01
air task archive --older-than=90d

# Preview before archiving
air task archive --all --dry-run

# List and search
air task list                          # Current tasks only
air task list --all                    # Include archived
air task list --archived               # Archived only
air task search "Phase 1" --all        # Search everywhere

# Restore
air task restore 20250901-1430
```

## Impact on Existing Features

### `air summary`

**Current behavior:** Summarizes all tasks in `.air/tasks/`

**New behavior:**
```bash
air summary                # Only current (non-archived) tasks
air summary --all          # Include archived tasks
air summary --month=2025-10 # Specific month (looks in archive/2025-10/)
```

### `air task list`

**Enhanced with filtering:**
```bash
air task list              # Current tasks
air task list --all        # All tasks
air task list --archived   # Archived only
air task list --since=2025-10-01
air task list --status=completed
```

### Templates (CLAUDE.md)

**Update task tracking guidelines:**
```markdown
## Task File Lifecycle

1. **Create** - When starting work
2. **Update** - As work progresses
3. **Complete** - Mark outcome when done
4. **Archive** - Move to archive after sprint/milestone

### When to Archive

**For AI Agents:**
- When user requests cleanup
- At end of major milestone
- When task count exceeds 20 files

**Manual archiving:**
```bash
# Archive all completed tasks older than 30 days
air task archive --older-than=30d --status=completed
```
```

## Configuration

Add to `air-config.json` (optional):
```json
{
  "task_archive": {
    "strategy": "by-month",
    "auto_archive": false,
    "auto_archive_days": 30,
    "keep_recent_count": 20
  }
}
```

Or global config at `~/.config/air/config.yaml`:
```yaml
task_archive:
  strategy: by-month
  auto_archive: false
  auto_archive_days: 30
```

## Migration Strategy

**For existing projects:**

1. Archive command automatically creates `archive/` directory
2. First run shows guidance:
   ```
   ℹ Creating archive directory: .air/tasks/archive/
   ✓ Archived 45 tasks to archive/2025-09/
   ℹ Tip: Use 'air task list --all' to see archived tasks
   ```

3. No breaking changes - tasks remain accessible via `--all` flag

## Testing Requirements

1. **Unit tests:**
   - Archive path calculation
   - Task file parsing for dates
   - Archive strategy selection

2. **Integration tests:**
   - Archive single task
   - Archive multiple tasks
   - Archive by date range
   - Restore task
   - List with/without archived
   - Search across archives

3. **Edge cases:**
   - Empty archive directory
   - Task already archived
   - Corrupted task filenames
   - Permission errors

## Documentation Updates

1. **COMMANDS.md** - Add `air task archive` documentation
2. **CLAUDE.md template** - Update task lifecycle guidance
3. **AI-INTEGRATION.md** - Best practices for AI archiving
4. **README.md** - Brief mention of archiving feature

## Success Criteria

✅ Can archive individual or multiple tasks
✅ Archive organized by month (configurable)
✅ Can list current vs archived tasks separately
✅ Can search across current and archived
✅ Can restore archived tasks
✅ `air summary` excludes archived by default
✅ Clear CLI semantics and help text
✅ Well-tested (>75% coverage)
✅ Documentation complete

## Timeline Estimate

- **Phase 1 (Core):** 1-2 days
  - Archive/restore commands
  - List filtering
  - Basic tests

- **Phase 2 (Enhanced):** 1 day
  - Search functionality
  - Archive statistics
  - Advanced filters

- **Phase 3 (Advanced):** Future
  - Auto-archiving
  - Compression
  - Analytics

## Open Questions

1. **Should we preserve git history when archiving?**
   - Git tracks moves, so `git mv` would maintain history
   - Consider: `--preserve-git-history` flag?

2. **Archive file format?**
   - Keep as `.md` files (current)
   - Convert to JSON for faster indexing?
   - Both?

3. **Conflict resolution?**
   - What if task with same ID exists in archive?
   - Overwrite, rename, or error?

4. **Maximum age for current tasks?**
   - Warning if tasks older than X days not archived?
   - Configurable threshold?

## Recommendation

**Implement Phase 1 with:**
- By-month archive organization (default)
- Manual archiving commands
- Simple list/restore functionality
- Clear, intuitive CLI semantics

**Defer to Phase 2:**
- Auto-archiving
- Advanced search/indexing
- Archive compression

This provides immediate value while keeping complexity manageable.
