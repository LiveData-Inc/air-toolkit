---
description: Generate work summary from all tasks
---

I'll generate a comprehensive summary of all work tracked in this AIR project.

First, let me check the project context:

```bash
air status --format=json
```

Now I'll compile all task files into a structured summary:

```bash
air summary --format=json
```

This will:
- Scan all task files in `.air/tasks/` (including archived)
- Parse task metadata (date, prompt, outcome, files changed)
- Aggregate by status (success/in-progress/partial/blocked)
- Generate structured output with:
  - Project overview
  - Task timeline
  - Outcomes summary
  - Files modified across all tasks
  - Key decisions and notes

The JSON format is optimized for AI parsing and includes:
```json
{
  "project": {...},
  "tasks": [{
    "id": "YYYYMMDD-NNN-HHMM",
    "title": "...",
    "date": "...",
    "outcome": "success",
    "files_changed": [...]
  }],
  "summary": {
    "total_tasks": N,
    "by_outcome": {...}
  }
}
```

I'll use this to understand the full context of work done in this project!
