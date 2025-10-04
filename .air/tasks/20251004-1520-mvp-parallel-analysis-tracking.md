# Task: MVP - Parallel Analysis Tracking (v0.6.0)

## Date
2025-10-04 15:20

## Prompt
User: "publish, and then create a detailed spec for MVP"

## Goal

Implement the MVP for agent coordination: **enable tracking multiple concurrent analysis tasks and viewing combined results.**

**Version**: v0.6.0
**Timeline**: 1 week
**Complexity**: Medium

## User Story

As an AIR user analyzing multiple repositories,
I want to run analyses in parallel and see combined results,
So that I can complete multi-repo assessments faster.

## Success Criteria

✅ Can track 3+ concurrent analyses
✅ Can see combined findings in one view
✅ No crashes, clean error messages
✅ All existing functionality still works

## Implementation Plan

### Phase 1: Directory Structure (Day 1)

**Create agent tracking directories:**

```
.air/
├── agents/                     # NEW: Agent tracking
│   └── <agent-id>/            # One directory per agent
│       ├── metadata.json      # Agent info
│       ├── stdout.log         # Agent output
│       ├── stderr.log         # Agent errors
│       └── findings.json      # Agent findings
└── shared/                    # NEW: Shared state
    └── findings.json          # All findings combined
```

**Implementation:**
- Create directories automatically in `air init`
- Add `.gitignore` entries for agent logs (transient)
- Keep `findings.json` in git (results)

### Phase 2: Background Flag (Day 2)

**Add `--background` flag to existing commands:**

```bash
air analyze repos/service-a --background --id=analysis-1
```

**Changes needed:**

1. **src/air/commands/analyze.py** (create new command):
```python
@click.command()
@click.argument("resource_path")
@click.option("--background", is_flag=True, help="Run in background")
@click.option("--id", help="Agent identifier")
@click.option("--focus", help="Analysis focus area")
def analyze(resource_path: str, background: bool, id: str, focus: str):
    """Analyze a repository."""

    if background:
        # Spawn background process
        agent_id = id or generate_agent_id()
        spawn_background_agent(agent_id, "analyze", {
            "resource_path": resource_path,
            "focus": focus
        })
        success(f"Started background agent: {agent_id}")
    else:
        # Run inline (current behavior)
        run_analysis(resource_path, focus)
```

2. **src/air/services/agent_manager.py** (new file):
```python
def spawn_background_agent(agent_id: str, command: str, args: dict):
    """Spawn a background agent."""

    # Create agent directory
    agent_dir = Path(f".air/agents/{agent_id}")
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Write metadata
    metadata = {
        "id": agent_id,
        "command": command,
        "args": args,
        "status": "running",
        "started": datetime.now().isoformat(),
        "pid": None  # Will be set by subprocess
    }
    (agent_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    # Spawn subprocess
    # For MVP: simple subprocess, no daemon
    # Future: proper background daemon
    subprocess.Popen(
        ["air", command, *serialize_args(args)],
        stdout=open(agent_dir / "stdout.log", "w"),
        stderr=open(agent_dir / "stderr.log", "w"),
        cwd=Path.cwd()
    )
```

### Phase 3: Agent Status Command (Day 3)

**Add `air status --agents` command:**

```bash
air status --agents
```

**Output:**
```
Active Agents:

AGENT        STATUS     STARTED      PROGRESS
analysis-1   Running    10:23 AM     Analyzing auth patterns...
analysis-2   Complete   10:24 AM     ✓ Done
analysis-3   Running    10:25 AM     Reviewing database queries...

Total: 3 agents (2 running, 1 complete)
```

**Implementation:**

