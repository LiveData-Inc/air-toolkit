# Task: Implement air task new Command

## Date
2025-10-03 14:15 UTC

## Prompt
Continue with "Complete Core Workflow" by implementing `air task new`

## Actions Taken
1. Created task file for air task new implementation
2. Planned implementation with TodoWrite (9 tasks)
3. Created task template (src/air/templates/ai/task.md.j2)
4. Implemented air task new command with full functionality
5. Fixed safe_filename to handle multiple spaces correctly
6. Created unit tests (8 tests)
7. Created integration tests (7 tests)
8. All tests passing (152 total tests)

## Files Changed
- src/air/commands/task.py - Implemented task_new command
  - Generate timestamped filenames (YYYYMMDD-HHMM-description.md)
  - Render task template with context
  - Validate project structure
  - Write task files to .air/tasks/
- src/air/templates/ai/task.md.j2 - New task template
  - Standard sections: Date, Prompt, Actions, Files, Outcome, Notes
  - Placeholder content for task tracking
- src/air/utils/paths.py - Enhanced safe_filename function
  - Handle multiple consecutive spaces
  - Remove special characters
  - Convert to lowercase with hyphens
- tests/unit/test_task_new.py - New file (8 tests)
  - Tests for filename generation
  - Tests for template rendering
  - Tests for special character handling
- tests/integration/test_commands.py - Added TestTaskNewCommand class (7 tests)
  - Integration tests for task creation
  - Tests for custom prompts
  - Tests for task listing integration

## Outcome
✅ Success

Successfully implemented `air task new` command:
- **Command**: `air task new DESCRIPTION [--prompt TEXT]`
- **Filename format**: YYYYMMDD-HHMM-safe-description.md
- **Template sections**: Date, Prompt, Actions, Files, Outcome, Notes
- **Auto-populated**: timestamp, date, prompt (defaults to description)
- **Safe filenames**: Special characters removed, spaces to hyphens
- **Validation**: Checks for AIR project and .air/tasks directory
- **Integration**: Works with air task list command
- Full test coverage (15 new tests)
- All 152 tests passing

## Notes
Key features:
- Timestamped filenames ensure uniqueness and chronological ordering
- Template provides consistent structure for task tracking
- safe_filename handles special characters: "fix: bug @#$" → "fix-bug"
- Multiple spaces collapsed: "test   spaces" → "test-spaces"
- Custom prompt support via --prompt flag
- Error handling for missing project or tasks directory
- Integrates seamlessly with existing task archive/list commands
