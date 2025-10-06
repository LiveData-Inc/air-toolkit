# Task: Add Writable Column to air status and air link list

## Date
2025-10-05 20:28

## Prompt
Feature: `air status` and `air link list` should show the writable attribute for each linked repo. Keep it simple, perhaps "Writable" as a column heading and Y/N or T/F for each row.

## Goal
Add a "Writable" column to resource tables showing whether AI can write to each repository.

## Actions Taken
1. ✅ Read air status command implementation
2. ✅ Read air link list command implementation
3. ✅ Identified that both commands use render_resource_table()
4. ✅ Updated render_resource_table() in src/air/utils/tables.py
5. ✅ Added "Writable" column (width=8) between Type and Path
6. ✅ Display "Y" if resource.writable else "N"
7. ✅ Update JSON output for air link list to include writable field
8. ✅ Tested both commands - column displays correctly
9. ✅ Verified JSON output includes writable: true/false

## Files Changed
- `src/air/utils/tables.py` - Added Writable column to render_resource_table()
- `src/air/commands/link.py` - Added writable field to JSON output

## Outcome
✅ Success

Both `air status` and `air link list` now show the Writable column:
- Human-readable: Shows "Y" or "N"
- JSON format: Shows "writable": true or "writable": false
- Column positioned between Type and Path for clarity

## Test Results
```
air link list output:
┃ Name          ┃ Type          ┃ Writable ┃ Path                 ┃
┃ test-repo     ┃ documentation ┃ N        ┃ /path/to/repo        ┃
┃ writable-repo ┃ documentation ┃ Y        ┃ /path/to/writable    ┃
```

## Notes
Simple implementation using Y/N for clarity. Both commands automatically show the column since they share the same table rendering function.
