#!/usr/bin/env python3
"""
Helper script to create a new task file
Usage:
  CLI:     python new-task.py "description of task"
  Library: from new_task import create_task
"""

import sys
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def to_kebab_case(text: str) -> str:
    """Convert text to kebab-case"""
    text = text.lower()
    text = text.replace(' ', '-')
    text = re.sub(r'[^a-z0-9-]', '', text)
    return text


def create_task(
    description: str,
    prompt: Optional[str] = None,
    silent: bool = False
) -> str:
    """
    Create a task file programmatically.

    Args:
        description: Brief task description (used for filename)
        prompt: Exact user prompt (populates Prompt section)
        silent: If True, don't print output messages

    Returns:
        Path to created task file
    """
    # Get current timestamp (UTC)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M")

    # Convert description to kebab-case
    kebab_description = to_kebab_case(description)

    # Create filename
    filename = f".air/tasks/{timestamp}-{kebab_description}.md"

    # Get current date for file content
    current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    # Create task content (no template needed)
    content = f"""# Task: {description}

## Date
{current_date}

## Prompt
{prompt if prompt else '[User prompt will be added]'}

## Actions Taken
1. [Actions will be documented as work progresses]

## Files Changed
- [Files will be listed as they are modified]

## Outcome
⏳ In Progress

[Work in progress]

## Notes
[Optional: Decisions, blockers, follow-up needed]
"""

    # Ensure .air/tasks directory exists
    Path(".air/tasks").mkdir(parents=True, exist_ok=True)

    # Write task file
    with open(filename, 'w') as f:
        f.write(content)

    if not silent:
        print(f"✅ Created task file: {filename}")

    return filename


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python new-task.py \"task description\"")
        print("Example: python new-task.py \"implement user authentication\"")
        sys.exit(1)

    description = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else None

    filename = create_task(description, prompt)

    print("")
    print("Task file ready for auto-documentation as work progresses.")
    print("")

    # Optionally open in editor
    editor = os.environ.get('EDITOR')
    if editor:
        try:
            response = input(f"Open in $EDITOR ({editor})? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                os.system(f"{editor} {filename}")
        except (EOFError, KeyboardInterrupt):
            print("")


if __name__ == "__main__":
    main()
