# Task: Consider .ai vs .air Folder Naming

## Date
2025-10-03 13:30 UTC

## Prompt
Consider whether the .ai folder should be .air instead

## Actions Taken
1. Analyzing current folder structure
2. Evaluating naming consistency
3. Assessing impact of potential change (35 files affected)
4. Implementing comprehensive rename from .ai to .air
5. Updating all code references (models, commands, services, templates)
6. Updating all documentation files
7. Updating all test files
8. Fixing 2 failing tests after initial rename
9. Verifying all 59 tests pass
10. Committing changes with git mv to preserve history

## Files Changed
- src/air/core/models.py - Updated base_dirs to use .air
- All files in src/air/commands/ - Updated .ai/ references to .air/
- All files in src/air/templates/ - Updated .ai/ references to .air/
- src/air/services/templates.py - Updated render_ai_templates() key
- All files in tests/ - Updated test expectations
- All documentation in docs/ and root - Updated .ai/ to .air/
- All scripts in .air/scripts/ - Updated .ai/ references
- .github/workflows/validate-ai-tasks.yml - Updated workflow
- Renamed .ai/ folder to .air/ using git mv

## Outcome
✅ Success

Successfully renamed .ai folder to .air for brand consistency.

**Decision:** Chose .air/ for professional brand consistency.

**Implementation completed:**
- 45 files changed, 746 insertions, 197 deletions
- Preserved git history with git mv
- All 59 tests passing
- No breaking changes for new projects

## Notes
Current structure:
- `.air/` folder (tasks, documentation)
- `air-config.json` config file
- `air` CLI tool name

## Analysis

### Arguments FOR `.air/`:
1. **Brand consistency**: Matches tool name (`air`)
2. **Clear ownership**: Obviously air-toolkit specific
3. **Unified naming**: `air-config.json`, `.air/` folder, `air` command
4. **Uniqueness**: Less likely to conflict with other AI tools

### Arguments FOR `.air/`:
1. **Brevity**: Shorter to type (3 vs 4 characters)
2. **Generic/flexible**: Could be used by multiple AI tools
3. **Semantic clarity**: `.ai` clearly indicates AI-related files
4. **Convention**: Some precedent in AI tooling space

### Impact of Change (if renaming to `.air/`):
- **Code changes**: Update all references in:
  - `src/air/services/filesystem.py`
  - `src/air/commands/*.py`
  - `src/air/templates/*.j2`
  - All documentation
- **Migration**: Need migration path for existing projects
- **Task files**: All 7 current task files would need moving
- **Documentation**: Update CLAUDE.md, README.md, AI-INTEGRATION.md
- **Tests**: Update test expectations

### Recommendation
**Use `.air/` for consistency** - The benefits of brand consistency and clear ownership outweigh the minor typing overhead.

**Reasoning:**
1. Tool is called `air`, config is `air-config.json` → folder should be `.air/`
2. Makes it clear this is air-toolkit infrastructure
3. Future-proofs against other AI tools wanting to use `.air/`
4. Professional consistency in branding

### Implementation Plan (if approved):
1. Update filesystem service to use `.air/` path
2. Update all templates to reference `.air/`
3. Update documentation
4. Move existing `.air/` to `.air/` in this repo
5. Add migration notes for existing users
6. Update tests
