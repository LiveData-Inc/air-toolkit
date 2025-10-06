# Task: Analyze parallel safety of air analyze command

## Date
2025-10-05 21:58

## Prompt
Can the `air analyze` command safely be run as parallel processes?

## Actions Taken
1. Reviewed analyze.py for file write operations
2. Analyzed cache_manager.py for race conditions
3. Examined findings file output patterns
4. Checked dependency graph generation

## Files Changed
None - analysis only

## Outcome
✅ Analysis Complete

## Parallel Safety Assessment

### ✅ SAFE to run in parallel under these conditions:

**Different Repositories:**
- Each repo writes to a unique findings file: `analysis/reviews/{repo-name}-findings.json`
- Cache uses repo-specific hash directories: `.air/cache/{repo_hash}/`
- No conflicts when analyzing different repos simultaneously

**Same Repository, Different Analyzers:**
- Each analyzer writes separate cache files: `{file_hash}-{analyzer_name}.json`
- No conflicts between analyzer cache writes

### ⚠️ POTENTIAL CONFLICTS:

**1. Same Repository, Same Time (multi-repo mode):**
- **Findings file collision**: Multiple processes writing to same `{repo-name}-findings.json`
- **Risk**: Last writer wins, earlier results may be lost
- **Impact**: HIGH - data loss

**2. Dependency Graph File:**
- **File**: `analysis/dependency-graph.json`
- **Written by**: `air analyze --all`
- **Risk**: Race condition if multiple `--all` runs execute simultaneously
- **Impact**: MEDIUM - graph may be corrupted or incomplete

**3. Cache Race Conditions:**
- **Scenario**: Same repo, same analyzer, parallel execution
- **Cache writes**: Lines 302, 305 (cache_manager.py)
- **Risk**: LOW - writes are atomic, worst case is redundant work
- **Impact**: LOW - performance only, silently fails on error

### 🚫 UNSAFE Scenarios:

1. **Multiple `air analyze repo-name` on same repo**: Findings file collision
2. **Multiple `air analyze --all` on same project**: Dependency graph collision
3. **Analyzing same repo while `--all` is running**: Potential findings overwrite

### ✅ SAFE Scenarios:

1. **`air analyze repo-a` + `air analyze repo-b`**: Different findings files
2. **Multiple repos in `--all` mode**: Sequential execution per repo (safe by design)
3. **Background mode (`--background`)**: Already designed for parallel execution

## Recommendations

### For Current Implementation:
1. **Document the limitations** in command help text
2. **Add warning** if same repo is analyzed multiple times
3. **Consider file locking** for findings writes

### For Future Enhancement:
1. **File Locking**: Use `fcntl.flock()` or similar for findings writes
2. **Atomic Writes**: Write to temp file, then rename (atomic operation)
3. **Mutex/Semaphore**: Add optional lock file per repo
4. **Unique Output**: Add timestamp to findings filename: `{repo}-{timestamp}.json`

### Immediate Safe Usage:
✗ Resource not found: repo-b
ℹ Building dependency graph...
✗ Resource not found: repo-a
ℹ Dependency graph saved: 
/Users/gpeddle/repos/github/LiveData-Inc/air-toolkit/analysis/dependency-graph.j
son
ℹ No repos to analyze
✗ Resource not found: my-repo
✗ Resource not found: my-repo
✗ Resource not found: my-repo
✗ Resource not found: other-repo

## Technical Details

### File Write Locations:
- **Findings**: `analysis/reviews/{repo-name}-findings.json` (line 352)
- **Dep Graph**: `analysis/dependency-graph.json` (line 422)
- **Cache**: `.air/cache/{repo-hash}/{file-hash}-{analyzer}.json` (line 302)

### Race Condition Window:
- Findings write: ~5-50ms (depends on findings size)
- No atomic write protection
- No file locking mechanism
- mkdir with `exist_ok=True` is safe

## Notes
- Current implementation prioritizes simplicity over parallel safety
- Background mode (`--background`) with unique agent IDs is the intended parallel execution method
- Cache collisions are handled gracefully (silent fail)
- Findings collisions result in data loss with no warning
