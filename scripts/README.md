# AIR Automation Scripts

Utility scripts for automating common AIR workflows.

## Daily Analysis (`daily-analysis.sh`)

Automates the daily workflow of pulling changes from linked repositories and running analysis.

### Usage

**Basic usage** (pull changes + analyze):
```bash
./scripts/daily-analysis.sh
```

**Dry run** (show what would happen):
```bash
./scripts/daily-analysis.sh --dry-run
```

**Skip git pull** (just analyze):
```bash
./scripts/daily-analysis.sh --no-pull
```

**Help**:
```bash
./scripts/daily-analysis.sh --help
```

### What It Does

1. **Validates environment**
   - Checks `air` is installed
   - Verifies you're in an AIR project
   - Gets list of linked repositories

2. **Updates repositories** (unless `--no-pull`)
   - Runs `git pull` on each linked repo
   - Skips repos with uncommitted changes
   - Reports updated/skipped/failed repos

3. **Runs analysis**
   - `air analyze --all` (dependency-aware, respects order by default)
   - Builds dependency graph
   - Detects gaps between linked repos

4. **Shows summary**
   - Displays high-severity findings
   - Provides commands for viewing results

### Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   AIR Daily Analysis Automation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Getting linked repositories...
✓ Found 3 linked repositories

🔄 Updating repositories...

  → shared-utils ✓ updated
  → api-service ✓ up to date
  → web-service ✓ updated

✓ Repository update complete
  Updated: 2, Skipped: 0, Failed: 0

🔍 Running dependency-aware analysis...

Building dependency graph...
Dependency graph saved: analysis/dependency-graph.json
Analysis order: 2 levels
  Level 1: shared-utils
  Level 2: api-service, web-service

Analyzing: shared-utils
✓ shared-utils: 12 findings

Analyzing: api-service
✓ api-service: 23 findings

Analyzing: web-service
✓ web-service: 18 findings

Checking for dependency gaps...
⚠️ Found 2 dependency issues:
  api-service uses shared-utils@1.2.0 but 1.3.0 is available
  web-service uses shared-utils@1.1.0 but 1.3.0 is available

✓ Analysis complete

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   High-Severity Findings Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠ Found 3 high-severity findings

[Detailed findings displayed here...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Daily analysis complete!

View all findings:
  air findings --all

View specific severity:
  air findings --all --severity=critical
  air findings --all --severity=high

View dependency graph:
  cat analysis/dependency-graph.json | jq
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Use Cases

**Daily standup preparation:**
```bash
# Every morning before standup
./scripts/daily-analysis.sh
```

**Pre-deployment check:**
```bash
# Before deploying
./scripts/daily-analysis.sh
air findings --all --severity=critical
```

**CI/CD integration:**
```bash
# In your CI pipeline
./scripts/daily-analysis.sh --no-pull  # repos already cloned
if [ $? -ne 0 ]; then
  echo "Analysis found critical issues"
  exit 1
fi
```

**Cron job** (Linux/macOS):
```bash
# Add to crontab: analyze daily at 9 AM
0 9 * * * cd /path/to/air-project && ./scripts/daily-analysis.sh
```

### Requirements

- `air` installed (`pip install air-toolkit`)
- `jq` for JSON parsing (`brew install jq` or `apt install jq`)
- Git repositories configured with appropriate credentials
- AIR project initialized with linked repos

### Troubleshooting

**Error: "air command not found"**
```bash
pip install air-toolkit
# or
pip install -e .  # if developing AIR itself
```

**Error: "Not in an AIR project"**
```bash
# Initialize AIR project first
air init my-project
cd my-project
air link add ~/repos/service-a
```

**Repos skipped with "uncommitted changes"**
- Commit or stash changes before running
- Or use `--no-pull` to skip git pull and just analyze

**jq not found**
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq

# CentOS/RHEL
sudo yum install jq
```

### Customization

You can customize the script by editing `daily-analysis.sh`:

**Change analysis options:**
```bash
# Skip isolated repos
air analyze --all --deps-only

# Parallel analysis (disable dependency order)
air analyze --all --no-order

# Focus on security
air analyze --all --focus=security
```

**Change findings display:**
```bash
# Show all findings, not just high
air findings --all

# Show only critical
air findings --all --severity=critical

# JSON output for further processing
air findings --all --format=json | jq '.findings[] | select(.severity == "critical")'
```

**Send notifications:**
```bash
# Add to end of script
if [ "$HIGH_COUNT" -gt 0 ]; then
  # Slack notification
  curl -X POST -H 'Content-type: application/json' \
    --data "{\"text\":\"⚠️ AIR found $HIGH_COUNT high-severity issues\"}" \
    $SLACK_WEBHOOK_URL

  # Email notification
  echo "Found $HIGH_COUNT high-severity issues" | \
    mail -s "AIR Daily Analysis Alert" your-email@example.com
fi
```

## Future Scripts

Planned automation scripts:

- `sync-repos.sh` - Pull all repos and show status
- `analyze-pr.sh` - Analyze specific PR branch across repos
- `generate-report.sh` - Generate HTML/PDF reports from findings
- `cleanup-old-findings.sh` - Archive old analysis results
