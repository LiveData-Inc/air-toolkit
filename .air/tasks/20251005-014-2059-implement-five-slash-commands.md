# Task: Implement Five New Slash Commands

## Date
2025-10-05 20:59

## Prompt
User: "yes. implement all, and update all documentation"

## Goal
Implement 5 new Claude Code slash commands for frequently-used AIR operations:
1. /air-analyze - Quick code analysis (air analyze --all)
2. /air-validate - Check project health (air validate --fix)
3. /air-status - Show project overview (air status --format=json)
4. /air-findings - View analysis results (air findings --all --html)
5. /air-summary - Generate work summary (air summary --format=json)

## Actions Taken
1. ✅ Create task file for tracking
2. ✅ Create .claude/commands/air-analyze.md
3. ✅ Create .claude/commands/air-validate.md
4. ✅ Create .claude/commands/air-status.md
5. ✅ Create .claude/commands/air-findings.md
6. ✅ Create .claude/commands/air-summary.md
7. ✅ Update documentation (README.md, QUICKSTART.md, docs/COMMANDS.md, PROJECT-STATUS.md)

## Files Changed
- `.air/tasks/{timestamp}-implement-five-slash-commands.md` - This task file
- `.claude/commands/air-analyze.md` - Comprehensive analysis slash command
- `.claude/commands/air-validate.md` - Validation slash command
- `.claude/commands/air-status.md` - Status slash command
- `.claude/commands/air-findings.md` - Findings report slash command
- `.claude/commands/air-summary.md` - Summary slash command
- `README.md` - Added Claude Code Integration section
- `QUICKSTART.md` - Added slash commands with examples
- `docs/COMMANDS.md` - Added dedicated section with comparison table
- `PROJECT-STATUS.md` - Updated to list all 9 slash commands

## Outcome
✅ Success

Created 5 new Claude Code slash commands and updated all documentation:

**New Slash Commands:**
1. /air-analyze - Run comprehensive analysis (air analyze --all)
2. /air-validate - Validate and auto-fix project (air validate --fix)
3. /air-status - Get project status (air status --format=json)
4. /air-findings - Generate HTML findings report (air findings --all --html)
5. /air-summary - Generate work summary (air summary --format=json)

**Documentation Updated:**
- README.md - Added Claude Code Integration section
- QUICKSTART.md - Added slash commands with usage examples
- docs/COMMANDS.md - Added dedicated slash commands section with table
- PROJECT-STATUS.md - Updated to show all 9 slash commands

All slash commands are clearly marked as Claude Code-specific.

## Notes
These commands cover the most common workflow operations:
- /air-analyze: Start comprehensive analysis
- /air-validate: Health check + auto-fix
- /air-status: Get project state for AI
- /air-findings: View analysis results
- /air-summary: End-of-session summary