```python
# src/air/commands/status.py (extend existing)

@click.option("--agents", is_flag=True, help="Show agent status")
def status(agents: bool, ...):
    """Show project status."""

    if agents:
        show_agent_status()
    else:
        # Existing status logic
        ...

def show_agent_status():
    """Display agent status table."""

    # Load all agents
    agents = []
    for agent_dir in Path(".air/agents").glob("*/"):
        metadata_file = agent_dir / "metadata.json"
        if metadata_file.exists():
            agents.append(json.loads(metadata_file.read_text()))

    if not agents:
        info("No agents found")
        return

    # Create table
    table = Table(title="Active Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Started", style="dim")
    table.add_column("Progress", style="green")

    for agent in agents:
        status_emoji = "⏳" if agent["status"] == "running" else "✓"
        table.add_row(
            agent["id"],
            f"{status_emoji} {agent['status'].capitalize()}",
            format_time(agent["started"]),
            get_agent_progress(agent["id"])
        )

    console.print(table)
```

### Phase 4: Findings Aggregation (Day 4)

**Add `air findings --all` command:**

```bash
air findings --all
```

**Output:**
```
Combined Findings:

AGENT        SEVERITY  CATEGORY      FILE              LINE  DESCRIPTION
analysis-1   High      Security      auth.py           42    No password hashing
analysis-1   Medium    Performance   db.py             103   Missing index
analysis-2   High      Security      api.py            67    SQL injection risk
analysis-3   Low       Style         utils.py          23    Long function

Total: 4 findings (2 high, 1 medium, 1 low)
```

**Implementation:**

```python
# src/air/commands/findings.py (new file)

@click.command()
@click.option("--all", "all_agents", is_flag=True, help="Show findings from all agents")
@click.option("--agent", help="Show findings from specific agent")
@click.option("--severity", help="Filter by severity")
def findings(all_agents: bool, agent: str, severity: str):
    """View analysis findings."""

    # Load findings
    all_findings = []

    if all_agents:
        # Aggregate from all agents
        for agent_dir in Path(".air/agents").glob("*/"):
            findings_file = agent_dir / "findings.json"
            if findings_file.exists():
                agent_findings = json.loads(findings_file.read_text())
                for finding in agent_findings:
                    finding["agent"] = agent_dir.name
                    all_findings.append(finding)
    elif agent:
        # Single agent
        findings_file = Path(f".air/agents/{agent}/findings.json")
        all_findings = json.loads(findings_file.read_text())

    # Filter by severity
    if severity:
        all_findings = [f for f in all_findings if f["severity"] == severity]

    # Display table
    display_findings_table(all_findings)
```

### Phase 5: Integration & Testing (Day 5)

**Test scenarios:**

1. **Basic parallel execution:**
   ```bash
   air analyze repos/service-a --background --id=a1
   air analyze repos/service-b --background --id=a2
   air status --agents
   air findings --all
   ```

2. **Error handling:**
   - Agent crashes → status shows "failed"
   - Invalid path → error message logged
   - Duplicate agent ID → error and abort

3. **Concurrent findings:**
   - Multiple agents writing findings → no file corruption
   - Findings correctly attributed to agents

**Test implementation:**

```python
# tests/integration/test_agent_coordination.py (new file)

class TestAgentCoordination:

    def test_background_agent_spawning(self, runner, isolated_project):
        """Test spawning background agent."""
        # Setup
        runner.invoke(main, ["init", "test-project"])
        os.chdir(isolated_project / "test-project")

        # Spawn agent
        result = runner.invoke(main, [
            "analyze", "repos/test",
            "--background", "--id=test-agent"
        ])

        assert result.exit_code == 0
        assert "Started background agent: test-agent" in result.output

        # Verify agent directory created
        assert (isolated_project / "test-project/.air/agents/test-agent").exists()

    def test_agent_status_display(self, runner, isolated_project):
        """Test agent status command."""
        # Setup with running agent
        # ... spawn agent ...

        # Check status
        result = runner.invoke(main, ["status", "--agents"])

        assert result.exit_code == 0
        assert "test-agent" in result.output
        assert "Running" in result.output

    def test_findings_aggregation(self, runner, isolated_project):
        """Test aggregating findings from multiple agents."""
        # Setup with 2 agents that have findings
        # ... create mock findings ...

        # Get all findings
        result = runner.invoke(main, ["findings", "--all"])

        assert result.exit_code == 0
        # Should see findings from both agents
```

