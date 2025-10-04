# Agent Coordination with AIR

**Version**: 0.6.0+
**Status**: Production Ready

AIR enables Claude Code to coordinate multiple analysis agents for complex workflows like gap analysis, parallel reviews, and comparative assessments.

## Key Insight

**Claude Code is already capable of directing multi-agent workflows** - AIR just provides the coordination substrate (project structure, process tracking, status APIs).

## Core Pattern

```
Human → Claude (coordinator) → AIR commands → Background workers
                              ↓
                         AIR status/findings APIs
                              ↓
                         Claude aggregates/synthesizes
                              ↓
                         Strategic analysis documents
```

## Available Commands

### Spawn Workers

```bash
# Launch background analysis
air analyze <path> --background --id=<worker-id> --focus=<area>
```

### Monitor Workers

```bash
# Check agent status
air status --agents

# Get status as JSON (for parsing)
air status --agents --format=json

# Wait for workers to complete (NEW in v0.6.0)
air wait --all                    # Wait for all agents
air wait --agents w1,w2,w3        # Wait for specific agents
air wait --all --timeout=300      # With timeout
```

### Aggregate Results

```bash
# Get all findings
air findings --all

# As JSON for parsing
air findings --all --format=json

# Filter by severity
air findings --all --severity=high
```

## Usage Pattern 1: Parallel Analysis

**Goal**: Analyze multiple repositories concurrently.

```bash
# Spawn workers
air analyze repos/service-a --background --id=worker-a
air analyze repos/service-b --background --id=worker-b
air analyze repos/service-c --background --id=worker-c

# Wait for completion
air wait --all

# Aggregate
air findings --all
```

**Claude's role**:
- Spawn workers
- Wait for completion
- Create comparative analysis document

## Usage Pattern 2: Gap Analysis

**Goal**: Compare library vs service to identify integration gaps.

**Setup**:
```bash
air init integration-analysis --mode=mixed
air link add ~/libs/library --type=review
air link add ~/libs/library-roadmap --type=review
air link add ~/services/service --type=develop
```

**Workflow**:
```bash
# Spawn 3 workers (library current, library future, service needs)
air analyze repos/library --background --id=lib-current --focus=capabilities
air analyze repos/library-roadmap --background --id=lib-future --focus=roadmap
air analyze repos/service --background --id=service-reqs --focus=requirements

# Wait
air wait --all

# Aggregate
air findings --all --format=json

# Claude synthesizes:
# - What library provides (now + planned)
# - What service needs (critical + nice-to-have)
# - Gaps (available, planned, missing)
# - Integration plan (phased approach)
```

**Deliverables**:
- `analysis/gap-analysis.md` - Detailed gap breakdown
- `analysis/integration-plan.md` - Phased migration plan
- `analysis/EXECUTIVE-SUMMARY.md` - Stakeholder summary

See: [CLAUDE-WORKFLOW-GAP-ANALYSIS.md](examples/CLAUDE-WORKFLOW-GAP-ANALYSIS.md)

## Usage Pattern 3: Multi-Service Comparison

**Goal**: Compare implementations across similar services.

```bash
# Spawn workers for each service
air analyze repos/service-a --background --id=svc-a --focus=architecture
air analyze repos/service-b --background --id=svc-b --focus=architecture
air analyze repos/service-c --background --id=svc-c --focus=architecture

# Wait
air wait --all

# Claude creates comparative analysis:
# - Common patterns
# - Divergences
# - Best practices
# - Recommendations for alignment
```

## Claude Integration

### Workflow Template for Claude

```markdown
1. Create coordination plan (TodoWrite)
2. Spawn workers (`air analyze --background`)
3. Wait for completion (`air wait --all`)
4. Aggregate findings (`air findings --all --format=json`)
5. Synthesize analysis (create analysis/*.md)
6. Report to human
```

### Example Claude Session

```
User: "Analyze integration between auth-sdk library and user-api service"

Claude: I'll coordinate a gap analysis.

[Creates TodoWrite with steps]

[Runs: air status --format=json]
Found: repos/auth-sdk, repos/auth-roadmap, repos/user-api

[Spawns 3 workers via air analyze --background]

[Runs: air wait --all]
Waiting for workers... (blocks until complete)

[Runs: air findings --all --format=json]
[Parses results]

[Creates analysis/gap-analysis.md]
[Creates analysis/integration-plan.md]
[Creates analysis/EXECUTIVE-SUMMARY.md]

Claude: Gap analysis complete!

Key finding: Service needs OAuth2 3 months before library will have it.
Recommendation: Service contributes OAuth2 to library.

See analysis/EXECUTIVE-SUMMARY.md
```

### Adding to CLAUDE.md

