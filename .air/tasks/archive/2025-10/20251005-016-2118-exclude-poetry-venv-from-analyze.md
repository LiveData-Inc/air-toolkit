# Task: Exclude .poetry and .venv from analyze --all

## Date
2025-10-05 21:18

## Prompt
`air analyze --all` includes unneeded reviews of code from `.poetry` and `.venv`. This makes the findings report unwieldy. Please review and correct.

## Actions Taken
1. Investigated the analyzer code to understand how files are scanned
2. Found that `path_filter.py` already existed with exclusion logic
3. Added `.poetry` to the `DEFAULT_EXCLUSIONS` list (was missing)
4. Updated `code_structure.py` analyzer to use centralized `should_exclude_path()` instead of inline filtering
5. Verified all 5 analyzers and found 3 more methods missing the filter
6. Fixed missing filters in:
   - `security.py`: `_check_security_headers()` and `_check_config_files()`
   - `architecture.py`: `_check_circular_imports()`
   - `quality.py`: `_check_documentation()`
   - `performance.py`: `_analyze_javascript_performance()`
7. Tested on meditech-rpa-cdk repo: findings dropped from 35 to 22, no .poetry/.venv refs

## Files Changed
- `src/air/services/path_filter.py` - Added `.poetry` to DEFAULT_EXCLUSIONS list
- `src/air/services/analyzers/code_structure.py` - Replaced inline filtering with `should_exclude_path()` (2 locations)
- `src/air/services/analyzers/security.py` - Added `should_exclude_path()` to 2 methods
- `src/air/services/analyzers/architecture.py` - Added `should_exclude_path()` to `_check_circular_imports()`
- `src/air/services/analyzers/quality.py` - Added `should_exclude_path()` to `_check_documentation()`
- `src/air/services/analyzers/performance.py` - Added `should_exclude_path()` to `_analyze_javascript_performance()`

## Outcome
✅ Success

All analyzers now properly exclude .poetry and .venv directories. Verified with test showing:
- Findings reduced: 35 → 22 (37% reduction)
- Security findings: 10 → 2
- Performance findings: 5 → 1
- Zero .poetry or .venv references in final report

## Notes
- The issue was that some analyzer methods had inline filtering instead of using the centralized `should_exclude_path()` function
- All 6 affected files have been updated to use the centralized filter consistently
- Users can still analyze vendor code with `--include-external` flag if needed
- The filter excludes: .poetry, .venv, venv, node_modules, build, dist, __pycache__, .git, and many more
