#!/usr/bin/env python3
"""
Archive old task files to keep tasks/ folder manageable
Usage: python archive-tasks.py <archive-name>
       ./archive-tasks.py <archive-name>
Example: python archive-tasks.py 2024-Q4
         python archive-tasks.py 2024-12
"""

import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from shutil import move


def is_git_repo():
    """Check if current directory is in a git repository"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--git-dir'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def git_move(source, dest):
    """
    Move file using git mv if in a git repo, otherwise use regular move.
    Returns True if successful, False otherwise.
    """
    try:
        # Try git mv first if we're in a git repo
        if is_git_repo():
            result = subprocess.run(
                ['git', 'mv', str(source), str(dest)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True
            # If git mv fails, fall back to regular move

        # Fall back to regular file system move
        move(str(source), str(dest))
        return True
    except Exception as e:
        print(f"  ⚠️  Error moving {source}: {e}")
        return False


def extract_date_from_filename(filename):
    """Extract YYYYMMDD from filename"""
    match = re.match(r'^(\d{8})', filename)
    if match:
        return match.group(1)
    return None


def has_success_outcome(filepath):
    """Check if task file has success outcome"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return '✅' in f.read()
    except Exception:
        return False


def archive_by_date_range(task_dir, archive_dir):
    """Archive tasks by date range"""
    start_date = input("Start date (YYYYMMDD): ").strip()
    end_date = input("End date (YYYYMMDD): ").strip()

    if not (re.match(r'^\d{8}$', start_date) and re.match(r'^\d{8}$', end_date)):
        print("Error: Invalid date format. Use YYYYMMDD")
        return

    count = 0
    for task_file in task_dir.glob("202*.md"):
        file_date = extract_date_from_filename(task_file.name)
        if file_date and start_date <= file_date <= end_date:
            if git_move(task_file, archive_dir / task_file.name):
                print(f"  Archived: {task_file.name}")
                count += 1

    return count


def archive_by_age(task_dir, archive_dir):
    """Archive tasks older than N days"""
    days_input = input("Archive tasks older than how many days? [90]: ").strip()
    days = int(days_input) if days_input else 90

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    count = 0
    for task_file in task_dir.glob("202*.md"):
        file_date = extract_date_from_filename(task_file.name)
        if file_date and file_date < cutoff_date:
            if git_move(task_file, archive_dir / task_file.name):
                print(f"  Archived: {task_file.name}")
                count += 1

    return count


def archive_completed(task_dir, archive_dir):
    """Archive all completed tasks"""
    count = 0
    for task_file in task_dir.glob("202*.md"):
        if has_success_outcome(task_file):
            if git_move(task_file, archive_dir / task_file.name):
                print(f"  Archived: {task_file.name}")
                count += 1

    return count


def main():
    if len(sys.argv) < 2:
        print("Usage: python archive-tasks.py <archive-name>")
        print("Example: python archive-tasks.py 2024-Q4")
        print("Example: python archive-tasks.py 2024-12")
        sys.exit(1)

    archive_name = sys.argv[1]
    task_dir = Path(".air/tasks")
    archive_dir = Path(f".air/archives/{archive_name}")

    if not task_dir.exists():
        print(f"Error: Task directory not found at {task_dir}")
        sys.exit(1)

    # Create archive directory
    archive_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Archiving tasks to: {archive_dir}")
    print("")

    # Ask user which tasks to archive
    print("Select tasks to archive:")
    print("  1) By date range")
    print("  2) Tasks older than N days")
    print("  3) All completed tasks")

    try:
        choice = input("Choice [1]: ").strip() or "1"

        if choice == "1":
            count = archive_by_date_range(task_dir, archive_dir)
        elif choice == "2":
            count = archive_by_age(task_dir, archive_dir)
        elif choice == "3":
            count = archive_completed(task_dir, archive_dir)
        else:
            print("Invalid choice")
            sys.exit(1)

        print("")
        print("✅ Archive complete!")
        print(f"   Archived tasks are in: {archive_dir}")
        print("")
        print("💡 Tip: Update .air/AI_CHANGELOG.md to reference this archive")

    except (EOFError, KeyboardInterrupt):
        print("\nArchive cancelled")
        sys.exit(1)


if __name__ == "__main__":
    main()
