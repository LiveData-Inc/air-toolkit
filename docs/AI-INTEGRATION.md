# AIR Toolkit - AI Integration Guide

**Version:** 0.2.3
**Last Updated:** 2025-10-04

## 1. Overview

AIR is designed to work **closely with AI agents** like Anthropic Claude and OpenAI Codex. The toolkit provides structure and automation that enables AI assistants to perform multi-project code assessment and tracking with minimal human intervention.

### 1.1 Core Principle: Zero-Friction AI Collaboration

**Traditional workflow:**
```
Human: "Review these three repos"
AI: Manually navigates, manually takes notes, loses context
Human: Has to repeatedly ask for status, summaries, etc.
```

**AIR workflow:**
```
Human: air init review && air link ... && .init "Review these repos"
AI: Automatically creates task files, documents findings, generates reports
Human: air status && air summary  # Instant visibility
```

### 1.2 AI-First Design

Every AIR feature is designed to:
- **Enable AI autonomy**: AI can use AIR commands to structure its work
- **Capture AI output**: Task files preserve AI analysis
- **Guide AI behavior**: CLAUDE.md and templates direct AI actions
- **Make AI work visible**: Status and summary commands expose AI progress

## 2. AI Agent Integration Points

### 2.1 Task Tracking: Automatic Documentation

**Problem AI Solves:**
AI assistants perform analysis but the work is ephemeral - lost when the chat ends.

**AIR Solution:**
```bash
# AI automatically creates task files as it works
.air/tasks/20251003-1200-review-ehr-inbound.md
.air/tasks/20251003-1315-compare-services.md
.air/tasks/20251003-1430-create-integration-plan.md
```

**AI Workflow:**
1. Human gives prompt
2. AI creates task file: `air task new "review ehr-inbound"`
3. AI documents actions in task file as it works
4. AI marks complete: `air task complete 20251003-1200`

**Result:** Complete audit trail of AI work

### 2.2 CLAUDE.md: AI Instruction File

**Purpose:** Give AI persistent instructions for working in the project.

**Example CLAUDE.md for Assessment Project:**

```markdown
# CLAUDE.md

## Project Context

This is an AIR assessment project comparing:
- repos/service-a - Service implementation
- repos/service-b - Alternative implementation
- repos/architecture - Shared architecture docs

## Your Tasks

1. ✅ Review both service implementations
2. ✅ Identify key differences and gaps
3. ✅ Create integration plan
4. ⏳ Review architecture docs for gaps

## Instructions for AI

### Automatic Task Tracking

- Create task file IMMEDIATELY when starting work
- Update task file as you progress
- Mark complete when done

### Analysis Location

- Store comparisons in `analysis/assessments/`
- Store architecture feedback in `analysis/improvements/`
- Create SUMMARY.md with executive overview

### Contribution Workflow

For `repos/architecture` (collaborative):
1. Identify gaps in documentation
2. Create improvements in `contributions/architecture/`
3. We'll submit via `air pr architecture`

### Read-Only Resources

Repos in `repos/` are READ-ONLY symlinks. Never attempt to modify.

## AI Commands to Use

```bash
# Check project status
air status

# Validate structure
air validate

# Create task
air task new "description"

# Generate summary
air summary --output=analysis/SUMMARY.md
```
```

### 2.3 .air/README.md: Task System Documentation

**Purpose:** Teach AI the task tracking protocol.

**Key Sections:**
- Task file format
- When to create tasks
- How to update tasks
- Outcome statuses

**AI reads this to learn:**
- I should create `.air/tasks/YYYYMMDD-HHMM-description.md`
- I should document actions as I take them
- I should mark outcome when complete

### 2.4 Templates: Guide AI Output

**Purpose:** Provide structure for AI-generated content.

**Example: Task Template**

```markdown
# Task: {{ description }}

## Date
{{ timestamp }}

## Prompt
{{ user_prompt }}

## Actions Taken
1. [AI fills this in as it works]
2.
3.

## Files Changed
- `path/to/file` - [AI describes changes]

## Outcome
⏳ In Progress

[AI adds summary when complete]
```

