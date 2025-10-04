# Parallel Analysis Quickstart

**Tutorial for AIR v0.6.0+**

Learn how to analyze multiple repositories in parallel using AIR's agent coordination system.

## Prerequisites

- Python 3.10 or later
- pip or pipx installed
- 2-3 repositories to analyze (can be local directories)

## Step 1: Install AIR Toolkit

### Option A: Using pipx (Recommended)

```bash
pipx install air-toolkit
```

### Option B: Using pip

```bash
pip install --user air-toolkit
```

### Verify Installation

```bash
air --version
# Output: air, version 0.6.0
```

## Step 2: Create an Assessment Project

Create a new AIR project to analyze multiple repositories:

```bash
# Create project directory
mkdir my-analysis
cd my-analysis

# Initialize AIR project
air init . --mode=mixed
```

**Expected output:**

```
ℹ Initializing AIR in current directory: my-analysis
ℹ Mode: mixed
ℹ Creating directory structure...
ℹ Generating project files...
✓ Project created successfully
```

## Step 3: Link Repositories to Analyze

Link the repositories you want to analyze. AIR creates symlinks so your original repos stay untouched.

### Example: Analyzing Local Projects

```bash
# Link a Python service
air link add ~/projects/my-api-service

# Link a documentation repo
air link add ~/projects/my-docs

# Link a library
air link add ~/projects/my-utils-lib
```

**What happens:**
- AIR creates symlinks in `repos/` directory
- Auto-detects repository type and technology stack
- Adds entries to `air-config.json`

### Example: Analyzing from Specific Paths

```bash
# If you cloned some repos to analyze
git clone https://github.com/example/service-a /tmp/service-a
git clone https://github.com/example/service-b /tmp/service-b

# Link them
air link add /tmp/service-a
air link add /tmp/service-b
```

### Verify Links

```bash
air link list
```

**Expected output:**

```
Review Resources (Read-Only)

Name             Type            Tech Stack      Path
my-api-service   library         Python/FastAPI  /Users/you/projects/my-api-service
my-docs          documentation   Markdown        /Users/you/projects/my-docs
my-utils-lib     library         Python          /Users/you/projects/my-utils-lib

Total: 3 resources
```

## Step 4: Run Parallel Analyses

Now the exciting part - run analyses in parallel!

### Spawn Background Agents

```bash
# Start 3 analyses running concurrently
air analyze repos/my-api-service --background --id=analysis-api
air analyze repos/my-docs --background --id=analysis-docs
air analyze repos/my-utils-lib --background --id=analysis-utils
```

**Expected output (for each):**

```
✓ Started background agent: analysis-api (PID: 12345)
```

### What Just Happened?

- 3 separate agents spawned as background processes
- Each agent analyzes its repository independently
- Results written to `.air/agents/<id>/` directories
- You can continue working while they run

## Step 5: Monitor Agent Progress

Check on your running analyses:

```bash
air status --agents
```

**Expected output:**

```
Active Agents

Agent           Status      Started    Progress
analysis-api    ⏳ Running  1m ago     Analyzing auth patterns...
analysis-docs   ✓ Complete  2m ago
analysis-utils  ⏳ Running  30s ago    Reviewing database queries...

Total: 3 agents (2 running, 1 complete, 0 failed)
```

### Check Status in JSON (for scripts)

```bash
air status --agents --format=json
```

## Step 6: View Aggregated Findings

Once analyses complete (usually 30 seconds to 2 minutes), view all findings together:

```bash
air findings --all
```

**Expected output:**

```
Analysis Findings

Source          Severity  Category        Description
my-api-service  ℹ️  Info   classification  High Python content (92%) with FastAPI...
my-docs         ℹ️  Info   classification  High documentation content (95%)
my-utils-lib    ℹ️  Info   classification  Python library with 15 dependencies

Total: 3 findings (0 high, 0 medium, 3 low)
```

### Filter by Severity

```bash
# Show only high-severity findings
air findings --all --severity=high

# Show medium and high
air findings --all --severity=medium
```

### Export as JSON

```bash
air findings --all --format=json > findings-report.json
```

## Step 7: Run Focused Analysis

Run analysis with a specific focus area:

```bash
# Security-focused analysis
air analyze repos/my-api-service --background --id=security-check --focus=security

# Architecture analysis
air analyze repos/my-api-service --background --id=arch-review --focus=architecture

# Performance analysis
air analyze repos/my-api-service --background --id=perf-check --focus=performance
```

## Advanced Usage

### Inline Analysis (No Background)

For quick checks without spawning agents:

```bash
air analyze repos/my-api-service
```

Output appears immediately in your terminal.

### Check Agent Logs

View detailed output from a specific agent:

