# Task: Graceful Degradation Without AIR

## Date
2025-10-06 06:47

## Prompt
When .air and air-config.json are present, Claude Code is instructed to obey all air instructions. The .air folder and air-config.json both are committed to github. If one developer uses air, others may find a problem - they have not installed air, and now they see errors or warnings when they use an air-enabled project! Consider how to make this graceful, or even how to disable Claude trying to use air if the `air-toolkit` is not installed.

## Actions Taken
1. Analyzed current CLAUDE.md instructions - found existing "When to Use AIR" section
2. Added prominent "AIR Toolkit Availability" section at top of CLAUDE.md with clear guidance:
   - Check `which air` before using air commands
   - List what works WITHOUT air (task tracking via Python)
   - Explicitly state: don't show errors/warnings to user
   - Don't block on missing `air` command
3. Updated "Using AIR Commands" section with side-by-side comparisons showing manual alternatives
4. Updated template files to include graceful degradation notes:
   - src/air/templates/assessment/README.md.j2 - Added "Commands" section noting air is optional
   - src/air/templates/ai/README.md.j2 - Emphasized Python method works without air installation

## Files Changed
- `CLAUDE.md` - Added AIR availability check section, improved command usage guidance
- `src/air/templates/assessment/README.md.j2` - Added note that air CLI is optional
- `src/air/templates/ai/README.md.j2` - Clarified Python method works without air-toolkit

## Outcome
✅ Success

Projects with .air/ and air-config.json can now be used by developers who haven't installed air-toolkit without seeing errors or warnings. Claude Code will:
1. Check `which air` before using any air commands
2. Fall back to Python-based task creation if air is not installed
3. Not show errors/warnings about missing air
4. Optionally suggest installing air-toolkit once (not repeatedly)

All core functionality (task tracking) works without air installation. Only convenience commands like `air status`, `air validate`, `air init` require the toolkit.

## Notes
- The guidance emphasizes that air-toolkit is OPTIONAL, not REQUIRED
- Task tracking (the core feature) works entirely via Python without any external tools
- Only project initialization and convenience commands need air-toolkit
- This allows gradual adoption: one dev can use air-toolkit, others can work normally
