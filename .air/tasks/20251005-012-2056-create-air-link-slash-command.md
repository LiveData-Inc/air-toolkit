# Task: Create /air-link Slash Command

## Date
2025-10-05 20:56

## Prompt
User: "the command `/air-link PATH` should act as `air link add PATH`" (via /air-begin)

## Goal
Create a new Claude Code slash command `/air-link` that provides a quick shorthand for `air link add PATH`.

## Rationale
- Faster workflow for linking repositories
- Consistent with other slash commands (/air-task, /air-review, /air-done)
- Makes common operation more discoverable in Claude Code

## Actions Taken
1. ⏳ Create task file for tracking
2. ✅ Create .claude/commands/air-link.md
3. ✅ Test the slash command
4. ✅ Update documentation (no changes needed)

## Files Changed
- `.air/tasks/{timestamp}-create-air-link-slash-command.md` - This task file
- `.claude/commands/air-link.md` - New slash command for linking repos

## Outcome
✅ Success

Created .claude/commands/air-link.md - a shorthand for `air link add PATH`.

Users can now use:
- `/air-link ~/repos/myapp` instead of manually running `air link add`
- Follows the same pattern as /air-task and /air-review
- Auto-suggests next steps after linking

## Notes
This complements the existing /air-task command and makes linking repos even faster.
