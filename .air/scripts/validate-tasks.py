#!/usr/bin/env python3
"""
Validate task files for completeness
Usage: python validate-tasks.py
       ./validate-tasks.py
"""

import sys
import re
from pathlib import Path


def validate_filename_format(filename):
    """Check if filename matches YYYYMMDD-HHMM-description.md"""
    pattern = r'^[0-9]{8}-[0-9]{4}-[a-z0-9-]+\.md$'
    return bool(re.match(pattern, filename))


def validate_required_sections(filepath):
    """Check if all required sections exist in file"""
    required_sections = [
        "# Task:",
        "## Date",
        "## Prompt",
        "## Actions Taken",
        "## Files Changed",
        "## Outcome"
    ]

    missing_sections = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

    except Exception as e:
        return [f"Error reading file: {e}"]

    return missing_sections


def check_prompt_placeholder(filepath):
    """Check if prompt section has placeholder text"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_prompt_section = False
        for line in lines:
            if "## Prompt" in line:
                in_prompt_section = True
                continue
            if in_prompt_section and line.startswith("##"):
                break
            if in_prompt_section and line.strip().startswith('['):
                return True

    except Exception:
        pass

    return False


def check_outcome_status(filepath):
    """Check if outcome status emoji exists"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            return any(emoji in content for emoji in ['⏳', '✅', '⚠️', '❌'])
    except Exception:
        return False


def main():
    task_dir = Path(".air/tasks")
    total_errors = 0
    total_warnings = 0

    if not task_dir.exists():
        print(f"Error: Task directory not found at {task_dir}")
        sys.exit(1)

    print("🔍 Validating AI Task Files")
    print("=" * 50)
    print("")

    task_files = sorted(task_dir.glob("202*.md"))

    for task_file in task_files:
        filename = task_file.name
        file_errors = 0
        file_warnings = 0

        # Check filename format
        if not validate_filename_format(filename):
            print(f"❌ {filename}: Invalid filename format")
            file_errors += 1

        # Check required sections
        missing = validate_required_sections(task_file)
        for section in missing:
            print(f"⚠️  {filename}: Missing section: {section}")
            file_warnings += 1

        # Check prompt placeholder
        if check_prompt_placeholder(task_file):
            print(f"⚠️  {filename}: Prompt section appears to be placeholder text")
            file_warnings += 1

        # Check outcome status
        if not check_outcome_status(task_file):
            print(f"⚠️  {filename}: No outcome status emoji found")
            file_warnings += 1

        # Check file size
        file_size = task_file.stat().st_size
        if file_size < 200:
            print(f"⚠️  {filename}: File seems too small ({file_size} bytes)")
            file_warnings += 1

        total_errors += file_errors
        total_warnings += file_warnings

    print("")
    print("=" * 50)

    if total_errors == 0 and total_warnings == 0:
        print("✅ All task files are valid!")
    else:
        print("Summary:")
        if total_errors > 0:
            print(f"  ❌ Errors: {total_errors}")
        if total_warnings > 0:
            print(f"  ⚠️  Warnings: {total_warnings}")

    print("")

    # Exit with error code if there were errors
    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
