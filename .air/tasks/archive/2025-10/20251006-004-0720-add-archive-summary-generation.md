# Task: Add archive summary generation

## Date
2025-10-06 07:20

## Prompt
As we archive tasks, consider updating a summary of all archived tasks.

## Actions Taken
1. Creating task file
2. Designing archive summary system
3. Added `generate_archive_summary()` function to `task_archive.py` that creates markdown summary organized by time period
4. Added `update_archive_summary()` function to regenerate ARCHIVE.md
5. Updated `air task archive` command to automatically generate/update ARCHIVE.md after archiving
6. Updated `air task restore` command to update ARCHIVE.md after restoration
7. Updated all documentation (COMMANDS.md, README.md, CLAUDE.md, CHANGELOG.md) to mention ARCHIVE.md

## Files Changed
- `src/air/services/task_archive.py` - Added `generate_archive_summary()` and `update_archive_summary()` functions
- `src/air/commands/task.py` - Import and call `update_archive_summary()` in archive and restore commands
- `docs/COMMANDS.md` - Updated archive and restore output examples to show ARCHIVE.md update
- `.air/README.md` - Added ARCHIVE.md to structure diagram and explained its purpose
- `CLAUDE.md` - Added ARCHIVE.md to project structure
- `CHANGELOG.md` - Added archive summary feature to v0.6.3 release notes
- `.air/tasks/20251006-004-0720-add-archive-summary-generation.md` - This task file

## Outcome
✅ Success

Successfully implemented automatic archive summary generation. The ARCHIVE.md file is now automatically created and updated whenever tasks are archived or restored, providing an organized index of all archived tasks with table of contents, task details, and quick navigation.

## Notes
**Implementation Details:**
- `ARCHIVE.md` is created at `.air/tasks/archive/ARCHIVE.md`
- Summary includes:
  - Total count of archived tasks
  - Table of contents with links to each time period
  - Tasks organized by period (2025-10, 2025-09, etc.)
  - For each task: emoji status, title, file path, date, status, and prompt summary (first 100 chars)
- Automatically updated on `air task archive` and `air task restore`
- Helps users understand project history without reading individual task files
- Reduces need to glob through archive directories

**Benefits:**
- Quick overview of all archived work
- Easy navigation with table of contents
- Maintains project history visibility
- No manual maintenance required
