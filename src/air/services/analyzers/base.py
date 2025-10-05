"""Base analyzer interface and data structures."""

from abc import ABC, abstractmethod
from enum import StrEnum
from pathlib import Path
from typing import Any


class FindingSeverity(StrEnum):
    """Severity levels for findings."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding:
    """A single finding from analysis."""

    def __init__(
        self,
        category: str,
        severity: FindingSeverity,
        title: str,
        description: str,
        location: str | None = None,
        line_number: int | None = None,
        suggestion: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize finding.

        Args:
            category: Finding category (e.g., "security", "performance")
            severity: Severity level
            title: Short title
            description: Detailed description
            location: File path or location
            line_number: Line number if applicable
            suggestion: Suggested fix or remediation
            metadata: Additional metadata
        """
        self.category = category
        self.severity = severity
        self.title = title
        self.description = description
        self.location = location
        self.line_number = line_number
        self.suggestion = suggestion
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "category": self.category,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "line_number": self.line_number,
            "suggestion": self.suggestion,
            "metadata": self.metadata,
        }


class AnalyzerResult:
    """Result from running an analyzer."""

    def __init__(
        self,
        analyzer_name: str,
        findings: list[Finding],
        summary: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Initialize analyzer result.

        Args:
            analyzer_name: Name of the analyzer
            findings: List of findings
            summary: Summary statistics
            metadata: Additional metadata
        """
        self.analyzer_name = analyzer_name
        self.findings = findings
        self.summary = summary or {}
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "analyzer": self.analyzer_name,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "metadata": self.metadata,
        }


class BaseAnalyzer(ABC):
    """Base class for all analyzers."""

    def __init__(self, resource_path: Path):
        """Initialize analyzer.

        Args:
            resource_path: Path to resource to analyze
        """
        self.resource_path = resource_path

    @abstractmethod
    def analyze(self) -> AnalyzerResult:
        """Run analysis and return results.

        Returns:
            AnalyzerResult with findings
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Get analyzer name."""
        pass

    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file.

        Args:
            file_path: Path to file

        Returns:
            Number of lines
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0

    def _read_file(self, file_path: Path) -> str:
        """Read file content.

        Args:
            file_path: Path to file

        Returns:
            File content as string
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception:
            return ""

    def _get_files_by_pattern(self, pattern: str) -> list[Path]:
        """Get files matching pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")

        Returns:
            List of matching file paths
        """
        try:
            return list(self.resource_path.glob(pattern))
        except Exception:
            return []
