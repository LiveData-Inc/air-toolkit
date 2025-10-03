#!/usr/bin/env python3
"""
List recent task files
Usage: python list-tasks.py [count]
       ./list-tasks.py [count]
Default count: 10
"""

import sys
import os
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


def extract_description(filename):
    """Extract description from task filename"""
    match = re.match(r'^\d{8}-\d{4}-(.*)\.md$', filename)
    if match:
        return match.group(1).replace('-', ' ')
    return filename


def extract_outcome(filepath):
    """Extract outcome emoji from task file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                match = re.match(r'^(⏳|✅|⚠️|❌)', line)
                if match:
                    return match.group(1)
    except Exception:
        pass
    return "  "


def main():
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Error: Invalid count '{sys.argv[1]}'")
            sys.exit(1)

    task_dir = Path(".air/tasks")

    if not task_dir.exists():
        print(f"Error: Task directory not found at {task_dir}")
        sys.exit(1)

    print(f"📋 Recent AI Tasks (last {count}):")
    print("")

    # Find all task files, sort by date (newest first), limit to count
    task_files = sorted(
        task_dir.glob("202*.md"),
        key=lambda x: x.name,
        reverse=True
    )[:count]

    for task_file in task_files:
        filename = task_file.name
        formatted_date = extract_datetime_from_filename(filename)
        description = extract_description(filename)
        outcome = extract_outcome(task_file)

        print(f"{outcome}  {formatted_date}  {description}")

    print("")
    print("💡 Tip: Use 'python search-tasks.py \"keyword\"' to find specific tasks")


if __name__ == "__main__":
    main()
