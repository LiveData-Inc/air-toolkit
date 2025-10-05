# Design: Analysis Caching by Git Commit Hash

## Problem Statement

Currently, `air analyze` re-runs full analysis even if the code hasn't changed since the last run. This:
- Wastes time on redundant analysis
- Causes agents to duplicate work
- Makes incremental workflows inefficient
- Doesn't leverage git's built-in versioning

**User insight:** "Should an agent determine that analysis has already been completed based on changeset hash?"

## Proposed Solution

Track the git commit hash of analyzed repositories and skip re-analysis if code hasn't changed.

## Design

### 1. Metadata Enhancement

Add version tracking to findings metadata:

```json
{
  "analysis_metadata": {
    "analyzed_at": "2025-10-04T17:30:00",
    "air_version": "0.6.0",
    "git_commit": "abc123def456...",
    "git_branch": "main",
    "git_dirty": false,
    "analyzers_run": ["security", "performance", "quality"],
    "focus": null
  },
  "findings": [...]
}
```

### 2. Cache Check Logic

Before running analysis:

```python
def should_reanalyze(resource_path: Path, focus: str | None) -> tuple[bool, str]:
    """Check if resource needs re-analysis.

    Returns:
        (should_analyze: bool, reason: str)
    """
    # 1. Load existing findings
    findings_file = get_findings_file(resource_path)
    if not findings_file.exists():
        return True, "No previous analysis found"

    # 2. Get current git state
    current_hash = get_git_commit_hash(resource_path)
    if not current_hash:
        return True, "Repository is not a git repo"

    # 3. Load previous metadata
    previous_metadata = load_analysis_metadata(findings_file)

    # 4. Compare hashes
    if previous_metadata.get("git_commit") != current_hash:
        return True, f"Code changed ({previous_metadata.get('git_commit')[:7]} → {current_hash[:7]})"

    # 5. Check if git working tree is dirty
    if is_git_dirty(resource_path):
        return True, "Repository has uncommitted changes"

    # 6. Check if same analyzers/focus
    if focus != previous_metadata.get("focus"):
        return True, f"Different focus requested"

    # 7. Cache hit!
    return False, "Using cached analysis (code unchanged)"
```

### 3. Command Enhancement

Add `--force` flag to bypass cache:

```bash
# Use cache if available
air analyze repos/myapp

# Force re-analysis
air analyze repos/myapp --force

# Show cache status
air analyze repos/myapp --dry-run
```

### 4. Output Behavior

**Cache hit:**
```
Analyzing: repos/myapp
Git commit: abc123d (unchanged since last analysis)
✓ Using cached analysis from 2 hours ago
  Security: 8 findings
  Performance: 12 findings
  Quality: 15 findings

Total: 35 findings (4 high, 12 medium, 19 low)
Use --force to re-analyze
```

**Cache miss:**
```
Analyzing: repos/myapp
Git commit: def456a (changed from abc123d)
Running fresh analysis...
[normal analysis proceeds]
```

## Implementation Details

### Git Integration

```python
# src/air/services/git_tracker.py

def get_git_commit_hash(repo_path: Path) -> str | None:
    """Get current git commit hash.

    Returns:
        Full commit hash or None if not a git repo
    """
    try:
        import git
        repo = git.Repo(repo_path)
        return repo.head.commit.hexsha
    except Exception:
        return None

def get_git_branch(repo_path: Path) -> str | None:
    """Get current branch name."""
    try:
        import git
        repo = git.Repo(repo_path)
        return repo.active_branch.name
    except Exception:
        return None

def is_git_dirty(repo_path: Path) -> bool:
    """Check if repo has uncommitted changes."""
    try:
        import git
        repo = git.Repo(repo_path)
        return repo.is_dirty()
    except Exception:
        return False

def get_git_info(repo_path: Path) -> dict:
    """Get complete git state."""
    return {
        "commit": get_git_commit_hash(repo_path),
        "branch": get_git_branch(repo_path),
        "dirty": is_git_dirty(repo_path),
    }
```

### Findings Structure Update

