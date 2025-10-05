# Task: Resource classification v0.3.0

**Created:** 2025-10-04 01:51 UTC

## Prompt

Implement air classify command to auto-classify linked resources by analyzing repository structure, detecting frameworks/languages, and suggesting appropriate resource types.

## Actions Taken

- Created task file for v0.3.0 work
- Designed classification algorithm with pattern matching
- Implemented air.services.classifier module with:
  - Language detection (Python, JS, TS, Go, Rust, Java, Ruby, PHP, C#, Swift, Kotlin)
  - Framework detection (Django, Flask, FastAPI, React, Vue, Angular, Next.js, Express, Rails, Spring)
  - Resource type classification with confidence scores
  - Smart library detection (vs applications)
- Implemented air classify command with:
  - Verbose mode (--verbose) showing detection details
  - Update mode (--update) to save to config
  - JSON output format (--format=json)
  - Specific resource classification by name
- Wrote 24 unit tests covering all detection scenarios
- Wrote 8 integration tests for command functionality
- All 237 tests passing ✅
- Updated CHANGELOG.md for v0.3.0
- Version bumped to 0.3.0 in pyproject.toml

## Files Changed

- src/air/commands/classify.py (implemented)
- src/air/services/classifier.py (new - 300+ lines)
- tests/unit/test_classifier.py (new - 24 tests)
- tests/integration/test_commands.py (added 8 tests)
- CHANGELOG.md (v0.3.0 release notes)
- pyproject.toml (version 0.3.0)

## Outcome

✅ Success

## Notes

**Completed:** Successfully implemented v0.3.0 resource classification feature

Delivered features:
- Automatic resource classification by analyzing repository structure
- Detects 11 programming languages
- Detects 10 major frameworks
- 4 resource types: implementation, documentation, library, service
- Confidence scoring (0.0 to 1.0)
- Verbose output with reasoning
- Config update capability
- Full test coverage: 237 tests passing (was 205, added 32)

Classification algorithm:
- File pattern matching for languages/frameworks
- Weighted scoring based on file counts
- Documentation ratio > 70% → documentation type
- Service indicators (Docker, K8s) + code → service type
- Library detection (package files, no main entry point) → library type
- Default → implementation type

Example usage:
```bash
air classify                  # Classify all resources
air classify myapp            # Classify specific resource
air classify --verbose        # Show detection details
air classify --update         # Update air-config.json
air classify --format=json    # JSON output
```
