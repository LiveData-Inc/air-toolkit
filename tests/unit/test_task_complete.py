"""Unit tests for task completion functionality."""

import re
from pathlib import Path


class TestOutcomeUpdate:
    """Test updating task outcome to complete."""

    def test_update_in_progress_to_success(self):
        """Update task with in-progress outcome to success."""
        content = """# Task: test task

## Prompt
Test prompt

## Actions Taken
- Action 1

## Files Changed
- file1.py

## Outcome

⏳ In Progress

## Notes

Some notes
"""
        outcome_pattern = r"(## Outcome\s*\n\s*)[^\n#]+"
        new_content = re.sub(outcome_pattern, r"\1✅ Success\n", content, count=1)

        assert "✅ Success" in new_content
        assert "⏳ In Progress" not in new_content
        assert "## Notes" in new_content  # Ensure structure preserved

    def test_update_blocked_to_success(self):
        """Update blocked task to success."""
        content = """# Task: test task

## Outcome

🚫 Blocked: dependency issue

## Notes
"""
        outcome_pattern = r"(## Outcome\s*\n\s*)[^\n#]+"
        new_content = re.sub(outcome_pattern, r"\1✅ Success\n", content, count=1)

        assert "✅ Success" in new_content
        assert "🚫 Blocked" not in new_content

    def test_preserves_other_sections(self):
        """Ensure all other sections are preserved."""
        content = """# Task: complex task

## Prompt
Original prompt

## Actions Taken
- Action 1
- Action 2

## Files Changed
- file1.py
- file2.py

## Outcome

⏳ In Progress

## Notes

Some important notes
"""
        outcome_pattern = r"(## Outcome\s*\n\s*)[^\n#]+"
        new_content = re.sub(outcome_pattern, r"\1✅ Success\n", content, count=1)

        # Check all sections are present
        assert "## Prompt" in new_content
        assert "Original prompt" in new_content
        assert "## Actions Taken" in new_content
        assert "- Action 1" in new_content
        assert "## Files Changed" in new_content
        assert "- file1.py" in new_content
        assert "## Notes" in new_content
        assert "Some important notes" in new_content


class TestNotesAppending:
    """Test appending completion notes."""

    def test_append_notes_to_empty_section(self):
        """Append notes when notes section is empty."""
        content = """# Task: test

## Outcome

✅ Success

## Notes

"""
        notes_text = "All tests passing"
        notes_pattern = r"(## Notes\s*\n)(.*?)($)"
        match = re.search(notes_pattern, content, re.DOTALL)

        assert match is not None
        existing_notes = match.group(2).strip()
        assert existing_notes == ""

        updated_notes = f"**Completed:** {notes_text}\n"
        new_content = re.sub(
            notes_pattern, rf"\1{updated_notes}", content, count=1
        )

        assert "**Completed:** All tests passing" in new_content

    def test_append_notes_to_existing_notes(self):
        """Append notes when notes section has existing content."""
        content = """# Task: test

## Outcome

✅ Success

## Notes

Existing note here
"""
        notes_text = "All tests passing"
        notes_pattern = r"(## Notes\s*\n)(.*?)($)"
        match = re.search(notes_pattern, content, re.DOTALL)

        assert match is not None
        existing_notes = match.group(2).strip()
        assert existing_notes == "Existing note here"

        updated_notes = f"{existing_notes}\n\n**Completed:** {notes_text}\n"
        new_content = re.sub(
            notes_pattern, rf"\1{updated_notes}", content, count=1
        )

        assert "Existing note here" in new_content
        assert "**Completed:** All tests passing" in new_content

    def test_notes_with_multiple_sections_after(self):
        """Handle notes section when it's at the end (no sections after)."""
        content = """# Task: test

## Outcome

✅ Success

## Notes

Original notes
"""
        notes_text = "Task completed successfully"
        notes_pattern = r"(## Notes\s*\n)(.*?)($)"
        match = re.search(notes_pattern, content, re.DOTALL)

        assert match is not None
        existing_notes = match.group(2).strip()
        updated_notes = f"{existing_notes}\n\n**Completed:** {notes_text}\n"

        new_content = re.sub(
            notes_pattern, rf"\1{updated_notes}", content, count=1
        )

        assert "Original notes" in new_content
        assert "**Completed:** Task completed successfully" in new_content


class TestPatternMatching:
    """Test pattern matching for task file sections."""

    def test_outcome_pattern_matches_various_formats(self):
        """Ensure outcome pattern works with different spacing."""
        outcome_pattern = r"(## Outcome\s*\n\s*)[^\n#]+"

        # With extra newlines
        content1 = "## Outcome\n\n⏳ In Progress\n"
        assert re.search(outcome_pattern, content1)

        # Minimal spacing
        content2 = "## Outcome\n⏳ In Progress\n"
        assert re.search(outcome_pattern, content2)

        # With text after
        content3 = "## Outcome\n\n✅ Success\n\n## Notes"
        assert re.search(outcome_pattern, content3)

    def test_notes_pattern_end_of_file(self):
        """Notes pattern works when Notes is last section."""
        notes_pattern = r"(## Notes\s*\n)(.*?)($)"

        content = """## Notes

Some notes at end of file"""
        match = re.search(notes_pattern, content, re.DOTALL)
        assert match is not None
        assert match.group(2).strip() == "Some notes at end of file"

    def test_notes_pattern_with_empty_notes(self):
        """Notes pattern works when notes section is empty."""
        notes_pattern = r"(## Notes\s*\n)(.*?)($)"

        content = """## Notes

"""
        match = re.search(notes_pattern, content, re.DOTALL)
        assert match is not None
        assert match.group(2).strip() == ""