**AI Benefits:**
- Knows what to include
- Consistent format
- Easy to parse later

### 2.5 Project Structure: Organize AI Output

**Directory structure tells AI where to put analysis:**

```
analysis/
├── SUMMARY.md              # AI: Executive overview here
├── assessments/            # AI: Analysis of review resources
│   ├── service-a.md
│   └── comparison.md
└── improvements/           # AI: Feedback on collaborative resources
    └── architecture-gaps.md
```

**AI reads structure and knows:**
- Assessments go in `assessments/`
- Architecture feedback goes in `improvements/`
- Summary goes in root

## 3. AI Workflows

### 3.1 Assessment Workflow

```bash
# 1. Human sets up project
air init service-review
cd service-review
air link --review service-a:~/repos/service-a
air link --review service-b:~/repos/service-b

# 2. Human starts AI session
# AI reads CLAUDE.md
# AI reads .air/README.md

# 3. AI creates task
# (AI internally): air task new "compare services"

# 4. AI performs analysis
# - Reads repos/service-a/
# - Reads repos/service-b/
# - Documents findings in task file

# 5. AI creates analysis document
# analysis/assessments/service-comparison.md

# 6. AI marks task complete
# (AI internally): air task complete 20251003-1200

# 7. AI creates summary
# (AI internally): air summary --output=analysis/SUMMARY.md

# 8. Human checks results
air status
cat analysis/SUMMARY.md
```

### 3.2 Contribution Workflow

```bash
# 1. Setup with collaborative resource
air init doc-review
air link --collaborate arch:~/repos/architecture --clone

# 2. AI reviews documentation
# AI creates: analysis/improvements/gaps.md

# 3. AI creates contributions
# AI creates: contributions/arch/new-guide.md
# AI creates: contributions/arch/adr-updates.md

# 4. Human submits PR
air pr arch --branch=add-integration-guide

# 5. GitHub PR created with AI's improvements
```

### 3.3 Continuous Development Workflow

```bash
# In any project (not just assessment)
cd ~/my-project

# Initialize tracking
air track init

# AI works on feature
# (AI internally): air task new "implement auth"
# AI codes, documents in task file
# (AI internally): air task complete 20251003-1400

# Later, generate summary
air summary --output=WORK-SUMMARY.md
```

## 4. AI Capabilities Enabled by AIR

### 4.1 Multi-Project Code Review

**What AI Can Do:**
- Analyze multiple repositories simultaneously
- Compare implementations across repos
- Identify integration gaps
- Create implementation plans
- Track its analysis progress

**Without AIR:**
- AI looks at one repo at a time
- Hard to maintain context across repos
- Analysis scattered in chat history
- No persistence

**With AIR:**
- All repos accessible in one project
- Structured analysis documents
- Persistent task tracking
- Clear deliverables

### 4.2 Documentation Gap Analysis

**What AI Can Do:**
- Review architecture documentation
- Identify missing docs
- Propose improvements
- Generate new documentation
- Track contribution status

**AIR Support:**
- `collaborate/` directory for docs
- `contributions/` for improvements
- `air pr` to submit changes
- Clear feedback loop

### 4.3 Self-Documenting Analysis

**What AI Can Do:**
- Document its own work automatically
- Create audit trail
- Generate summaries on demand
- Show progress to human

**AIR Support:**
- Task file format AI understands
- Templates guide AI output
- Summary generation built-in
- Status commands for visibility

### 4.4 Long-Running Analysis

**Problem:**
AI sessions have limited context windows and can be interrupted.

**AIR Solution:**

**Session 1:**
```
Human: Review service-a
AI: Creates task, analyzes, documents in task file
```

**Session 2 (days later):**
```
Human: Continue the review
AI: Reads task files, sees what was done, continues
```