Add this to your project's `CLAUDE.md`:

```markdown
## Gap Analysis Workflow

When analyzing library-service integration:

1. Check resources: `air status`
2. Spawn workers for each resource: `air analyze --background`
3. Wait: `air wait --all`
4. Aggregate: `air findings --all --format=json`
5. Create gap analysis in `analysis/gap-analysis.md`
6. Create integration plan in `analysis/integration-plan.md`
7. Create executive summary in `analysis/EXECUTIVE-SUMMARY.md`

See: docs/examples/CLAUDE-WORKFLOW-GAP-ANALYSIS.md for details.
```

## Architecture Decisions

### Why Not Build a "Director Agent"?

**We considered** building a custom director agent layer that orchestrates workers.

**We chose** to rely on Claude's native capabilities because:
1. ✅ Claude can already plan multi-step workflows
2. ✅ Claude can spawn processes via shell commands
3. ✅ Claude can parse JSON and synthesize findings
4. ✅ Simpler architecture (fewer moving parts)
5. ✅ More flexible (Claude adapts to different scenarios)

**AIR's role**: Provide coordination primitives
- `air analyze --background` - Spawn workers
- `air status --agents` - Monitor progress
- `air wait --all` - Block until complete
- `air findings --all` - Aggregate results

**Claude's role**: Strategic coordination
- Plan workflow
- Spawn workers
- Monitor/wait
- Synthesize findings
- Create strategic analysis

### Why `air wait` Command?

**Problem**: Claude would need polling loop:
```bash
while true; do
  STATUS=$(air status --agents --format=json)
  # Check if complete...
  sleep 5
done
```

**Solution**: Blocking wait command:
```bash
air wait --all  # Blocks until all agents complete
```

**Benefits**:
- ✅ Cleaner Claude logic
- ✅ Less shell scripting
- ✅ Better error handling
- ✅ Timeout support

## Implementation Status

### v0.6.0 (Current)
- ✅ `air analyze --background` - Spawn workers
- ✅ `air status --agents` - Monitor agents
- ✅ `air findings --all` - Aggregate findings
- ✅ `air wait` - Block until agents complete
- ✅ Cross-platform process checking (psutil)
- ✅ Auto-update agent status when processes exit
- ✅ Workflow documentation for Claude

### Future Enhancements

**v0.7.0** (Optional):
- `air orchestrate` - One-command pattern execution
- Analysis templates (gap-analysis, comparison, security-audit)
- Better progress indicators
- Agent dependency graphs

**Not planned**:
- ❌ Custom director agent infrastructure (Claude does this)
- ❌ Complex agent coordination layers (keep it simple)
- ❌ Agent-to-agent communication (workers are independent)

## Best Practices

### For Humans

**Do**:
- ✅ Use clear agent IDs: `--id=security-auth-service` not `--id=agent1`
- ✅ Give Claude clear objectives in CLAUDE.md
- ✅ Review Claude's coordination plan before execution
- ✅ Check `air status --agents` to see what happened

**Don't**:
- ❌ Spawn too many workers (>10) - can overwhelm system
- ❌ Reuse agent IDs while agents running
- ❌ Modify files while agents analyzing

### For Claude

**Do**:
- ✅ Use TodoWrite to track coordination workflow
- ✅ Use `air wait --all` instead of polling
- ✅ Parse JSON findings programmatically
- ✅ Be specific in analysis (exact features, timelines)
- ✅ Create phased plans (not all-or-nothing)

**Don't**:
- ❌ Skip the coordination plan
- ❌ Poll manually when `air wait` exists
- ❌ Be vague in gap analysis
- ❌ Ignore risk mitigation

## Examples

See `docs/examples/` for complete examples:
- `director-gap-analysis.md` - Conceptual director pattern
- `claude-gap-analysis-pattern.md` - Claude-native pattern
- `CLAUDE-WORKFLOW-GAP-ANALYSIS.md` - Step-by-step workflow

## Troubleshooting

### Agents Stuck in "Running"

**Before v0.6.0**: Status didn't update when process died

**v0.6.0+**: `air status --agents` auto-detects dead processes and updates status

### Workers Fail Silently

Check logs:
```bash
cat .air/agents/<agent-id>/stderr.log
```

### Coordination Workflow Breaks

Claude can read task files to recover:
```bash
cat .air/tasks/20251004-*.md
```

Then resume from last successful step.

## Summary

**AIR provides**: Coordination substrate (spawn, monitor, aggregate)

**Claude provides**: Strategic coordination (plan, synthesize, decide)

**Result**: Powerful multi-agent workflows without complex infrastructure.

---

**Next**: See [parallel-analysis-quickstart.md](tutorials/parallel-analysis-quickstart.md) for hands-on tutorial.
