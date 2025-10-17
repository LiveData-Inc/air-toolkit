# Task: Fix upgrade, Claude commands, and repo path handling

## Date
2025-10-17 06:27

## Prompt
```
excellent. We have several changes to make, on a branch. 1. remove the scripts/daily-analysis.sh file, it should not be added during air upgrade. 2) ensure that the claude tasks (e.g. /air-task ) are properly added to the project during init and upgrade. 3) revise how the linked repos are found, by makeing tehm relative paths under a user's designated folder. the user's designated folder will be found by consulting environment variable GIT_REPOS_PATH.
```

## Actions Taken
1. Created feature branch: `fix/upgrade-repo-paths`
2. **Removed daily-analysis.sh from upgrade command**:
   - Updated `src/air/commands/upgrade.py` to remove daily-analysis.sh from scripts list
   - Removed special handling in `_create_file` function
   - Updated docstring to reflect changes
3. **Added Claude commands support to init and upgrade**:
   - Moved `_create_claude_commands` from `init.py` to `templates.py` as shared function
   - Added `_needs_claude_commands` helper in `upgrade.py` to detect missing commands
   - Updated `upgrade` command to check for and create missing Claude slash commands
   - Ensured 9 slash commands are created: air-analyze, air-findings, air-link, air-review, air-status, air-summary, air-task-complete, air-task, air-validate
4. **Implemented GIT_REPOS_PATH environment variable support**:
   - Added `resolve_repo_path()` to `src/air/utils/paths.py` - resolves relative paths relative to `` if set
   - Added `get_relative_repo_path()` to display paths relative to `` when applicable
   - Updated `src/air/commands/link.py` to use `resolve_repo_path()` for all path resolution
   - Updated help text in `link add` to document path resolution behavior
   - Updated `src/air/utils/tables.py` to display relative paths in status output
5. Fixed linting issues in modified files
6. Symlink behavior unchanged (still using ln/mklink)

## Files Changed
- `src/air/commands/upgrade.py` - Removed daily-analysis.sh, added Claude commands check
- `src/air/services/templates.py` - Added shared `create_claude_commands()` function
- `src/air/commands/init.py` - Refactored to use shared template function
- `src/air/utils/paths.py` - Added `resolve_repo_path()` and `get_relative_repo_path()`
- `src/air/commands/link.py` - Updated to use new path resolution, updated help text
- `src/air/utils/tables.py` - Display relative paths in status tables
- `.air/tasks/20251017-001-0627-fix-upgrade-and-repo-path-handling.md` - This task file

## Outcome
✅ Success

All three requirements implemented:
1. ✅ daily-analysis.sh removed from upgrade
2. ✅ Claude slash commands properly added during init and upgrade
3. ✅ GIT_REPOS_PATH support for relative repo paths

Path resolution behavior:
- Relative paths: Use `/path` if env var is set, otherwise CWD
- Absolute paths: Work as before (including ~ expansion)
- Display: Shows relative paths in `air status` when within GIT_REPOS_PATH

## Notes
- Pre-existing test failures in test_link.py (tests need .air/ directory setup)
- Linting cleaned up for all modified files
- All changes on branch `fix/upgrade-repo-paths`
- Ready for commit and PR
