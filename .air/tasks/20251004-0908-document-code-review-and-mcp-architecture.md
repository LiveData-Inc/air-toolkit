# Task: Document Code Review and MCP Architecture

## Date
2025-10-04 09:08

## Prompt
User: "Task: write an architectural description of these options in docs/"

Follow-up: "make a doc for code reviews and separate doc for claude MCP server"

Follow-up: "rename `REVIEW-ARCHITECTURE.md` to `CODE-REVIEW.md`"

Follow-up: "commit open changes"

Follow-up: "add the task file before commit"

## Actions Taken

1. **Created docs/CODE-REVIEW.md** (originally REVIEW-ARCHITECTURE.md, then renamed)
   - Comprehensive AI-powered code review architecture design
   - 5 implementation phases spanning 16 weeks
   - Covers local development reviews, multi-repo analysis, CI/CD integration
   - Complete with data flows, component diagrams, code examples
   - AIR review commands: `air review`, `air review-project`, `air review-gate`, `air claude`
   - Claude Code integration via slash commands
   - GitHub Actions workflow templates
   - Detailed output formats (markdown and JSON)
   - Success metrics and technical decisions
   - File size: 39KB

2. **Created docs/MCP-SERVER.md**
   - Model Context Protocol server architecture
   - Native Claude Code integration design (no shell parsing needed)
   - Complete tool specifications with TypeScript interfaces
   - Server implementation examples in Python using MCP SDK
   - Client configuration for Claude Desktop and VS Code
   - Resource providers and context injection
   - Performance considerations: caching, async, lazy loading
   - Security considerations: path validation, safe API handling
   - 4 implementation phases spanning 8 weeks
   - Migration path from shell commands to MCP
   - File size: 27KB

3. **Updated README.md**
   - Added references to new architecture documents (lines 155-156)
   - Links in documentation section
   - Marked as "(future)" to indicate design phase

4. **Fixed task file timestamps**
   - Renamed 3 task files from UTC to local time for proper chronological sorting
   - Updated Date fields inside renamed files
   - Updated CLAUDE.md to enforce local time usage (not UTC)

5. **Completed NAME:PATH format removal**
   - Updated 18 integration tests to use new positional PATH syntax
   - Removed 4 uses of deprecated `--path` option
   - Updated documentation: README.md, QUICKSTART.md, docs/ARCHITECTURE.md
   - All 325 tests passing ✅

6. **Created task file for NAME:PATH removal work**
   - `.air/tasks/20251004-0810-remove-deprecated-name-path-format.md`

7. **Committed all changes**
   - Commit: `feat: Complete v0.4.3 and add architecture docs`
   - 25 files changed (+3,270, -351)

## Files Changed

### New Architecture Documentation
- `docs/CODE-REVIEW.md` (new, 39KB)
  - Vision: Context-aware AI code reviews using AIR's multi-repo knowledge
  - Phase 1 (Weeks 1-3): Local development reviews
  - Phase 2 (Weeks 4-6): Multi-repository analysis
  - Phase 3 (Weeks 7-10): CI/CD pipeline integration
  - Phase 4 (Weeks 11-14): Advanced features (learning, checklists)
  - Phase 5 (Weeks 15-16): Tool integration (SonarQube, security scanners)
  - Complete API specifications and data flows
  - GitHub Actions workflow example
  - Success metrics and open questions

- `docs/MCP-SERVER.md` (new, 27KB)
  - MCP overview and benefits over shell commands
  - Architecture: server, tools, resources, prompts, context providers
  - Tool specifications: air__status, air__review, air__task_*, air__link_*, air__classify, air__validate
  - Server implementation using Python MCP SDK
  - Client configuration examples
  - Integration examples showing improved workflows
  - Performance: async operations, caching, lazy loading
  - Security: path validation, command injection prevention
  - Testing strategy
  - 4-phase implementation (8 weeks)
  - Migration strategy from shell to MCP

### README Updates
- `README.md` (lines 155-156)
  - Added: `[Code Review](docs/CODE-REVIEW.md) - AI-powered code review design (future)`
  - Added: `[MCP Server](docs/MCP-SERVER.md) - Model Context Protocol integration (future)`

### Task File Timestamp Fixes
- `.air/tasks/20251004-1001-v0.4.0-nomenclature-refactoring.md` → `20251004-0607-v0.4.0-nomenclature-refactoring.md`
- `.air/tasks/20251004-1430-implement-interactive-link-v0-4-1.md` → `20251004-0631-implement-interactive-link-v0-4-1.md`
- `.air/tasks/20251004-1500-v0.4.2-resource-type-simplification.md` → `20251004-0648-v0.4.2-resource-type-simplification.md`
- Updated Date fields from UTC to local time in all 3 files

