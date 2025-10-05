# Task: Add Interactive Mode to `air link remove`

## Date
2025-10-04 13:34

## Prompt
User: "Task: `air link remove -i` should display a numbered list of currently linked repos, and invite the user to select one by number"

## Goal

Add `-i/--interactive` flag to `air link remove` command for numbered list selection.

### Current Behavior
- `air link remove NAME` → Removes resource by name
- Requires knowing the exact resource name

### New Behavior with -i flag
- `air link remove -i` → Shows numbered list of linked resources
- User selects by number (1, 2, 3, etc.)
- Confirms removal before proceeding
- More user-friendly than remembering exact names

## Actions Taken

1. **Added `-i/--interactive` flag to `air link remove` command**
   - Modified `src/air/commands/link.py` line 572-586
   - Added Click option for interactive mode
   - Made NAME argument optional (`required=False`)
   - Added `@click.pass_context` to access context for usage display

2. **Extracted removal logic into helper function**
   - Created `_remove_resource()` helper function (lines 517-569)
   - Allows reuse from both interactive and non-interactive modes
   - Handles resource lookup, validation, symlink removal, config update

3. **Implemented interactive numbered selection**
   - Displays all resources (review + develop) in Rich table
   - Numbered list with columns: #, Name, Type, Relationship, Path
   - Prompts user to select by number or 'q' to quit
   - Shows confirmation with resource details before removal
   - Handles invalid input, cancellation (Ctrl+C), empty list gracefully

4. **Updated behavior when no arguments provided**
   - Changed from error message to usage display
   - Shows full command help with examples
   - More helpful for users learning the command

5. **Added comprehensive test**
   - `test_link_remove_no_name_without_interactive` - Verifies usage display
   - All 337 tests passing ✅

6. **Updated documentation**
   - `docs/COMMANDS.md` - Complete rewrite of `air link remove` section
   - Added `-i` flag documentation with example session
   - Provided both interactive and non-interactive usage examples
   - Updated CHANGELOG.md with v0.5.11 additions

## Files Changed

- `src/air/commands/link.py` - Added `-i` flag, extracted `_remove_resource()`, implemented interactive selection
- `tests/integration/test_commands.py` - Added `test_link_remove_no_name_without_interactive` test
- `docs/COMMANDS.md` - Rewrote `air link remove` section with interactive mode docs
- `CHANGELOG.md` - Added interactive remove to v0.5.11 entry

## Outcome
✅ Success

Successfully implemented interactive mode for `air link remove -i` with numbered list selection and confirmation. All 337 tests passing. Part of v0.5.11 release.

## Notes

### Design Decisions

1. **Numbered list** - Easy to select without typing exact names
2. **Show both review and develop** - All resources in one list
3. **Confirmation** - Ask before removing to prevent mistakes
4. **Display details** - Show name, type, path for context
5. **Graceful exit** - Allow user to cancel selection
