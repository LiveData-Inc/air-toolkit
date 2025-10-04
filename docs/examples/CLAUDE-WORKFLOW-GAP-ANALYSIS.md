# Claude Workflow: Library-Service Gap Analysis

**Add this to your project's CLAUDE.md when doing gap analysis.**

## When to Use This Workflow

Use when analyzing integration between:
- A library (with current features + roadmap)
- A service that wants to adopt the library

## Workflow Steps

### Step 1: Understand the Project

```bash
# Check what resources are available
air status --format=json
```

Expected resources:
- Library current state (e.g., `repos/auth-sdk`)
- Library roadmap/docs (e.g., `repos/auth-roadmap`)
- Service to integrate (e.g., `repos/user-api`)

### Step 2: Create Coordination Plan

Use TodoWrite to track the workflow:

```
Todo List:
1. Spawn parallel analysis workers
2. Wait for workers to complete
3. Aggregate findings
4. Perform gap analysis
5. Create integration plan
6. Generate executive summary
```

### Step 3: Spawn Workers in Parallel

Launch background analyses for each resource:

```bash
# Analyze library current state
air analyze repos/library --background \
  --id=lib-current \
  --focus=capabilities

# Analyze library roadmap
air analyze repos/library-roadmap --background \
  --id=lib-future \
  --focus=roadmap

# Analyze service requirements
air analyze repos/service --background \
  --id=service-reqs \
  --focus=requirements
```

Mark step 1 complete, move to step 2.

### Step 4: Wait for Workers

```bash
# Block until all workers complete
air wait --all
```

This command waits until all background agents finish. No polling needed!

Mark step 2 complete, move to step 3.

### Step 5: Aggregate Findings

```bash
# Get all findings as JSON
air findings --all --format=json
```

Parse the JSON to understand:
- What the library currently provides
- What the library plans to add (from roadmap)
- What the service requires
- What the service is concerned about

Mark step 3 complete, move to step 4.

### Step 6: Perform Gap Analysis

Create `analysis/gap-analysis.md` by comparing:

For each service requirement:
- ✅ **Available now**: In library current capabilities
- 🟡 **Planned**: In library roadmap (note timeline)
- 🔴 **Missing**: Not in library current or roadmap
- ⚠️ **Blocker**: Library changes that would break service

Example structure:

```markdown
# Gap Analysis: Library vs Service

## Service Requirements

### Critical
- OAuth2 support → 🔴 Missing (planned v3.0 Q2 2025)
- Rate limiting → ✅ Available now

### Important
- SSO integration → 🟡 Planned (v3.0 Q2 2025)
- Audit logging → 🟡 Planned (v3.1 Q3 2025)

### Nice-to-Have
- Multi-tenancy → 🔴 Missing (not planned)

## Timeline Analysis

Service timeline:
- Needs OAuth2 by: Q1 2025
- Wants SSO by: Q2 2025

Library timeline:
- OAuth2 available: Q2 2025 (3 months late!)
- SSO available: Q2 2025 (on time)

## Gap Summary

**Critical blocker**: OAuth2 is 3 months late for service needs.

**Options**:
1. Service waits → delays service launch
2. Service contributes OAuth2 → accelerates library timeline
3. Service uses temporary workaround → technical debt

See integration plan for recommendation.
```

Mark step 4 complete, move to step 5.

### Step 7: Create Integration Plan

Create `analysis/integration-plan.md` with phased approach:

```markdown
# Integration Plan: Service Adoption of Library

## Recommended Approach: Phased + Contribution

### Phase 1: Quick Wins (Week 1-2)
**Goal**: Adopt what's ready now

- [ ] Replace homegrown JWT with library JWT
- [ ] Adopt rate limiting from library
- [ ] Test session management

**Risk**: Low - stable features
**Benefit**: Immediate maintenance reduction

### Phase 2: Contribute OAuth2 (Month 1-2)
**Goal**: Fill critical gap

- [ ] Service team implements OAuth2 for library
- [ ] Submit PR to library maintainers
- [ ] Work with maintainers on review/merge

**Risk**: Medium - requires library team buy-in
**Benefit**:
- Get OAuth2 when needed (vs 3 months late)
- Help open source community
- Influence design

**Mitigation**:
- Engage library maintainers BEFORE coding
- Align on design/API first
- Be prepared to maintain if not merged

### Phase 3: Beta Test v3.0 (Month 3)
**Goal**: Early SSO access

- [ ] Integrate v3.0-beta with OAuth2 (contributed)
- [ ] Test SSO integration
- [ ] Provide feedback to library team

**Risk**: Medium - beta stability
**Benefit**: Early access to SSO, influence final release

### Phase 4: Full Migration (Month 4-5)
**Goal**: Complete adoption

- [ ] Switch to library v3.0 stable
- [ ] Remove all legacy auth code
- [ ] Document migration for future teams

**Risk**: Low - proven integration
**Benefit**: 80% reduction in auth maintenance

## Success Metrics

- [ ] Reduce auth codebase by 80%
- [ ] OAuth2 available by Month 3 (not Month 6)
- [ ] Zero auth-related incidents during migration
- [ ] 2+ features contributed to library

## Alternative: Wait for Library

If contributing is not feasible:

- Use temporary OAuth2 workaround (Month 1-3)
- Adopt library v3.0 when released (Month 6+)
- Accept 3-month delay
- Technical debt from workaround

**Not recommended** - delays service, creates debt.
```

Mark step 5 complete, move to step 6.

