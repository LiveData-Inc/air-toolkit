#!/usr/bin/env python3
"""
Generate statistics about AI tasks
Usage: python task-stats.py
       ./task-stats.py
"""

import sys
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


def extract_outcome(filepath):
    """Extract outcome emoji from task file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if '✅' in content:
                return 'success'
            elif '⏳' in content:
                return 'in_progress'
            elif '⚠️' in content:
                return 'partial'
            elif '❌' in content:
                return 'blocked'
    except Exception:
        pass
    return None


def extract_month_from_filename(filename):
    """Extract YYYYMM from filename"""
    match = re.match(r'^(\d{6})', filename)
    if match:
        return match.group(1)
    return None


def extract_date_from_filename(filename):
    """Extract YYYYMMDD from filename"""
    match = re.match(r'^(\d{8})', filename)
    if match:
        return match.group(1)
    return None


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


def main():
    task_dir = Path(".air/tasks")

    if not task_dir.exists():
        print(f"Error: Task directory not found at {task_dir}")
        sys.exit(1)

    print("📊 AI Task Statistics")
    print("=" * 40)
    print("")

    # Get all task files
    task_files = list(task_dir.glob("202*.md"))

    # Total tasks
    total_tasks = len(task_files)
    print(f"Total Tasks: {total_tasks}")
    print("")

    # Tasks by outcome
    print("By Outcome:")
    outcomes = defaultdict(int)
    for task_file in task_files:
        outcome = extract_outcome(task_file)
        if outcome:
            outcomes[outcome] += 1

    print(f"  ✅ Success:     {outcomes['success']}")
    print(f"  ⏳ In Progress: {outcomes['in_progress']}")
    print(f"  ⚠️  Partial:     {outcomes['partial']}")
    print(f"  ❌ Blocked:     {outcomes['blocked']}")
    print("")

    # Tasks by month
    print("By Month:")
    months = defaultdict(int)
    for task_file in task_files:
        month = extract_month_from_filename(task_file.name)
        if month:
            months[month] += 1

    for month in sorted(months.keys()):
        year = month[0:4]
        mon = month[4:6]
        count = months[month]
        print(f"  {year}-{mon}: {count:2d} tasks")
    print("")

    # Most recent task
    print("Most Recent Task:")
    if task_files:
        most_recent = sorted(task_files, key=lambda x: x.name, reverse=True)[0]
        formatted_date = extract_datetime_from_filename(most_recent.name)
        description = extract_description(most_recent.name)
        print(f"  {formatted_date} - {description}")
    else:
        print("  No tasks found")
    print("")

    # Activity last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
    recent_tasks = []
    for task_file in task_files:
        file_date = extract_date_from_filename(task_file.name)
        if file_date and file_date >= thirty_days_ago:
            recent_tasks.append(task_file)

    recent_count = len(recent_tasks)
    avg_per_week = recent_count // 4
    print(f"Activity (last 30 days): {recent_count} tasks (~{avg_per_week} per week)")
    print("")

    print("💡 Tip: Use 'python list-tasks.py' to see recent tasks")


if __name__ == "__main__":
    main()
