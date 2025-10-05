# Design: Dependency-Aware Multi-Repo Analysis

## Problem Statement

Currently, `air analyze` treats all repos as independent:
- No understanding of dependencies between linked repos
- Can't detect if service-a depends on library-b
- Analyzes in arbitrary order, not dependency order
- Wastes time analyzing repos with no dependencies

**User insight:** "Use project files to understand dependencies, and do not analyze if there are no dependencies."

## Key Distinction

### Single-Repo Analysis
```bash
# Outside AIR project OR analyzing external repo
cd ~/my-repo
air analyze .
```
- **Context:** Standalone repository
- **Goal:** Analyze this one repo
- **Dependencies:** Not relevant
- **Output:** Findings for this repo only

### Multi-Repo Analysis
```bash
# Inside AIR project with linked repos
cd my-assessment
air analyze --all
```
- **Context:** AIR project with multiple linked repos
- **Goal:** Understand relationships across repos
- **Dependencies:** Critical for ordering and gap analysis
- **Output:** Cross-repo insights, dependency gaps

## Dependency Detection

### 1. Detect Dependencies from Project Files

```python
# src/air/services/dependency_detector.py

def detect_dependencies(repo_path: Path) -> set[str]:
    """Detect external dependencies from project files.

    Returns:
        Set of package names this repo depends on
    """
    dependencies = set()

    # Python: requirements.txt, pyproject.toml
    if (repo_path / "requirements.txt").exists():
        deps = parse_requirements(repo_path / "requirements.txt")
        dependencies.update(deps)

    if (repo_path / "pyproject.toml").exists():
        deps = parse_pyproject_toml(repo_path / "pyproject.toml")
        dependencies.update(deps)

    # JavaScript: package.json
    if (repo_path / "package.json").exists():
        deps = parse_package_json(repo_path / "package.json")
        dependencies.update(deps)

    # Go: go.mod
    if (repo_path / "go.mod").exists():
        deps = parse_go_mod(repo_path / "go.mod")
        dependencies.update(deps)

    # Java: pom.xml, build.gradle
    # Rust: Cargo.toml
    # etc.

    return dependencies

def parse_requirements(file_path: Path) -> set[str]:
    """Parse Python requirements.txt."""
    deps = set()
    for line in file_path.read_text().split('\n'):
        line = line.strip()
        if line and not line.startswith('#'):
            # Extract package name (before ==, >=, etc.)
            pkg = re.split(r'[=<>!]', line)[0].strip()
            deps.add(pkg.lower())
    return deps

def parse_package_json(file_path: Path) -> set[str]:
    """Parse Node package.json."""
    data = json.loads(file_path.read_text())
    deps = set()
    deps.update(data.get('dependencies', {}).keys())
    deps.update(data.get('devDependencies', {}).keys())
    return deps
```

### 2. Build Cross-Repo Dependency Graph

```python
def build_dependency_graph(config: AirConfig) -> dict[str, set[str]]:
    """Build graph of dependencies between linked repos.

    Returns:
        {repo_name: set of repo names it depends on}
    """
    graph = {}

    # Get all linked repos and their package names
    repo_packages = {}  # {package_name: repo_name}

    for resource in config.resources:
        repo_path = Path(resource.path)

        # Detect what this repo provides (its package name)
        package_name = detect_package_name(repo_path)
        if package_name:
            repo_packages[package_name] = resource.name

    # For each repo, check if it depends on other linked repos
    for resource in config.resources:
        repo_path = Path(resource.path)
        deps = detect_dependencies(repo_path)

        # Find which linked repos this depends on
        linked_deps = set()
        for dep in deps:
            if dep in repo_packages:
                linked_deps.add(repo_packages[dep])

        graph[resource.name] = linked_deps

    return graph

def detect_package_name(repo_path: Path) -> str | None:
    """Detect the package name this repo provides."""
    # Python: pyproject.toml [project] name or setup.py
    if (repo_path / "pyproject.toml").exists():
        data = toml.loads((repo_path / "pyproject.toml").read_text())
        return data.get("project", {}).get("name")

    # JavaScript: package.json name
    if (repo_path / "package.json").exists():
        data = json.loads((repo_path / "package.json").read_text())
        return data.get("name")

    # Go: module name from go.mod
    if (repo_path / "go.mod").exists():
        content = (repo_path / "go.mod").read_text()
        match = re.search(r'^module\s+(\S+)', content, re.MULTILINE)
        if match:
            return match.group(1).split('/')[-1]

    return None
```

## Analysis Modes

### Mode 1: Single Repo (Standalone)

```bash
# Analyze one repo, not in AIR project context
air analyze repos/myapp
```

