#!/usr/bin/env python3
"""
Search task files for a keyword
Usage: python search-tasks.py "keyword"
       ./search-tasks.py "keyword"
"""

import sys
import re
from pathlib import Path


def extract_datetime_from_filename(filename):
    """Extract and format datetime from task filename"""
    match = re.match(r'^(\d{8})-(\d{4})', filename)
    if not match:
        return "Unknown"

    date_part = match.group(1)  # YYYYMMDD
    time_part = match.group(2)  # HHMM

    year = date_part[0:4]
    month = date_part[4:6]
    day = date_part[6:8]
    hour = time_part[0:2]
    minute = time_part[2:4]

    return f"{year}-{month}-{day} {hour}:{minute}"


def search_file(filepath, search_term):
    """Search file for term and return matching lines with context"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        matches = []
        for i, line in enumerate(lines):
            if search_term.lower() in line.lower():
                # Get context: previous line, match, next line
                context = []
                if i > 0:
                    context.append(lines[i - 1].rstrip())
                context.append(f">>> {line.rstrip()}")
                if i < len(lines) - 1:
                    context.append(lines[i + 1].rstrip())

                matches.append('\n'.join(context))

                # Limit to first 10 matches
                if len(matches) >= 10:
                    break

        return matches
    except Exception as e:
        return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python search-tasks.py \"search term\"")
        print("Example: python search-tasks.py \"authentication\"")
        sys.exit(1)

    search_term = sys.argv[1]
    task_dir = Path(".ai/tasks")

    if not task_dir.exists():
        print(f"Error: Task directory not found at {task_dir}")
        sys.exit(1)

    print(f"🔍 Searching for: \"{search_term}\"")
    print("")

    # Search in task files, sorted by date (newest first)
    task_files = sorted(
        task_dir.glob("202*.md"),
        key=lambda x: x.name,
        reverse=True
    )

    matches_found = 0

    for task_file in task_files:
        matches = search_file(task_file, search_term)

        if matches:
            matches_found += 1
            filename = task_file.name
            formatted_date = extract_datetime_from_filename(filename)

            print(f"📄 {filename} ({formatted_date})")
            for match in matches:
                print(match)
            print("")

    if matches_found == 0:
        print(f"No tasks found matching \"{search_term}\"")

    print("")
    print("💡 Tip: Use 'python list-tasks.py' to see recent tasks")


if __name__ == "__main__":
    main()
