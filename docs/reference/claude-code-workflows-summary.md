# Claude Code Development Workflows vs AIR Project

**Source:** substack-how-claude-code-is-built.pdf
**Date:** September 23, 2025
**Analyzed:** 2025-10-04

## PDF Overview

The PDF describes how Anthropic's Claude Code team operates in an "AI-first" development environment.

### Key Workflows

- **Rapid prototyping**: 20 functional prototypes built in 2 days for a single feature
- **High velocity**: ~5 pull requests per engineer per day, 60-100 internal releases/day
- **AI-everywhere approach**: 90% of Claude Code written by Claude Code itself
- **Minimal scaffolding**: Letting the model do most work, deleting code with each model improvement
- **TDD renaissance**: Test-driven development is practical again with AI writing tests
- **AI in all processes**: Code reviews, security reviews, test writing, incident triage, GitHub issue handling

### Team Characteristics

- Small team (~10 engineers), highly autonomous product-minded engineers
- No designers, no PMs on the team initially
- Obsessive dogfooding (80% of Anthropic uses Claude Code daily)
- Priorities: Security > Reliability > Speed of iteration
- Tech stack chosen to be "on distribution" for the model (TypeScript, React, Ink, Yoga, Bun)

### Notable Practices

1. **Parallel coding**: 25% of Claude Max users run multiple agents in parallel daily
2. **Delete code with model releases**: Half the system prompt deleted with Claude 4.0
3. **Compile-time feature flags only**: To avoid slowing down shipping
4. **Vibe coding**: Custom Markdown renderer built day before release
5. **Context-aware UX**: Loading messages that reflect what the model is thinking

## Similarities with AIR Project

1. **AI-centric design**: Both are built for AI agent workflows
2. **Task tracking emphasis**: AIR requires `.air/tasks/` files; Claude Code team tracks work systematically
3. **Documentation-driven**: Both value clear documentation (AIR's CLAUDE.md ≈ Claude Code team's context)
4. **Rapid iteration**: Both encourage fast feedback loops
5. **Structured metadata**: Both use JSON config files and markdown for context

## Key Differences

### 1. Purpose & Scale

- **Claude Code**: Product development team shipping features to millions
- **AIR**: Assessment framework for analyzing/reviewing existing codebases

### 2. Workflow Philosophy

- **Claude Code**: Build 5-10 prototypes/day, ship fast, minimal planning, throw away work frequently
- **AIR**: Structured analysis, careful documentation, preservation of findings, archival system

### 3. Code Interaction

- **Claude Code**: Full modification rights, deletes code regularly, ships to production
- **AIR**: READ-ONLY repos for review, analysis documents only, contributions go to separate folder

### 4. Task Management

- **Claude Code**: Fluid, informal, focus on speed (no feature flags to avoid slowdown)
- **AIR**: Mandatory task files for EVERY piece of work, formal outcome tracking (⏳/✅/⚠️/❌)

### 5. Development Pace

- **Claude Code**: 5 PRs/day/engineer, features shipped in days
- **AIR**: Thorough analysis over speed, monthly task archival, focus on completeness

### 6. AI Usage Depth

- **Claude Code**: AI for coding, testing, reviews, security, incidents, monitoring queries
- **AIR**: AI for analysis and development, but humans validate and review findings

### 7. Prototyping vs. Analysis

- **Claude Code**: Prototype directly, skip mockups, build to learn
- **AIR**: Analyze existing patterns, document architectures, compare implementations

### 8. Team Structure

- **Claude Code**: No designers/PMs initially, engineers own everything
- **AIR**: Designed for solo developers or small teams doing assessment work

### 9. Risk Tolerance

- **Claude Code**: Ship fast, learn from production, minimal feature flags
- **AIR**: Validate before completion, structured outcomes, careful tracking

### 10. Resource Constraints

- **Claude Code**: Unlimited access to latest models, no cost consideration
- **AIR**: Designed for teams with budget constraints and usage limits

## Lessons for AIR Users

### What to Adopt

1. **Embrace rapid prototyping**: Build 5-10 analysis approaches quickly rather than one perfect one
2. **Product-minded analysis**: Put yourself in shoes of the developers whose code you're reviewing
3. **Simplicity first**: Choose the simplest analytical approach that works
4. **Delete fearlessly**: Remove outdated analysis notes as you learn more
5. **Parallel agents**: Run multiple analysis tasks concurrently when appropriate

### What to Adapt (Not Copy Directly)

1. **Feature flags**: AIR's structured task tracking serves a different purpose than avoiding slowdowns
2. **Speed over safety**: Analysis requires rigor; don't sacrifice thoroughness for velocity
3. **Unlimited AI usage**: Most teams need to budget AI usage carefully
4. **No formal process**: AIR assessments benefit from structured documentation
5. **Vibe coding in production**: Analysis documents should be deliberate, not last-minute

### AIR-Specific Strengths to Preserve

1. **Task archival system**: Maintains historical record of analysis evolution
2. **Read-only discipline**: Prevents accidental modifications to reviewed code
3. **Contribution separation**: Clear boundary between analysis and proposed improvements
4. **Outcome tracking**: Explicit success/partial/blocked states for accountability
5. **Validation requirements**: `air validate` ensures assessment quality

## Bottom Line

**Claude Code workflow** = Move fast, build many prototypes, delete liberally, ship continuously, let AI do maximum work

**AIR workflow** = Analyze carefully, document thoroughly, preserve findings, track meticulously, use AI as assistant for deep analysis

The Claude Code team's workflow is about **velocity in production development**; AIR is about **rigor in codebase assessment**.

Both leverage AI heavily, but:
- Claude Code pushes the boundaries of AI autonomy in product development
- AIR maintains structured human oversight for analysis quality and accountability

## Key Insights

1. **"On distribution" matters**: Claude Code chose TypeScript/React because the model knows them well. Similarly, AIR users should analyze codebases in languages/frameworks the AI understands deeply.

2. **90% AI-written is achievable**: But requires the right problem domain (Claude Code building Claude Code is ideal; general codebase analysis is more varied).

3. **TDD renaissance**: Writing tests first works better with AI because the model can iterate against a concrete target.

4. **Product-minded engineers are force multipliers with AI**: Experience + entrepreneurial mindset + AI tools = extreme productivity.

5. **Context is everything**: Anthropic is a research lab building an LLM. Their practices emerge from that unique context. AIR serves a different purpose and should adapt, not copy wholesale.

## Questions for Further Exploration

1. How can AIR leverage parallel agents for comparing multiple codebases simultaneously?
2. Could AIR develop "analysis subagents" similar to Claude Code's custom subagents?
3. What's the right balance between analysis speed and thoroughness in AIR workflows?
4. How can AIR users implement effective "dogfooding" of their analysis practices?
5. Should AIR have an "analysis prototype" mode separate from formal documentation mode?

---

**Note**: This summary was created as part of AIR task tracking to understand modern AI-assisted development workflows and their applicability to code assessment practices.
