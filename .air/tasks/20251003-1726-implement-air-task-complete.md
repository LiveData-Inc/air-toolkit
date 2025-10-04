# Task: implement air task complete command

**Created:** 2025-10-03 17:26 UTC

## Prompt

Add command to mark tasks as complete by updating their outcome section

## Actions Taken

- Starting implementation of air task complete

## Files Changed

- src/air/commands/task.py
- tests/unit/test_task_complete.py
- tests/integration/test_commands.py

## Outcome

✅ Success

## Notes

Implementing full task lifecycle: new → work → complete

**Completed:** Successfully implemented `air task complete` command with:
- Regex-based outcome section update (preserves all content)
- Optional --notes flag to add completion notes
- Proper handling of Notes section at end of file
- Fixed template to include trailing newline after ## Notes
- 9 unit tests + 7 integration tests
- All 186 tests passing ✅
