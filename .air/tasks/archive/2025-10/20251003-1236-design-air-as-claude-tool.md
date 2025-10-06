# Task: Design AIR as a First-Class Claude Code Tool

## Date
2025-10-03 12:36 UTC

## Prompt
Let'''s review how to design this so that Claude code will use `air` as a tool, similar to how it uses `Bash`.

## Actions Taken
1. Starting design discussion for AI-native CLI interface

## Files Changed
- None yet (design phase)

## Outcome
✅ Success

Design finalized with 6 key decisions for making AIR a first-class Claude Code tool.

## Notes
## Design Principles Identified

1. **Auto-Discovery**: Claude should detect AIR projects by presence of air-config.json or .air/ directory
2. **Machine-Readable Output**: All commands need --format=json option for AI parsing
3. **Idempotent Commands**: Safe to run repeatedly (validate, status are read-only)
4. **Self-Documenting**: Rich --help with examples and related commands
5. **Explicit Integration**: CLAUDE.md should give explicit "WHEN to use" instructions
6. **Error Messages**: Include fix suggestions ("Hint: Run air init")
7. **Task File Automation**: Claude can use Python directly or air task new command

## Final Design Decisions

1. **Config filename**: ✅ air-config.json (not .assess-config.json)
   - Cleaner, matches tool name

2. **JSON Output**: ✅ All commands support --format=json
   - Enables AI parsing of command results
   - Default: Rich human output
   - --format=json: Structured data for AI

3. **Task Creation**: ✅ Option B (Python direct) + air task new for humans
   - Claude uses Python directly: Path(f".air/tasks/{timestamp}-desc.md").write_text(content)
   - Faster, zero friction, no subprocess overhead
   - Provide air task new command for human users

4. **CLAUDE.md Style**: ✅ Active/explicit instructions
   - Tell Claude WHEN to use commands: "REQUIRED: Before ANY code changes, run air task new"
   - Explicit triggers work better than passive documentation
   - Clear, prescriptive guidance

5. **Error Handling**: ✅ Use air if available, hint about installing otherwise
   - Commands detect if air is installed
   - Errors include installation hints: "💡 Install: pip install air-toolkit"
   - Graceful degradation when air not available

6. **Auto-Detection**: ✅ Check for air availability
   - Detect air-config.json or .air/ directory
   - If air installed: use it automatically
   - If not installed: include hint in error messages

