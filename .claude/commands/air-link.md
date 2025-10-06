---
description: Quickly link a repository to the current AIR project
---

I'll link a repository to your AIR project.

First, let me check if we're in an AIR project:

```bash
air status --format=json
```

Now I'll link the repository:

```bash
air link add {{ARGS}}
```

What would you like to do next? I can:
- Analyze the newly linked repository (`air analyze repos/NAME`)
- Create a task for reviewing it (`air task new "review NAME repository"`)
- Show all linked resources (`air link list`)