**AIR enables:**
- Session continuity via task files
- State preservation
- Pick up where left off

## 5. Recommended AI Instructions

### 5.1 In CLAUDE.md

```markdown
# Instructions for AI Assistants

## Task Tracking Protocol

**CRITICAL**: Create task files automatically as you work.

1. When user gives you work to do, IMMEDIATELY create task file:
   ```
   File: .air/tasks/YYYYMMDD-HHMM-brief-description.md
   ```

2. Document actions AS YOU TAKE THEM:
   - List each file you read
   - Document each analysis you perform
   - Note decisions and trade-offs

3. Mark outcome when complete:
   - ✅ Success - Task completed
   - ⏳ In Progress - Still working
   - ⚠️ Partial - Incomplete
   - ❌ Blocked - Cannot proceed

## Analysis Documents

Store analysis in structured documents:

- `analysis/assessments/*.md` - For review-only resources
- `analysis/improvements/*.md` - For collaborative resources
- `analysis/SUMMARY.md` - Executive overview

## Contributing to Collaborative Resources

For resources in `collaborate/`:

1. Create improvements in `contributions/[resource]/`
2. Notify human when ready
3. Human will run: `air pr [resource]`

## Commands Available to You

```bash
air status              # Check project status
air validate            # Validate structure
air task new "desc"     # Create task (you should do this!)
air task list           # List tasks
air summary             # Generate summary
air classify            # Classify resources
```

## What NOT to Do

- ❌ Do NOT modify resources in `review/` or `collaborate/`
- ❌ Do NOT skip task file creation
- ❌ Do NOT lose track of your work
- ✅ DO document everything
- ✅ DO use structured analysis documents
- ✅ DO follow templates
```

### 5.2 In Project README.md

```markdown
## For AI Assistants

Read these files in order:
1. `.air/README.md` - Task tracking protocol
2. `CLAUDE.md` - Project-specific instructions
3. `README.md` (this file) - Project goals

Your goals for this project:
1. [Goal 1]
2. [Goal 2]
3. [Goal 3]

Deliverables expected:
- [ ] `analysis/assessments/[specific-analysis].md`
- [ ] `analysis/SUMMARY.md`
- [ ] `.air/tasks/` - Complete task files

Use `air status` to check your progress.
```

## 6. AI Agent Types and AIR Usage

### 6.1 Anthropic Claude (Claude Code)

**Strengths:**
- Long context window - can read multiple repos
- Excellent code analysis
- Good at structured output
- Follows instructions well

**AIR Usage:**
- Ideal for multi-project assessment
- Creates detailed analysis documents
- Follows CLAUDE.md instructions
- Automatically creates task files

**Example Session:**
```
User: /init

Claude: Reading .air/README.md and CLAUDE.md...
Claude: Creating task file: .air/tasks/20251003-1200-review-repos.md
Claude: Reading repos/service-a/...
Claude: Reading repos/service-b/...
Claude: Creating analysis/assessments/comparison.md...
Claude: Updating task file...
Claude: Task complete. See analysis/SUMMARY.md
```

### 6.2 OpenAI GPT-4 / Codex

**Strengths:**
- Code generation
- Quick analysis
- Good at following templates

**AIR Usage:**
- Can use for focused analysis
- Template-guided output
- Task tracking

**Integration:**
```bash
# Via CLI tool or API
openai-assistant \
  --instructions-from CLAUDE.md \
  --task "Review repos/service-a" \
  --output analysis/assessments/service-a.md
```

### 6.3 GitHub Copilot

**Strengths:**
- Code completion
- In-editor assistance

**AIR Usage:**
- Can read CLAUDE.md for context
- Assist in creating analysis documents
- Help with task file generation

## 7. Advanced AI Integration

### 7.1 Automated Workflows (Future)

```bash
# AI agent runs entire workflow
air-agent \
  --project my-review \
  --goal "Compare services and create plan" \
  --auto-create-tasks \
  --auto-generate-summary

# AI:
# 1. Creates assessment project
# 2. Links repositories
# 3. Analyzes each repo
# 4. Creates comparison
# 5. Generates plan
# 6. Creates summary
# All with automatic task tracking
```

### 7.2 Continuous AI Analysis (Future)

```yaml
# .github/workflows/ai-review.yml
name: AI Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run AIR analysis
        run: |
          air init pr-review
          air link --review current:.
          ai-agent --analyze --output=analysis/pr-review.md
      - name: Post comment
        run: |
          air summary | gh pr comment --body-file -
```

### 7.3 Multi-Agent Collaboration (Future)

```
Agent 1 (Code Analyzer):
  - Analyzes implementation
  - Creates technical assessment
  - Documents in analysis/assessments/

Agent 2 (Documentation Reviewer):
  - Reviews architecture docs
  - Identifies gaps
  - Creates contributions/

Agent 3 (Integration Planner):
  - Reads outputs from Agent 1 & 2
  - Creates integration plan
  - Generates SUMMARY.md

All tracked in .air/tasks/
Human reviews: air status && air summary
```

## 8. Best Practices

### 8.1 For Humans Working With AI

**Do:**
- ✅ Set up project structure before AI session
- ✅ Provide clear goals in README.md
- ✅ Review CLAUDE.md before starting AI
- ✅ Use `air status` to check AI progress
- ✅ Read `.air/tasks/` to understand what AI did

**Don't:**
- ❌ Skip project initialization
- ❌ Give vague goals
- ❌ Ignore AI's task files
- ❌ Forget to run `air validate`

### 8.2 For AI Agents

**Do:**
- ✅ Read .air/README.md FIRST
- ✅ Read CLAUDE.md for project instructions
- ✅ Create task files IMMEDIATELY
- ✅ Update task files as you work
- ✅ Follow directory structure
- ✅ Use templates

**Don't:**
- ❌ Skip task file creation
- ❌ Modify read-only resources
- ❌ Lose track of your work
- ❌ Create analysis files in wrong locations

## 9. Measuring AI Effectiveness

### 9.1 Metrics

**Without AIR:**
- AI analysis scattered in chat
- No persistence
- Hard to measure completeness
- Manual tracking required

**With AIR:**
- Clear deliverables in `analysis/`
- Complete task history
- Measurable: `air status` shows progress
- Automatic audit trail

### 9.2 Success Indicators

```bash
# Complete analysis
$ air status
Review Resources: 3 (all analyzed)
Analysis Documents: 5
Task Files: 8 (all complete)
Summary: Generated

# Incomplete analysis
$ air status
Review Resources: 3 (2 analyzed)
Analysis Documents: 2
Task Files: 3 (1 in progress, 2 blocked)
Summary: Not generated
```

## 10. Future: AI-Native Features

### 10.1 Semantic Analysis

```bash
air analyze --semantic \
  --find-duplicates \
  --find-inconsistencies \
  --suggest-refactoring
```

### 10.2 AI-Assisted Classification

```bash
air classify --ai-powered
# Uses AI to classify resources
# Analyzes code vs docs
# Suggests resource types
```

### 10.3 Intelligent Summarization

```bash
air summary --ai-enhance
# AI reads task files
# Creates narrative summary
# Highlights key findings
# Suggests next steps
```

## 11. Conclusion

AIR is **AI-first by design**:

- **Structured** - AI knows where to put analysis
- **Documented** - AI creates audit trail automatically
- **Persistent** - AI work survives session boundaries
- **Visible** - Humans can track AI progress
- **Integrated** - AI uses commands, humans use commands

The result: **AI agents become more effective code reviewers** because AIR provides the structure, persistence, and visibility they need.

---

**Next Steps:**
1. Read [SPECIFICATION.md](SPECIFICATION.md) for feature details
2. Read [ARCHITECTURE.md](ARCHITECTURE.md) for technical design
3. Try creating an assessment project and watch AI work within it
