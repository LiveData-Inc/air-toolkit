# Task: Add Interactive Flag to `air link add`

## Date
2025-10-04 12:25

## Prompt
User: "Task: add a '-i' flag to `air link add` command, such that it interactively prompts for defaults. Without the -i flag, the command should accept defaults without prompting. This will apply only in the `air link add [PATH]` scenario, because other scenarios must consider args. (e.g. `air link add /path/to/foo` will classify the project, accept the folder name as name, and otherwise make the command happen immediately without any additional user interaction."

## Goal

Change `air link add` behavior to be non-interactive by default, with `-i/--interactive` flag for interactive mode.

### Current Behavior (v0.5.1)
- `air link add PATH` → Prompts interactively for name, relationship, type
- User must answer questions before link is created

### New Behavior
**Non-interactive (default):**
- `air link add /path/to/foo` → Immediate, no prompts
  - Name: "foo" (folder name)
  - Relationship: review (default)
  - Type: Auto-detected via classification
  - Creates link immediately

**Interactive (with -i flag):**
- `air link add /path/to/foo -i` → Prompts for everything
  - Shows defaults in prompts
  - Allows user to customize
  - Shows confirmation panel

**With explicit args (always non-interactive):**
- `air link add /path/to/foo --name myname --review --type library` → Immediate
  - Uses provided values
  - No prompts

## Actions Taken

1. **Added `-i/--interactive` flag to `air link add` command signature**
   - Modified `src/air/commands/link.py` line 296-300
   - Added Click option for interactive mode

2. **Implemented non-interactive mode as default**
   - Modified `link_add()` function to check if `-i` flag provided
   - If no `-i`, uses smart defaults (folder name, auto-classification)
   - If `-i`, calls `_interactive_link_add()` for guided prompts

3. **Updated logic for auto-classification**
   - When `--type` not provided, runs `classify_resource()` automatically
   - No user prompts, just informational output
   - Detects technology stack and resource type

4. **Added comprehensive tests**
   - `test_link_add_auto_classify` - Tests auto-classification without --type
   - `test_link_add_folder_name_default` - Tests folder name as default
   - `test_link_add_fully_automatic` - Tests both defaults (key test)
   - All 336 tests passing ✅

5. **Updated documentation**
   - `docs/COMMANDS.md` - Complete rewrite of `air link add` section
   - Added `-i` flag documentation
   - Documented smart defaults and auto-classification
   - Provided migration guide

6. **Updated CHANGELOG.md**
   - Added v0.5.11 entry
   - Documented all changes, additions, and testing
   - Included migration guide for users

7. **Updated version numbers**
   - `pyproject.toml` → 0.5.11
   - `src/air/__init__.py` → 0.5.11
   - `docs/COMMANDS.md` → 0.5.11

## Files Changed

- `src/air/commands/link.py` - Added `-i` flag, updated `link_add()` logic for non-interactive default
- `tests/integration/test_commands.py` - Added 3 new tests for new behavior (lines 1116-1220)
- `docs/COMMANDS.md` - Rewrote `air link add` section, updated version to 0.5.11
- `CHANGELOG.md` - Added v0.5.11 entry with complete changelog
- `pyproject.toml` - Updated version to 0.5.11
- `src/air/__init__.py` - Updated version to 0.5.11

## Outcome
✅ Success

Successfully implemented non-interactive mode as default for `air link add` with `-i` flag for interactive mode. All 336 tests passing. Documentation updated. Ready for release as v0.5.11.

## Notes

### Design Decisions

1. **Default should be fast** - Most common use case is quick linking
2. **-i for customization** - When user wants to override defaults
3. **Explicit args override** - If name/relationship/type provided, skip prompts
4. **Classification still runs** - Auto-detect type even in non-interactive mode
5. **Folder name is good default** - Most users want resource name = folder name