```bash
# View stdout
cat .air/agents/analysis-api/stdout.log

# View stderr (errors)
cat .air/agents/analysis-api/stderr.log

# View metadata
cat .air/agents/analysis-api/metadata.json
```

### Project Status Overview

See your entire project status:

```bash
air status
```

**Shows:**
- Linked resources
- Analysis files created
- Task tracking stats

## Real-World Example: Multi-Microservice Analysis

Analyze an entire microservices architecture:

```bash
# 1. Create analysis project
mkdir microservices-review
cd microservices-review
air init . --mode=review

# 2. Link all microservices
air link add ~/services/auth-service
air link add ~/services/user-service
air link add ~/services/payment-service
air link add ~/services/notification-service
air link add ~/services/api-gateway

# 3. Run parallel security analysis on all services
air analyze repos/auth-service --background --id=sec-auth --focus=security
air analyze repos/user-service --background --id=sec-user --focus=security
air analyze repos/payment-service --background --id=sec-payment --focus=security
air analyze repos/notification-service --background --id=sec-notif --focus=security
air analyze repos/api-gateway --background --id=sec-gateway --focus=security

# 4. Monitor progress
watch -n 2 'air status --agents'

# 5. View security findings across all services
air findings --all --severity=high
```

## Troubleshooting

### Agent Stuck in "Running" State

Check if the process is still alive:

```bash
# View agent metadata
cat .air/agents/<agent-id>/metadata.json | grep pid

# Check if process exists
ps -p <PID>
```

### No Findings Generated

Check the agent logs:

```bash
cat .air/agents/<agent-id>/stderr.log
```

### Agent Failed to Start

Ensure you're in an AIR project directory:

```bash
air status
# Should show project info, not an error
```

## Directory Structure

After following this tutorial, your project looks like:

```
my-analysis/
├── .air/
│   ├── agents/              # NEW: Agent tracking
│   │   ├── analysis-api/
│   │   │   ├── metadata.json
│   │   │   ├── stdout.log
│   │   │   └── stderr.log
│   │   ├── analysis-docs/
│   │   └── analysis-utils/
│   ├── shared/              # NEW: Shared state
│   ├── tasks/               # Task tracking
│   └── context/             # Project context
├── repos/                   # Symlinks to repositories
│   ├── my-api-service@
│   ├── my-docs@
│   └── my-utils-lib@
├── analysis/
│   └── reviews/             # Analysis findings
│       ├── my-api-service-findings.json
│       ├── my-docs-findings.json
│       └── my-utils-lib-findings.json
├── air-config.json          # Project configuration
├── CLAUDE.md                # AI assistant guidance
└── README.md                # Project overview
```

## Next Steps

1. **Explore findings files**: Check `analysis/reviews/*.json` for detailed results

2. **Learn more commands**: Run `air --help` to see all available commands

3. **Read the roadmap**: See `.air/tasks/20251004-1520-mvp-parallel-analysis-tracking.md` for upcoming features

4. **Try advanced workflows**:
   - Chain analyses with different focus areas
   - Export findings to CI/CD pipelines
   - Integrate with GitHub Actions

## Key Concepts

### Background vs Inline

- **Background** (`--background`): Agent runs independently, you continue working
- **Inline** (default): Analysis runs in foreground, output to terminal

### Agent Lifecycle

1. **Spawn**: `air analyze --background --id=<id>`
2. **Running**: Agent analyzes repository
3. **Complete**: Findings written to `analysis/reviews/`
4. **Monitor**: `air status --agents` shows current state

### Findings Aggregation

- Each analysis creates `<resource>-findings.json`
- `air findings --all` aggregates across all JSON files
- Filter by severity, export as JSON
- Perfect for generating reports

## Tips & Best Practices

### ✅ DO

- Use descriptive agent IDs: `--id=security-auth-service` not `--id=agent1`
- Run 3-5 agents concurrently for best performance
- Check `air status --agents` periodically during long analyses
- Use `--focus` to target specific concerns (security, architecture)

### ❌ DON'T

- Don't spawn too many agents (>10) - can overwhelm system
- Don't reuse agent IDs while agents are still running
- Don't modify files in `repos/` - they're symlinks to your originals

## Help & Support

- **Documentation**: See `docs/COMMANDS.md` for complete reference
- **Examples**: Check `docs/examples/` for more scenarios
- **Issues**: Report bugs at https://github.com/anthropics/air-toolkit/issues

---

**Congratulations!** You've successfully run parallel repository analysis with AIR v0.6.0. 🎉

You can now:
- Analyze multiple repositories simultaneously
- Monitor agent progress in real-time
- Aggregate findings across projects
- Export results for reports

Explore the [full documentation](../COMMANDS.md) to learn about all AIR features.
