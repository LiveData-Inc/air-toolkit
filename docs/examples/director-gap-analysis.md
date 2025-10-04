# Director Agent: Library-Service Gap Analysis

## Purpose

Coordinate gap analysis between a library and a service that wants to adopt it.

## Scenario

- **Library**: Provides functionality (current + roadmap)
- **Service**: Wants to adopt library (has requirements + concerns)
- **Goal**: Identify gaps, create integration plan, suggest contributions

## Agent Workflow

### Phase 1: Parallel Understanding

Spawn 3 worker agents to analyze independently:

```bash
# Worker 1: Library capabilities (current state)
air analyze repos/library --background \
  --id=worker-lib-current \
  --focus=capabilities

# Worker 2: Library roadmap (future state)
air analyze repos/library-roadmap --background \
  --id=worker-lib-future \
  --focus=roadmap

# Worker 3: Service requirements
air analyze repos/service --background \
  --id=worker-service-reqs \
  --focus=requirements
```

**Wait for workers to complete:**
```bash
# Poll every 30 seconds
while true; do
  STATUS=$(air status --agents --format=json)
  RUNNING=$(echo $STATUS | jq '.agents[] | select(.status=="running") | .id')

  if [ -z "$RUNNING" ]; then
    echo "All workers complete"
    break
  fi

  echo "Waiting for: $RUNNING"
  sleep 30
done
```

### Phase 2: Comparative Analysis

Director performs gap analysis:

```markdown
## Gap Analysis Checklist

For each service requirement:
1. Is it available in library now? → analysis/library-assessment.md
2. Is it planned in roadmap? → analysis/library-roadmap.md
3. When is it planned? → Extract timeline
4. If not planned, could service contribute?

Categories:
- ✅ Available now - Use immediately
- 🟡 Planned soon - Wait or contribute to accelerate
- 🔴 Not planned - Service must contribute or find alternative
- ⚠️ Blocker - Library change would break service
```

**Director creates:**
- `analysis/gap-analysis.md` - Detailed gap breakdown
- `analysis/integration-plan.md` - Phased migration plan
- `analysis/contribution-opportunities.md` - What service could contribute

### Phase 3: Strategic Planning

Director synthesizes findings into actionable plan:

```markdown
# Integration Plan Template

## Executive Summary
[One paragraph: Current situation, key gaps, recommended approach]

## Current State
### Library Capabilities (Current)
- Feature 1
- Feature 2

### Library Roadmap (Planned)
- Feature X (Q2 2025)
- Feature Y (Q3 2025)

### Service Requirements
- Critical: [...]
- Important: [...]
- Nice-to-have: [...]

## Gap Analysis

### Available Now
[Features service needs that library has]

### Available Soon
[Features service needs that are planned]

### Missing
[Features service needs that aren't planned]

### Blockers
[Library changes that would break service]

## Recommended Approach

### Option 1: Wait for Library Roadmap
- Timeline: [...]
- Pros: [...]
- Cons: [...]
- Recommendation: [When to choose this]

### Option 2: Contribute to Library
- What to contribute: [...]
- Timeline: [...]
- Pros: [...]
- Cons: [...]
- Recommendation: [When to choose this]

### Option 3: Hybrid Approach (Recommended)
- Phase 1: Adopt what's available now
- Phase 2: Contribute critical missing features
- Phase 3: Adopt roadmap features when available
- Timeline: [...]
- Pros: [...]
- Cons: [...]

## Phased Integration Plan

### Phase 1: Quick Wins (Week 1-2)
- [ ] Adopt feature X
- [ ] Replace service code Y with library
- Risk: Low
- Benefit: Immediate value

### Phase 2: Contributions (Month 1-2)
- [ ] Implement missing feature Z
- [ ] Submit PR to library
- Risk: Medium
- Benefit: Get features when needed

[... continue with phases ...]

## Success Metrics
- [ ] Metric 1
- [ ] Metric 2

## Risk Mitigation
1. **Risk**: Library team rejects contributions
   - Mitigation: [...]
   - Fallback: [...]

2. **Risk**: Timeline slips
   - Mitigation: [...]
   - Fallback: [...]

## Next Steps
1. [ ] Review plan with stakeholders
2. [ ] Engage library maintainers
3. [ ] Begin Phase 1
```

### Phase 4: Output Generation

Director creates all deliverables:

```bash
# Create comprehensive documentation
analysis/
├── library-assessment.md       # From worker-lib-current
├── library-roadmap.md          # From worker-lib-future
├── service-requirements.md     # From worker-service-reqs
├── gap-analysis.md             # Director synthesis
├── integration-plan.md         # Director recommendation
└── EXECUTIVE-SUMMARY.md        # Director high-level report

# Create contribution proposals (if applicable)
contributions/
└── library/
    ├── oauth2-implementation-proposal.md
    └── migration-guide-contribution.md
```

## Director Agent Instructions

