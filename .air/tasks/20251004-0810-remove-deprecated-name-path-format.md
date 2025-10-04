# Task: Remove Deprecated NAME:PATH Format

## Date
2025-10-04 08:10

## Prompt
User: "yes. The NAME:PATH format must be completely removed everywhere"

## Actions Taken

1. **Searched for all NAME:PATH format usage**
   - Found 18 occurrences in `tests/integration/test_commands.py`
   - Found 4 occurrences using `--path` option (deprecated)
   - Found references in documentation files

2. **Updated Integration Tests** (18 replacements)
   - Changed from: `runner.invoke(main, ["link", "add", f"name:{path}", "--review"])`
   - Changed to: `runner.invoke(main, ["link", "add", str(path), "--name", "name", "--review"])`
   - All test invocations now use new positional PATH argument syntax

3. **Fixed `--path` Option Usage** (4 replacements)
   - Removed `--path` option from validate command tests
   - Changed from: `["link", "add", "--path", str(path), "--name", "name", ...]`
   - Changed to: `["link", "add", str(path), "--name", "name", ...]`

4. **Updated Documentation**
   - `README.md`: Updated command reference to show `air link add PATH` instead of `NAME:PATH`
   - `QUICKSTART.md`: Updated examples and quick reference table
   - `docs/ARCHITECTURE.md`: Removed obsolete `repos-to-link.txt` format example
   - Left CHANGELOG.md historical entries unchanged (they document past versions)

5. **Verified Removal**
   - Searched entire codebase for remaining NAME:PATH references
   - Only historical references remain in task files and CHANGELOG (as expected)
   - All active code and documentation now use new format

## Files Changed

### Tests Updated
- `tests/integration/test_commands.py`
  - 18 test invocations updated from NAME:PATH to positional PATH
  - 4 test invocations updated to remove `--path` option
  - All 325 tests now passing ✅

### Documentation Updated  
- `README.md` (line 181)
  - Updated command reference section
  - Added proper option descriptions

- `QUICKSTART.md` (lines 70-72, 303)
  - Updated quick command examples
  - Updated quick reference table

- `docs/ARCHITECTURE.md` (lines 257-265)
  - Removed obsolete `repos-to-link.txt` format section

## Outcome
✅ Success

All NAME:PATH format references completely removed from active codebase:
- **325 tests passing** ✅ (was 306 passing, 19 failing)
- All integration tests updated to new format
- All documentation updated
- No deprecated syntax remains in active code

## Notes

### What Was Removed

The deprecated NAME:PATH format allowed specifying resource name and path together:
```bash
# OLD (deprecated)
air link add service-a:~/repos/service-a --review
```

This has been completely replaced with positional PATH argument:
```bash
# NEW (current)
air link add ~/repos/service-a --name service-a --review
```

### Historical Records Preserved

The following files retain NAME:PATH references for historical documentation purposes:
- `.air/tasks/*.md` - Task files are immutable historical records
- `CHANGELOG.md` - Changelog entries document version history

These are intentionally preserved as they document what happened in past versions.

### Test Improvements

The test updates improved clarity by making the command syntax explicit:
- Before: `f"name:{path}"` - hard to read string interpolation
- After: `str(path), "--name", "name"` - clear, separate arguments

### Breaking Change Complete

This completes the breaking change announced in v0.4.3:
- Removed `--path` option (use positional PATH)
- Removed NAME:PATH format completely
- All documentation reflects new syntax
- All tests use new syntax
