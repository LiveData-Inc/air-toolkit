"""Parse task markdown files for summary generation."""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class TaskInfo:
    """Parsed task file information."""

    filename: str
    title: str
    date: str | None
    prompt: str | None
    actions: list[str]
    files_changed: list[str]
    outcome: str | None
    notes: str | None
    timestamp: datetime | None


def parse_task_file(task_path: Path) -> TaskInfo:
    """Parse a task markdown file.

    Args:
        task_path: Path to task file

    Returns:
        TaskInfo with extracted data
    """
    content = task_path.read_text()

    # Extract title
    title_match = re.search(r"^#\s+Task:\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Unknown"

    # Extract date
    date_match = re.search(r"^##\s+Date\s*\n(.+)$", content, re.MULTILINE)
    date = date_match.group(1).strip() if date_match else None

    # Extract prompt
    prompt_match = re.search(r"^##\s+Prompt\s*\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL)
    prompt = prompt_match.group(1).strip() if prompt_match else None

    # Extract actions taken
    actions = []
    actions_match = re.search(
        r"^##\s+Actions Taken\s*\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if actions_match:
        actions_text = actions_match.group(1).strip()
        # Extract numbered/bulleted list items
        action_items = re.findall(r"^[\d\-\*]+\.\s*(.+)$", actions_text, re.MULTILINE)
        actions = [a.strip() for a in action_items]

    # Extract files changed
    files_changed = []
    files_match = re.search(
        r"^##\s+Files Changed\s*\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if files_match:
        files_text = files_match.group(1).strip()
        # Extract list items starting with - or file paths
        file_items = re.findall(r"^-\s*(.+?)(?:\s+-|$)", files_text, re.MULTILINE)
        files_changed = [f.strip() for f in file_items if f.strip() and f.strip() != "(to be documented)"]

    # Extract outcome
    outcome_match = re.search(
        r"^##\s+Outcome\s*\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL
    )
    if outcome_match:
        outcome_text = outcome_match.group(1).strip()
        # Extract status emoji and text
        if "✅" in outcome_text or "Success" in outcome_text:
            outcome = "success"
        elif "⏳" in outcome_text or "In Progress" in outcome_text:
            outcome = "in_progress"
        elif "⚠" in outcome_text or "Partial" in outcome_text:
            outcome = "partial"
        elif "🚫" in outcome_text or "Blocked" in outcome_text:
            outcome = "blocked"
        else:
            outcome = "unknown"
    else:
        outcome = None

    # Extract notes
    notes_match = re.search(r"^##\s+Notes\s*\n(.+?)(?=\n##|\Z)", content, re.MULTILINE | re.DOTALL)
    notes = notes_match.group(1).strip() if notes_match else None

    # Parse timestamp from filename
    from air.utils.dates import parse_task_timestamp

    timestamp = parse_task_timestamp(task_path.name)

    return TaskInfo(
        filename=task_path.name,
        title=title,
        date=date,
        prompt=prompt,
        actions=actions,
        files_changed=files_changed,
        outcome=outcome,
        notes=notes,
        timestamp=timestamp,
    )


def get_all_task_info(tasks_dir: Path, since: datetime | None = None) -> list[TaskInfo]:
    """Get information from all task files.

    Args:
        tasks_dir: Path to .air/tasks directory
        since: Optional datetime to filter tasks after this date

    Returns:
        List of TaskInfo objects, sorted by timestamp
    """
    task_files = sorted(tasks_dir.glob("*.md"))
    task_info_list = []

    for task_file in task_files:
        # Skip archive directory and TASKS.md
        if task_file.name == "TASKS.md" or "archive" in str(task_file):
            continue

        try:
            info = parse_task_file(task_file)

            # Filter by date if specified
            if since and info.timestamp and info.timestamp < since:
                continue

            task_info_list.append(info)
        except Exception:
            # Skip files that can't be parsed
            continue

    # Sort by timestamp (newest first)
    task_info_list.sort(key=lambda x: x.timestamp or datetime.min, reverse=True)

    return task_info_list
