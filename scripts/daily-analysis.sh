#!/bin/bash
# Daily Analysis Automation Script
#
# Usage:
#   ./scripts/daily-analysis.sh              # Analyze all repos
#   ./scripts/daily-analysis.sh --dry-run    # Show what would be updated
#   ./scripts/daily-analysis.sh --no-pull    # Skip git pull, just analyze
#
# This script:
# 1. Pulls latest changes for all linked repos
# 2. Runs dependency-aware analysis on all repos
# 3. Shows high-severity findings

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=false
NO_PULL=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --no-pull)
            NO_PULL=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be updated without making changes"
            echo "  --no-pull    Skip git pull, just run analysis"
            echo "  -h, --help   Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   AIR Daily Analysis Automation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if air is installed
if ! command -v air &> /dev/null; then
    echo -e "${RED}✗ Error: 'air' command not found${NC}"
    echo "  Install with: pip install air-toolkit"
    exit 1
fi

# Check if in AIR project
if ! air status &> /dev/null; then
    echo -e "${RED}✗ Error: Not in an AIR project${NC}"
    echo "  Run 'air init' to create a project"
    exit 1
fi

# Get list of linked repos
echo -e "${BLUE}📋 Getting linked repositories...${NC}"
REPOS_JSON=$(air link list --format=json 2>/dev/null)

if [ -z "$REPOS_JSON" ]; then
    echo -e "${YELLOW}⚠ No linked repositories found${NC}"
    echo "  Use 'air link add' to link repositories"
    exit 0
fi

# Count repos
REPO_COUNT=$(echo "$REPOS_JSON" | jq -r '.resources | length')
echo -e "${GREEN}✓ Found $REPO_COUNT linked repositories${NC}"
echo ""

# Update each repository
if [ "$NO_PULL" = false ]; then
    echo -e "${BLUE}🔄 Updating repositories...${NC}"
    echo ""

    UPDATED=0
    FAILED=0
    SKIPPED=0

    echo "$REPOS_JSON" | jq -r '.resources[] | "\(.name)|\(.path)"' | while IFS='|' read -r name path; do
        # Expand tilde in path
        expanded_path="${path/#\~/$HOME}"

        if [ ! -d "$expanded_path" ]; then
            echo -e "${YELLOW}  ⊘ $name${NC} - Path not found: $expanded_path"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        if [ ! -d "$expanded_path/.git" ]; then
            echo -e "${YELLOW}  ⊘ $name${NC} - Not a git repository"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        if [ "$DRY_RUN" = true ]; then
            echo -e "${BLUE}  → $name${NC} (would pull from: $expanded_path)"
            continue
        fi

        # Check for uncommitted changes
        if ! git -C "$expanded_path" diff-index --quiet HEAD -- 2>/dev/null; then
            echo -e "${YELLOW}  ⚠ $name${NC} - Has uncommitted changes (skipping pull)"
            SKIPPED=$((SKIPPED + 1))
            continue
        fi

        # Pull latest changes
        echo -n "  → $name"
        if OUTPUT=$(git -C "$expanded_path" pull 2>&1); then
            if echo "$OUTPUT" | grep -q "Already up to date"; then
                echo -e " ${GREEN}✓ up to date${NC}"
            else
                echo -e " ${GREEN}✓ updated${NC}"
                UPDATED=$((UPDATED + 1))
            fi
        else
            echo -e " ${RED}✗ failed${NC}"
            echo "    Error: $OUTPUT"
            FAILED=$((FAILED + 1))
        fi
    done

    echo ""
    echo -e "${GREEN}✓ Repository update complete${NC}"
    echo "  Updated: $UPDATED, Skipped: $SKIPPED, Failed: $FAILED"
    echo ""
fi

# Run analysis
if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}Would run: air analyze --all${NC}"
    exit 0
fi

echo -e "${BLUE}🔍 Running dependency-aware analysis...${NC}"
echo ""

# Run analysis (default: respects dependencies, checks deps)
if ! air analyze --all; then
    echo ""
    echo -e "${RED}✗ Analysis failed${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Analysis complete${NC}"
echo ""

# Show high-severity findings
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   High-Severity Findings Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Get findings
FINDINGS_JSON=$(air findings --all --format=json 2>/dev/null || echo '{"findings":[],"count":0}')
HIGH_COUNT=$(echo "$FINDINGS_JSON" | jq -r '[.findings[] | select(.severity == "high" or .severity == "critical")] | length')

if [ "$HIGH_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✓ No high-severity findings${NC}"
else
    echo -e "${YELLOW}⚠ Found $HIGH_COUNT high-severity findings${NC}"
    echo ""
    air findings --all --severity=high --details
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✓ Daily analysis complete!${NC}"
echo ""
echo "View all findings:"
echo "  air findings --all"
echo ""
echo "View specific severity:"
echo "  air findings --all --severity=critical"
echo "  air findings --all --severity=high"
echo ""
echo "View dependency graph:"
echo "  cat analysis/dependency-graph.json | jq"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
