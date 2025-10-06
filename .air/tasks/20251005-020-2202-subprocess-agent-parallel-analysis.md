# Task: Design subprocess agent-based parallel analysis

## Date
2025-10-05 22:02

## Prompt
Consider dispatching analysis tasks to sub process agents using JSON, and reading back the result as JSON. This allows a central process to collect and store the results.

## Design Goals

### Architecture Benefits
- **True Parallelism**: Multiple analyzers run simultaneously across CPU cores
- **Isolation**: Each analyzer in separate process (crash isolation)
- **Centralized Control**: Main process coordinates and aggregates results
- **No File Conflicts**: Results returned via JSON, written once by coordinator
- **Progress Tracking**: Main process monitors all subprocess status
- **Resource Management**: Control max concurrent processes

## Actions Taken
✅ Design phase complete

## Proposed Architecture

### Component Overview

```
Main Process (Coordinator)
    ├─> Subprocess Agent 1: SecurityAnalyzer(repo-a) → JSON
    ├─> Subprocess Agent 2: PerformanceAnalyzer(repo-a) → JSON
    ├─> Subprocess Agent 3: SecurityAnalyzer(repo-b) → JSON
    └─> Subprocess Agent 4: QualityAnalyzer(repo-b) → JSON

Coordinator collects all JSON → aggregates → writes findings file
```

### Key Components

#### 1. Analysis Worker (Subprocess Entry Point)
**New file**: `src/air/services/analysis_worker.py`

- Entry point for subprocess execution
- Loads analyzer class dynamically
- Executes analysis in isolation
- Returns JSON-serializable result
- Includes timing and metadata

#### 2. Analysis Orchestrator (Process Pool Manager)
**Update**: `src/air/services/agent_manager.py`

- Manages ProcessPoolExecutor
- Submits analyzer tasks
- Collects results as they complete
- Handles timeouts and errors
- Provides progress callbacks

#### 3. Updated Analyze Command
**Update**: `src/air/commands/analyze.py`

- Add `--parallel` flag
- Add `--workers=N` option
- Coordinate subprocess execution
- Aggregate results
- Single atomic findings write

## Command Interface

### New Options
```bash
# Control parallelism
air analyze repo-name --parallel           # Use all CPU cores
air analyze repo-name --workers=4          # Limit to 4 workers
air analyze --all --parallel               # Parallel multi-repo

# Show progress
air analyze --all --parallel --progress    # Show live progress bar
```

### Expected Performance

**Single Repo (5 analyzers):**
- Sequential: 10.17s
- Parallel (4 cores): ~3.5s (2.9x speedup)

**Multi-Repo (10 repos, 5 analyzers = 50 tasks):**
- Sequential: ~85s
- Parallel (8 cores): ~15s (5.7x speedup)

## Benefits

### 1. Performance
- 2-6x speedup depending on CPU cores
- CPU-bound analyzers benefit most
- Scales with available cores

### 2. Safety
- **No file conflicts**: Single coordinator writes files
- **Process isolation**: Analyzer crash doesn't kill main process
- **Atomic writes**: All findings written once
- **Solves parallel safety issues** from task 019

### 3. Scalability
- **Resource control**: `--workers=N` limits concurrency
- **Memory management**: Processes can be recycled
- **Gradual rollout**: Keep sequential as fallback

### 4. Monitoring
- Progress tracking per analyzer
- Error handling without blocking
- More granular timing data

## Implementation Phases

### Phase 1: Core Infrastructure (2-3 days)
- [ ] Create `analysis_worker.py` with subprocess runner
- [ ] Add `AnalysisOrchestrator` to `agent_manager.py`
- [ ] Implement JSON serialization for all analyzers
- [ ] Add unit tests for worker process

### Phase 2: Single Repo Parallel (1-2 days)
- [ ] Update `_analyze_single_repo()` with parallel option
- [ ] Add `--parallel` and `--workers` flags
- [ ] Test with all 5 analyzers
- [ ] Benchmark performance improvements

### Phase 3: Multi-Repo Parallel (2-3 days)
- [ ] Implement parallel multi-repo analysis
- [ ] Handle dependency-ordered parallel execution
- [ ] Add progress indicators
- [ ] Test with 10+ repos

### Phase 4: Polish & Documentation (1 day)
- [ ] Add progress bars with rich library
- [ ] Update docs with parallel usage examples
- [ ] Add `--parallel` to examples
- [ ] Performance benchmarking report

## Technical Considerations

### Serialization
- All `AnalyzerResult` objects already have `.to_dict()`
- `Finding` objects already serializable
- Config can be passed as JSON string

### Process Management
- Use `ProcessPoolExecutor` for automatic cleanup
- Set timeout for analyzer tasks (e.g., 5 minutes)
- Handle SIGTERM/SIGINT gracefully

### Error Handling
- Capture subprocess exceptions
- Continue analysis if one analyzer fails
- Report failures in final summary

### Backwards Compatibility
- Keep sequential execution as default
- `--parallel` is opt-in flag
- Fallback to sequential on error

### Dependency-Ordered Execution
- Parallel within dependency levels
- Sequential across levels
- Max parallelism = repos_in_level × analyzers_count

## Files to Change

**New Files:**
- `src/air/services/analysis_worker.py` - Subprocess worker
- `tests/unit/test_analysis_worker.py` - Worker tests
- `tests/integration/test_parallel_analysis.py` - Integration tests

**Modified Files:**
- `src/air/commands/analyze.py` - Add parallel flags and orchestration
- `src/air/services/agent_manager.py` - Add AnalysisOrchestrator
- `docs/COMMANDS.md` - Document parallel options

## Outcome
✅ Design Complete - Ready for Implementation

## Notes
- This addresses the parallel safety issues identified in task 019
- Subprocess approach is more robust than threading (Python GIL)
- JSON communication is simple and debuggable
- Can add message queue (e.g., Redis) later for distributed execution
- Consider rate limiting for external API calls in analyzers
- All existing analyzer code remains unchanged (backwards compatible)
