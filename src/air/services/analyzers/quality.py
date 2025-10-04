"""Code quality analyzer - detects code quality issues."""

import re
from pathlib import Path

from .base import AnalyzerResult, BaseAnalyzer, Finding, FindingSeverity


class QualityAnalyzer(BaseAnalyzer):
    """Analyzes code quality."""

    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "quality"

    def analyze(self) -> AnalyzerResult:
        """Analyze code quality.

        Returns:
            AnalyzerResult with quality findings
        """
        findings = []

        # Check for common code smells
        smells = self._detect_code_smells()
        findings.extend(smells)

        # Check documentation
        doc_findings = self._check_documentation()
        findings.extend(doc_findings)

        # Check test coverage (basic heuristic)
        test_findings = self._check_test_presence()
        findings.extend(test_findings)

        # Summary
        summary = {
            "code_smells": len(smells),
            "documentation_issues": len(doc_findings),
            "test_issues": len(test_findings),
        }

        return AnalyzerResult(
            analyzer_name=self.name,
            findings=findings[:30],  # Limit findings
            summary=summary,
        )

    def _detect_code_smells(self) -> list[Finding]:
        """Detect common code smells."""
        findings = []

        for py_file in self._get_files_by_pattern("**/*.py"):
            if any(part in ["test", "tests", "__pycache__", "venv"]
                   for part in py_file.parts):
                continue

            content = self._read_file(py_file)

            # Long functions (>100 lines)
            functions = self._find_functions(content)
            for func_name, func_lines in functions:
                if func_lines > 100:
                    findings.append(
                        Finding(
                            category="quality",
                            severity=FindingSeverity.LOW,
                            title="Long function",
                            description=f"Function '{func_name}' has {func_lines} lines",
                            location=str(py_file.relative_to(self.resource_path)),
                            suggestion="Consider breaking into smaller functions",
                            metadata={"function": func_name, "lines": func_lines},
                        )
                    )

            # Too many parameters
            params = self._find_long_parameter_lists(content)
            for func_name, param_count in params:
                findings.append(
                    Finding(
                        category="quality",
                        severity=FindingSeverity.LOW,
                        title="Too many parameters",
                        description=f"Function '{func_name}' has {param_count} parameters",
                        location=str(py_file.relative_to(self.resource_path)),
                        suggestion="Consider using a config object or builder pattern",
                        metadata={"function": func_name, "parameters": param_count},
                    )
                )

            # Commented code
            commented_lines = content.count("\n#")
            total_lines = content.count("\n")
            if total_lines > 0 and (commented_lines / total_lines) > 0.2:
                findings.append(
                    Finding(
                        category="quality",
                        severity=FindingSeverity.LOW,
                        title="Excessive comments",
                        description=f"File has {commented_lines}/{total_lines} commented lines",
                        location=str(py_file.relative_to(self.resource_path)),
                        suggestion="Remove commented-out code or use git history",
                    )
                )

        return findings

    def _find_functions(self, content: str) -> list[tuple[str, int]]:
        """Find functions and their line counts.

        Args:
            content: File content

        Returns:
            List of (function_name, line_count) tuples
        """
        functions = []

        # Split into lines
        lines = content.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Match function definition
            match = re.match(r'def\s+(\w+)\s*\(', line)
            if match:
                func_name = match.group(1)
                func_start = i

                # Find end of function (next def or class at same indent level)
                indent = len(lines[i]) - len(lines[i].lstrip())
                i += 1

                while i < len(lines):
                    current_indent = len(lines[i]) - len(lines[i].lstrip())
                    current_line = lines[i].strip()

                    if current_line and current_indent <= indent and (
                        current_line.startswith("def ") or current_line.startswith("class ")
                    ):
                        break

                    i += 1

                func_lines = i - func_start
                if func_lines > 5:  # Ignore trivial functions
                    functions.append((func_name, func_lines))

            i += 1

        return functions

    def _find_long_parameter_lists(self, content: str) -> list[tuple[str, int]]:
        """Find functions with too many parameters.

        Args:
            content: File content

        Returns:
            List of (function_name, parameter_count) tuples
        """
        results = []

        # Match function definitions
        pattern = r'def\s+(\w+)\s*\(([^)]*)\)'
        matches = re.finditer(pattern, content)

        for match in matches:
            func_name = match.group(1)
            params_str = match.group(2)

            # Count parameters (simple split by comma)
            if params_str.strip():
                params = [p.strip() for p in params_str.split(",")]
                # Filter out self, cls
                params = [p for p in params if not p.startswith("self") and not p.startswith("cls")]

                if len(params) > 5:
                    results.append((func_name, len(params)))

        return results

    def _check_documentation(self) -> list[Finding]:
        """Check for documentation."""
        findings = []

        # Check for README
        has_readme = any(
            (self.resource_path / name).exists()
            for name in ["README.md", "README.rst", "README.txt", "README"]
        )

        if not has_readme:
            findings.append(
                Finding(
                    category="quality",
                    severity=FindingSeverity.MEDIUM,
                    title="Missing README",
                    description="Project lacks a README file",
                    suggestion="Add README.md with project description and setup instructions",
                )
            )

        # Check for docstrings in Python files
        py_files = list(self._get_files_by_pattern("**/*.py"))
        undocumented = 0

        for py_file in py_files:
            if any(part in ["test", "tests", "__pycache__"]
                   for part in py_file.parts):
                continue

            content = self._read_file(py_file)

            # Count functions
            func_count = len(re.findall(r'^def\s+\w+', content, re.MULTILINE))

            # Count docstrings
            docstring_count = len(re.findall(r'"""[^"]', content))

            if func_count > 3 and docstring_count < func_count * 0.5:
                undocumented += 1

        if undocumented > 0:
            findings.append(
                Finding(
                    category="quality",
                    severity=FindingSeverity.LOW,
                    title="Missing docstrings",
                    description=f"{undocumented} Python files lack adequate docstrings",
                    suggestion="Add docstrings to public functions and classes",
                    metadata={"undocumented_files": undocumented},
                )
            )

        return findings

    def _check_test_presence(self) -> list[Finding]:
        """Check for test presence."""
        findings = []

        # Find code files
        code_files = len(list(self._get_files_by_pattern("**/*.py")))

        # Find test files
        test_files = 0
        for pattern in ["**/test_*.py", "**/*_test.py", "**/tests/**/*.py"]:
            test_files += len(list(self._get_files_by_pattern(pattern)))

        # Heuristic: at least 30% test coverage by file count
        if code_files > 10 and test_files < code_files * 0.3:
            findings.append(
                Finding(
                    category="quality",
                    severity=FindingSeverity.MEDIUM,
                    title="Low test coverage",
                    description=f"Only {test_files} test files for {code_files} code files",
                    suggestion="Add more unit tests (target: 1 test file per 3 code files)",
                    metadata={"code_files": code_files, "test_files": test_files},
                )
            )

        return findings
