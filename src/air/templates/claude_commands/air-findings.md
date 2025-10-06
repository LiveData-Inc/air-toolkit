---
description: View analysis findings as rich HTML report
---

I'll generate a comprehensive HTML report of all analysis findings.

First, let me check the project status:

```bash
air status --format=json
```

Now I'll aggregate findings from all analyzed repositories and generate an HTML report:

```bash
air findings --all --html
```

This will:
- Collect findings from all `analysis/reviews/{repo}-findings.json` files
- Aggregate by repository and severity
- Generate a rich HTML report with:
  - Table of contents with repository navigation
  - Severity badges (Critical, High, Medium, Low, Info)
  - Detailed findings with file locations and line numbers
  - Syntax-highlighted code snippets
  - Recommendations for each issue
- Save to `analysis/findings-report.html`

The HTML report is self-contained (embedded CSS) and can be:
- Opened in your browser for review
- Shared with team members
- Archived with your assessment

Report generated at: `analysis/findings-report.html`
