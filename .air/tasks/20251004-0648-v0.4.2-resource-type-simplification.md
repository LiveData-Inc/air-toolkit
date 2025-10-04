# Task: v0.4.2 - Resource Type Simplification and Technology Stack

## Date
2025-10-04 06:48

## Prompt
User: "let's replace implementation with library. We should also give some thought about a second dimension of classification (e.g. a webapp, but also it is a React/Typescript, or a service, but also a it is a Python/FastAPI)"

Follow-ups:
- "this goal suggests that classification is opt-out! 0.4 is already a set of breaking changes, so we can continue here with 0.4.2 as the version."
- "note that classification may sometimes find multiple projects in a linked repo - if so, the result should be 'mixed' or something similar" (noted for future v0.4.3+)

## Actions Taken

1. **Resource Type Simplification**
   - Removed `IMPLEMENTATION` from ResourceType enum
   - Kept only: `LIBRARY`, `DOCUMENTATION`, `SERVICE`
   - Updated all code to use `LIBRARY` as default for code repositories
   - Reasoning: "implementation" was vague; "library" is clearer for any code repo

2. **Added Technology Stack Field**
   - Added `technology_stack: str | None` to Resource model
   - Captures language + framework combination
   - Examples: "Python/FastAPI", "TypeScript/React", "Go", "Rust"
   - Created helper function `_generate_technology_stack()` in classifier

3. **Updated Classifier**
   - Modified ClassificationResult to include `technology_stack`
   - Updated all classification returns to populate tech stack
   - Logic: primary_language/primary_framework format
   - Falls back to just language or just framework if one is missing

4. **Changed Classification to Opt-Out**
   - Changed interactive prompt default from `False` to `True`
   - Auto-classification now happens by default
   - Users can still skip if desired
   - Non-interactive mode doesn't auto-classify (sets technology_stack=None)

5. **Updated Link Command**
   - Changed default type from "implementation" to "library"
   - Updated --type choices to ["library", "documentation", "service"]
   - Display technology_stack in confirmation panel
   - Store technology_stack in Resource creation
   - Updated docstring and examples

6. **Test Updates**
   - Updated all tests using IMPLEMENTATION → LIBRARY
   - Updated integration tests with --type=implementation → --type=library
   - Fixed classifier tests for new behavior
   - Fixed model tests
   - All 318 tests passing ✅

7. **Documentation Updates**
   - COMMANDS.md: Updated resource types and defaults
   - ARCHITECTURE.md: Fixed ResourceType enum
   - SPECIFICATION.md: Updated examples and version to 0.4.2
   - Updated CHANGELOG with v0.4.2 entry

8. **Version Updates**
   - pyproject.toml: 0.4.1 → 0.4.2
   - src/air/__init__.py: 0.4.1 → 0.4.2
   - docs/SPECIFICATION.md: 0.4.1 → 0.4.2

## Files Changed

- `src/air/core/models.py` - Removed IMPLEMENTATION, added technology_stack field to Resource
- `src/air/services/classifier.py` - Added technology_stack to ClassificationResult, added _generate_technology_stack()
- `src/air/commands/link.py` - Updated defaults, interactive prompt, resource creation
- `src/air/commands/classify.py` - Updated docstring for new types
- `tests/integration/test_commands.py` - Updated all --type=implementation to --type=library
- `tests/unit/test_classifier.py` - Updated tests for LIBRARY default
- `tests/unit/test_models.py` - Updated ResourceType.IMPLEMENTATION → ResourceType.LIBRARY
- `tests/unit/test_link.py` - Updated ResourceType references
- `docs/COMMANDS.md` - Updated resource types throughout
- `docs/ARCHITECTURE.md` - Fixed ResourceType enum
- `docs/SPECIFICATION.md` - Updated examples and version
- `CHANGELOG.md` - Added v0.4.2 section
- `pyproject.toml` - Version 0.4.2
- `src/air/__init__.py` - Version 0.4.2

## Outcome
✅ Success

Successfully implemented v0.4.2 with:

**Breaking Changes:**
- `implementation` → `library` (resource type rename)
- Simplified to 3 types: library, documentation, service
- All code repos now classified as library

**New Features:**
- `technology_stack` field on all resources
- Auto-populated during classification
- Displayed in interactive UI
- Stored in air-config.json

**Behavior Changes:**
- Auto-classification now opt-out (defaults to YES)
- Default type changed to "library"
- Classifier returns tech stack information

**Testing:**
- All 318 tests passing ✅
- Complete test coverage for new features

**Commit:**
- feat: v0.4.2 - Resource type simplification and technology stack (3998914)

## Notes

### Design Decisions

1. **Why Remove "Implementation":**
   - Too vague - what's an "implementation"?
   - "Library" is more precise and intuitive
   - Everything code-based is a library (can be imported/used)
   - Services are libraries with deployment infrastructure

2. **Technology Stack Format:**
   - Format: `"Language/Framework"` (e.g., "Python/FastAPI")
   - Falls back to language only if no framework
   - Falls back to framework only if no language
   - Returns None if neither detected
   - Displayed alongside type: "library (Python/Django)"

3. **Opt-Out vs Opt-In Classification:**
   - User feedback: "this goal suggests that classification is opt-out!"
   - Makes sense: if we're capturing tech stack, we need to classify
   - Default to YES provides better UX
   - Still allows users to skip if desired

4. **Classification Logic:**
   - Library: Default for all code repos
   - Service: Code repo + deployment configs (Docker, k8s, etc.)
   - Documentation: >70% doc files
   - Tech stack populated for all types

### Future Enhancements (v0.4.3+)

From user feedback:
1. **Mixed Type for Monorepos:**
   - Detect multiple projects in one repo
   - Type: "mixed"
   - Tech stack: "React/TypeScript,Python/FastAPI" (comma-separated)

2. **Interactive UX Improvements:**
   - Path autocomplete
   - Up/down arrows for command history

### Migration Guide

For existing configs with `"type": "implementation"`:
- Manually change to `"type": "library"`
- System doesn't auto-migrate (would require reading/writing all configs)
- Consider it deprecated but may still work in some contexts

### Technical Details

**Technology Stack Detection:**
```python
def _generate_technology_stack(languages: list[str], frameworks: list[str]) -> str | None:
    primary_lang = languages[0].capitalize() if languages else None
    primary_framework = frameworks[0].capitalize() if frameworks else None

    if primary_lang and primary_framework:
        return f"{primary_lang}/{primary_framework}"
    elif primary_lang:
        return primary_lang
    elif primary_framework:
        return primary_framework
    return None
```

**Classification Flow:**
1. Detect languages (file extensions + package files)
2. Detect frameworks (package contents + config files)
3. Calculate doc/code/service scores
4. Determine type based on ratios
5. Generate technology_stack from detected lang/framework
6. Return ClassificationResult with both

**Resource Model:**
```python
class Resource(BaseModel):
    name: str
    path: str
    type: ResourceType  # library, documentation, service
    technology_stack: str | None  # "Python/FastAPI", etc.
    relationship: ResourceRelationship
    clone: bool = False
    ...
```
