# AIR Code Review Architecture

**Version:** 0.5.0 (Future)
**Status:** Design Document
**Last Updated:** 2025-10-04

## Overview

This document describes the architecture for integrating AIR (AI Review) toolkit with Claude Code and other AI assistants to perform automated code reviews, both in local development and in CI/CD pipelines.

## Vision

Enable AI-assisted code reviews that leverage AIR's multi-repository context awareness to:
- Provide deeper, more contextual code reviews
- Detect cross-repository patterns and inconsistencies
- Learn from project history and coding standards
- Integrate seamlessly into development workflows
- Automate PR reviews in CI/CD pipelines

## Core Principles

1. **Context-Aware Reviews** - Use AIR's linked resources to compare patterns across repositories
2. **Workflow Integration** - Zero-friction integration into existing git workflows
3. **Progressive Enhancement** - Start simple (local), scale to complex (CI/CD)
4. **Tool Agnostic** - Design works with any AI assistant that can execute shell commands
5. **Learning System** - Improve review quality over time from feedback

## Architecture Components

### 1. AIR Review Commands

New CLI commands specifically designed for code review workflows.

#### 1.1 `air review`

**Purpose:** Generate review context for local development.

```bash
# Basic usage - review uncommitted changes
air review

# Review specific files
air review src/api/routes.py src/models/user.py

# Review current PR branch
air review --pr

# Review against specific branch
air review --base=main

# Output formats
air review --format=json    # Machine-readable for AI
air review --format=markdown # Human-readable
```

**Output Structure (JSON):**

```json
{
  "mode": "local-review",
  "base_branch": "main",
  "target_branch": "feature/add-auth",
  "changes": {
    "files_changed": 3,
    "insertions": 156,
    "deletions": 23,
    "files": [
      {
        "path": "src/api/auth.py",
        "status": "modified",
        "diff": "...",
        "language": "python",
        "lines_added": 87,
        "lines_removed": 12
      }
    ]
  },
  "context": {
    "project": {
      "name": "my-service",
      "mode": "mixed",
      "linked_resources": 3
    },
    "related_resources": [
      {
        "name": "service-a",
        "path": "repos/service-a",
        "relevance": "similar auth implementation"
      }
    ],
    "recent_tasks": [
      {
        "file": ".air/tasks/20251003-1400-implement-auth.md",
        "description": "Implement authentication",
        "outcome": "success"
      }
    ],
    "standards": {
      "security": ".air/context/security.md",
      "python": ".air/context/python-standards.md"
    }
  },
  "metadata": {
    "generated_at": "2025-10-04T08:30:00-04:00",
    "air_version": "0.5.0",
    "git_hash": "abc123"
  }
}
```

**Implementation Details:**

```python
# air/commands/review.py

@cli.command()
@click.option("--base", default="main", help="Base branch to compare")
@click.option("--pr", is_flag=True, help="Review current PR branch")
@click.option("--format", type=click.Choice(["json", "markdown"]), default="json")
@click.argument("files", nargs=-1, type=click.Path())
def review(base: str, pr: bool, format: str, files: tuple):
    """Generate code review context."""

    # 1. Validate we're in a git repo
    git_repo = get_git_repo()

    # 2. Get changes
    if pr:
        diff = get_pr_diff(git_repo)
    elif files:
        diff = get_file_diff(git_repo, files, base)
    else:
        diff = get_uncommitted_changes(git_repo)

    # 3. Build context
    context = ReviewContext(
        changes=parse_diff(diff),
        project_context=get_air_context(),
        related_resources=find_related_resources(diff.files),
        recent_tasks=get_recent_tasks(limit=5),
        standards=load_coding_standards()
    )

    # 4. Output
    if format == "json":
        console.print_json(context.to_json())
    else:
        console.print(format_review_prompt(context))
```

#### 1.2 `air review-project`

**Purpose:** Multi-repository analysis for AIR review projects.

```bash
# Create review project
air init code-review-2025-10 --mode=review

# Link repositories
air link add ~/repos/service-a --review
air link add ~/repos/service-b --review

# Classify resources
air classify

# Review entire project
air review-project

# Focus on specific areas
air review-project --focus=security
air review-project --focus=architecture
air review-project --focus=performance

# Review depth
air review-project --depth=quick      # High-level overview
air review-project --depth=standard   # Normal review
air review-project --depth=deep       # Comprehensive analysis
```

**Output Structure:**