**Behavior:**
- Analyze this repo only
- No dependency considerations
- Standard security/quality/performance analysis

### Mode 2: Multi-Repo (Dependency-Aware)

```bash
# In AIR project, analyze all linked repos
air analyze --all

# Or analyze specific repo in project context
air analyze myapp --context
```

**Behavior:**
1. Build dependency graph
2. Topological sort (libraries before services)
3. Skip isolated repos (no dependencies)
4. Parallel analysis where possible

**Example:**
```
Dependency Graph:
  shared-utils (provides: shared-utils)
    ↓
  ├─ service-a (depends on: shared-utils)
  └─ service-b (depends on: shared-utils)

  docs (no dependencies)

Analysis Order:
  1. Analyze shared-utils (no deps)
  2. Analyze service-a + service-b in parallel (both depend on shared-utils)
  3. Skip docs (no code dependencies)

Output:
  ✓ shared-utils: 12 findings
  ✓ service-a: 23 findings + 3 dependency gaps
  ✓ service-b: 18 findings + 1 dependency gap
  ⊘ docs: skipped (no dependencies)
```

### Mode 3: Gap Analysis

```bash
# Analyze library vs services that use it
air analyze --gap shared-utils
```

**Behavior:**
1. Find all repos that depend on `shared-utils`
2. Analyze `shared-utils` capabilities
3. Analyze dependent services' usage patterns
4. Report gaps and mismatches

**Example Output:**
```
Gap Analysis: shared-utils

Provides:
  - Authentication helpers
  - Database utils
  - Logging

Used By:
  - service-a: Uses auth, database
  - service-b: Uses auth only

Gaps Found:
  ⚠️  service-a: Missing error handling for DB connection failures
  ℹ️  service-b: Not using available logging utilities
  ⚠️  Both services: Using deprecated auth.login() (should use auth.authenticate())
```

## Command Design

### Enhanced `air analyze`

```bash
# Single repo (current behavior)
air analyze repos/myapp

# Multi-repo: analyze all with dependencies
air analyze --all

# Multi-repo: dependency-aware order
air analyze --all --respect-deps

# Skip repos with no dependencies
air analyze --all --deps-only

# Gap analysis for specific library
air analyze --gap shared-utils

# Analyze repo in project context (check for dependency issues)
air analyze myapp --context
```

### New Options

```python
@click.command()
@click.argument("resource", required=False)
@click.option("--all", is_flag=True, help="Analyze all linked repos")
@click.option("--respect-deps", is_flag=True, help="Analyze in dependency order")
@click.option("--deps-only", is_flag=True, help="Only analyze repos with dependencies")
@click.option("--gap", help="Gap analysis for this library vs dependents")
@click.option("--context", is_flag=True, help="Analyze in project context (check deps)")
```

## Implementation

### Topological Sort

```python
def topological_sort(graph: dict[str, set[str]]) -> list[list[str]]:
    """Sort repos by dependency order, return levels for parallel execution.

    Returns:
        List of lists - each inner list can be analyzed in parallel
    """
    # Calculate in-degree
    in_degree = {node: 0 for node in graph}
    for deps in graph.values():
        for dep in deps:
            if dep in in_degree:
                in_degree[dep] += 1

    # Process by levels
    levels = []
    remaining = set(graph.keys())

    while remaining:
        # Find nodes with no dependencies
        level = [node for node in remaining if in_degree[node] == 0]
        if not level:
            # Circular dependency!
            raise ValueError(f"Circular dependency detected in: {remaining}")

        levels.append(level)

        # Remove this level and update in-degrees
        for node in level:
            remaining.remove(node)
            for dep_node in graph.get(node, set()):
                in_degree[dep_node] -= 1

    return levels
```

### Multi-Repo Analysis Workflow

```python
def analyze_multi_repo(config: AirConfig, respect_deps: bool, deps_only: bool):
    """Analyze multiple repos with dependency awareness."""

    # 1. Build dependency graph
    graph = build_dependency_graph(config)

    # 2. Filter if deps_only
    if deps_only:
        # Only analyze repos that have dependencies OR are depended upon
        relevant = set()
        for repo, deps in graph.items():
            if deps:  # Has dependencies
                relevant.add(repo)
                relevant.update(deps)  # Include what it depends on

        # Filter
        graph = {k: v for k, v in graph.items() if k in relevant}

    # 3. Determine order
    if respect_deps:
        levels = topological_sort(graph)
    else:
        levels = [list(graph.keys())]  # All in one level (parallel)

    # 4. Analyze by level
    all_results = {}

    for level_num, repos_in_level in enumerate(levels, 1):
        info(f"Level {level_num}: Analyzing {len(repos_in_level)} repos...")

        # Analyze this level in parallel
        agents = []
        for repo_name in repos_in_level:
            agent_id = f"level-{level_num}-{repo_name}"
            spawn_background_agent(
                agent_id=agent_id,
                command="analyze",
                resource_path=f"repos/{repo_name}",
            )
            agents.append(agent_id)

        # Wait for this level to complete before next
        wait_for_agents(agents)

        # Collect results
        for repo_name in repos_in_level:
            results = load_findings(repo_name)
            all_results[repo_name] = results

    # 5. Cross-repo analysis
    detect_dependency_gaps(all_results, graph)

    return all_results
```

