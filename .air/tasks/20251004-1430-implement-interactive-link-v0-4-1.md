# Task: Implement interactive link command for v0.4.1

## Date
2025-10-04 14:30

## Prompt
Task: for v0.4.1 we will refactor `air link` to be interactive by default. Please make a plan and ask questions before proceeding.

Follow-up: Make --review the default.

## Actions Taken

1. **Planning Phase**
   - Analyzed current `air link` implementation
   - Created detailed plan with questions about default behavior, auto-classification, partial arguments, name suggestions
   - User provided decisions: default to interactive, opt-in for classification, deprecate NAME:PATH format
   - Finalized plan with user approval

2. **Interactive Link Implementation**
   - Created `_interactive_link_add()` helper function with 5 steps:
     - Step 1: Path prompt with validation loop
     - Step 2: Name prompt with folder name default and uniqueness checking
     - Step 3: Relationship prompt (review/develop)
     - Step 4: Optional auto-classification (opt-in for performance)
     - Step 5: Confirmation panel with summary
   - Updated `link_add` command signature to accept optional --path and --name
   - Added deprecation warning for NAME:PATH format (removal in v0.5.0)
   - Implemented interactive mode detection based on missing arguments

3. **Test Updates**
   - Updated 7 link command integration tests to use new --path/--name format
   - Replaced invalid format test with type flag test
   - Updated deprecated format test to show warning
   - All tests updated to new non-interactive syntax

4. **Default Review Mode**
   - Made --review the default relationship when neither flag specified
   - Simplified minimal usage: `air link add --path PATH --name NAME`
   - Removed validation requiring relationship flag in non-interactive mode
   - Added test for default review behavior

5. **Documentation Updates**
   - Updated COMMANDS.md with comprehensive interactive link documentation
   - Added examples for interactive, non-interactive, and minimal usage
   - Documented all interactive features and deprecation notice
   - Marked --review as [default] in options

6. **Version Updates**
   - Updated version to 0.4.1 in `__init__.py` and `pyproject.toml`
   - Updated CHANGELOG.md with complete feature list and changes

## Files Changed

- `src/air/commands/link.py` - Added interactive mode with _interactive_link_add() function, updated command signature, added deprecation warning
- `tests/integration/test_commands.py` - Updated 7 tests for new format, added test for default review behavior
- `docs/COMMANDS.md` - Comprehensive documentation update for interactive link command
- `CHANGELOG.md` - Added v0.4.1 section with features, changes, deprecation notice
- `src/air/__init__.py` - Version bump to 0.4.1
- `pyproject.toml` - Version bump to 0.4.1

## Outcome
✅ Success

Successfully implemented interactive link command for v0.4.1:

**Key Features:**
- Interactive by default with guided prompts
- Smart defaults (folder name, review mode, implementation type)
- Path validation with retry loops
- Name uniqueness validation
- Optional auto-classification (opt-in)
- Confirmation panel before creating link
- Partial argument support
- Minimal usage: `air link add --path PATH --name NAME`

**Testing:**
- All 318 tests passing ✅
- 8 link-related tests (7 updated + 1 new)

**Commits:**
- feat: Add interactive link command for v0.4.1 (d68ae51)
- feat: Make --review the default for air link add (bd7f562)

**Deprecation:**
- NAME:PATH format deprecated, shows warning, removal in v0.5.0

## Notes

### Design Decisions

1. **Interactive vs Non-Interactive Detection:**
   - Interactive triggers when path OR name missing
   - All other args are optional with smart defaults
   - Allows partial arguments with prompting for missing values

2. **Performance - Opt-in Classification:**
   - User requested opt-in (not opt-out) for auto-classification
   - Reason: Link command should run quickly without folder scan
   - Default in interactive prompt is "No" for classification

3. **Default Review Mode:**
   - User requested --review as default (most common case)
   - Simplifies usage: `air link add --path PATH --name NAME`
   - --develop flag required only when contributing back

4. **Deprecation Strategy:**
   - NAME:PATH format shows warning in v0.4.1
   - Planned removal in v0.5.0
   - Parse and use if provided, but warn user

### Technical Implementation

**Interactive Flow:**
```
1. Show welcome panel
2. Prompt for path (validate exists, is directory)
3. Prompt for name (default: folder name, validate uniqueness)
4. Prompt for relationship (review/develop, default: review)
5. Optional: Auto-classify resource type
6. Manual type selection if not classified
7. Show confirmation panel
8. Create symlink and update config
```

**Non-Interactive Requirements:**
- --path (required)
- --name (required)
- --review or --develop (defaults to --review)
- --type (defaults to "implementation")

### Related Files

- Planning discussion in conversation summary
- User decisions captured in plan recap
- Implementation follows approved design