```json
{
  "mode": "multi-repo-review",
  "project": {
    "name": "code-review-2025-10",
    "resources": 3,
    "total_loc": 45231
  },
  "focus": "security",
  "depth": "standard",
  "resources": [
    {
      "name": "service-a",
      "type": "library",
      "stack": "Python/FastAPI",
      "structure": {
        "directories": 15,
        "files": 87,
        "loc": 12456
      },
      "metrics": {
        "complexity": 6.2,
        "test_coverage": 0.84,
        "documentation": 0.72
      },
      "patterns": {
        "auth": "JWT with refresh tokens",
        "database": "PostgreSQL with SQLAlchemy",
        "caching": "Redis",
        "api_style": "REST"
      },
      "concerns": [
        {
          "type": "security",
          "severity": "warning",
          "description": "JWT tokens don't expire",
          "location": "src/auth/jwt.py:45"
        }
      ]
    }
  ],
  "cross_repo_analysis": {
    "duplicated_code": [
      {
        "code": "email validation regex",
        "locations": ["service-a/utils.py:23", "service-b/validators.py:67"]
      }
    ],
    "inconsistent_patterns": [
      {
        "pattern": "error handling",
        "service-a": "custom exceptions",
        "service-b": "HTTP exceptions"
      }
    ],
    "shared_dependencies": {
      "fastapi": "0.104.1",
      "pydantic": "2.5.0"
    }
  }
}
```

#### 1.3 `air review-gate`

**Purpose:** Quality gate for CI/CD pipelines.

```bash
# Run review and enforce quality standards
air review-gate --fail-on=critical

# Different thresholds
air review-gate --fail-on=warning
air review-gate --fail-on=suggestion

# Output results
air review-gate --output=review-results.json

# Combined with other tools
air review-gate --include-sonar --include-coverage
```

**Exit Codes:**
- `0` - Review passed, no issues above threshold
- `1` - Critical issues found
- `2` - Warnings found (if `--fail-on=warning`)
- `3` - Parse error or tool failure

#### 1.4 `air claude` Subcommands

AI-optimized commands that return clean, parseable output.

```bash
# Get comprehensive context
air claude context --format=json

# Start tracked work
air claude task-start "add rate limiting"
# Returns: .air/tasks/20251004-0830-add-rate-limiting.md

# Update task as work progresses
air claude task-update .air/tasks/20251004-0830-add-rate-limiting.md \
  "Added RateLimiter middleware"

# Complete task
air claude task-complete .air/tasks/20251004-0830-add-rate-limiting.md \
  --status=success

# Generate commit from task
air claude commit .air/tasks/20251004-0830-add-rate-limiting.md

# Suggest next actions
air claude suggest
```

### 2. Claude Code Integration

#### 2.1 Slash Commands

Custom slash commands for workflow integration.

**Location:** `.claude/commands/`

**Key Commands:**

**`/air-review`** - Local code review
```markdown
# .claude/commands/air-review.md
---
description: Review code changes using AIR context
---

I'll review your code changes with full project context.

Running: air review --format=json

Analyzing:
- Code quality and best practices
- Consistency with project patterns
- Security concerns
- Performance implications
- Test coverage
- Documentation needs

Comparing against:
- Patterns in linked resources
- Project coding standards
- Recent similar changes

Generating review...
```

**`/air-review-interactive`** - Interactive review session
```markdown
# .claude/commands/air-review-interactive.md
---
description: Interactive code review with discussion
---

Let's review your changes together.

I'll analyze each file and we can discuss:
1. Issues found
2. Suggested improvements
3. Questions about design choices

After review, I can:
- Add TODO comments in code
- Update documentation
- Generate PR description
- Create follow-up tasks

Ready to start?
```

**`/air-analyze-repos`** - Multi-repository analysis
```markdown
# .claude/commands/air-analyze-repos.md
---
description: Analyze all linked repositories
---

Analyzing all repositories in this AIR project:

Running: air review-project --format=json

Looking for:
- Code duplication across repos
- Inconsistent patterns
- Security issues
- Architecture anti-patterns
- Tech stack alignment

Output: analysis/reviews/{date}-cross-repo-analysis.md
```

**`/air-begin`** - Start AIR-tracked work
```markdown
# .claude/commands/air-begin.md
---
description: Start AIR-tracked task
---

Starting new tracked task:

1. Get project context: air claude context
2. Create task file: air claude task-start "{{prompt}}"
3. Review recent similar work
4. Create implementation plan

Ready to begin work on: {{prompt}}
```