### Dependency Gap Detection

```python
def detect_dependency_gaps(results: dict, graph: dict) -> list[Finding]:
    """Detect issues across repo dependencies."""
    gaps = []

    for repo, deps in graph.items():
        if not deps:
            continue

        repo_findings = results.get(repo, {})

        for dep_repo in deps:
            dep_findings = results.get(dep_repo, {})

            # Check version mismatches
            used_version = get_dependency_version(f"repos/{repo}", dep_repo)
            available_version = get_package_version(f"repos/{dep_repo}")

            if used_version and available_version:
                if used_version != available_version:
                    gaps.append(Finding(
                        category="dependency",
                        severity=FindingSeverity.MEDIUM,
                        title="Dependency version mismatch",
                        description=f"{repo} uses {dep_repo}@{used_version} but {available_version} is available",
                        suggestion=f"Update dependency to {available_version}",
                    ))

            # Check for deprecated API usage
            # (would need more sophisticated analysis)

    return gaps
```

## Example Workflows

### Example 1: Library + Services

```bash
# Setup
air init integration-analysis
air link add ~/libs/auth-lib
air link add ~/services/api-service
air link add ~/services/web-service

# Detect dependencies
$ air analyze --all --deps-only --respect-deps

Dependency Graph:
  auth-lib (provides: auth-lib)
    ↓
  ├─ api-service (depends on: auth-lib@1.2.0)
  └─ web-service (depends on: auth-lib@1.1.0)

Analysis Plan:
  Level 1: auth-lib
  Level 2: api-service, web-service (parallel)

Analyzing...
✓ auth-lib: 8 findings (current version: 1.3.0)
✓ api-service: 15 findings
✓ web-service: 12 findings

Dependency Gaps:
  ⚠️  api-service: Using auth-lib@1.2.0, but 1.3.0 available
  ⚠️  web-service: Using auth-lib@1.1.0, but 1.3.0 available (2 versions behind!)
  ℹ️  web-service: Missing new SSO features from auth-lib 1.2+
```

### Example 2: Gap Analysis

```bash
# Focus on one library and its dependents
$ air analyze --gap auth-lib

Gap Analysis: auth-lib

Library Capabilities:
  - Basic authentication (since 1.0)
  - Session management (since 1.1)
  - SSO support (since 1.2) ← NEW
  - Multi-factor auth (since 1.3) ← NEW

Dependent Services:
  api-service:
    ✓ Using: Basic auth, sessions, SSO
    ⚠️  Missing: Multi-factor auth (available in 1.3)
    ⚠️  Version: 1.2.0 (1 version behind)

  web-service:
    ✓ Using: Basic auth, sessions
    ⚠️  Missing: SSO (available since 1.2)
    ⚠️  Missing: Multi-factor auth (available in 1.3)
    🔴 Version: 1.1.0 (2 versions behind!)

Recommendations:
  1. Upgrade web-service to auth-lib@1.3
  2. Upgrade api-service to auth-lib@1.3
  3. Implement multi-factor auth in both services
```

## Benefits

1. **Intelligent Analysis:** Only analyze what matters
2. **Correct Order:** Libraries before services
3. **Parallel Where Possible:** Independent repos in parallel
4. **Gap Detection:** Find version mismatches and missing features
5. **Time Savings:** Skip isolated documentation repos

## Configuration

```json
{
  "analysis": {
    "dependency_detection": true,
    "skip_isolated_repos": true,
    "respect_dependency_order": true
  }
}
```

## Rollout

**Phase 1 (v0.6.0):**
- Basic dependency detection
- `--deps-only` flag
- Dependency graph building

**Phase 2 (v0.7.0):**
- Topological sort
- `--respect-deps` analysis ordering
- Gap detection

**Phase 3 (v0.8.0):**
- `--gap` analysis mode
- Version mismatch detection
- Deprecated API detection

This makes AIR truly understand the relationships between repos, not just analyze them in isolation!
