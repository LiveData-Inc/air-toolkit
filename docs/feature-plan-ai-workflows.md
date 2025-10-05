# AIR Feature Plan: AI-First Development Workflows

**Created:** 2025-10-04
**Inspired by:** Claude Code team workflows (Anthropic)
**Status:** Planning

## Executive Summary

This plan proposes enhancements to AIR that enable AI-first assessment workflows while preserving AIR's core mission: rigorous, documented codebase analysis. Features are categorized by priority and aligned with AIR's strengths rather than blindly copying Claude Code's production development approach.

## Guiding Principles

1. **Analysis rigor over speed** - Don't sacrifice thoroughness for velocity
2. **Structured documentation** - Preserve audit trails and reasoning
3. **AI as assistant, human as validator** - Maintain accountability
4. **Budget-conscious design** - Not everyone has unlimited AI access
5. **Read-only respect** - Never compromise the safety of reviewed codebases

## Priority 1: Core Workflow Enhancements

### 1.1 Parallel Analysis Agents (`air analyze --parallel`)

**Inspiration:** Claude Code's 25% of users running multiple agents in parallel

**Feature:**
```bash
air analyze --parallel repos/service-a repos/service-b repos/service-c
```

**Behavior:**
- Launch separate Claude Code agents for each repository
- Each agent works independently, creating its own analysis document
- Terminal UI shows progress for all agents (similar to background tasks pill)
- Final summary compares findings across all repos

**Implementation:**
- Extend `air-config.json` with parallel analysis settings
- Create `.air/parallel/` directory for coordination
- Generate comparative analysis in `analysis/reviews/comparison.md`

**Value:**
- Analyze multiple codebases simultaneously
- Natural comparison workflow for similar services
- Faster completion for multi-repo assessments

---

### 1.2 Analysis Prototyping Mode (`air prototype`)

**Inspiration:** Building 5-10 prototypes per day to find the best approach

**Feature:**
```bash
air prototype "analyze authentication patterns"
```

**Behavior:**
- Creates temporary workspace in `.air/prototypes/YYYYMMDD-HHMM-description/`
- Runs rapid analysis WITHOUT creating formal documentation
- Generates lightweight findings for quick review
- Human reviews prototypes and selects best approach
- Promotes selected prototype to formal analysis

**Commands:**
```bash
air prototype list                          # Show all prototypes
air prototype promote <id>                  # Promote to formal analysis
air prototype cleanup --before=2025-09-01   # Remove old prototypes
```

**Value:**
- Experiment with different analysis approaches quickly
- Learn which analytical frameworks work best
- Don't pollute formal analysis with exploratory work

---

### 1.3 Custom Analysis Subagents

**Inspiration:** Claude Code's custom subagents feature

**Feature:**
```bash
air subagent create security-focused
air subagent create architecture-patterns
air subagent create performance-analysis
```

**Implementation:**
- Subagent definitions in `.air/subagents/*.md`
- Similar to Claude Code's subagent markdown format
- Invoked via `air analyze --subagent=security-focused`

**Example Subagent Definition:**
```markdown
# Subagent: Security-Focused Analysis

## Focus Areas
- Authentication and authorization patterns
- Input validation and sanitization
- Secret management
- SQL injection vulnerabilities
- XSS prevention

## Output Format
- Critical findings first
- Risk ratings (High/Medium/Low)
- Code examples with line references
- Remediation recommendations

## Context
Use OWASP Top 10 as framework
```

**Value:**
- Specialized analysis for different concerns
- Reusable analytical frameworks
- Team can share subagent definitions

---

### 1.4 Interactive Analysis Dashboard (`air dashboard`)

**Inspiration:** Claude Code's contextual loading messages and terminal UX innovations

**Feature:**
```bash
air dashboard
```

**Behavior:**
- Live terminal UI showing current analysis state
- Active agent status with contextual messages ("Analyzing database patterns...", "Comparing API designs...")
- Progress indicators for multi-step analyses
- Quick access to toggle detailed view (like Ctrl+T for todos)
- Background analyses shown as pills

