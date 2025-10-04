# Gap Analysis Pattern for Claude Code

**No custom director needed** - Claude Code can coordinate this workflow directly.

## Pattern Overview

Human gives Claude a high-level goal. Claude:
1. Creates coordination plan (using TodoWrite)
2. Spawns worker processes via AIR commands
3. Monitors workers until complete
4. Aggregates findings
5. Creates gap analysis and integration plan

## Instructions for Claude

Add to your project's `CLAUDE.md`:

```markdown
## Gap Analysis Workflow

When asked to analyze integration between a library and service:

### Step 1: Create Coordination Plan

Use TodoWrite to track your work:
```
1. Understand project resources (air status)
2. Spawn parallel analysis workers
3. Monitor worker completion
4. Aggregate findings
5. Perform gap analysis
6. Create integration plan
```

### Step 2: Spawn Workers in Parallel

Launch background analyses:
```bash
# Analyze library current state
air analyze repos/library --background --id=lib-current --focus=capabilities

# Analyze library roadmap
air analyze repos/library-roadmap --background --id=lib-future --focus=roadmap

# Analyze service requirements
air analyze repos/service --background --id=service-reqs --focus=requirements
```

### Step 3: Monitor Until Complete

Check status periodically:
```bash
air status --agents --format=json
```

When all agents show status="complete", proceed to next step.

### Step 4: Aggregate Findings

Load all worker results:
```bash
air findings --all --format=json
```

### Step 5: Gap Analysis

For each service requirement, determine:
- ✅ Available in library now?
- 🟡 Planned in library roadmap? When?
- 🔴 Not planned → contribution opportunity?
- ⚠️ Blocker → compatibility concern?

Create `analysis/gap-analysis.md` with:
- Service requirements (critical/important/nice-to-have)
- Library capabilities (current/planned/missing)
- Gaps identified with severity
- Timeline analysis

### Step 6: Integration Planning

Create `analysis/integration-plan.md` with:

1. **Current State**: What's available now
2. **Gap Summary**: What's missing and when it's planned
3. **Options**:
   - Option 1: Wait for library roadmap
   - Option 2: Service contributes to library
   - Option 3: Hybrid (adopt now + contribute gaps)
4. **Recommended Approach**: Phased plan
5. **Risk Mitigation**: What if timelines slip?

### Step 7: Executive Summary

Create `analysis/EXECUTIVE-SUMMARY.md`:
- One paragraph situation
- Key gaps identified
- Recommended approach
- Timeline estimate
- Success metrics

## Example Session

```
User: "Analyze integration between auth-sdk library and user-api service"

Claude: I'll coordinate a gap analysis. Let me start by understanding the project.

[Runs: air status]

Claude: Found 3 resources:
- repos/auth-sdk (library)
- repos/auth-roadmap (library docs)
- repos/user-api (service)

[Creates TodoWrite plan with 7 steps]

Claude: Spawning 3 worker agents to analyze in parallel...

[Spawns background agents via air analyze]

Claude: Workers started. Monitoring progress...

[Polls air status --agents every 30 seconds]

Claude: All workers complete. Aggregating findings...

[Loads findings via air findings --all]

Claude: Creating gap analysis...

[Writes analysis/gap-analysis.md]

Gap identified: Service needs OAuth2 (critical), library plans it for v3.0 Q2 2025.
Recommendation: Service could contribute OAuth2 implementation to accelerate.

[Writes analysis/integration-plan.md]

Claude: Created integration plan with 5 phases:
1. Adopt current features (Week 1-2)
2. Contribute OAuth2 to library (Month 1-2)
3. Beta test library v3.0 (Month 3)
4. Full adoption (Month 4-5)

[Writes analysis/EXECUTIVE-SUMMARY.md]

Claude: Gap analysis complete. See analysis/EXECUTIVE-SUMMARY.md
```
```

## AIR Commands Needed

Claude uses these commands (all already available):

```bash
# Understand project
air status --format=json

# Spawn workers (runs in background)
air analyze <path> --background --id=<worker-id> --focus=<focus-area>

# Monitor workers
air status --agents --format=json

# Aggregate findings
air findings --all --format=json

# Check worker logs if needed
cat .air/agents/<worker-id>/stdout.log
cat .air/agents/<worker-id>/stderr.log
```