**`/air-done`** - Complete and commit work
```markdown
# .claude/commands/air-done.md
---
description: Complete task and commit changes
---

Completing current task:

1. Find active task file
2. Update with final actions
3. Mark as completed
4. Generate commit message from task
5. Stage changes
6. Create commit

Ready to commit?
```

#### 2.2 Enhanced CLAUDE.md

Project-specific instructions for Claude Code behavior.

```markdown
# CLAUDE.md

## AI Code Review Protocol

When reviewing code in this project:

**Before every review:**
1. Run `air claude context --format=json` to understand project state
2. Check recent tasks in `.air/tasks/` for relevant history
3. Review coding standards in `.air/context/`
4. Identify related resources with similar code

**During review:**
1. Compare changes against patterns in linked resources
2. Check for consistency with project standards
3. Reference specific examples from other repos
4. Cite task history for context on decisions

**Review checklist:**
- [ ] Security: No vulnerabilities (check .air/context/security.md)
- [ ] Performance: No obvious bottlenecks
- [ ] Architecture: Follows project patterns
- [ ] Testing: Adequate test coverage (>80%)
- [ ] Documentation: Public APIs documented
- [ ] Consistency: Matches style in linked repos

**Output format:**
```markdown
## Code Review: {branch-name}

### Summary
{brief overview}

### Critical Issues 🔴
{blocking issues}

### Warnings ⚠️
{should-fix issues}

### Suggestions 💡
{nice-to-have improvements}

### Context from AIR
{relevant patterns from linked repos}
{related task history}

### References
- Similar code: {repo}/{file}:{line}
- Standards: {.air/context/file}
- Related task: {.air/tasks/file}
```

## Automatic Task Creation

**Every code change MUST create a task file:**

```python
# Before first edit
task_file = run_command("air claude task-start", description)

# As work progresses
run_command("air claude task-update", task_file, action)

# When complete
run_command("air claude task-complete", task_file, status="success")
```
```

### 3. CI/CD Pipeline Integration

#### 3.1 GitHub Actions Workflow

```yaml
# .github/workflows/air-review.yml

name: AIR Code Review

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for context

      - name: Checkout base branch
        run: |
          git fetch origin ${{ github.base_ref }}

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install AIR
        run: |
          pip install air-toolkit
          air --version

      - name: Setup Claude Code
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          curl -fsSL https://claude.ai/install.sh | sh
          claude auth $ANTHROPIC_API_KEY

      - name: Initialize AIR context (if needed)
        run: |
          # Check if air-config.json exists
          if [ ! -f "air-config.json" ]; then
            echo "Not an AIR project, skipping context setup"
          else
            # Link any configured resources (if they're available)
            air validate || true
          fi

      - name: Generate review context
        id: context
        run: |
          air review --pr --base=${{ github.base_ref }} --format=json > review-context.json

          # Save context as output
          echo "context_file=review-context.json" >> $GITHUB_OUTPUT

          # Show summary
          echo "## Review Context Generated" >> $GITHUB_STEP_SUMMARY
          echo "- Files changed: $(jq '.changes.files_changed' review-context.json)" >> $GITHUB_STEP_SUMMARY
          echo "- Insertions: $(jq '.changes.insertions' review-context.json)" >> $GITHUB_STEP_SUMMARY
          echo "- Deletions: $(jq '.changes.deletions' review-context.json)" >> $GITHUB_STEP_SUMMARY

      - name: Run AI code review
        id: review
        run: |
          # Use Claude Code to review (via slash command or direct invocation)
          claude run /air-review-ci < review-context.json > review-output.md

          echo "review_file=review-output.md" >> $GITHUB_OUTPUT

          # Extract summary for step summary
          head -20 review-output.md >> $GITHUB_STEP_SUMMARY

      - name: Check quality gate
        id: gate
        run: |
          air review-gate \
            --fail-on=critical \
            --output=review-results.json \
            < review-output.md
        continue-on-error: true

      - name: Post review as PR comment
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const review = fs.readFileSync('review-output.md', 'utf8');
            const results = JSON.parse(fs.readFileSync('review-results.json', 'utf8'));

            // Build comment body
            let body = `## 🤖 AIR Code Review\n\n`;
            body += `**Status:** ${results.passed ? '✅ Passed' : '❌ Failed'}\n\n`;
            body += `**Issues Found:**\n`;
            body += `- 🔴 Critical: ${results.critical}\n`;
            body += `- ⚠️  Warnings: ${results.warnings}\n`;
            body += `- 💡 Suggestions: ${results.suggestions}\n\n`;
            body += `---\n\n${review}`;

            // Post comment
            await github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Create task file
        if: always()
        run: |
          air claude task-start "PR Review: ${{ github.event.pull_request.title }}" \
            --template=pr-review \
            --pr-number=${{ github.event.pull_request.number }} \
            --pr-url="${{ github.event.pull_request.html_url }}" \
            > task-file.txt

          TASK_FILE=$(cat task-file.txt)

          # Update task with review results
          air claude task-update "$TASK_FILE" \
            "Reviewed PR #${{ github.event.pull_request.number }}" \
            "Found: ${{ steps.gate.outputs.critical }} critical, ${{ steps.gate.outputs.warnings }} warnings"

          # Complete task
          air claude task-complete "$TASK_FILE" \
            --status="${{ steps.gate.outcome }}"

      - name: Upload review artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: air-review-results
          path: |
            review-context.json
            review-output.md
            review-results.json

      - name: Fail if quality gate failed
        if: steps.gate.outcome == 'failure'
        run: exit 1