**Value:**
- Better visibility into long-running analyses
- More engaging user experience
- Easy to monitor multiple analyses

---

## Priority 2: Enhanced Task Management

### 2.1 Task Templates by Analysis Type

**Inspiration:** Claude Code's minimal but effective task tracking

**Feature:**
```bash
air task new --template=architecture-review "Review payment service"
air task new --template=security-audit "Audit authentication"
air task new --template=comparison "Compare REST implementations"
```

**Templates** in `.air/templates/tasks/`:
- `architecture-review.md`
- `security-audit.md`
- `performance-analysis.md`
- `comparison.md`
- `contribution-prep.md`

**Value:**
- Consistent task structure by analysis type
- Faster task creation
- Built-in checklists for common workflows

---

### 2.2 Task Dependency Tracking

**Inspiration:** Claude Code's todo lists showing "step 2 of 4"

**Feature:**
```yaml
# In task file frontmatter
depends_on:
  - 20251003-1430-analyze-service-a
  - 20251003-1445-analyze-service-b
blocks:
  - 20251004-0900-create-comparison
```

**Commands:**
```bash
air task deps <task-id>        # Show dependency tree
air task ready                 # List tasks ready to start
air task blocked               # List blocked tasks
```

**Value:**
- Clear sequencing for complex assessments
- Prevents starting comparisons before individual analyses
- Better project planning

---

## Priority 3: AI Integration Enhancements

### 3.1 Analysis Review Agent (`air review`)

**Inspiration:** Claude doing first-pass code reviews at Anthropic

**Feature:**
```bash
air review analysis/reviews/service-a.md
```

**Behavior:**
- AI reviews the analysis document for:
  - Completeness (did we cover all stated objectives?)
  - Clarity (is reasoning explained well?)
  - Evidence (are claims backed by code references?)
  - Consistency (any contradictions?)
- Generates review checklist
- Human makes final decision

**Output:**
```markdown
# Analysis Review: service-a.md

## Completeness ✅
- Architecture overview: Complete
- Design patterns: Complete
- Security analysis: **Missing** - No discussion of authentication

## Clarity ⚠️
- Section 3.2: Unclear what "legacy pattern" refers to
- Recommend: Add code example

## Evidence ✅
- 15 code references with line numbers
- All claims traceable

## Recommendations
1. Add security analysis section
2. Clarify "legacy pattern" in section 3.2
3. Consider adding sequence diagram for data flow
```

**Value:**
- Quality control before finalizing analysis
- Catches gaps and inconsistencies
- Improves analysis completeness

---

### 3.2 Smart Context Loading

**Inspiration:** Claude Code's "on distribution" tech stack choice

**Feature:**
Automatically detect codebase languages/frameworks and load appropriate context

**Implementation:**
```bash
air analyze repos/service-a --auto-context
```

**Behavior:**
- Scans repo for `package.json`, `requirements.txt`, `go.mod`, etc.
- Loads framework-specific analysis patterns
- Suggests relevant subagents
- Warns if off-distribution technologies detected

**Example:**
```
Detected: Python 3.11, FastAPI, SQLAlchemy, Pytest
Loading context:
  ✓ Python best practices
  ✓ FastAPI patterns
  ✓ SQLAlchemy security considerations
  ✓ Pytest conventions

Suggested subagents:
  - python-security
  - api-design
  - database-patterns

⚠️  Off-distribution: Custom auth framework (limited AI knowledge)
   Recommendation: Human-led analysis for auth system
```

**Value:**
- Better AI analysis for familiar tech stacks
- Explicit warnings for unusual technologies
- Framework-specific insights

---

### 3.3 Iterative Analysis Mode

**Inspiration:** TDD renaissance - iterate against a concrete target

**Feature:**
```bash
air analyze --iterative repos/service-a
```