## Why This Works Without Custom Director

**Claude already has:**
- ✅ Planning ability (TodoWrite for coordination tasks)
- ✅ Process spawning (Bash tool with `--background`)
- ✅ Monitoring (can poll `air status --agents`)
- ✅ Synthesis (reads JSON, creates analysis docs)
- ✅ Multi-step coordination (follows workflow)

**AIR provides:**
- ✅ Worker spawning (`air analyze --background`)
- ✅ Status tracking (`.air/agents/*/metadata.json`)
- ✅ Findings aggregation (`air findings --all`)
- ✅ Project organization (repos, analysis directories)

**Result:** Claude + AIR = Coordinated gap analysis, no extra infrastructure needed.

## Enhancements to Make This Smoother

### Enhancement 1: Better Monitoring

Currently Claude has to poll. We could add:

```bash
# Wait for all agents to complete
air wait --agents worker-1,worker-2,worker-3

# Or wait for all
air wait --all-agents
```

This blocks until workers finish, so Claude doesn't need polling loop.

### Enhancement 2: Analysis Templates

Provide templates for common outputs:

```bash
# Generate gap analysis from findings
air gap-analysis \
  --library=repos/library \
  --service=repos/service \
  --output=analysis/gap-analysis.md
```

Claude can still review and customize, but starts with structure.

### Enhancement 3: Workflow Helpers

```bash
# Spawn all analyses for gap analysis pattern
air orchestrate gap-analysis \
  --library=repos/library \
  --service=repos/service

# Spawns appropriate workers, waits, generates template
# Claude then fills in strategic analysis
```

## Template: Gap Analysis Prompt

To make it easy for humans to invoke, provide this template:

```markdown
# Gap Analysis Request

Analyze integration between:
- **Library**: repos/auth-sdk (current state)
- **Roadmap**: repos/auth-roadmap (future plans)
- **Service**: repos/user-api (integration candidate)

**Goal**: Identify gaps, create integration plan, suggest contributions.

**Deliverables**:
1. `analysis/gap-analysis.md` - Detailed gap breakdown
2. `analysis/integration-plan.md` - Phased migration plan
3. `analysis/EXECUTIVE-SUMMARY.md` - High-level summary

**Workflow**:
1. Spawn 3 workers to analyze library (current/future) and service
2. Monitor workers until complete
3. Aggregate findings
4. Perform gap analysis (what service needs vs what library provides)
5. Create phased integration plan with options
6. Identify contribution opportunities

Please coordinate this analysis.
```

Human just pastes this, Claude executes the workflow.

## Real Example

```bash
# Human setup
mkdir auth-integration && cd auth-integration
air init . --mode=mixed
air link add ~/libs/auth-sdk --type=review
air link add ~/libs/auth-sdk/docs --type=review --name=roadmap
air link add ~/services/user-api --type=develop

# Human invokes Claude
# Pastes gap analysis template from above

# Claude executes (no human intervention needed):
# 1. Creates coordination plan (TodoWrite)
# 2. Spawns: air analyze repos/auth-sdk --background --id=lib-current
# 3. Spawns: air analyze repos/roadmap --background --id=lib-future
# 4. Spawns: air analyze repos/user-api --background --id=service-reqs
# 5. Monitors: air status --agents (polls until complete)
# 6. Aggregates: air findings --all --format=json
# 7. Creates: analysis/gap-analysis.md (detailed gaps)
# 8. Creates: analysis/integration-plan.md (phased approach)
# 9. Creates: analysis/EXECUTIVE-SUMMARY.md (one-pager)
# 10. Reports: "Gap analysis complete, see analysis/"

# Human reviews results
cat analysis/EXECUTIVE-SUMMARY.md
```

## Key Insight

**You don't need a director agent - Claude IS the director.**

Just provide:
1. Clear workflow pattern (in CLAUDE.md or prompt)
2. AIR commands for coordination (already exist)
3. Templates for deliverables (optional but helpful)

Claude's native capabilities + AIR's coordination primitives = Powerful multi-agent workflows.
