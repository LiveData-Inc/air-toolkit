# Task: Fix --develop flag to set writable=true

## Date
2025-10-06 10:32

## Prompt
`air link add ... --develop` must mark the repo as writeable=true in air-config.json.

## Actions Taken
1. Creating task file
2. Investigated `src/air/commands/link.py` to find where resources are created
3. Added logic to automatically set `writable=True` when `--develop` flag is used (both interactive and non-interactive modes)
4. Added unit tests in `tests/unit/test_link.py` to verify the logic
5. Added integration test `test_link_add_develop_auto_writable` to verify end-to-end behavior
6. Ran tests - all link tests pass (24 passed)

## Files Changed
- `src/air/commands/link.py` - Added `if is_develop and not writable: writable = True` in two places (non-interactive and interactive modes)
- `tests/unit/test_link.py` - Added `TestDevelopFlagWritable` class with 4 unit tests
- `tests/integration/test_commands.py` - Added `test_link_add_develop_auto_writable` integration test
- `.air/tasks/20251006-001-1032-fix-develop-flag-writable-setting.md` - This task file

## Outcome
✅ Success

The `--develop` flag now automatically sets `writable: true` in air-config.json. This applies to both:
- Non-interactive mode: `air link add PATH --develop`
- Interactive mode: selecting "develop" relationship

## Notes
**Implementation Details:**
- Logic added at line 416-418 (non-interactive) and 172-174 (interactive)
- The check is: `if is_develop and not writable: writable = True`
- This allows explicit `--writable` flag to still work if someone wants to explicitly set it
- Review resources (`--review`) remain read-only by default (writable=False)

**Test Coverage:**
- 4 unit tests verify the logic behavior
- 1 integration test verifies end-to-end functionality
- All 24 existing link tests still pass