**Behavior:**
1. Define analysis objectives upfront (like writing tests first)
2. AI generates initial findings
3. AI self-checks findings against objectives
4. AI refines findings
5. Human validates final output

**Workflow:**
```
> air analyze --iterative repos/service-a

Step 1: Define objectives
- Understand authentication flow
- Identify security vulnerabilities
- Document API design patterns

Step 2: Initial analysis...
[AI analyzes codebase]

Step 3: Self-validation...
✓ Authentication flow: Documented
⚠️ Security vulnerabilities: Only found 2, objective was comprehensive scan
✓ API patterns: Documented

Step 4: Refinement...
[AI does deeper security scan]

Step 5: Final validation...
✓ All objectives met

Human review? (y/n)
```

**Value:**
- Higher quality analyses
- Self-correcting AI behavior
- Clearer success criteria

---

## Priority 4: Collaboration Features

### 4.1 Shared Subagent Library

**Inspiration:** Claude Code teams sharing settings files

**Feature:**
```bash
air subagent pull github:LiveData-Inc/air-subagents
air subagent publish security-focused --to=team-repo
```

**Implementation:**
- Git-based subagent sharing
- Team repository of vetted subagents
- Version control for analytical frameworks

**Value:**
- Consistent analysis across team
- Share expertise via subagents
- Continuous improvement of frameworks

---

### 4.2 Analysis Comparison Tool

**Inspiration:** Multiple prototypes to find best approach

**Feature:**
```bash
air compare analysis/reviews/service-a-v1.md analysis/reviews/service-a-v2.md
```

**Output:**
```markdown
# Analysis Comparison

## Coverage
v1: 5 sections, 2,300 words
v2: 7 sections, 3,100 words
→ v2 adds: Performance Analysis, Testing Strategy

## Findings
v1: 12 issues identified
v2: 18 issues identified
→ v2 found 6 additional security concerns

## Code References
v1: 23 references
v2: 34 references
→ v2 has 48% more evidence

## Recommendation
Use v2 as base, consider adding v1's clearer architecture diagrams
```

**Value:**
- Learn which analytical approaches work better
- Combine strengths of different analyses
- Evidence-based improvement of methodology

---

## Priority 5: Developer Experience

### 5.1 Analysis Checkpoints

**Inspiration:** Claude Code's compile-time flags and minimal feature flags

**Feature:**
```bash
air checkpoint save "completed-architecture-section"
air checkpoint list
air checkpoint restore "completed-architecture-section"
```

**Behavior:**
- Save analysis state at key points
- Roll back if analysis goes off track
- Experiment fearlessly with different approaches

**Value:**
- Undo for analysis work
- Safe experimentation
- Recovery from AI hallucinations

---

### 5.2 Analysis Metrics Dashboard

**Inspiration:** Claude Code's BigQuery monitoring dashboards

**Feature:**
```bash
air metrics
```

**Output:**
```
AIR Metrics - AA-test-review

Analysis Progress:
  Repositories reviewed: 2/3 (67%)
  Total findings: 34
  Code references: 89

Task Status:
  Completed: 5
  In Progress: 1
  Pending: 2

Time Tracking:
  Total analysis time: 8.5 hours
  Average per repo: 4.25 hours

Coverage:
  Architecture: 100%
  Security: 67%
  Performance: 33%
  Testing: 100%

AI Usage (est.):
  Total tokens: ~450K
  Cost estimate: $12.50
```

**Value:**
- Track assessment progress
- Identify coverage gaps
- Budget AI costs
- Report to stakeholders

---

### 5.3 Quick Analysis Snippets

**Inspiration:** Claude Code's vibe coding and rapid prototyping

**Feature:**
```bash
air snippet "find all API endpoints"
air snippet "security quick scan"
air snippet "list all database queries"
```

**Behavior:**
- Pre-defined quick analyses
- Results to terminal, not formal docs
- Fast answers to specific questions
- Can be promoted to formal analysis if useful

