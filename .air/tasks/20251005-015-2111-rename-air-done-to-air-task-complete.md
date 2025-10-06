# Task: Rename /air-done to /air-task-complete

## Date
2025-10-05 21:11

## Prompt
User: "yes. `/air-task-complete` is much more clear and the verbosity is not a problem."

## Goal
Rename the /air-done slash command to /air-task-complete for better clarity and semantic consistency with air task complete command.

## Rationale
- More explicit about what it does (completes task + commits)
- Mirrors the actual CLI command: air task complete
- Creates clear pairing with /air-task (create → complete)
- Better discoverability for new users
- Verbosity acceptable for end-of-session command

## Actions Taken
1. ✅ Create task file for tracking
2. ✅ Rename .claude/commands/air-done.md to air-task-complete.md
3. ✅ Update description in front matter
4. ✅ Update all documentation references
5. ✅ Commit changes (pending)

## Files Changed
- `.air/tasks/{timestamp}-rename-air-done-to-air-task-complete.md` - This task file
- `.claude/commands/air-done.md` → `.claude/commands/air-task-complete.md` (renamed)
- `.claude/commands/air-task-complete.md` - Updated description
- `README.md` - Updated slash command list
- `QUICKSTART.md` - Updated slash command list
- `docs/COMMANDS.md` - Updated table and examples
- `PROJECT-STATUS.md` - Updated references (2 locations)

## Outcome
✅ Success

Renamed /air-done to /air-task-complete for better clarity and semantic consistency.

**Changes:**
- Renamed .claude/commands/air-done.md → air-task-complete.md
- Updated description in front matter
- Updated all documentation to reflect new name

**Benefits:**
- More explicit about functionality (completes task + commits)
- Mirrors the actual CLI command: air task complete
- Creates clear pairing with /air-task (create → complete)
- Better discoverability for new users

All 9 slash commands now follow consistent naming patterns.

## Notes
New slash command lineup (9 total):
- /air-task - Create and start new task
- /air-link - Link repository
- /air-analyze - Run analysis
- /air-validate - Validate project
- /air-status - Get status
- /air-findings - Generate report
- /air-summary - Work summary
- /air-review - Code review context
- /air-task-complete - Complete task and commit (renamed from /air-done)
