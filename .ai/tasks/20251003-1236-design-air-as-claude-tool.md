# Task: Design AIR as a First-Class Claude Code Tool

## Date
2025-10-03 12:36 UTC

## Prompt
Let'''s review how to design this so that Claude code will use `air` as a tool, similar to how it uses `Bash`.

## Actions Taken
1. Starting design discussion for AI-native CLI interface

## Files Changed
- (In progress)

## Outcome
⏳ In Progress

Discussing design principles for making AIR discoverable and usable by Claude Code.

## Notes
Key areas to consider:
- Command discoverability
- Machine-readable output formats
- Auto-invocation triggers
- Error handling for AI consumption
- Integration with existing workflows

## Design Decisions Made

1. **Config filename**: Change from .assess-config.json to air-config.json
   - Rationale: Cleaner, matches tool name, less confusing
   - Impact: Update all references in code, docs, templates