**Example:**
```bash
> air snippet "find all API endpoints" repos/service-a

Found 23 API endpoints:

GET    /api/users
POST   /api/users
GET    /api/users/:id
PUT    /api/users/:id
DELETE /api/users/:id
...

Add to formal analysis? (y/n)
```

**Value:**
- Quick answers during analysis
- Exploratory investigation
- Lightweight alternative to full analysis

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- [ ] Parallel analysis agents
- [ ] Analysis prototyping mode
- [ ] Task templates

### Phase 2: AI Enhancement (Weeks 5-8)
- [ ] Custom subagents
- [ ] Analysis review agent
- [ ] Smart context loading

### Phase 3: Workflow Optimization (Weeks 9-12)
- [ ] Interactive dashboard
- [ ] Task dependency tracking
- [ ] Iterative analysis mode

### Phase 4: Collaboration (Weeks 13-16)
- [ ] Shared subagent library
- [ ] Analysis comparison tool
- [ ] Analysis checkpoints

### Phase 5: Polish (Weeks 17-20)
- [ ] Analysis metrics dashboard
- [ ] Quick analysis snippets
- [ ] Documentation and examples

## Technical Considerations

### Architecture
- **Parallel execution**: Use Python's `asyncio` or `multiprocessing`
- **Agent coordination**: Shared state in `.air/parallel/state.json`
- **Dashboard UI**: Use Rich or Textual for terminal UI
- **Subagent storage**: Markdown files with YAML frontmatter

### Backwards Compatibility
- All new features are opt-in
- Existing AIR projects work without changes
- New features available via flags or subcommands

### Performance
- Parallel agents limited to N concurrent (configurable)
- Prototype cleanup to prevent disk bloat
- Incremental analysis for large codebases

### Cost Management
- Token estimation before parallel analyses
- Budget limits in config
- Warning when approaching limits
- Option to use smaller models for prototyping

## What NOT to Implement

### ❌ Full Production Development Features
- Live code modification in reviewed repos (violates read-only principle)
- Automatic PR creation from analysis (analysis should inform, not automate changes)
- Feature flags (analysis doesn't ship to production)

### ❌ Speed-Over-Quality Features
- Skip validation modes (thoroughness is core value)
- Auto-approve analysis (human validation required)
- Minimal documentation options (audit trail is essential)

### ❌ Unlimited AI Features
- Assume unlimited AI budget (most users have limits)
- Require latest/most expensive models (should work with various models)
- No cost visibility (users need to know what they're spending)

## Success Metrics

After implementation, measure:

1. **Velocity**: Time to complete assessment (should decrease 30-50%)
2. **Quality**: Findings per hour (should increase)
3. **Coverage**: % of codebase analyzed (should increase)
4. **User satisfaction**: Survey responses (target: 8+/10)
5. **AI efficiency**: Cost per analysis (should stabilize or decrease)
6. **Adoption**: % of users using new features (target: 60%+ within 6 months)

## Open Questions

1. Should parallel agents share findings in real-time or work independently?
2. What's the right limit for concurrent parallel analyses (3? 5? 10?)?
3. Should prototyping mode use cheaper/faster models by default?
4. How to handle subagent conflicts (multiple security subagents)?
5. What's the best UX for checkpoint management (Git-like? Simpler?)?

## Next Steps

1. **Validate with users**: Survey AIR users about top 3 desired features
2. **Build prototype**: Implement parallel analysis as MVP
3. **Gather feedback**: Dogfood with internal assessments
4. **Iterate**: Refine based on usage data
5. **Expand**: Add features based on validated need

## Conclusion

These features would bring AIR's analytical workflows closer to Claude Code's velocity while preserving AIR's core strengths: rigorous documentation, structured methodology, and accountability. The key is adaptation, not imitation—taking inspiration from production development workflows and tailoring them for the assessment use case.

**Core philosophy**: Make AI-assisted codebase assessment as fast and powerful as AI-assisted development, without sacrificing the rigor that makes assessments valuable.
