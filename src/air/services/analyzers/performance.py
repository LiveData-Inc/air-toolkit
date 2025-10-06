"""Performance analyzer - detects performance anti-patterns."""

import re
from pathlib import Path

from air.services.path_filter import should_exclude_path
from .base import AnalyzerResult, BaseAnalyzer, Finding, FindingSeverity


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzes code for performance issues."""

    def __init__(self, repo_path: Path, include_external: bool = False):
        """Initialize performance analyzer.

        Args:
            repo_path: Path to repository
            include_external: If True, include external/vendor code in analysis
        """
        super().__init__(repo_path)
        self.include_external = include_external

    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "performance"

    def analyze(self) -> AnalyzerResult:
        """Analyze code for performance issues.

        Returns:
            AnalyzerResult with performance findings
        """
        findings = []

        # Analyze Python files
        python_findings = self._analyze_python_performance()
        findings.extend(python_findings)

        # Analyze JavaScript/TypeScript files
        js_findings = self._analyze_javascript_performance()
        findings.extend(js_findings)

        # Create summary
        summary = {
            "total_findings": len(findings),
            "critical": sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == FindingSeverity.HIGH),
            "medium": sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM),
        }

        return AnalyzerResult(
            analyzer_name=self.name,
            findings=findings[:40],  # Limit to top 40
            summary=summary,
        )

    def _analyze_python_performance(self) -> list[Finding]:
        """Analyze Python files for performance issues."""
        findings = []

        for py_file in self._get_files_by_pattern("**/*.py"):
            # Use path_filter to exclude external code
            rel_path = py_file.relative_to(self.repo_path)
            if should_exclude_path(rel_path, self.include_external):
                continue

            content = self._read_file(py_file)
            if not content:
                continue

            # Check for N+1 query patterns (Django/SQLAlchemy)
            n_plus_one = self._detect_n_plus_one(py_file, content)
            findings.extend(n_plus_one)

            # Check for nested loops
            nested_loops = self._detect_nested_loops(py_file, content)
            findings.extend(nested_loops)

            # Check for inefficient string concatenation
            string_concat = self._detect_string_concatenation(py_file, content)
            findings.extend(string_concat)

            # Check for list comprehension opportunities
            list_append = self._detect_list_append_in_loop(py_file, content)
            findings.extend(list_append)

            # Check for missing pagination
            pagination = self._detect_missing_pagination(py_file, content)
            findings.extend(pagination)

        return findings

    def _detect_n_plus_one(self, file_path: Path, content: str) -> list[Finding]:
        """Detect potential N+1 query problems."""
        findings = []

        # Pattern: loop over queryset with related object access
        lines = content.split("\n")
        for i, line in enumerate(lines):
            # Django ORM pattern
            if re.search(r'for\s+\w+\s+in\s+\w+\.(?:objects\.)?(?:all|filter)\(', line):
                # Check next 10 lines for related object access
                for j in range(i + 1, min(i + 11, len(lines))):
                    if re.search(r'\.\w+\.(?:all|filter|get)\(', lines[j]):
                        findings.append(
                            Finding(
                                category="performance",
                                severity=FindingSeverity.HIGH,
                                title="Potential N+1 query",
                                description="Loop over queryset with related object access",
                                location=str(file_path.relative_to(self.resource_path)),
                                line_number=i + 1,
                                suggestion="Use select_related() or prefetch_related()",
                                metadata={"pattern": "n_plus_one_django"},
                            )
                        )
                        break

        return findings

    def _detect_nested_loops(self, file_path: Path, content: str) -> list[Finding]:
        """Detect nested loops (potential O(n²) or worse)."""
        findings = []

        lines = content.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]

            # Match outer for loop
            if re.search(r'^\s*for\s+\w+\s+in\s+', line):
                outer_indent = len(line) - len(line.lstrip())

                # Look for nested for loop
                for j in range(i + 1, min(i + 20, len(lines))):
                    inner_line = lines[j]
                    inner_indent = len(inner_line) - len(inner_line.lstrip())

                    # Check if this is a nested loop at deeper indent
                    if (inner_indent > outer_indent and
                        re.search(r'for\s+\w+\s+in\s+', inner_line)):

                        findings.append(
                            Finding(
                                category="performance",
                                severity=FindingSeverity.MEDIUM,
                                title="Nested loop detected",
                                description="Nested loops may cause O(n²) performance",
                                location=str(file_path.relative_to(self.resource_path)),
                                line_number=i + 1,
                                suggestion="Consider using set operations or dictionary lookups",
                                metadata={"pattern": "nested_loop"},
                            )
                        )
                        break

            i += 1

        return findings

    def _detect_string_concatenation(self, file_path: Path, content: str) -> list[Finding]:
        """Detect inefficient string concatenation in loops."""
        findings = []

        # Pattern: result = ""; for x in y: result += x
        if re.search(r'(\w+)\s*=\s*["\'][\'"]\s*\n.*for\s+\w+.*:\s*\n.*\1\s*\+=', content, re.MULTILINE):
            findings.append(
                Finding(
                    category="performance",
                    severity=FindingSeverity.LOW,
                    title="Inefficient string concatenation",
                    description="String concatenation in loop creates many intermediate objects",
                    location=str(file_path.relative_to(self.resource_path)),
                    suggestion="Use ''.join(list) or io.StringIO",
                    metadata={"pattern": "string_concat_loop"},
                )
            )

        return findings

    def _detect_list_append_in_loop(self, file_path: Path, content: str) -> list[Finding]:
        """Detect opportunities for list comprehension."""
        findings = []

        # Pattern: result = []; for x in y: result.append(transform(x))
        pattern = r'(\w+)\s*=\s*\[\]\s*\n.*for\s+(\w+)\s+in\s+.*:\s*\n.*\1\.append\('

        if re.search(pattern, content, re.MULTILINE):
            findings.append(
                Finding(
                    category="performance",
                    severity=FindingSeverity.LOW,
                    title="List comprehension opportunity",
                    description="Simple append in loop can be list comprehension",
                    location=str(file_path.relative_to(self.resource_path)),
                    suggestion="Use list comprehension for better performance and readability",
                    metadata={"pattern": "list_comprehension"},
                )
            )

        return findings

    def _detect_missing_pagination(self, file_path: Path, content: str) -> list[Finding]:
        """Detect queries without pagination."""
        findings = []

        # Django: .all() without [:limit] or pagination
        if re.search(r'\.objects\.all\(\)(?!\[)', content):
            findings.append(
                Finding(
                    category="performance",
                    severity=FindingSeverity.MEDIUM,
                    title="Query without pagination",
                    description="Fetching all objects without limit can cause memory issues",
                    location=str(file_path.relative_to(self.resource_path)),
                    suggestion="Add pagination or limit results with [:n] or .paginate()",
                    metadata={"pattern": "missing_pagination"},
                )
            )

        return findings

    def _analyze_javascript_performance(self) -> list[Finding]:
        """Analyze JavaScript/TypeScript performance."""
        findings = []

        for pattern in ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"]:
            for js_file in self._get_files_by_pattern(pattern):
                # Skip node_modules and dist
                if any(part in ["node_modules", "dist", "build"]
                       for part in js_file.parts):
                    continue

                content = self._read_file(js_file)

                # Detect missing React.memo or useMemo
                if "React" in content:
                    # Component without memo
                    if re.search(r'function\s+\w+\s*\([^)]*\)\s*{', content):
                        if "React.memo" not in content and "useMemo" not in content:
                            findings.append(
                                Finding(
                                    category="performance",
                                    severity=FindingSeverity.LOW,
                                    title="React component without memoization",
                                    description="Component may re-render unnecessarily",
                                    location=str(js_file.relative_to(self.resource_path)),
                                    suggestion="Consider React.memo() or useMemo() for expensive components",
                                    metadata={"pattern": "react_memo"},
                                )
                            )

                # Detect forEach instead of map
                if re.search(r'\.forEach\([^)]*push\(', content):
                    findings.append(
                        Finding(
                            category="performance",
                            severity=FindingSeverity.LOW,
                            title="Use map instead of forEach+push",
                            description="forEach with push can be replaced with map",
                            location=str(js_file.relative_to(self.resource_path)),
                            suggestion="Use .map() for transformations",
                            metadata={"pattern": "foreach_push"},
                        )
                    )

        return findings
