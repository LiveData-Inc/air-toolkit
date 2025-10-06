---
description: Run comprehensive code analysis on all linked repositories
---

I'll run a comprehensive code analysis on your AIR project.

First, let me check the project status:

```bash
air status --format=json
```

Now I'll analyze all linked repositories with dependency-aware ordering:

```bash
air analyze --all
```

This will:
- Detect dependencies between repositories
- Analyze in the correct order (libraries first, then consumers)
- Run 5 specialized analyzers (Security, Performance, Quality, Architecture, Structure)
- Exclude external libraries (.venv, node_modules, etc.) by default
- Save findings to `analysis/reviews/{repo}-findings.json`

Once complete, you can:
- View findings: `air findings --all`
- Generate HTML report: `air findings --all --html`
- Check specific repo: Open `analysis/reviews/{repo}-findings.json`

Analysis running...
