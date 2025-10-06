# AIR Toolkit - Future Enhancements

**Version:** 0.6.3
**Last Updated:** 2025-10-05

This document tracks planned enhancements for future AIR releases.

## v0.7.0 - Structural Improvements (Planned)

### Move air-config.json into .air/ Directory

**Status:** Proposed
**Breaking Change:** Yes
**Target:** v0.7.0

#### Rationale

Currently:
```
project/
├── air-config.json          # AIR config (top level)
├── .air/                    # AIR directory
│   ├── tasks/
│   └── context/
```

Proposed:
```
project/
├── .air/                    # All AIR files together
│   ├── config.json          # Moved here
│   ├── tasks/
│   └── context/
```

**Benefits:**
- All AIR-related files in one place (cleaner project root)
- Easier to exclude AIR entirely (one `.gitignore` entry)
- Clearer separation between AIR and project files
- More modular architecture

#### Implementation Plan

**Phase 1: Dual Support (v0.7.0)**
- Read from `.air/config.json` first, fallback to `air-config.json`
- `air init` creates `.air/config.json`
- Warning when old location detected

**Phase 2: Migration Helper**
```bash
# Automatic migration
air upgrade  # Detects air-config.json, moves to .air/config.json
```

**Phase 3: Deprecation (v0.8.0)**
- Remove fallback support for `air-config.json`
- Only read from `.air/config.json`

#### Code Changes Required

**Files to Update:**
- `src/air/services/filesystem.py` - `get_project_root()`
- `src/air/commands/init.py` - Config creation
- `src/air/commands/upgrade.py` - Migration logic
- All commands that read config
- Templates (README, CLAUDE.md)
- Documentation

**Migration Test:**
```python
def test_config_migration():
    # Old project with air-config.json
    project = create_old_project()
    assert (project / "air-config.json").exists()

    # Run upgrade
    run_air_upgrade(project)

    # Verify migration
    assert (project / ".air" / "config.json").exists()
    assert not (project / "air-config.json").exists()
```

---

## v0.7.0+ - Additional Enhancements

### 1. Improved Graceful Degradation

**Status:** In Progress (v0.6.3)

Current improvements in v0.6.3:
- ✅ Updated `.air/README.md` template with "AIR is optional" notice
- ✅ Updated project `README.md` template with prerequisites section
- ✅ Created `docs/GRACEFUL-DEGRADATION.md` guide
- ✅ CLAUDE.md already checks for installation

Future improvements:
- [ ] Add `air check` command to verify installation
- [ ] Add `air doctor` to diagnose configuration issues
- [ ] Slash command fallbacks for missing installation

### 2. Analysis Caching Improvements

**Status:** Planned
**Target:** v0.7.1

**Current:**
- File-level caching based on modification time
- Cache invalidation on file changes

**Proposed:**
- Git commit-based caching (cache until commit changes)
- Shared cache across repos (analyze once, use everywhere)
- Cache compression for large findings
- Cache statistics and cleanup

### 3. Additional Language Support

**Status:** Planned
**Target:** v0.7.x

**Currently Supported:**
- Python, JavaScript/TypeScript, Go

**Planned:**
- Java (Spring, Maven, Gradle)
- Ruby (Rails, Bundler)
- PHP (Laravel, Composer)
- Rust (Cargo)
- C# (.NET)

### 4. MCP Server Implementation

**Status:** In Progress (docs only)
**Target:** v0.8.0

Implement Model Context Protocol server for AIR:
- Expose findings via MCP
- Real-time analysis updates
- Integration with Claude Desktop
- VS Code extension compatibility

### 5. Web UI for Findings

**Status:** Planned
**Target:** v0.8.0

Currently: HTML reports via `air findings --html`

Planned:
- Interactive web dashboard
- Filter/sort findings in browser
- Drill-down into file locations
- Compare findings across commits
- Export to PDF

### 6. CI/CD Integration

**Status:** Planned
**Target:** v0.7.2

**GitHub Actions:**
```yaml
- name: AIR Analysis
  uses: livedata-inc/air-action@v1
  with:
    focus: security
    fail-on-critical: true
```

**GitLab CI:**
```yaml
air_analysis:
  script:
    - air analyze --all --format=json
    - air findings --severity=critical --exit-code
```

### 7. Custom Analyzer Plugins

**Status:** Planned
**Target:** v0.8.0

Allow users to write custom analyzers:

```python
# .air/analyzers/custom_security.py
from air.services.analyzers.base import BaseAnalyzer

class CustomSecurityAnalyzer(BaseAnalyzer):
    def analyze(self):
        # Custom logic
        return AnalyzerResult(...)
```

```bash
air analyze --analyzer=.air/analyzers/custom_security.py
```

### 8. Incremental Analysis

**Status:** Planned
**Target:** v0.7.2

Only analyze changed files since last run:

```bash
# Analyze only files changed since last commit
air analyze --incremental

# Analyze only files changed in branch
air analyze --incremental --base=main
```

### 9. Team Collaboration Features

**Status:** Planned
**Target:** v0.8.0

- Shared findings database (SQLite)
- Finding assignment and tracking
- Finding comments and discussions
- Finding resolution workflow

### 10. Performance Improvements

**Status:** Ongoing

**v0.6.3 Improvements:**
- ✅ Parallel analysis with `--parallel`
- ✅ Subprocess-based execution (bypasses GIL)
- ✅ File-level caching

**Planned:**
- Streaming analysis for large repos
- Lazy loading of findings
- Batch file processing
- Memory-mapped file reading

---

## How to Contribute Ideas

Have an idea for AIR? Here's how to propose it:

1. **Check Existing:** Review this file and open issues
2. **Create Issue:** Open GitHub issue with `enhancement` label
3. **Discuss:** Engage with maintainers and community
4. **Prototype:** (Optional) Create proof-of-concept
5. **PR:** Submit pull request with implementation

**Issue Template:**
```markdown
## Enhancement Proposal

**Feature:** Brief description

**Motivation:** Why is this needed?

**Proposed Solution:** How should it work?

**Alternatives:** What other approaches exist?

**Breaking Changes:** Any compatibility concerns?
```

---

## Release Planning

### v0.7.0 (Q1 2026) - Structural Improvements
- Move `air-config.json` → `.air/config.json`
- Improved caching
- Additional language support
- CI/CD integration

### v0.8.0 (Q2 2026) - Advanced Features
- MCP server
- Web UI
- Custom analyzers
- Team collaboration

### v0.9.0 (Q3 2026) - Performance & Scale
- Incremental analysis
- Large repo optimization
- Distributed analysis

### v1.0.0 (Q4 2026) - Production Hardening
- Stable API
- Long-term support
- Enterprise features
- Complete documentation