```

#### 3.2 CI-Specific Slash Command

```markdown
# .claude/commands/air-review-ci.md
---
description: CI/CD pipeline code review
---

Running automated PR review in CI/CD pipeline.

Context received via stdin (JSON format).

Analyzing:
- Pull request diff
- Changed files and their relationships
- Test coverage changes
- Security implications
- Performance impacts

Review standards:
- Critical issues: Block merge
- Warnings: Should fix before merge
- Suggestions: Consider for follow-up

Output format: GitHub-flavored markdown

Generating review...
```

#### 3.3 Quality Gate Configuration

```yaml
# .air/review-config.yml

quality_gates:
  critical:
    block_merge: true
    checks:
      - security_vulnerabilities
      - syntax_errors
      - breaking_changes

  warnings:
    block_merge: false  # Can override in CI
    checks:
      - code_smells
      - test_coverage_decrease
      - missing_documentation

  suggestions:
    block_merge: false
    checks:
      - code_style
      - performance_improvements
      - refactoring_opportunities

review_focus:
  security:
    - sql_injection
    - xss
    - hardcoded_secrets
    - improper_auth

  performance:
    - n_plus_one_queries
    - missing_indexes
    - inefficient_algorithms
    - memory_leaks

  architecture:
    - separation_of_concerns
    - dependency_injection
    - error_handling
    - api_design

  testing:
    - test_coverage: 0.80
    - edge_cases
    - integration_tests
    - mock_usage

tech_stack_specific:
  "Python/FastAPI":
    - async_await_usage
    - pydantic_validation
    - dependency_injection
    - openapi_documentation

  "TypeScript/React":
    - hook_dependencies
    - prop_types
    - accessibility
    - performance_optimization

  "Python/Lambda":
    - cold_start_optimization
    - timeout_handling
    - iam_permissions
    - error_handling
```

### 4. Review Output Formats

#### 4.1 Markdown Format (Human-Readable)

```markdown
# Code Review: feature/add-auth → main

**Reviewed:** 2025-10-04 08:30 EDT
**Reviewer:** AIR + Claude Code
**Files Changed:** 3 (+156, -23)

---

## Summary

Adding JWT-based authentication to FastAPI service. Implementation follows
patterns from service-a but introduces refresh token logic.

---

## Critical Issues 🔴

None found.

---

## Warnings ⚠️

### 1. Password Storage (src/api/auth.py:45)

**Issue:** Passwords stored in plain text

```python
# Current (problematic)
user.password = request.password

# Should be
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"])
user.password = pwd_context.hash(request.password)
```

**Context:** service-a uses bcrypt (see `repos/service-a/auth.py:23`)

**Severity:** High - Security vulnerability

---

### 2. Missing Rate Limiting (src/api/auth.py)

**Issue:** Login endpoint has no rate limiting

