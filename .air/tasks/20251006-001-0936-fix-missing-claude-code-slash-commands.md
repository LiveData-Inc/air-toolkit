# Task: Fix missing Claude Code slash commands after air init

## Date
2025-10-06 09:36

## Prompt
I created a new empty project and ran `air init`, then opened and initialized Claude Code using `/init`. After init, the various /air-... commands were not available to me. I checked the .claude folder and the files are not present.

## Actions Taken
1. Creating task file
2. Investigating issue - found that `air init` was not copying Claude Code slash commands
3. Created `src/air/templates/claude_commands/` directory
4. Copied 9 slash command files from `.claude/commands/` to templates
5. Added `_create_claude_commands()` helper function to `init.py`
6. Updated `air init` to call the helper when `--track` is enabled
7. Created `__init__.py` for claude_commands package
8. Tested fix - confirmed `.claude/commands/` is now created with all 9 files

## Files Changed
- `src/air/commands/init.py` - Added `_create_claude_commands()` function and call
- `src/air/templates/claude_commands/` - Created directory with 9 command files:
  - `air-analyze.md`
  - `air-findings.md`
  - `air-link.md`
  - `air-review.md`
  - `air-status.md`
  - `air-summary.md`
  - `air-task-complete.md`
  - `air-task.md`
  - `air-validate.md`
- `src/air/templates/claude_commands/__init__.py` - Package marker
- `.air/tasks/20251006-001-0936-fix-missing-claude-code-slash-commands.md` - This task file

## Outcome
✅ Success

Claude Code slash commands are now automatically created in `.claude/commands/` when running `air init`. Tested successfully in `/tmp/test-air-init`.

## Notes
The slash command files are embedded in the package templates and copied during `air init` when task tracking is enabled (`--track`, which is the default). This ensures all new AIR projects have the `/air-*` slash commands available immediately.
