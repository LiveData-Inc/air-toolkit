# AIR Toolkit - Graceful Degradation Guide

**Version:** 0.6.3
**Last Updated:** 2025-10-05

## Problem Statement

When a project uses AIR (`.air/` directory and `air-config.json` are committed), developers who clone the repository may not have `air-toolkit` installed. This can lead to:

1. **Claude Code errors** - When trying to execute `air` commands mentioned in `CLAUDE.md`
2. **Confusion** - Developers unsure if AIR is required
3. **Broken workflows** - Commands that fail without clear guidance

## Solution: Multi-Layer Graceful Degradation

AIR implements graceful degradation at multiple levels to ensure smooth developer experience regardless of installation status.

### Layer 1: CLAUDE.md Instructions

The generated `CLAUDE.md` file (committed with projects) includes:

```markdown
## Using AIR Commands (When Available)

**ALWAYS check if air is available first:**
```bash
which air  # Check if installed
```

**If air is installed, use it for:**
- Task tracking, validation, analysis, etc.

**If air is NOT installed:**
- Continue with manual Python task file creation
- Mention to user: "💡 Tip: Install air-toolkit: `pip install air-toolkit`"
- Don't let missing tool block progress
```

**Key Principle:** Claude Code checks for `air` installation before using it, and has fallback instructions.

### Layer 2: README Documentation

Both `.air/README.md` and project `README.md` clearly state:

```markdown
## ⚠️ Important: AIR Toolkit is Optional

This project uses AIR for AI-assisted development tracking.
**You do NOT need to install `air-toolkit` to work on this project.**

- **With air-toolkit**: Streamlined `air` commands
- **Without air-toolkit**: Python scripts or manual task creation
- **Claude Code**: Automatically adapts based on installation
```

### Layer 3: Manual Fallback Methods

The `.air/README.md` provides complete manual alternatives:

**Creating Task Files Manually:**
```python
from datetime import datetime
from pathlib import Path

timestamp = datetime.now().strftime("%Y%m%d-%H%M")
description = "task-description"
filename = f".air/tasks/{timestamp}-{description}.md"

content = """# Task: Task Description
## Date
2025-10-05 14:30

## Prompt
[User's request]

## Actions Taken
1. [Action 1]

## Files Changed
- file.py - What changed

## Outcome
⏳ In Progress

## Notes
"""

Path(filename).write_text(content)
```

**Viewing Project Status Manually:**
```bash
# Instead of: air status
cat air-config.json | python -m json.tool

# Instead of: air task list
ls -lt .air/tasks/
```

### Layer 4: No Hard Dependencies

**AIR never blocks workflows:**
- `.air/` directory structure works standalone
- `air-config.json` is just a JSON file
- Task files are plain markdown
- No proprietary formats or lock-in

## Developer Experience Examples

### Scenario 1: Developer Without AIR (Happy Path)

```bash
# Clone project
git clone https://github.com/example/my-project.git
cd my-project

# See .air/ directory and air-config.json
ls -la

# Read .air/README.md
# Sees: "⚠️ AIR Toolkit is Optional"
# Understands: Can work without installing anything

# Create task manually (if using Claude Code)
python -c "from pathlib import Path; from datetime import datetime; ..."

# Continue normal development
git add .
git commit -m "feat: add feature"
```

**Result:** ✅ No errors, no confusion, smooth workflow

### Scenario 2: Developer Wants AIR Features

```bash
# Read README, decides to install
pip install air-toolkit

# Verify
air --version
# AIR Toolkit v0.6.3

# Use enhanced commands
air task new "implement feature X"
air analyze --all
air findings --all --html
```

**Result:** ✅ Enhanced productivity with optional tool

### Scenario 3: Claude Code Usage

**Without AIR:**
```
Claude: Let me check if air is installed...
Claude: $ which air
Claude: (not found) I'll create the task file manually using Python
Claude: [creates .air/tasks/20251005-1430-description.md]
Claude: ℹ️ Tip: Install air-toolkit for streamlined workflow: pip install air-toolkit
```

**With AIR:**
```
Claude: Let me check if air is installed...
Claude: $ which air
Claude: /usr/local/bin/air
Claude: $ air task new "description"
Claude: ✅ Created task: .air/tasks/20251005-1430-description.md
```

**Result:** ✅ Claude adapts seamlessly

## Best Practices for Project Maintainers

### 1. Document AIR as Optional in README

```markdown
## Development Setup

### Optional: AIR Toolkit

This project uses AIR for AI-assisted development tracking (optional).

```bash
# Install if you want enhanced workflow
pip install air-toolkit
```

See `.air/README.md` for manual alternatives.
```

### 2. Don't Mention AIR in Required Steps

❌ **Bad:** "Install dependencies: `npm install && pip install air-toolkit`"
✅ **Good:** "Install dependencies: `npm install`" (AIR in optional section)

### 3. Provide .gitignore for Local AIR Data (If Needed)

Some teams may want local-only AIR usage:

```bash
# .gitignore
.air/agents/          # Local agent metadata
.air/shared/          # Local shared state
```

Commit: `.air/tasks/`, `.air/context/`, `air-config.json`

### 4. Update CLAUDE.md for Team Preferences

If your team prefers not to use AIR commands:

```markdown
## Task Tracking

This project uses manual task files in `.air/tasks/`.
**Do not use `air` commands - use the Python examples below.**
```

## Technical Implementation

### Detection in CLAUDE.md

```bash
# ALWAYS check first
which air || echo "air not installed"
```

### Fallback in Python

```python
import subprocess

def is_air_installed():
    try:
        subprocess.run(["air", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

if is_air_installed():
    # Use air command
    subprocess.run(["air", "task", "new", "description"])
else:
    # Manual fallback
    create_task_manually("description")
```

## Testing Graceful Degradation

### Test Without AIR

```bash
# Create fresh virtualenv
python -m venv test-env
source test-env/bin/activate

# Verify air not installed
which air  # Should fail

# Clone/create AIR project
air init my-project  # Won't work, that's the point

# Verify documentation is clear
cat my-project/.air/README.md
# Should see: "⚠️ AIR Toolkit is Optional"

# Test manual workflow
cd my-project
python -c "..." # Create task manually
# Should work fine
```

### Test With AIR

```bash
pip install air-toolkit
air init my-project
cd my-project
air task new "test"
air task list
# Should work smoothly
```

## FAQ

**Q: Why commit `.air/` if AIR is optional?**
A: Task files provide valuable project history. They work as plain markdown even without AIR.

**Q: Can I use AIR privately without committing?**
A: Yes! Add `.air/` to `.gitignore` for local-only usage.

**Q: What if team doesn't want AIR at all?**
A: Don't run `air init`. The `.air/` directory is only created when you choose to use AIR.

**Q: Will Claude Code break without AIR?**
A: No. CLAUDE.md instructs Claude to check for AIR and use fallbacks.

**Q: Can I mix - some devs use AIR, others don't?**
A: Yes! That's the entire point of graceful degradation. Both workflows coexist.

## Summary

AIR is designed as an **optional enhancement**, not a required dependency. Every feature has a manual alternative, and documentation makes this clear at multiple levels. Developers can clone any AIR-enabled project and work productively without ever installing `air-toolkit`.

**Core Principle:** AIR enhances workflows when present, but never blocks them when absent.
