---
description: Start AIR-tracked work session
---

I'll help you start a new tracked task.

First, let me check the project context:

```bash
air claude context --format=json 2>/dev/null || air status --format=json 2>/dev/null || echo '{"note":"Not an AIR project, task tracking available after air init"}'
```

Now I'll create a task file for this work:

What would you like to work on? (I can infer from your next instruction, or you can tell me now)

Once you tell me, I'll:
1. Create `.air/tasks/YYYYMMDD-HHMM-description.md`
2. Review recent similar work for context
3. Present an implementation plan
4. Track progress as we work

Ready to begin!
