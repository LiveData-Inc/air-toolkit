---
description: Validate project structure and auto-fix issues
---

I'll validate your AIR project structure and automatically fix any issues.

First, let me check if we're in an AIR project:

```bash
air status --format=json
```

Now I'll validate the project structure with auto-fix enabled:

```bash
air validate --fix
```

This will:
- Check all required directories exist
- Verify configuration file is valid
- Check linked repository symlinks
- **Auto-fix broken symlinks** (reconnect to targets)
- Verify task tracking structure
- Check template files

Common fixes applied automatically:
- Recreate broken symlinks to repositories
- Create missing directories (.air/tasks, analysis/reviews, etc.)
- Restore missing configuration fields

After validation, your project will be in a healthy state!