**Recommendation:** Add slowapi rate limiting (standard across project)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/login")
@limiter.limit("5/minute")  # Standard: 5 attempts per minute
async def login(...):
```

**Context:** All other services use 5 req/min (see .air/context/security.md)

---

## Suggestions 💡

### 1. JWT Refresh Token Logic (src/api/auth.py:67)

**Observation:** Refresh tokens don't have expiration

**Suggestion:** Consider adding refresh token rotation

**Reference:** service-a implements rotation (repos/service-a/auth.py:89)

---

### 2. Error Messages (src/api/auth.py:52)

**Current:** Generic "Invalid credentials" message

**Suggestion:** Consider more specific errors for better debugging (while
maintaining security)

---

## Good Practices ✓

- ✓ Proper type hints throughout
- ✓ Comprehensive error handling
- ✓ Tests included (coverage: 87%)
- ✓ OpenAPI documentation complete
- ✓ Follows FastAPI dependency injection pattern

---

## Test Coverage

| File | Coverage | Change |
|------|----------|--------|
| src/api/auth.py | 87% | +87% |
| src/models/user.py | 92% | +5% |
| src/dependencies.py | 100% | - |

**Overall:** 89% (+8%)

---

## Context from AIR Project

### Related Resources
- **service-a** (repos/service-a/)
  - Similar auth implementation
  - Uses bcrypt for passwords
  - Implements JWT refresh rotation

### Recent Tasks
- `.air/tasks/20251003-1400-implement-auth.md`
  - Original auth implementation plan
  - Decision: Use JWT over sessions

### Coding Standards
- `.air/context/security.md` - Security requirements
- `.air/context/python-standards.md` - Python conventions

---

## Recommendations

### Must Fix (Before Merge)
1. ✗ Hash passwords with bcrypt
2. ✗ Add rate limiting to login endpoint

### Should Fix
1. ⚠ Add refresh token expiration/rotation
2. ⚠ Improve error messages

### Follow-Up Tasks
1. 💡 Consider 2FA implementation (mentioned in project goals)
2. 💡 Add password strength requirements

---

## Next Steps

1. Address critical security issues (password hashing, rate limiting)
2. Update tests to cover edge cases
3. Add refresh token expiration
4. Request re-review once changes made

**Estimated time to fix:** 2-3 hours
```

#### 4.2 JSON Format (Machine-Readable)

```json
{
  "review_id": "rev_20251004_083045",
  "timestamp": "2025-10-04T08:30:45-04:00",
  "pr": {
    "source_branch": "feature/add-auth",
    "target_branch": "main",
    "number": 123
  },
  "summary": {
    "files_changed": 3,
    "insertions": 156,
    "deletions": 23,
    "critical_issues": 0,
    "warnings": 2,
    "suggestions": 2,
    "passed": false
  },
  "issues": [
    {
      "id": "sec_001",
      "severity": "warning",
      "category": "security",
      "title": "Password stored in plain text",
      "file": "src/api/auth.py",
      "line": 45,
      "description": "Passwords should be hashed before storage",
      "recommendation": "Use bcrypt password hashing",
      "code_snippet": "user.password = request.password",
      "suggested_fix": "user.password = pwd_context.hash(request.password)",
      "context": {
        "reference": "repos/service-a/auth.py:23",
        "standard": ".air/context/security.md"
      }
    },
    {
      "id": "sec_002",
      "severity": "warning",
      "category": "security",
      "title": "Missing rate limiting",
      "file": "src/api/auth.py",
      "line": null,
      "description": "Login endpoint lacks rate limiting",
      "recommendation": "Add slowapi rate limiter (5 req/min standard)",
      "context": {
        "standard": ".air/context/security.md",
        "project_pattern": "5 requests per minute"
      }
    }
  ],
  "test_coverage": {
    "overall": 0.89,
    "change": 0.08,
    "files": [
      {
        "path": "src/api/auth.py",
        "coverage": 0.87,
        "change": 0.87
      }
    ]
  },
  "air_context": {
    "related_resources": [
      {
        "name": "service-a",
        "path": "repos/service-a",
        "relevance": "similar authentication implementation"
      }
    ],
    "recent_tasks": [
      {
        "file": ".air/tasks/20251003-1400-implement-auth.md",
        "description": "Implement authentication",
        "relevant_decisions": ["Use JWT over sessions"]
      }
    ]
  },
  "recommendations": {
    "must_fix": [
      "Hash passwords with bcrypt",
      "Add rate limiting to login endpoint"
    ],
    "should_fix": [
      "Add refresh token expiration/rotation",
      "Improve error messages"
    ],
    "follow_up": [
      "Consider 2FA implementation",
      "Add password strength requirements"
    ]
  },
  "metadata": {
    "air_version": "0.5.0",
    "claude_model": "claude-sonnet-4.5",
    "review_duration_seconds": 45,
    "confidence": 0.92
  }
}
```

