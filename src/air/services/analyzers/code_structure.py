"""Code structure analyzer - analyzes repository structure and metrics."""

from pathlib import Path

from air.services.path_filter import should_exclude_path
from .base import AnalyzerResult, BaseAnalyzer, Finding, FindingSeverity


class CodeStructureAnalyzer(BaseAnalyzer):
    """Analyzes code structure and basic metrics."""

    def __init__(self, repo_path: Path, include_external: bool = False):
        """Initialize code structure analyzer.

        Args:
            repo_path: Path to repository
            include_external: If True, include external/vendor code in analysis
        """
        super().__init__(repo_path)
        self.repo_path = repo_path
        self.include_external = include_external

    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "code_structure"

    def analyze(self) -> AnalyzerResult:
        """Analyze code structure.

        Returns:
            AnalyzerResult with structure findings
        """
        findings = []

        # Count files and LOC
        file_stats = self._analyze_file_structure()

        # Check for large files
        large_files = self._find_large_files(max_lines=500)
        for file_path, line_count in large_files:
            findings.append(
                Finding(
                    category="code_structure",
                    severity=FindingSeverity.LOW,
                    title="Large file detected",
                    description=f"File has {line_count} lines (threshold: 500)",
                    location=str(file_path.relative_to(self.resource_path)),
                    suggestion="Consider splitting into smaller, more focused modules",
                    metadata={"line_count": line_count},
                )
            )

        # Check directory structure
        structure_issues = self._check_directory_structure()
        findings.extend(structure_issues)

        # Create summary
        summary = {
            "total_files": file_stats["total_files"],
            "total_lines": file_stats["total_lines"],
            "code_files": file_stats["code_files"],
            "test_files": file_stats["test_files"],
            "doc_files": file_stats["doc_files"],
            "largest_file": file_stats["largest_file"],
            "languages": file_stats["languages"],
        }

        return AnalyzerResult(
            analyzer_name=self.name,
            findings=findings,
            summary=summary,
        )

    def _analyze_file_structure(self) -> dict:
        """Analyze file structure and count LOC."""
        stats = {
            "total_files": 0,
            "total_lines": 0,
            "code_files": 0,
            "test_files": 0,
            "doc_files": 0,
            "largest_file": None,
            "largest_file_lines": 0,
            "languages": {},
        }

        # Common code extensions
        code_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
            ".rb", ".php", ".cs", ".swift", ".kt", ".cpp", ".c", ".h"
        }

        for file_path in self.resource_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip hidden and build directories
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if any(part in ["node_modules", "__pycache__", "dist", "build", "target"]
                   for part in file_path.parts):
                continue

            stats["total_files"] += 1

            # Count lines
            line_count = self._count_lines(file_path)
            stats["total_lines"] += line_count

            # Track largest file
            if line_count > stats["largest_file_lines"]:
                stats["largest_file_lines"] = line_count
                stats["largest_file"] = str(file_path.relative_to(self.resource_path))

            # Categorize by type
            ext = file_path.suffix.lower()

            if ext in code_extensions:
                stats["code_files"] += 1
                stats["languages"][ext] = stats["languages"].get(ext, 0) + 1

            if "test" in file_path.name.lower() or "test" in str(file_path.parent).lower():
                stats["test_files"] += 1

            if ext in [".md", ".rst", ".txt"]:
                stats["doc_files"] += 1

        return stats

    def _find_large_files(self, max_lines: int = 500) -> list[tuple[Path, int]]:
        """Find files exceeding line count threshold.

        Args:
            max_lines: Maximum acceptable lines

        Returns:
            List of (file_path, line_count) tuples
        """
        large_files = []

        code_extensions = {
            ".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs",
            ".rb", ".php", ".cs", ".swift", ".kt"
        }

        for file_path in self.resource_path.rglob("*"):
            if not file_path.is_file():
                continue

            # Skip tests and non-code files
            if file_path.suffix.lower() not in code_extensions:
                continue

            # Skip hidden and build directories
            if any(part.startswith(".") for part in file_path.parts):
                continue
            if any(part in ["node_modules", "__pycache__", "dist", "build", "target"]
                   for part in file_path.parts):
                continue

            line_count = self._count_lines(file_path)
            if line_count > max_lines:
                large_files.append((file_path, line_count))

        return sorted(large_files, key=lambda x: x[1], reverse=True)[:10]  # Top 10

    def _check_directory_structure(self) -> list[Finding]:
        """Check for directory structure issues.

        Returns:
            List of findings
        """
        findings = []

        # Check for tests directory
        has_tests = any(
            (self.resource_path / path).exists()
            for path in ["tests", "test", "__tests__", "spec"]
        )

        if not has_tests:
            findings.append(
                Finding(
                    category="code_structure",
                    severity=FindingSeverity.MEDIUM,
                    title="No test directory found",
                    description="Repository appears to lack a dedicated tests directory",
                    suggestion="Consider organizing tests in a 'tests/' or 'test/' directory",
                )
            )

        # Check for documentation
        has_docs = any(
            (self.resource_path / path).exists()
            for path in ["docs", "documentation", "README.md"]
        )

        if not has_docs:
            findings.append(
                Finding(
                    category="code_structure",
                    severity=FindingSeverity.LOW,
                    title="Limited documentation",
                    description="No docs/ directory or README.md found",
                    suggestion="Add README.md or create docs/ directory",
                )
            )

        return findings
