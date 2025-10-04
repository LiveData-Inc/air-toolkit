# AIR Toolkit - Feature Specification

**Version:** 0.4.2
**Status:** Active
**Last Updated:** 2025-10-04

## 1. Overview

### 1.1 Purpose

AIR (AI Review) is a unified toolkit providing two complementary capabilities:

1. **Multi-Project Assessment**: Structured framework for analyzing and comparing multiple codebases
2. **AI Task Tracking**: Automatic task file generation and tracking for AI-assisted development

### 1.2 Goals

- Provide consistent, repeatable process for multi-project code reviews
- Enable AI assistants to automatically track work with zero friction
- Support both review-only and collaborative workflows
- Cross-platform distribution (macOS, Linux, Windows)
- Simple installation via pip/pipx

### 1.3 Non-Goals

- IDE integration (VS Code extension, etc.)
- Web-based UI or dashboard
- Team collaboration features (Phase 1)
- CI/CD integration (Phase 1)

## 2. Core Concepts

### 2.1 Two Resource Types

**Review-Only Resources**
- Implementation projects owned by other teams
- Read-only access (symlinks)
- Output: Analysis documents ABOUT them
- Location: `repos/` directory

**Collaborative Resources**
- Shared documentation with write access
- Can be cloned or symlinked
- Output: Contributions TO them
- Location: `repos/` directory

### 2.2 Project Modes

**Review Mode** (`--mode=review`)
- Single-purpose: assess other teams' work
- Creates: `repos/`, `analysis/reviews/`
- Workflow: Review → Analyze → Document → Share

**Development Mode** (`--mode=develop`)
- Single-purpose: improve shared documentation
- Creates: `repos/`, `analysis/improvements/`, `contributions/`
- Workflow: Review → Analyze → Contribute → PR

**Mixed Mode** (`--mode=mixed`, default)
- Both review and developer resources
- Complete directory structure
- Supports both workflows

### 2.3 Task Tracking System

**Automatic Task Files**
- AI creates task files as work progresses
- Format: `.air/tasks/YYYYMMDD-HHMM-description.md`
- Zero friction - no user action required
- Structured markdown format

**Context Management**
- `.air/context/architecture.md` - System design
- `.air/context/language.md` - Language conventions
- `.air/context/decisions.md` - Key decisions

## 3. Features

### 3.1 Assessment Features

#### 3.1.1 Project Initialization

**Command:** `air init [name] [options]`

**Capabilities:**
- Create new assessment project with specified mode
- Set up directory structure based on mode
- Initialize git repository
- Create README.md, CLAUDE.md, .gitignore
- Optionally initialize .air/ tracking
- Generate air-config.json

**Options:**
- `--mode=review|collaborate|mixed` - Project mode (default: mixed)
- `--track/--no-track` - Initialize .air/ tracking (default: true)

**Output Structure (Mixed Mode):**
```
project-name/
├── README.md              # Project goals and overview
├── CLAUDE.md              # AI assistant instructions
├── air-config.json        # Project configuration
├── repos/                # Review-only resources
├── repos/           # Collaborative resources
├── analysis/              # Our analysis
│   ├── SUMMARY.md
│   ├── assessments/      # About review resources
│   └── improvements/     # About developer resources
├── contributions/         # Proposed improvements
├── .air/                  # Task tracking
│   ├── README.md
│   ├── tasks/
│   ├── context/
│   └── templates/
└── scripts/              # Helper scripts
```

#### 3.1.2 Repository Linking

**Command:** `air link [options]`

**Capabilities:**
- Link review-only repositories (symlinks)
- Clone or link collaborative repositories
- Read from `repos-to-link.txt` configuration file
- Update `air-config.json` with resource metadata
- Validate repository accessibility

**Options:**
- `--review NAME:PATH` - Add review resource (multiple allowed)
- `--develop NAME:PATH` - Add collaborative resource (multiple allowed)
- `--clone` - Clone instead of symlink (for collaborative)

**Configuration File Format (`repos-to-link.txt`):**
```
# Review-only resources
review:service-a:~/repos/service-a
review:service-b:~/repos/service-b

# Collaborative resources
collaborate:architecture:~/repos/architecture-docs
```

#### 3.1.3 Project Validation

**Command:** `air validate [options]`

**Checks:**
- Directory structure exists and is complete
- Symlinks point to valid locations
- Cloned repositories are accessible
- `air-config.json` is valid
- Git repository status (if applicable)

**Options:**
- `--type=structure|links|config|all` - What to validate (default: all)
- `--fix` - Attempt automatic fixes

**Exit Codes:**
- 0: Valid
- 1: Validation errors found
- 2: Critical errors (missing config, etc.)

#### 3.1.4 Status Reporting

**Command:** `air status [options]`

**Displays:**
- Project mode and configuration
- Linked resources (count by type)
- Analysis documents created
- Contribution status (for developer resources)
- Recent AI tasks

**Options:**
- `--type=review|collaborate|all` - Filter by resource type
- `--contributions` - Show detailed contribution tracking