### 5. Data Flow

#### 5.1 Local Development Flow

```
┌──────────────────────────────────────────────────────────────┐
│ Developer makes changes                                       │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Developer: claude /air-review                                 │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Claude Code executes: air review --format=json               │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ AIR gathers context:                                          │
│ - Git diff                                                    │
│ - AIR project status                                          │
│ - Related resources                                           │
│ - Recent tasks                                                │
│ - Coding standards                                            │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ AIR outputs JSON to Claude Code                               │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Claude Code analyzes:                                         │
│ - Code quality                                                │
│ - Security issues                                             │
│ - Pattern consistency                                         │
│ - Performance                                                 │
│ - Test coverage                                               │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Claude Code generates review (markdown)                       │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Developer reads review and makes fixes                        │
└──────────────────────────────────────────────────────────────┘
```

#### 5.2 CI/CD Pipeline Flow

```
┌──────────────────────────────────────────────────────────────┐
│ PR opened/updated on GitHub                                   │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ GitHub Actions: Checkout code                                 │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Install: AIR + Claude Code                                    │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ air review --pr --base=$BASE_REF --format=json                │
│ → review-context.json                                         │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ claude run /air-review-ci < review-context.json               │
│ → review-output.md                                            │
└───────────────┬──────────────────────────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ air review-gate --fail-on=critical < review-output.md         │
│ → review-results.json                                         │
│ → exit code (0=pass, 1=fail)                                  │
└───────────────┬──────────────────────────────────────────────┘
                │
                ├──────────────────────────────────────────────┐
                │                                               │
                ↓                                               ↓
┌──────────────────────────┐               ┌──────────────────────────┐
│ Post comment to PR        │               │ Create task file         │
│ (via GitHub API)          │               │ air claude task-start    │
└──────────────────────────┘               └──────────────────────────┘
                │                                               │
                ↓                                               ↓
┌──────────────────────────┐               ┌──────────────────────────┐
│ Upload artifacts          │               │ Commit task to repo      │
│ - context.json            │               │ (optional)               │
│ - review.md               │               │                          │
│ - results.json            │               │                          │
└──────────────────────────┘               └──────────────────────────┘
                │
                ↓
┌──────────────────────────────────────────────────────────────┐
│ Set workflow status (pass/fail)                               │
└──────────────────────────────────────────────────────────────┘
```

## Implementation Phases

### Phase 1: Local Development (Weeks 1-3)

**Deliverables:**
- `air review` command with JSON output
- `.claude/commands/air-review.md` slash command
- `.claude/commands/air-review-interactive.md` slash command
- Enhanced CLAUDE.md with review protocols
- Documentation and examples

**Success Criteria:**
- Developer can run `/air-review` and get actionable feedback
- Review completes in < 2 minutes
- Issues found correlate with project patterns

### Phase 2: Multi-Repo Analysis (Weeks 4-6)

**Deliverables:**
- `air review-project` command
- Cross-repository pattern detection
- `.claude/commands/air-analyze-repos.md`
- Review project workflow documentation

**Success Criteria:**
- Detect code duplication across repos
- Identify inconsistent patterns
- Generate comprehensive analysis reports

### Phase 3: CI/CD Integration (Weeks 7-10)

**Deliverables:**
- `air review-gate` command
- GitHub Actions workflow template
- `.claude/commands/air-review-ci.md`
- CI/CD integration documentation
- Quality gate configuration

**Success Criteria:**
- Automated reviews post to PRs within 5 minutes
- Quality gates enforce standards
- False positive rate < 10%

### Phase 4: Advanced Features (Weeks 11-14)

**Deliverables:**
- `air claude` subcommands
- Review history and learning
- Custom review checklists
- Differential reviews
- Tech stack-specific reviews

**Success Criteria:**
- Review quality improves over time
- Tech-specific issues detected
- Incremental reviews work correctly

### Phase 5: Tool Integration (Weeks 15-16)

**Deliverables:**
- SonarQube integration
- Security scanner integration
- Test coverage integration
- Combined reports

**Success Criteria:**
- Tools work together seamlessly
- Unified quality dashboard
- No duplicate findings

## Technical Decisions

### 1. Shell vs MCP Server

**Decision:** Start with shell commands, evolve to MCP server.

