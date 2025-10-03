# AIR as a Claude Code Tool - Design Document

**Version:** 0.1.0
**Date:** 2025-10-03
**Status:** Finalized

## Overview

This document defines how AIR is designed to work as a first-class tool for Claude Code and other AI assistants, similar to how they use bash, git, and other CLI tools.

## Core Design Principle

**AIR should be discoverable, usable, and helpful to AI agents with zero manual configuration.**

## Design Decisions

### 1. Configuration File Naming

**Decision:** Use `air-config.json` (not `.assess-config.json`)

**Rationale:**
- Cleaner, matches tool name
- Easier to discover and understand purpose
- Consistent with tool branding

### 2. Machine-Readable Output

**Decision:** All commands support `--format=json` option

**Implementation:**
```bash
# Default: Rich human output
air status
# ✅ Project: my-review
# 📊 Mode: mixed

# Machine-readable: JSON
air status --format=json
# {"name":"my-review","mode":"mixed","resources":{"review":3,"collaborate":2}}
```

**Benefits:**
- AI can parse and act on results
- Enables programmatic decision-making
- Maintains human-friendly default experience

**Requirements:**
- Consistent JSON schema across commands
- Document schema in command help
- Include schema files in future releases

### 3. Task File Creation Strategy

**Decision:** Support both direct Python (for AI) and CLI command (for humans)

**For AI Agents (Option B - Direct Python):**
```python
from datetime import datetime, timezone
from pathlib import Path

timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
description = "task-description"
filename = f".air/tasks/{timestamp}-{description}.md"
Path(filename).write_text(content)
```

**For Human Users:**
```bash
air task new "implement feature X"
# Creates: .air/tasks/20251003-1200-implement-feature-x.md
```

**Rationale:**
- Zero friction for AI: no subprocess overhead
- Direct file creation is faster and simpler
- CLI command provides better UX for humans
- Both methods produce identical results

### 4. CLAUDE.md Instructions Style

**Decision:** Active/explicit instructions (not passive documentation)

**Implementation:**

✅ **Do this:**
```markdown
## When to Use AIR

ALWAYS check if air is available first:
```bash
which air
```

If air is installed, use it for:
1. Before starting work: `air status`
2. When validating: `air validate --format=json`
```

❌ **Not this:**
```markdown
## Available Commands
- air status - Show project status
- air validate - Validate structure
```

**Rationale:**
- AI agents follow explicit instructions better
- Clear triggers ("ALWAYS", "WHEN") > vague documentation
- Reduces ambiguity in AI decision-making

### 5. Error Handling and Availability

**Decision:** Graceful degradation with helpful hints

**When air IS installed:**
```bash
air status
# Error: Not an AIR project
# 💡 Hint: Run 'air init' to create a new project
```

**When air is NOT installed:**
- AI continues with manual methods (Python direct task creation)
- AI mentions to user: "💡 Tip: Install air-toolkit for streamlined workflow: `pip install air-toolkit`"
- Never block progress due to missing tool

**Implementation:**
```python
# All error messages include actionable hints
def handle_error(msg: str, hint: str | None = None) -> None:
    console.print(f"[red]✗[/red] {msg}")
    if hint:
        console.print(f"[dim]💡 Hint: {hint}[/dim]")
    sys.exit(1)
```

### 6. Auto-Detection

**Decision:** Detect AIR projects automatically, use air when available

**Detection Methods:**
1. Check for `air-config.json` in current/parent directories
2. Check for `.air/` directory structure
3. Check if `air` command is available: `which air`

**AI Behavior:**
```python
# Pseudo-code for AI decision making
if air_project_detected():
    if air_command_available():
        # Use air commands
        result = run_bash("air status --format=json")
    else:
        # Manual methods + hint
        create_task_directly()
        hint_user_about_air()
else:
    # Not an AIR project, proceed normally
    pass
```

## Implementation Requirements

### For All Commands

1. **JSON Output Support:**
   - Add `--format=json` option to every command
   - Consistent schema: `{"success": bool, "data": {}, "error": str | null}`
   - Document schema in `--help`

2. **Exit Codes:**
   - `0`: Success
   - `1`: User/business error
   - `2`: System error
   - `3`: Validation failure (air validate only)

3. **Help Text:**
   - Include examples
   - Reference related commands
   - Show both human and JSON output formats

4. **Error Messages:**
   - Clear, actionable errors
   - Always include hint when possible
   - Reference help: "Try: air <command> --help"

### For CLAUDE.md Files

1. **Structure:**
   - Task tracking protocol (existing)
   - AIR command usage (new)
   - Project-specific context
   - When to use what

2. **Tone:**
   - Explicit: "ALWAYS do X before Y"
   - Conditional: "IF air installed, use it for Z"
   - Helpful: Include installation hints

3. **Examples:**
   - Show exact commands to run
   - Include expected output
   - Demonstrate `--format=json` usage

## Success Criteria

✅ AI agents can:
1. Detect AIR projects automatically
2. Check if air is installed
3. Use air commands when available
4. Parse JSON output for decision-making
5. Fall back gracefully when air not available
6. Provide helpful hints to users

✅ Human users get:
1. Rich, colorful terminal output by default
2. Helpful error messages with suggestions
3. Comprehensive help text with examples
4. Optional JSON output when needed

## Examples

### Example 1: AI Detects AIR Project

```bash
# AI checks context
ls -la
# Sees: air-config.json, .air/

# AI checks availability
which air
# Returns: /usr/local/bin/air

# AI uses air
air status --format=json
# {"name":"my-review","mode":"mixed","resources":{"review":2}}

# AI makes decision based on result
# "I see this is a review-mode AIR project with 2 review resources..."
```

### Example 2: AIR Not Installed

```python
# AI checks
run_bash("which air")
# Returns: (exit code 1)

# AI proceeds manually
from pathlib import Path
from datetime import datetime, timezone

# Create task file directly
timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")
Path(f".air/tasks/{timestamp}-review-services.md").write_text(content)

# AI hints to user
print("💡 Tip: Install air-toolkit for enhanced workflow: pip install air-toolkit")
```

### Example 3: Error with Hint

```bash
$ air validate
✗ Not an AIR project (missing air-config.json)
💡 Hint: Run 'air init' to create a new AIR project

$ echo $?
1
```

## Future Enhancements

1. **Schema Files:** Publish JSON schemas for all command outputs
2. **Bash Completion:** Enable tab-completion for better discoverability
3. **Plugin System:** Allow custom commands and validators
4. **Config Inheritance:** Global → project config merging
5. **Auto-Update:** Check for updates and notify

## References

- [AIR Toolkit Architecture](./ARCHITECTURE.md)
- [AI Integration Guide](./AI-INTEGRATION.md)
- [Commands Reference](./COMMANDS.md)
- [CLAUDE.md Template](../CLAUDE.md)
