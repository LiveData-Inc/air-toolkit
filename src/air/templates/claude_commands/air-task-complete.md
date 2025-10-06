---
description: Complete current task and commit changes (mirrors air task complete)
---

I'll help you complete the current task and commit your work.

Let me check what we've been working on:

```bash
# Find the most recent in-progress task file
find .air/tasks -name "*.md" -type f -exec grep -l "⏳ In Progress" {} \; | sort -r | head -1
```

I'll:
1. **Review changes** - Show what was modified
2. **Update task file** - Mark as completed with summary
3. **Generate commit message** - Based on task content
4. **Create commit** - With AIR co-authorship tag
5. **Ask about next steps** - Push? Create PR?

Let's complete this work session!