**Rationale:**
- Shell commands work immediately with any AI assistant
- No special integration required
- Easy to test and debug
- MCP server can be added later for better integration

**Implementation:**
```bash
# Phase 1-3: Shell-based
air review --format=json | claude run /air-review

# Phase 4+: MCP Server
# Claude Code natively calls air__review() tool
```

### 2. Review Storage

**Decision:** Store reviews in `.air/reviews/` directory.

**Structure:**
```
.air/reviews/
├── history.jsonl                    # Review history log
├── 2025-10-04-pr-123.md             # Individual PR reviews
├── 2025-10-04-cross-repo.md         # Multi-repo analysis
└── stats/
    └── 2025-10.json                 # Monthly statistics
```

**Benefits:**
- Track review quality over time
- Learn from past reviews
- Generate metrics and trends
- Version control review history

### 3. Context Limits

**Challenge:** Large diffs may exceed Claude's context window.

**Solutions:**
1. **Chunk large diffs** - Review file-by-file for large PRs
2. **Smart summarization** - Provide abbreviated context for large changes
3. **Focused reviews** - `--focus` option to target specific concerns
4. **Incremental reviews** - Review only new changes since last review

```bash
# For large PRs
air review --pr --chunk-size=5  # Review 5 files at a time

# Focus on specific areas
air review --focus=security     # Only security review

# Incremental
air review --since-last-review  # Only new changes
```

### 4. Authentication for CI

**GitHub Actions:**
- Use repository secrets for API keys
- ANTHROPIC_API_KEY stored securely
- Minimal permissions (read code, write comments)

**Security:**
- Never commit API keys
- Use short-lived tokens where possible
- Audit access logs
- Rate limit API usage

## Success Metrics

### Local Development
- **Speed:** Review completion < 2 minutes
- **Quality:** 80% of developers find reviews helpful
- **Accuracy:** < 10% false positives
- **Adoption:** 50% of commits reviewed before push

### CI/CD Pipeline
- **Speed:** PR review posted < 5 minutes after PR created
- **Quality:** Catches issues missed by automated tools
- **Reliability:** < 5% workflow failures
- **ROI:** Reduced review time for human reviewers

### Multi-Repo Analysis
- **Detection:** 90%+ accuracy on pattern detection
- **Coverage:** All linked repos analyzed
- **Insights:** Actionable cross-repo recommendations
- **Value:** Architectural improvements identified

## Future Enhancements

### 1. Learning System

Store review feedback and improve over time:

```python
# .air/reviews/feedback.jsonl
{"review_id": "rev_123", "issue_id": "sec_001", "feedback": "correct", "timestamp": "..."}
{"review_id": "rev_123", "issue_id": "perf_002", "feedback": "false_positive", "timestamp": "..."}

# Use feedback to improve
air claude learn-from-reviews
```

### 2. Custom Review Templates

```yaml
# .air/templates/review-python-api.yml
name: Python API Review
applies_to:
  - language: python
  - framework: fastapi

checklist:
  - async_await: Proper async/await usage
  - pydantic: Pydantic validation for inputs
  - openapi: OpenAPI documentation complete
  - error_handling: Comprehensive error handling
  - security: Authentication, authorization, rate limiting
```

### 3. Visual Diff Review

Future: Support for reviewing visual changes (UI screenshots, etc.)

### 4. Team Collaboration

```bash
# Assign reviewers based on expertise
air review --suggest-reviewers

# Track review metrics per reviewer
air review stats --reviewer=alice
```

## Open Questions

1. **Claude Code API Access**
   - How does Claude Code expose API for CI/CD?
   - Rate limits for automated reviews?
   - Authentication model?

2. **Context Window Management**
   - How to handle very large PRs?
   - Smart chunking strategies?
   - Summary vs full context tradeoffs?

3. **Multi-Platform Support**
   - GitLab and Bitbucket integration?
   - Self-hosted git support?
   - Different CI/CD systems?

4. **Review Quality**
   - How to measure review quality?
   - How to prevent AI hallucinations?
   - Human-in-the-loop for high-stakes reviews?

## References

- [AIR Architecture](./ARCHITECTURE.md)
- [AIR Commands](./COMMANDS.md)
- [AI Integration](./AI-INTEGRATION.md)
- [Task Archive Design](./TASK-ARCHIVE-DESIGN.md)

## Changelog

- **2025-10-04** - Initial architecture document