```markdown
# You are the Gap Analysis Director Agent

## Your Mission
Coordinate analysis of a library and service to identify integration gaps and create actionable plans.

## Phase 1: Understanding (Parallel)

1. Identify resources:
   ```bash
   air status --format=json
   ```

2. Spawn workers for each resource:
   - Library current state → capabilities analysis
   - Library roadmap → future plans
   - Service → requirements and concerns

3. Monitor workers:
   ```bash
   air status --agents --format=json
   ```

4. Wait for all workers to complete

## Phase 2: Gap Analysis (Sequential)

1. Load worker findings:
   ```bash
   air findings --all --format=json
   ```

2. For each service requirement, determine:
   - Available in library now?
   - Planned in library roadmap? When?
   - Not planned → contribution opportunity?
   - Blocker → compatibility issue?

3. Categorize gaps:
   - ✅ Available now
   - 🟡 Planned (extract timeline)
   - 🔴 Not planned (contribution needed)
   - ⚠️ Blocker (compatibility risk)

4. Create `analysis/gap-analysis.md` with detailed breakdown

## Phase 3: Planning (Strategic)

1. Generate integration options:
   - Option 1: Wait for library
   - Option 2: Contribute to library
   - Option 3: Hybrid approach (usually best)

2. Create phased plan:
   - Phase 1: Quick wins (adopt what's ready)
   - Phase 2: Contributions (build what's missing)
   - Phase 3+: Adopt roadmap features over time

3. Identify success metrics and risks

4. Create `analysis/integration-plan.md`

## Phase 4: Synthesis (Communication)

1. Create executive summary for stakeholders
2. Identify contribution opportunities
3. Generate recommendations with pros/cons
4. Create `analysis/EXECUTIVE-SUMMARY.md`

## Output Requirements

### Must Create
- `analysis/gap-analysis.md` - Detailed gap breakdown
- `analysis/integration-plan.md` - Phased approach
- `analysis/EXECUTIVE-SUMMARY.md` - High-level summary

### Should Create (if applicable)
- `contributions/library/feature-proposal.md` - Features service could contribute
- `analysis/risk-assessment.md` - Detailed risk analysis
- `analysis/timeline-comparison.md` - Service needs vs library roadmap

## Key Principles

1. **Be specific**: Don't say "some features missing", list exact features
2. **Include timelines**: When is it planned? When does service need it?
3. **Show opportunities**: What can service contribute to accelerate?
4. **Mitigate risks**: What if library team says no? What if timeline slips?
5. **Phased approach**: Don't recommend all-or-nothing, show incremental path

## Example Output Snippet

```markdown
## Gap: OAuth2 Support

**Service needs**: OAuth2 for third-party integrations (Critical, needed by Q2 2025)
**Library status**: Planned for v3.0 (Q2 2025)
**Gap severity**: 🟡 Planned but timing is tight

**Options**:
1. Wait for library v3.0 (Risk: Timeline slip delays service)
2. Service contributes OAuth2 to library (Risk: Library team rejects)
3. **Recommended**: Engage library team now, offer to contribute, align on design

**Action items**:
- [ ] Contact library maintainers (Week 1)
- [ ] Propose OAuth2 implementation approach (Week 2)
- [ ] Get buy-in before coding (Week 3)
- [ ] Implement if approved OR wait if team prefers (Week 4+)
```

## Success Criteria

Your analysis is successful if:
- ✅ All gaps between library and service are identified
- ✅ Each gap has timeline and severity
- ✅ Multiple integration options are presented
- ✅ Recommended approach is phased and pragmatic
- ✅ Contribution opportunities are identified
- ✅ Risks are identified with mitigation strategies
- ✅ Executive summary is concise and actionable
```

## Example Invocation

```bash
# Setup project
air init auth-integration --mode=mixed
cd auth-integration

# Link resources
air link add ~/libs/auth-sdk --type=review
air link add ~/libs/auth-sdk/docs --type=review --name=auth-roadmap
air link add ~/services/user-api --type=develop

# Invoke director agent (via Claude Code)
# Director reads: docs/examples/director-gap-analysis.md
# Director executes: phases 1-4
# Director outputs: analysis/*, contributions/*

# Human reviews
air status
cat analysis/EXECUTIVE-SUMMARY.md
cat analysis/integration-plan.md
```

## Variations

### Variation 1: Multiple Services, One Library
```
Library: auth-sdk
Services: user-api, billing-api, admin-api

Director spawns:
- 1 worker for library
- 1 worker for roadmap
- 3 workers for services

Gap analysis per service:
- Which services have same gaps? (Common needs → higher priority contribution)
- Which services can migrate first? (Least gaps → early adopter)
- Which services should wait? (Most gaps → later migration)
```

### Variation 2: Multiple Libraries, One Service
```
Service: user-api
Libraries: auth-sdk, logging-sdk, metrics-sdk

Director spawns:
- 3 workers for libraries
- 1 worker for service

Gap analysis:
- Which library to adopt first? (Best fit)
- Are there conflicts between libraries? (Integration issues)
- Can service use subset of each? (Partial adoption)
```

### Variation 3: Library Migration (Old → New)
```
Old Library: legacy-auth v1.x
New Library: modern-auth v2.x
Service: Currently using legacy-auth

Gap analysis:
- What does service use from legacy?
- Does modern equivalent exist in new?
- What's the migration path?
- Breaking changes impact?
```

## Related Patterns

- **Parallel Analysis**: Workers analyze independently
- **Comparative Analysis**: Director compares findings
- **Contribution Planning**: Identify opportunities for service to contribute
- **Phased Migration**: Incremental adoption plan

## Next Steps

1. Test this pattern with real library-service pair
2. Refine director agent instructions based on results
3. Create templates for common gap analysis scenarios
4. Build `air gap-analysis` command to automate setup
