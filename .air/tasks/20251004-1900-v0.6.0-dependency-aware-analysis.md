# Task: v0.6.0 - Dependency-Aware Multi-Repo Analysis

## Date
2025-10-04 19:00

## Prompt
User: "correction - the dependency graph should be aware of library import dependencies. We should classify API dependencies as a separate category and a separate analysis."

Context: Implementing dependency-aware analysis for multi-repo projects based on earlier design work.

## Actions Taken

### 1. Created dependency_detector.py
- `detect_dependencies(repo_path)` - Parse package dependencies from project files
- `detect_package_name(repo_path)` - Determine what package a repo provides
- `get_dependency_version(repo_path, package_name)` - Get version of specific dependency
- Supports: Python (requirements.txt, pyproject.toml), JavaScript (package.json), Go (go.mod)

### 2. Created dependency_graph.py
- `build_dependency_graph(config)` - Build cross-repo dependency graph
- `topological_sort(graph)` - Sort repos by dependency order for parallel execution
- `filter_repos_with_dependencies(graph)` - Filter to only repos with dependencies
- `detect_dependency_gaps(config, graph)` - Find version mismatches between repos

### 3. Enhanced analyze command
Added multi-repo analysis modes:
- `air analyze --all` - Analyze all linked repos
- `air analyze --all --respect-deps` - Analyze in dependency order (topological sort)
- `air analyze --all --deps-only` - Only analyze repos with dependencies
- `air analyze --gap library-name` - Gap analysis for library vs dependents
- `air analyze myapp --context` - Single repo with dependency checking

Enhanced single-repo analysis:
- Accept resource names (not just paths): `air analyze myapp`
- Consistent with other commands like `air pr` and `air classify`
- Falls back to path resolution if name not found

### 4. Added load_config() to filesystem.py
- Loads air-config.json and returns AirConfig instance
- Validates JSON and handles errors
- Required for multi-repo analysis

### 5. JSON dependency graph output
- Saves dependency graph to `analysis/dependency-graph.json`
- Serializable format for consumption by other tools
- Shows which repos depend on which

### 6. Fixed config.resources access
- Changed from `config.resources` (dict) to `config.get_all_resources()` (list)
- Fixed in: analyze.py, dependency_graph.py
- All tests now passing

## Files Changed

### New Files:
- `src/air/services/dependency_detector.py` - Package dependency detection
- `src/air/services/dependency_graph.py` - Dependency graph building and analysis

### Modified Files:
- `src/air/commands/analyze.py` - Multi-repo analysis modes, resource name resolution
- `src/air/services/filesystem.py` - Added load_config() function
- `.air/tasks/20251004-1900-v0.6.0-dependency-aware-analysis.md` - This task file

## Outcome

✅ Success

All 372 tests passing. Dependency-aware analysis foundation complete.

## Architecture

### Single-Repo Analysis
```bash
# Standalone (outside AIR project)
air analyze /path/to/repo

# Within AIR project (by name or path)
air analyze myapp
air analyze repos/service-a
air analyze myapp --context  # Check dependency issues
```

### Multi-Repo Analysis
```bash
# Analyze all linked repos
air analyze --all

# Respect dependency order (libraries before services)
air analyze --all --respect-deps

# Skip isolated repos (only analyze those with dependencies)
air analyze --all --deps-only

# Gap analysis (library vs dependents)
air analyze --gap shared-utils
```

### Dependency Graph
Saved to `analysis/dependency-graph.json`:
```json
{
  "service-a": ["shared-utils", "auth-lib"],
  "service-b": ["shared-utils"],
  "shared-utils": [],
  "auth-lib": [],
  "docs": []
}
```

### Topological Sort
For `--respect-deps`, repos are analyzed in levels:
```
Level 1: shared-utils, auth-lib (no deps)
Level 2: service-a, service-b (depend on Level 1)
```

Each level can be analyzed in parallel.

## User Feedback to Address

1. **Import dependencies**: Current implementation detects package dependencies from manifest files (requirements.txt, package.json). User wants actual code import detection (`import foo`, `require('bar')`).

2. **API dependencies**: HTTP/REST API calls between services should be a separate analysis category.

3. **Language/framework agnostic**: The dependency graph should work for any combination of languages and frameworks.

## Next Steps (Future)

### Phase 1: Import Dependency Detection (v0.6.3)
- Parse Python files for `import` statements
- Parse JavaScript files for `require()` and `import` statements
- Parse Go files for `import` statements
- Build import-based dependency graph

### Phase 2: API Dependency Detection (v0.7.0)
- Detect HTTP client calls (requests, axios, fetch, http.Client)
- Map API endpoints to services
- Build service-to-service API dependency graph
- Separate from library/import dependencies

### Phase 3: Enhanced Gap Analysis (v0.7.1)
- Detect deprecated API usage in dependents
- Find breaking changes between versions
- Suggest upgrade paths

## Impact

**New capabilities:**
- Multi-repo dependency-aware analysis
- Topological sort for proper analysis order
- Skip isolated repos (--deps-only)
- Gap analysis between library versions
- Resource name resolution (consistent with other commands)

**Typical workflow:**
```bash
# Setup assessment with multiple repos
air init microservices-review
air link add ~/repos/shared-utils
air link add ~/repos/api-service
air link add ~/repos/web-service

# Analyze in dependency order
air analyze --all --respect-deps

# Output:
# Building dependency graph...
# Dependency graph saved: analysis/dependency-graph.json
# Analysis order: 2 levels
#   Level 1: shared-utils
#   Level 2: api-service, web-service
# 
# Checking for dependency gaps...
# ⚠️  Found 2 dependency issues:
#   api-service uses shared-utils@1.2.0 but 1.3.0 is available
#   web-service uses shared-utils@1.1.0 but 1.3.0 is available
```

## Statistics

- Total tests: 372 (all passing ✅)
- New files: 2 (dependency_detector.py, dependency_graph.py)
- Modified files: 2 (analyze.py, filesystem.py)
- Lines of code added: ~550
- Supported languages: Python, JavaScript/TypeScript, Go
- Analysis modes: 5 (single, multi, respect-deps, deps-only, gap)

This completes the v0.6.0 dependency-aware analysis foundation.
