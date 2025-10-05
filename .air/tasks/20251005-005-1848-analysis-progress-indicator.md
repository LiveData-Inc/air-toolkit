# Task: Analysis Progress Indicator

## Date
2025-10-05 18:48

## Prompt
Feature: When analyzing repos, preface the output text with a progress indication. e.g, instead of "Analyzing: NAME", show "[3/7] Analyzing NAME", where NAME is the 3rd of 7 repos being analyzed.

## Goal
Add progress indicators to multi-repo analysis output to show users which repo is being analyzed out of the total.

## Actions Taken

1. ✅ Created task file
2. ✅ Added optional `current_index` and `total_count` parameters to `_analyze_single_repo`
3. ✅ Updated info message to show "[X/Y] Analyzing: NAME" when progress params provided
4. ✅ Updated `_analyze_multi_repo` to count total repos and track current index
5. ✅ Updated `_analyze_gap` to count total repos (library + dependents) and track progress
6. ✅ All 414 tests passing
7. ✅ Updated CHANGELOG.md

## Files Changed
- `src/air/commands/analyze.py` - Added progress tracking to analysis functions

## Outcome
✅ Success

Multi-repo analysis now shows progress indicators:
- `air analyze --all` shows "[3/7] Analyzing: repo-name"
- `air analyze --gap library` shows "[2/4] Analyzing: dependent-name"
- Single repo analysis (no --all) continues to show "Analyzing: repo-name" without progress

## Notes
This improves UX by showing users exactly where they are in a long analysis operation.

Implementation details:
- Added optional parameters with default None to maintain backward compatibility
- Progress tracking counts total repos upfront and increments counter during iteration
- Only displays progress indicator when both current_index and total_count are provided
