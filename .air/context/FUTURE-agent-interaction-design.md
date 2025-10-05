# Future Design: Agent Interaction and Shared Context

**Status**: Design Exploration
**Target**: v0.7.0+
**Created**: 2025-10-04

## User Requirement

> "Eventually we want the agents to be able to interact and ask each other questions that can be served from context."

## Current State (v0.6.0)

Workers are **independent**:
- Each agent analyzes its own resource
- No communication between agents
- Claude (coordinator) aggregates results after completion
- Findings written to separate JSON files

## Proposed: Shared Context Layer

### Option 1: Shared Knowledge Base

```
.air/shared/
├── context.json          # Shared context across agents
├── findings/             # Incremental findings as agents work
│   ├── agent-1.json
│   ├── agent-2.json
│   └── agent-3.json
└── queries/              # Agent-to-agent queries
    └── agent-1-asks-agent-2.json
```

**Workflow:**
```python
# Agent 1 finds something
agent_1.write_finding({
    "type": "authentication_pattern",
    "pattern": "JWT with HS256",
    "confidence": 0.95
})

# Agent 2 can query shared context
auth_patterns = query_shared_context("authentication_pattern")
# Returns findings from all agents that have written auth patterns

# Agent 2 uses this to compare
if auth_patterns["agent-1"] != my_auth_pattern:
    flag_inconsistency("Different auth patterns across services")
```

### Option 2: Message Queue

```
.air/agents/messages/
├── agent-1-to-agent-2.json
├── agent-2-to-agent-3.json
└── broadcast.json
```

**Workflow:**
```python
# Agent 1 asks a question
send_message(
    to="agent-2",
    question="What authentication pattern did you find?"
)

# Agent 2 responds
send_message(
    to="agent-1",
    answer="JWT with HS256"
)
```

### Option 3: Semantic Search (Vector DB)

```
.air/shared/
└── embeddings.db  # Vector database (sqlite-vss)
```

**Workflow:**
```python
# Agent 1 writes findings with embeddings
store_finding(
    text="Service uses JWT authentication with HS256 signing",
    metadata={"agent": "agent-1", "topic": "authentication"}
)

# Agent 2 queries semantically
similar_findings = semantic_search("authentication methods")
# Returns findings from all agents related to authentication
```

### Option 4: Coordinator Pattern (Current Best)

**Don't build infrastructure** - let Claude coordinate via AIR commands:

```python
# Agent 1 finishes
air analyze repos/service-a --background --id=agent-1
# Writes: analysis/reviews/service-a-findings.json

# Agent 2 can read Agent 1's findings
findings_1 = read_json("analysis/reviews/service-a-findings.json")

# Agent 2 uses this context
if my_auth_pattern != findings_1["authentication"]:
    create_finding("Inconsistent auth across services")
```

**Benefits**:
- ✅ Simple (use filesystem, no new infrastructure)
- ✅ Already works (findings are in JSON)
- ✅ Visible to humans (files on disk)
- ✅ Debuggable (can inspect JSON)
- ✅ Claude can coordinate this today

## Recommendation: Start with Option 4

**Phase 1 (v0.6.x)**: Coordinator pattern
- Agents write findings to `analysis/reviews/`
- Later agents can read earlier findings
- Claude coordinates read order

**Phase 2 (v0.7.0)**: Shared context helper
- Add `air context set <key> <value>`
- Add `air context get <key>`
- Stored in `.air/shared/context.json`
- Agents can share simple key-value data

**Phase 3 (v0.8.0)**: Semantic search
- Add vector database for finding similarity
- `air findings search "authentication patterns"`
- Enables "what did agents find about X?"

## Example Workflows

### Gap Analysis with Shared Context

```bash
# Agent 1: Analyze library capabilities
air analyze repos/library --background --id=lib-caps
# Writes: analysis/reviews/library-findings.json

# Agent 2: Analyze service needs (can read lib-caps findings)
air analyze repos/service --background --id=service-needs
# Reads: analysis/reviews/library-findings.json
# Compares: service needs vs library capabilities
# Writes: analysis/reviews/service-needs-findings.json with gap analysis

# Agent 3: Synthesize (reads both)
air analyze --synthesize --inputs=lib-caps,service-needs
# Creates: analysis/gap-analysis.md
```

### Consistency Checker

```bash
# Agents analyze 5 microservices in parallel
air analyze repos/service-* --background

# Consistency agent runs last
air consistency-check --compare=authentication,logging,error-handling

# Reads all findings
# Identifies inconsistencies
# Creates report: analysis/consistency-report.md
```

### Progressive Discovery

```bash
# Agent 1: Quick classification
air analyze repos/service-a --quick --id=classify-a
# Writes: {"type": "fastapi_service", "has_auth": true}

# Agent 2: Deep dive (uses classification)
read_classification = analysis/reviews/service-a-findings.json
if read_classification["has_auth"]:
    air analyze repos/service-a --focus=security --id=security-a
```

## Implementation Sketch (v0.7.0)

### Shared Context API

```python
# src/air/services/shared_context.py

def set_context(key: str, value: Any) -> None:
    """Set shared context value."""
    context_file = Path(".air/shared/context.json")
    context = load_or_empty(context_file)
    context[key] = value
    context_file.write_text(json.dumps(context, indent=2))

def get_context(key: str) -> Any:
    """Get shared context value."""
    context_file = Path(".air/shared/context.json")
    if not context_file.exists():
        return None
    context = json.loads(context_file.read_text())
    return context.get(key)

def query_findings(query: str) -> list[dict]:
    """Query all findings (simple text search)."""
    findings = []
    for f in Path("analysis/reviews").glob("*.json"):
        data = json.loads(f.read_text())
        if query.lower() in json.dumps(data).lower():
            findings.append(data)
    return findings
```

### CLI Commands

```bash
# Set context
air context set auth_pattern "JWT with HS256"

# Get context
air context get auth_pattern
# Output: JWT with HS256

# Query findings
air findings search "authentication"
# Returns all findings mentioning authentication
```

### Agent Usage

```python
# In analyze.py, agents can use shared context

# Write to context
from air.services.shared_context import set_context
set_context(f"auth_pattern_{resource_name}", auth_info)

# Read from context
from air.services.shared_context import get_context, query_findings
other_auth_patterns = query_findings("authentication")
```

## Questions to Resolve

1. **Timing**: When can Agent B read Agent A's findings?
   - Option: Agent A must complete first (sequential)
   - Option: Agents write incrementally, Agent B polls

2. **Discovery**: How does Agent B know what Agent A found?
   - Option: Agent B reads all findings files
   - Option: Shared index/manifest

3. **Conflicts**: What if agents write conflicting data?
   - Option: Last write wins
   - Option: Conflict detection and merge

4. **Scale**: What if 100 agents write simultaneously?
   - Option: File locking
   - Option: SQLite for atomic writes

## Next Steps

1. **Validate with real use case**: Try coordinator pattern (Option 4) first
2. **Gather feedback**: Does Claude need more than file-based coordination?
3. **Prototype v0.7.0**: Implement shared context API if needed
4. **Measure**: Do agents actually benefit from sharing context?

## Related

- `docs/AGENT-COORDINATION.md` - Current coordination patterns
- `docs/examples/CLAUDE-WORKFLOW-GAP-ANALYSIS.md` - Gap analysis workflow
- This builds on v0.6.0 parallel analysis foundation