### CLAUDE.md Updates
- `CLAUDE.md` (lines 70-74)
  - Changed from `datetime.now(timezone.utc)` to `datetime.now()`
  - Added comment: "IMPORTANT: Use LOCAL time, not UTC, for proper chronological sorting"

### NAME:PATH Format Removal
- `tests/integration/test_commands.py` (18 test updates)
  - Old: `runner.invoke(main, ["link", "add", f"name:{path}", "--review"])`
  - New: `runner.invoke(main, ["link", "add", str(path), "--name", "name", "--review"])`
  - Removed `--path` option (4 occurrences)

- `README.md` (line 181)
  - Updated command reference to show positional PATH

- `QUICKSTART.md` (lines 70-72, 303)
  - Updated examples and quick reference table

- `docs/ARCHITECTURE.md` (lines 257-265)
  - Removed obsolete `repos-to-link.txt` format section

### Other Changes (from v0.4.3 work)
- `src/air/utils/tables.py` (new)
  - Shared resource table rendering function
  - Used by both `air link list` and `air status`

- `tests/unit/test_validate.py` (new)
  - Tests for validate --fix functionality

- `src/air/commands/validate.py`
  - Added --fix option to recreate missing/broken symlinks

- `CHANGELOG.md`
  - Enhanced v0.4.3 entry with all improvements

## Outcome
✅ Success

Created comprehensive architecture documentation for two major future features:

**CODE-REVIEW.md:**
- AI-powered code reviews leveraging AIR's multi-repo context
- Progressive implementation: Local dev → Multi-repo → CI/CD → Advanced
- 16-week implementation plan
- Complete with examples, data flows, and API specifications

**MCP-SERVER.md:**
- Native Claude Code integration via Model Context Protocol
- Type-safe tool interfaces (no shell parsing)
- 8-week implementation plan
- Migration strategy from shell commands to MCP

Also completed v0.4.3 work:
- Fixed task file timestamp sorting issue
- Removed deprecated NAME:PATH format completely
- All 325 tests passing ✅

## Notes

### Design Document Status

Both CODE-REVIEW.md and MCP-SERVER.md are **design documents** for future work, not current implementation:

- **Purpose:** Define architecture before coding
- **Audience:** Developers, stakeholders, AI assistants
- **Next Steps:** Review → Prioritize → Create issues → Implement

### Key Architectural Decisions

**Code Review (shell-first approach):**
1. Start with shell commands for immediate compatibility
2. Works with any AI assistant that can run bash
3. Progressive enhancement: local → CI/CD → advanced
4. Context-aware: uses AIR's linked resources for pattern comparison

**MCP Server (future native integration):**
1. Type-safe interfaces vs text parsing
2. Better performance (no shell overhead)
3. Richer error handling
4. Seamless Claude Code integration

**Integration Strategy:**
```
Phase 1-3: Shell-based reviews
  air review --format=json | claude run /air-review

Phase 4+: Native MCP tools
  review_result = await air__review(pr=true, base="main")
```

### Documentation Quality

Both documents include:
- Clear vision and benefits
- Component architecture diagrams (ASCII art)
- Complete API specifications with types
- Implementation phases with timelines
- Code examples in Python, TypeScript, YAML
- Success metrics for measuring effectiveness
- Open questions needing discussion
- References to related documentation

### Task File Timestamp Fix

**Problem:** Task files mixed UTC and local time, breaking chronological sort

**Solution:**
- Standardized on local time (not UTC)
- Renamed affected files
- Updated CLAUDE.md to prevent future UTC usage
- Now all Oct 4 files sort correctly: 0607 → 0631 → 0648 → 0707 → 0810

### Test Coverage

All 325 tests passing after NAME:PATH removal:
- Updated 18 integration tests
- Updated 7 link command tests
- Removed deprecated NAME:PATH format test
- All tests now use clean positional PATH syntax

### Commit Structure

Single commit captures all related work:
- v0.4.3 completion (timestamps, NAME:PATH removal, tests)
- Architecture documentation (CODE-REVIEW.md, MCP-SERVER.md)
- Supporting changes (tables.py, validate tests)

### Future Work

**Immediate (v0.4.4):**
- This task file
- Any remaining documentation updates

**Short-term (v0.5.0):**
- Begin Code Review Phase 1: Local development reviews
- Implement `air review` command
- Create slash commands for Claude Code

**Mid-term (v0.6.0):**
- Begin MCP Server Phase 1: Core server implementation
- Implement basic tools: status, task management
- Test with Claude Desktop

**Long-term:**
- Complete all review phases (16 weeks)
- Complete all MCP phases (8 weeks)
- Unified AI-assisted development workflow