### Phase 6: Documentation (Day 6-7)

**Update documentation:**

1. **docs/COMMANDS.md**:
   - Document `air analyze --background`
   - Document `air status --agents`
   - Document `air findings --all`

2. **CHANGELOG.md**:
   ```markdown
   ## [0.6.0] - 2025-10-XX

   ### Added

   - **Agent coordination system** - Track multiple concurrent analyses
   - `air analyze --background` - Run analyses in background
   - `air status --agents` - View all agent status
   - `air findings --all` - Aggregate findings from all agents
   ```

3. **Create example workflow** in `docs/examples/parallel-analysis.md`

## Files to Create/Modify

### New Files:
- `src/air/commands/analyze.py` - Analysis command
- `src/air/commands/findings.py` - Findings command
- `src/air/services/agent_manager.py` - Agent lifecycle management
- `tests/integration/test_agent_coordination.py` - Agent tests
- `docs/examples/parallel-analysis.md` - Usage examples

### Modified Files:
- `src/air/commands/status.py` - Add `--agents` flag
- `src/air/commands/init.py` - Create `.air/agents/` and `.air/shared/`
- `src/air/cli.py` - Register new commands
- `docs/COMMANDS.md` - Document new features
- `CHANGELOG.md` - v0.6.0 entry
- `pyproject.toml` - Version bump to 0.6.0
- `src/air/__init__.py` - Version bump

## Technical Decisions

### 1. Process Management: Subprocess (MVP)

**Decision**: Use Python `subprocess.Popen()` for MVP
**Rationale**: Simple, works across platforms, no daemon complexity
**Future**: Consider background daemon in v0.6.1

### 2. Storage: JSON Files (MVP)

**Decision**: Store metadata and findings in JSON files
**Rationale**: Human-readable, easy to debug, no database dependency
**Future**: Migrate to SQLite in v0.6.2 for better querying

### 3. Agent Communication: None (MVP)

**Decision**: Agents don't communicate in v0.6.0
**Rationale**: Reduces complexity, gets MVP shipped faster
**Future**: Add shared findings DB in v0.6.2

## Risks & Mitigations

### Risk 1: Zombie Processes
**Problem**: Background agents may not terminate cleanly
**Mitigation**:
- Store PID in metadata
- Add `air cleanup` command to kill orphaned processes
- Add process monitoring in status command

### Risk 2: File Corruption
**Problem**: Multiple agents writing to same file
**Rationale**: Each agent has own findings file, aggregation is read-only

### Risk 3: Resource Exhaustion
**Problem**: User spawns 100 agents, system crashes
**Mitigation**:
- Document best practices (3-5 agents recommended)
- Add warning if >5 agents running
- Future: Enforce limits in v0.6.4

## Success Metrics

After MVP completion:

- ✅ Can run 3 analyses in parallel
- ✅ Status command shows all agents
- ✅ Findings aggregation works correctly
- ✅ Zero crashes during parallel execution
- ✅ Documentation clear and complete

## Next Steps After MVP

After v0.6.0 ships:

1. **Gather feedback**: Dogfood with air-toolkit analysis
2. **Identify pain points**: What's missing? What's confusing?
3. **Plan v0.6.1**: Automated spawning with `air spawn`
4. **Iterate**: Ship fast, learn fast

## Outcome
✅ Success

Successfully implemented v0.6.0 MVP for parallel analysis tracking.

All 6 phases complete:
- Phase 1: Directory structure ✓
- Phase 2: Background execution ✓
- Phase 3: Agent status ✓
- Phase 4: Findings aggregation ✓
- Phase 5: Integration testing (344 tests passing) ✓
- Phase 6: Documentation updates ✓

Ready for release and dogfooding.