```python
# When saving findings in analyze.py

findings_data = {
    "analysis_metadata": {
        "analyzed_at": datetime.now().isoformat(),
        "air_version": __version__,
        "git_commit": git_info.get("commit"),
        "git_branch": git_info.get("branch"),
        "git_dirty": git_info.get("dirty"),
        "analyzers_run": [a.name for a in analyzers],
        "focus": focus,
    },
    "findings": all_findings_list,
}
```

## Advanced Features

### Incremental Analysis

For large repos, analyze only changed files:

```python
def get_changed_files(repo_path: Path, since_commit: str) -> list[Path]:
    """Get files changed since commit."""
    import git
    repo = git.Repo(repo_path)
    diff = repo.git.diff(since_commit, name_only=True).split('\n')
    return [Path(repo_path) / f for f in diff if f]

# Only analyze changed files
if not force and previous_commit:
    changed_files = get_changed_files(resource, previous_commit)
    findings = analyze_only_files(changed_files)
    # Merge with previous findings for unchanged files
```

### Multi-Branch Support

Track analysis per branch:

```
analysis/reviews/
├── myapp-findings.json              # Current branch
├── myapp-findings-main.json         # Main branch cache
├── myapp-findings-develop.json      # Develop branch cache
└── .cache/
    └── myapp-metadata.json          # Track all branches
```

### Agent Coordination

Agents can check if another agent already analyzed:

```python
# Agent 1 starts analyzing
create_lock_file(resource, agent_id)

# Agent 2 checks
if is_being_analyzed(resource):
    wait_for_completion(resource)
    # Use results from Agent 1
```

## Configuration

Add to `air-config.json`:

```json
{
  "analysis": {
    "cache_enabled": true,
    "cache_ttl_hours": 24,
    "require_clean_working_tree": false,
    "incremental_analysis": false
  }
}
```

## Benefits

1. **Performance:** Skip redundant analysis (50-90% time savings)
2. **Agent Efficiency:** Multiple agents don't duplicate work
3. **CI/CD:** Fast checks when code unchanged
4. **Incremental:** Only analyze what changed
5. **Auditability:** Know exactly what version was analyzed

## Edge Cases

1. **Non-git repos:** Fall back to timestamp comparison
2. **Dirty working tree:**
   - Option A: Always re-analyze (safe)
   - Option B: Use cache but warn (fast)
3. **Detached HEAD:** Use commit hash only
4. **Submodules:** Track parent + submodule hashes
5. **AIR version change:** Re-analyze if AIR updated

## Rollout Plan

### Phase 1: Basic Caching (v0.6.0)
- Add git hash to findings metadata
- Check hash before analysis
- Show "using cached" message
- Add --force flag

### Phase 2: Smart Invalidation (v0.7.0)
- Per-analyzer caching
- Cache TTL configuration
- Branch-aware caching

### Phase 3: Incremental Analysis (v0.8.0)
- Analyze only changed files
- Merge with previous findings
- Agent coordination via locks

## Example Workflow

```bash
# First analysis
$ air analyze repos/myapp
Analyzing: repos/myapp (commit: abc123d)
Running security analysis...
[full analysis - takes 30s]

# No code changes, run again
$ air analyze repos/myapp
Analyzing: repos/myapp (commit: abc123d - unchanged)
✓ Using cached analysis from 5 minutes ago
[instant results]

# Make code changes and commit
$ git commit -m "fix security issue"

# Analysis detects change
$ air analyze repos/myapp
Analyzing: repos/myapp (commit: def456a - changed from abc123d)
Code changed, running fresh analysis...
[full analysis]

# Force re-analysis
$ air analyze repos/myapp --force
Analyzing: repos/myapp (commit: def456a)
Forcing fresh analysis (--force flag)
[full analysis even though cached]
```

## Questions to Resolve

1. **Cache TTL:** Should cached results expire after N hours?
2. **Dirty repos:** Analyze dirty working trees or require clean?
3. **Granularity:** Per-repo or per-analyzer caching?
4. **Storage:** Embed in findings or separate cache files?
5. **Invalidation:** When AIR version changes, invalidate cache?

## Recommendation

**Start with Phase 1 (Basic Caching) for v0.6.0:**
- Simple hash comparison
- Show cached status
- --force flag to bypass
- Low complexity, high value

This addresses the user's core insight while keeping implementation simple.
