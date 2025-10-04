# Task: Enhance analysis depth

## Date
2025-10-04 17:30

## Prompt
User: "improve analysis depth"

Context: Current analysis only does basic classification (tech stack, languages, frameworks). User wanted deeper, more useful analysis.

## Actions Taken

1. Created modular analyzer system
   - src/air/services/analyzers/__init__.py - Package exports
   - src/air/services/analyzers/base.py - Base analyzer interface and data structures
   - Introduced Finding, FindingSeverity, AnalyzerResult, BaseAnalyzer

2. Implemented 4 specialized analyzers:
   - **CodeStructureAnalyzer** - Repository structure and metrics
     - Counts files, lines of code
     - Detects large files (>500 lines)
     - Checks for test/docs directories

   - **SecurityAnalyzer** - Security issue detection
     - Hardcoded secrets/API keys
     - SQL injection risks
     - Weak cryptography (MD5, SHA1, DES)
     - eval/exec usage
     - Debug mode enabled
     - Insecure deserialization
     - Shell injection risks
     - Missing security headers
     - Config files not in .gitignore

   - **ArchitectureAnalyzer** - Architecture and dependencies
     - Dependency analysis (pinned vs unpinned)
     - Circular import detection
     - Architectural pattern detection (API, models, services)

   - **QualityAnalyzer** - Code quality issues
     - Long functions (>100 lines)
     - Too many parameters (>5)
     - Excessive comments
     - Missing docstrings
     - Missing README
     - Low test coverage (heuristic)

3. Integrated analyzers into analyze command
   - Modified src/air/commands/analyze.py
   - Focus flag determines which analyzers run:
     - `--focus=security` → SecurityAnalyzer only
     - `--focus=architecture` → ArchitectureAnalyzer only
     - `--focus=quality` → QualityAnalyzer only
     - No focus → All analyzers run
   - Findings aggregated and saved to JSON
   - Summary statistics displayed to user

4. Added comprehensive tests
   - tests/unit/test_analyzers.py (14 new tests)
   - Tests for each analyzer type
   - Integration test running all analyzers
   - All 370 tests passing ✅

## Files Changed

### New Files Created:
- `src/air/services/analyzers/__init__.py` - Package exports
- `src/air/services/analyzers/base.py` - Base interfaces (Finding, AnalyzerResult, BaseAnalyzer)
- `src/air/services/analyzers/code_structure.py` - Structure analyzer
- `src/air/services/analyzers/security.py` - Security analyzer
- `src/air/services/analyzers/architecture.py` - Architecture analyzer
- `src/air/services/analyzers/quality.py` - Quality analyzer
- `tests/unit/test_analyzers.py` - Test suite (14 tests)
- `.air/tasks/20251004-1730-enhance-analysis-depth.md` - This task file

### Modified Files:
- `src/air/commands/analyze.py` - Integrated all analyzers based on focus flag

## Outcome

✅ Success

Significantly enhanced analysis depth. Analysis now provides:
- **Security findings** with severity levels (critical/high/medium/low)
- **Code structure metrics** (files, LOC, languages)
- **Architecture insights** (patterns, dependencies)
- **Code quality issues** (long functions, missing docs, test coverage)

Example output from test:
```
Security findings: 6 (4 high, 2 medium)
Code structure: 127 files, 84,448 lines
  - 62 code files, 20 test files, 26 doc files
  - Languages: Python (61), JavaScript (1)
  - Largest file: 500+ lines
```

## Technical Details

**Design Pattern:**
- Base Analyzer interface (ABC)
- Each analyzer returns AnalyzerResult with:
  - List of Findings
  - Summary statistics
  - Metadata

**Finding Structure:**
```python
Finding(
    category="security",
    severity=FindingSeverity.HIGH,
    title="Hardcoded API key",
    description="...",
    location="app.py",
    line_number=15,
    suggestion="Use environment variables",
    metadata={...}
)
```

**Focus Flag Behavior:**
- `--focus=security` → Only security issues
- `--focus=architecture` → Only architectural analysis
- `--focus=quality` → Only quality issues
- No flag → Comprehensive analysis (all analyzers)

**Test Coverage:**
- 14 new unit tests
- Tests for each analyzer type
- Integration test running all analyzers together
- Total test count: 370 (up from 356)

## Impact

**Before:**
- Basic classification only (tech stack, languages)
- Findings: ~1 item (classification summary)
- Depth: Superficial

**After:**
- Multi-dimensional analysis
- Findings: 10-50+ items per repository
- Depth: Actionable security/quality/architecture insights

This makes `air analyze` genuinely useful for code assessment instead of just classification.

## Next Steps

Potential enhancements for future versions:
1. **Performance analysis** - detect slow operations, N+1 queries
2. **Dependency vulnerability scanning** - check for known CVEs
3. **License compliance** - check dependency licenses
4. **Custom rules** - user-defined patterns to detect
5. **AI-powered analysis** - integrate with LLM for deeper insights
6. **Trend analysis** - track metrics over time

See `.air/tasks/FUTURE-agent-interaction-design.md` for related future work.