#### 3.1.5 Resource Classification

**Command:** `air classify [options]`

**Capabilities:**
- Analyze linked resources
- Detect resource characteristics (code vs docs, git repo, etc.)
- Suggest classification (review vs collaborative)
- Interactive prompts for ambiguous cases
- Update configuration

**Options:**
- `--verbose` - Show detailed classification reasoning
- `--update` - Update `air-config.json` automatically

**Classification Heuristics:**
- Git repository with remotes → Potentially collaborative
- Documentation-heavy → Likely collaborative
- Implementation code → Likely review-only
- No git or read-only mount → Review-only

#### 3.1.6 Pull Request Creation

**Command:** `air pr [resource] [options]`

**Workflow:**
1. Validate resource is collaborative type
2. Check `contributions/[resource]/` has content
3. Create git branch
4. Copy contribution files to target locations
5. Commit changes
6. Push branch
7. Create PR via GitHub CLI (`gh`)

**Options:**
- `--branch=NAME` - Branch name (default: auto-generated)
- `--message=TEXT` - Commit message
- `--draft` - Create as draft PR
- `--dry-run` - Preview without executing

**Requirements:**
- GitHub CLI (`gh`) installed and authenticated
- Resource must be a git clone (not symlink)
- Contributions exist in `contributions/[resource]/`

### 3.2 Task Tracking Features

#### 3.2.1 Task File Creation

**Command:** `air task new DESCRIPTION [options]`

**Capabilities:**
- Create timestamped task file
- Use template from `.air/templates/task.md`
- Pre-populate with description and optional prompt
- Auto-open in editor (optional)

**Options:**
- `--prompt=TEXT` - User prompt that triggered task

**Task File Format:**
```markdown
# Task: [Description]

## Date
YYYY-MM-DD HH:MM

## Prompt
[User's exact request]

## Actions Taken
1. [Action 1]
2. [Action 2]

## Files Changed
- `path/file.ext` - [Description of changes]

## Outcome
⏳ In Progress / ✅ Success / ⚠️ Partial / ❌ Blocked

[Summary]

## Notes
[Optional technical notes]
```

#### 3.2.2 Task Listing

**Command:** `air task list [options]`

**Capabilities:**
- List all task files in `.air/tasks/`
- Parse and display status
- Filter by status or date
- Sort by creation time

**Options:**
- `--status=all|in-progress|success|blocked` - Filter by status

**Output Format:**
```
AI Tasks (5 total)

✅ 20251003-1200-implement-feature-x.md (Success)
   Prompt: Add user authentication
   Files: 3 changed

⏳ 20251003-1315-fix-bug-y.md (In Progress)
   Prompt: Fix login redirect issue
   Files: 1 changed
```

#### 3.2.3 Task Completion

**Command:** `air task complete TASK_ID`

**Capabilities:**
- Find task file by ID prefix
- Update outcome status to ✅ Success
- Optionally add completion timestamp

**ID Matching:**
- Full timestamp: `20251003-1200`
- Partial: `20251003` (if unique)
- Fuzzy: `1003-1200`

#### 3.2.4 Tracking Initialization

**Command:** `air track init [options]`

**Capabilities:**
- Add `.air/` structure to any existing project
- Copy templates
- Create README.md with instructions
- Optionally create CLAUDE.md

**Options:**
- `--minimal` - Minimal structure (no full templates)

**Creates:**
```
.air/
├── README.md              # System documentation
├── tasks/                 # Task files
├── context/               # Context files
│   ├── architecture.md
│   ├── language.md
│   └── decisions.md
└── templates/             # Task templates
    └── task.md
```

#### 3.2.5 Tracking Status

**Command:** `air track status`

**Displays:**
- Whether `.air/` exists
- Task count and breakdown by status
- Recent tasks
- Context files present

#### 3.2.6 Summary Generation

**Command:** `air summary [options]`

**Capabilities:**
- Compile all task files into summary
- Multiple output formats
- Filter by date range
- Include statistics

**Options:**
- `--output=FILE` - Write to file (default: stdout)
- `--format=markdown|json|text` - Output format
- `--since=YYYY-MM-DD` - Include only tasks since date

**Output Includes:**
- Total task count
- Status breakdown
- Chronological task list
- Files changed summary
- Key decisions/notes

## 4. Configuration

### 4.1 Project Configuration

**File:** `air-config.json`

```json
{
  "version": "2.0.0",
  "name": "project-name",
  "mode": "mixed",
  "created": "2025-10-03",

  "resources": {
    "review": [
      {
        "name": "service-a",
        "path": "~/repos/service-a",
        "type": "library",
        "relationship": "review-only",
        "outputs": [
          "analysis/reviews/service-a-analysis.md"
        ]
      }
    ],
    "develop": [
      {
        "name": "architecture",
        "path": "~/repos/architecture-docs",
        "type": "documentation",
        "relationship": "contributor",
        "clone": true,
        "outputs": [
          "analysis/improvements/architecture-gaps.md"
        ],
        "contributions": [
          {
            "source": "contributions/architecture/new-guide.md",
            "target": "docs/guides/new-guide.md",
            "status": "proposed"
          }
        ]
      }
    ]
  },

  "goals": [
    "Compare service implementations",
    "Create integration plan",
    "Improve architecture documentation"
  ]
}
```

