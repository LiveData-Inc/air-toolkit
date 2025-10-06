---
description: Get current AIR project status and context
---

I'll retrieve the current AIR project status for you.

```bash
air status --format=json
```

This provides structured information about:

**Project Configuration:**
- Project name and mode (review/develop/mixed)
- Creation date and version

**Linked Resources:**
- All linked repositories with paths
- Resource types (library/service/documentation)
- Relationship (review-only or developer access)
- Writable status (Y/N)
- Current branch and sync status

**Background Agents:**
- Running analysis agents
- Agent status and progress

**Task Tracking:**
- Active tasks count
- Recent task activity

I'll use this information to understand the project context and help you work more effectively!
