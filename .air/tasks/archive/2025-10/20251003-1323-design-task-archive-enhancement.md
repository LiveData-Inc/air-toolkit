# Task: Design Task Archive Enhancement

## Date
2025-10-03 13:23 UTC

## Prompt
Enhance the design to ability to archive task files by moving them to a subfolder tasks/archive. This allows the user to see the current and recent tasks without having an overwhelming number of historical tasks in the tasks/ folder. Discuss the air cli command semantics and propose a plan for this enhancement.

## Actions Taken
1. Analyzing current task file structure
2. Designing CLI command semantics
3. Creating comprehensive enhancement plan

## Files Changed
- docs/TASK-ARCHIVE-DESIGN.md - Created comprehensive design proposal

## Outcome
✅ Success

Completed comprehensive task archive design with:
- CLI command semantics (archive, restore, list, search)
- 3 archive structure options (recommended: by-month organization)
- 3-phase implementation plan
- Impact analysis on existing features (air summary, task list)
- Testing requirements and success criteria
- Timeline estimates (Phase 1: 1-2 days)

## Notes
Design decisions made:
- **Archive structure**: By-month organization (`.air/tasks/archive/2025-10/`)
- **CLI pattern**: `air task <action> [selector] [options]`
- **Phase 1 scope**: Core archive/restore/list commands with manual archiving
- **Phase 2+**: Auto-archiving, compression, analytics (future)

Key design questions answered:
- Manual archiving for Phase 1, auto-archiving in Phase 2
- By-month organization balances granularity and simplicity
- Search across current and archived with `--all` flag
- `air summary` excludes archived by default, `--all` to include
