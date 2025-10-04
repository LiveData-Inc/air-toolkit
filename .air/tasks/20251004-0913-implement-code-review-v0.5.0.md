# Task: Implement Code Review (v0.5.0)

## Date
2025-10-04 09:13

## Prompt
User: "Task: proceed with implementing code review."

## Plan

Implementing **Option A: Quick Win Path** from architecture review.

### Week 1: Foundation (Current)
1. Create `.claude/commands/` directory structure
2. Implement `air review` command
3. Implement `air claude` subcommands
4. Create slash commands for Claude Code
5. Basic testing

### Week 2-3: Polish & Release
- User testing with real projects
- Documentation and examples
- Bug fixes and improvements
- Release as v0.5.0

## Goals

**v0.5.0 Deliverables:**
- ✅ `air review` - Generate review context from git changes
- ✅ `air claude context` - Get project context for AI
- ✅ `/air-review` - Claude Code slash command for code review
- ✅ `/air-begin` - Start AIR-tracked work
- ✅ `/air-done` - Complete and commit work
- ✅ Tests and documentation

**Success Metrics:**
- Review completes in < 2 minutes
- Finds actionable issues
- Works with any git repository
- Seamless Claude Code integration

## Actions Taken

[Work in progress - will update as implementation proceeds]

## Files Changed

[Will be populated during implementation]

## Outcome
⏳ In Progress

Implementing code review capability for v0.5.0.

## Notes

Following the architecture from `docs/CODE-REVIEW.md`.

Starting with shell-based approach (no MCP server yet) for fastest time to value.
