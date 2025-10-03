# Task: Support air init in Existing Projects

## Date
2025-10-03 13:45 UTC

## Prompt
Support running `air init` in an existing project. the default should be to not create, but with a flag, we can create a new folder and then run initialize .air inside it.

## Actions Taken
1. Analyzing current `air init` behavior
2. Designing new semantics for existing projects
3. Updating command implementation with backward compatibility
4. Adding 9 comprehensive integration tests
5. Running all tests to verify (110 tests total, all passing)

## Files Changed
- src/air/commands/init.py - Enhanced with new semantics for existing projects
- tests/integration/test_commands.py - Added 9 new tests for init behavior

## Outcome
✅ Success

Successfully enhanced `air init` to support existing projects with:
- **Default behavior**: `air init` (no args) initializes in current directory
- **Create directory**: `air init <name>` creates new directory (backward compat)
- **Explicit flag**: `air init --create-dir <name>` creates directory
- **Mode support**: `air init --mode=review` in current directory
- **Smart warnings**: Warns when initializing in directory with existing files
- **Error handling**: Prevents double-initialization, non-empty new directories
- **All existing tests pass**: 100% backward compatibility maintained

New usage patterns:
- `air init` - Initialize AIR in current project directory
- `air init --mode=review` - Initialize with specific mode in current dir
- `air init my-project` - Create new directory (backward compatible)
- `air init --create-dir new-proj` - Explicit directory creation

## Notes
Current behavior:
- `air init <name>` creates new directory
- `air init .` initializes in current directory

New design:
- `air init` (no args) - Initialize in current directory (default)
- `air init --create-dir=<name>` - Create directory and initialize
- Backward compatible with existing usage