### Step 8: Generate Executive Summary

Create `analysis/EXECUTIVE-SUMMARY.md` for stakeholders:

```markdown
# Executive Summary: Auth Library Integration

## Situation

Service needs to replace homegrown auth with **auth-sdk** library to reduce maintenance burden.

## Gap Identified

**Critical blocker**: Service needs OAuth2 by Q1 2025, but library won't have it until Q2 2025 (3-month gap).

## Recommendation

**Phased migration with contribution**:
1. Adopt stable features immediately (Week 1-2)
2. Service team contributes OAuth2 to library (Month 1-2)
3. Benefit from early v3.0 access (Month 3+)
4. Complete migration (Month 4-5)

## Benefits

- ✅ Get OAuth2 when needed (not 3 months late)
- ✅ Reduce auth code by 80%
- ✅ Contribute to open source
- ✅ Influence library design

## Timeline

- **Week 1-2**: Quick wins (stable features)
- **Month 1-2**: OAuth2 contribution
- **Month 3**: Beta testing v3.0
- **Month 4-5**: Full migration

## Next Steps

1. [ ] Get stakeholder approval for contribution approach
2. [ ] Engage library maintainers on OAuth2 design
3. [ ] Begin Phase 1 (quick wins)

See `analysis/integration-plan.md` for detailed plan.
```

Mark step 6 complete.

### Step 9: Report to Human

```
Gap analysis complete!

Created:
- analysis/gap-analysis.md (detailed gaps)
- analysis/integration-plan.md (phased approach)
- analysis/EXECUTIVE-SUMMARY.md (stakeholder summary)

Key finding: Service needs OAuth2 3 months before library will have it.
Recommendation: Service contributes OAuth2 to library (mutual benefit).

See EXECUTIVE-SUMMARY.md for details.
```

## Complete Example Session

```
Human: "Analyze integration between auth-sdk library and user-api service"

Claude: I'll coordinate a gap analysis between the library and service.

[Runs: air status]

Claude: Found 3 resources:
- repos/auth-sdk (library current)
- repos/auth-roadmap (library plans)
- repos/user-api (service)

[Creates TodoWrite with 6 steps]

Claude: Step 1/6 - Spawning 3 worker agents...

[Runs:]
air analyze repos/auth-sdk --background --id=lib-current --focus=capabilities
air analyze repos/auth-roadmap --background --id=lib-future --focus=roadmap
air analyze repos/user-api --background --id=service-reqs --focus=requirements

Claude: Workers started. Waiting for completion...

[Runs: air wait --all]
[Blocks until workers finish]

Claude: Step 2/6 complete - All workers finished

[Runs: air findings --all --format=json]
[Reads findings]

Claude: Step 3/6 complete - Findings aggregated

Claude: Step 4/6 - Performing gap analysis...

[Creates analysis/gap-analysis.md]

Claude: Gap identified: Service needs OAuth2 by Q1 2025, library plans Q2 2025 (3-month gap)

Claude: Step 5/6 - Creating integration plan...

[Creates analysis/integration-plan.md with phased approach]

Claude: Recommendation: Service contributes OAuth2 to accelerate timeline

Claude: Step 6/6 - Generating executive summary...

[Creates analysis/EXECUTIVE-SUMMARY.md]

Claude: Gap analysis complete!

Created:
- analysis/gap-analysis.md
- analysis/integration-plan.md
- analysis/EXECUTIVE-SUMMARY.md

Key finding: OAuth2 timing gap (3 months)
Recommendation: Service contributes to library (mutual benefit)

Next step: Review EXECUTIVE-SUMMARY.md and discuss with stakeholders.
```

## Tips for Claude

### Do:
- ✅ Use TodoWrite to track workflow progress
- ✅ Use `air wait --all` instead of polling
- ✅ Parse JSON findings programmatically
- ✅ Be specific in gap analysis (exact features, exact timelines)
- ✅ Provide multiple options (wait, contribute, hybrid)
- ✅ Include risk mitigation strategies

### Don't:
- ❌ Skip the TodoWrite plan
- ❌ Poll `air status --agents` manually (use `air wait`)
- ❌ Be vague about gaps ("some features missing")
- ❌ Recommend all-or-nothing approaches
- ❌ Ignore timeline mismatches

## Extending the Pattern

### Multiple Services, One Library

Spawn one worker per service:
```bash
air analyze repos/library --background --id=lib-current
air analyze repos/service-a --background --id=service-a-reqs
air analyze repos/service-b --background --id=service-b-reqs
air analyze repos/service-c --background --id=service-c-reqs
air wait --all
```

Gap analysis: Which service should migrate first? (Least gaps)

### Multiple Libraries, One Service

Spawn one worker per library:
```bash
air analyze repos/lib-a --background --id=lib-a-caps
air analyze repos/lib-b --background --id=lib-b-caps
air analyze repos/service --background --id=service-reqs
air wait --all
```

Gap analysis: Which library is best fit? Can service use both?

## Human Prompt Template

Humans can use this template to invoke the workflow:

```
Analyze integration between library and service:

Library (current): repos/auth-sdk
Library (roadmap): repos/auth-roadmap
Service: repos/user-api

Goal: Identify gaps, create integration plan, recommend contribution opportunities.

Deliverables:
1. analysis/gap-analysis.md
2. analysis/integration-plan.md
3. analysis/EXECUTIVE-SUMMARY.md

Follow the gap analysis workflow.
```

Claude reads this, executes the workflow, creates deliverables.
