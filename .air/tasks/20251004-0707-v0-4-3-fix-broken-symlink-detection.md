# Task: v0.4.3 - Fix Broken Symlink Detection

## Date
2025-10-04 07:07

## Prompt
User: "I manually tested `air link` and it worked as expected to link a library. However, when I manually `rm` the symlink, `air link list` still shows the link! Also `air validate` does not find this problem."

Follow-up: "are there any other commands that should be reviewed based on this finding?"

Follow-up: "Task: Correct issues from missing or broken symlinks. this will be part of v0.4.2" [Note: Actually v0.4.3, since v0.4.2 was already released]

## Actions Taken

1. **Investigated Commands Affected by Broken Symlinks**
   - Reviewed all commands that work with linked resources
   - Identified 5 commands with issues:
     - `air validate` - Only checks existing symlinks, doesn't detect missing ones
     - `air link list` - Shows all resources without checking if they exist
     - `air status` - Same issue as link list
     - `air classify` - Would crash if resource path doesn't exist
     - `air pr` - Would crash if resource path doesn't exist

2. **Fixed `air validate` Command**
   - Added config cross-reference to detect missing resources
   - Now checks if configured resources exist in `repos/` directory
   - Detects when symlink is missing entirely
   - Detects when symlink exists but target is broken
   - Error messages clearly indicate the problem
   - Location: `src/air/commands/validate.py:102-141`

3. **Added Path Existence Checks**
   - `air classify` - Checks resource path exists before attempting classification
   - `air pr` - Checks resource path exists before git operations
   - Both provide helpful error messages directing users to run `air validate`

4. **Added Status Indicators**
   - `air link list` - New "Status" column shows:
     - ✓ valid - Resource exists and symlink is good
     - ✗ broken - Symlink exists but target is missing
     - ⚠ missing - Resource not found in repos/
   - `air status` - Same status indicators in resource tables
   - Both commands now give immediate visual feedback on resource health

5. **Testing**
   - All 318 existing tests still passing ✅
   - Added 2 new integration tests:
     - `test_validate_detects_missing_symlink` - Tests detection of removed symlink
     - `test_validate_detects_broken_symlink` - Tests detection of broken target
   - All 320 tests passing ✅

6. **Version and Documentation Updates**
   - Updated `pyproject.toml`: 0.4.2 → 0.4.3
   - Updated `src/air/__init__.py`: 0.4.2 → 0.4.3
   - Added comprehensive CHANGELOG entry for v0.4.3

## Files Changed

### Core Validation Fix
- `src/air/commands/validate.py` (lines 102-141)
  - Added config cross-reference logic
  - Detects missing resources from config
  - Detects broken symlinks

### Path Existence Checks
- `src/air/commands/classify.py` (lines 98-107)
  - Added resource path existence check
  - Helpful error message with hint

- `src/air/commands/pr.py` (lines 123-132)
  - Added resource path existence check
  - Uses PathError for consistent error handling

### Status Indicators
- `src/air/commands/link.py` (lines 533-579)
  - Added Status column to both review and collaborative tables
  - Logic checks link_path.exists() and resource_path.exists()
  - Three states: valid, broken, missing

- `src/air/commands/status.py` (lines 154-209)
  - Added Status column to resource tables
  - Same three-state logic as link list

### Tests
- `tests/integration/test_commands.py` (lines 277-357)
  - Added `test_validate_detects_missing_symlink`
  - Added `test_validate_detects_broken_symlink`

### Version Files
- `pyproject.toml` - version = "0.4.3"
- `src/air/__init__.py` - __version__ = "0.4.3"
- `CHANGELOG.md` - Added v0.4.3 section

## Outcome
✅ Success

Successfully implemented v0.4.3 with comprehensive broken symlink detection:

**Bugs Fixed:**
- `air validate` now detects missing/broken symlinks
- All commands handle missing resources gracefully
- No more crashes when resources are removed manually

**UX Improvements:**
- Status indicators in `air link list` and `air status`
- Clear error messages guide users to `air validate`
- Immediate visual feedback on resource health

**Testing:**
- All 320 tests passing ✅ (added 2 new tests)
- Full coverage of broken symlink scenarios

## Notes

### Design Decisions

1. **Three-State Status:**
   - **✓ valid** - Both symlink and target exist
   - **✗ broken** - Symlink exists but target removed
   - **⚠ missing** - Symlink not found in repos/

   This covers all possible states and gives users clear indication of the problem.

2. **Error Message Strategy:**
   - All path-related errors now suggest running `air validate`
   - Consistent messaging across all commands
   - Uses existing PathError infrastructure for `air pr`
   - Custom messages for `air classify` (uses console.print)

3. **Validation Logic:**
   - Cross-references config with filesystem
   - Checks all configured resources, not just existing files
   - Separates "missing" from "broken" symlinks
   - Clear, actionable error messages

### Technical Details

**Validation Cross-Reference:**
```python
# Load config and check all configured resources
config = AirConfig(**config_data)
for resource in config.get_all_resources():
    link_path = project_root / "repos" / resource.name
    if not link_path.exists():
        errors.append(f"Missing resource: repos/{resource.name} ...")
    elif link_path.is_symlink() and not is_symlink_valid(link_path):
        errors.append(f"Broken symlink: repos/{resource.name}")
```

**Status Indicator Logic:**
```python
resource_path = Path(resource.path)
link_path = project_root / "repos" / resource.name

if link_path.exists() and resource_path.exists():
    status = "[green]✓ valid[/green]"
elif link_path.exists() and not resource_path.exists():
    status = "[red]✗ broken[/red]"
else:
    status = "[yellow]⚠ missing[/yellow]"
```

### User Impact

**Before:**
- Manually removing a symlink left config inconsistent
- `air link list` showed resource as if it were valid
- `air validate` didn't detect the problem
- `air classify` and `air pr` would crash with unhelpful errors

**After:**
- `air validate` detects and reports missing/broken symlinks
- `air link list` shows status: ✓/✗/⚠
- `air status` shows same status indicators
- `air classify` and `air pr` fail gracefully with helpful messages
- Users get clear guidance to run `air validate`

### Version Note

User initially said "this will be part of v0.4.2", but since v0.4.2 was already released (resource type simplification), this became v0.4.3.

## Commit Message

```
fix: v0.4.3 - Detect and handle broken/missing symlinks

Fixes issue where manually removed symlinks weren't detected by validate,
and link list/status showed resources as valid when they were broken.

Changes:
- air validate: Cross-reference config with filesystem
- air validate: Detect missing resources and broken symlinks
- air link list: Show status indicators (✓ valid, ✗ broken, ⚠ missing)
- air status: Show status indicators for all resources
- air classify: Fail gracefully if resource path missing
- air pr: Fail gracefully if resource path missing

Testing: All 320 tests passing (added 2 new tests)
```