### 4.2 Global Configuration

**File:** `~/.config/air/config.yaml` (future)

```yaml
# GitHub settings
github:
  default_org: "LiveData-Inc"
  pr_template: "standard"

# Editor preferences
editor: "vim"
auto_open_tasks: true

# Output preferences
color: true
verbose: false
```

## 5. Workflows

### 5.1 Review-Only Workflow

```bash
# 1. Create project
air init service-review --mode=review

# 2. Link repositories
cd service-review
air link --review service-a:~/repos/service-a
air link --review service-b:~/repos/service-b

# 3. Validate
air validate

# 4. AI analysis session
# .init → AI reads repos, creates analysis

# 5. Check status
air status

# 6. View results
cat analysis/reviews/comparison.md

# 7. Share findings
# Present to team, create tickets, etc.
```

### 5.2 Collaborative Workflow

```bash
# 1. Create project
air init doc-improvement --mode=develop

# 2. Clone documentation
cd doc-improvement
air link --develop arch:~/repos/architecture --clone

# 3. AI review session
# .init → AI reviews docs, identifies gaps

# 4. Review analysis
cat analysis/improvements/gaps.md

# 5. Create contributions
# AI or manual: edit contributions/arch/new-guide.md

# 6. Submit PR
air pr arch --branch=add-implementation-guide

# 7. Track PR
# Monitor GitHub for review and merge
```

### 5.3 Mixed Workflow (AA-ingest-review Pattern)

```bash
# 1. Create project
air init inbound-review

# 2. Link both types
cd inbound-review
air link --review ehr-inbound:~/repos/ehr-inbound-data-flow
air link --review change-lib:~/repos/change-command-lib
air link --develop arch:~/repos/cloud-native-architecture --clone

# 3. Classify resources
air classify --verbose

# 4. AI analysis
# Creates both assessments and improvements

# 5. Check outputs
air status --contributions

# 6. Submit collaborative improvements
air pr arch
```

## 6. Technical Requirements

### 6.1 Platform Support

- macOS 12+ (primary target)
- Linux (Ubuntu 20.04+, other distros)
- Windows 10+ (via WSL or native)

### 6.2 Dependencies

**Required:**
- Python 3.10+
- Git 2.30+

**Optional:**
- GitHub CLI (`gh`) - for PR creation

**Python Packages:**
- click >= 8.1.0 - CLI framework
- rich >= 13.0.0 - Terminal formatting
- pydantic >= 2.0.0 - Data validation
- pyyaml >= 6.0 - YAML configuration
- gitpython >= 3.1.0 - Git operations

### 6.3 Installation Methods

**Development:**
```bash
git clone https://github.com/LiveData-Inc/air-toolkit.git
cd air-toolkit
pip install -e .
```

**PyPI (future):**
```bash
pip install air-toolkit
# or
pipx install air-toolkit
```

**System Package Managers (future):**
```bash
brew install air-toolkit  # macOS
apt install air-toolkit   # Ubuntu
choco install air-toolkit # Windows
```

## 7. Success Metrics

### 7.1 Phase 1 Success Criteria

- ✅ Tool installs on macOS, Linux, Windows
- ✅ Can create assessment project in < 1 minute
- ✅ Can link repositories and validate structure
- ✅ Can initialize .air/ tracking in any project
- ✅ Can create and list task files
- ✅ Documentation complete and clear

### 7.2 Usage Metrics (Future)

- Time saved vs manual setup
- Number of assessment projects created
- Number of PRs submitted via tool
- User satisfaction scores

## 8. Future Enhancements

### 8.1 Phase 2 Features

- Auto-detection of resource types
- Integration with CI/CD pipelines
- Team collaboration (shared assessments)
- Report generation (PDF, HTML)
- Dashboard/web UI
- GitLab/Bitbucket support (beyond GitHub)

### 8.2 Phase 3 Features

- IDE extensions (VS Code, PyCharm)
- AI-assisted gap detection
- Automated contribution generation
- Template marketplace
- Multi-language support (i18n)

## 9. Open Questions

1. ✅ RESOLVED: Config file is `air-config.json` (not `.assess-config.json`)
2. Should we support configuration inheritance (global → project)?
3. How to handle private repositories (SSH keys, tokens)?
4. Should `air summary` be merged with `air status`?
5. Support for non-git repositories (SVN, Mercurial)?

## 10. References

- [AA-ingest-review Project](../AA-ingest-review) - Original inspiration
- [Two Resource Types Pattern](../AA-ingest-repos/docs/two-resource-types-pattern.md)
- [Assessment Tool v2 Design](../AA-ingest-repos/docs/assessment-tool-v2-design.md)
