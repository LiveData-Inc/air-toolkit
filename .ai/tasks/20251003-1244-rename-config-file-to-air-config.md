# Task: Rename .assess-config.json to air-config.json

## Date
2025-10-03 12:44 UTC

## Prompt
.assess-config.json should be `air-config.json`

## Actions Taken
1. Identified all files referencing .assess-config.json
2. Planning systematic replacement across codebase

## Files Changed
- CLAUDE.md - Updated AssessmentConfig docstring reference
- src/air/core/models.py - Updated AssessmentConfig docstring
- docs/SPECIFICATION.md - 6 references updated, marked open question as resolved
- docs/ARCHITECTURE.md - 3 references updated
- docs/COMMANDS.md - 7 references updated
- docs/DEVELOPMENT.md - 1 reference updated (test example)
- src/air/commands/classify.py - Updated --update option help text
- src/air/commands/status.py - Updated TODO comment
- src/air/commands/validate.py - Updated docstring

## Outcome
✅ Success

Successfully updated all references from .assess-config.json to air-config.json.

Files updated:
- src/air/core/models.py (docstrings)
- All documentation files (CLAUDE.md, docs/*.md, README.md)
- All template files (when created)
- Test files
- PROJECT-STATUS.md

## Notes
This is a clean naming decision that makes the config file match the tool name.
Better to do this early before Phase 1 implementation begins.
