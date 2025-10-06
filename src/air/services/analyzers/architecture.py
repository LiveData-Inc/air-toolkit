"""Architecture analyzer - analyzes dependencies and design patterns."""

import re
from pathlib import Path

from air.services.path_filter import should_exclude_path
from .base import AnalyzerResult, BaseAnalyzer, Finding, FindingSeverity


class ArchitectureAnalyzer(BaseAnalyzer):
    """Analyzes architecture and dependencies."""

    def __init__(self, repo_path: Path, include_external: bool = False):
        """Initialize architecture analyzer.

        Args:
            repo_path: Path to repository
            include_external: If True, include external/vendor code in analysis
        """
        super().__init__(repo_path)
        self.include_external = include_external

    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "architecture"

    def analyze(self) -> AnalyzerResult:
        """Analyze architecture.

        Returns:
            AnalyzerResult with architecture findings
        """
        findings = []

        # Analyze dependencies
        dep_findings = self._analyze_dependencies()
        findings.extend(dep_findings)

        # Check for circular dependencies (Python)
        circular = self._check_circular_imports()
        findings.extend(circular)

        # Check for common patterns
        pattern_findings = self._detect_patterns()
        findings.extend(pattern_findings)

        # Summary
        summary = {
            "dependencies_found": len(dep_findings),
            "patterns_detected": len(pattern_findings),
        }

        return AnalyzerResult(
            analyzer_name=self.name,
            findings=findings,
            summary=summary,
        )

    def _analyze_dependencies(self) -> list[Finding]:
        """Analyze project dependencies."""
        findings = []

        # Check Python dependencies
        requirements_files = list(self.resource_path.glob("*requirements*.txt"))
        requirements_files.extend(self.resource_path.glob("pyproject.toml"))

        for req_file in requirements_files:
            content = self._read_file(req_file)

            # Check for unpinned dependencies
            if req_file.suffix == ".txt":
                unpinned = re.findall(r'^([a-zA-Z0-9_-]+)\s*$', content, re.MULTILINE)
                if unpinned:
                    findings.append(
                        Finding(
                            category="architecture",
                            severity=FindingSeverity.MEDIUM,
                            title="Unpinned dependencies",
                            description=f"Found {len(unpinned)} unpinned dependencies",
                            location=str(req_file.relative_to(self.resource_path)),
                            suggestion="Pin dependency versions for reproducible builds",
                            metadata={"unpinned_count": len(unpinned)},
                        )
                    )

        # Check Node dependencies
        package_json = self.resource_path / "package.json"
        if package_json.exists():
            content = self._read_file(package_json)

            # Count dependencies
            deps = content.count('"dependencies"')
            dev_deps = content.count('"devDependencies"')

            if deps + dev_deps > 0:
                findings.append(
                    Finding(
                        category="architecture",
                        severity=FindingSeverity.INFO,
                        title="Node.js dependencies detected",
                        description=f"Project has {deps + dev_deps} dependency sections",
                        location="package.json",
                        metadata={"dependencies": deps, "devDependencies": dev_deps},
                    )
                )

        return findings

    def _check_circular_imports(self) -> list[Finding]:
        """Check for potential circular imports in Python."""
        findings = []

        # This is a simplified check - real circular dependency detection is complex
        py_files = list(self._get_files_by_pattern("**/*.py"))

        import_graph = {}
        for py_file in py_files:
            if any(part in ["test", "tests", "__pycache__"]
                   for part in py_file.parts):
                continue

            content = self._read_file(py_file)
            imports = re.findall(r'from\s+(\S+)\s+import', content)
            imports.extend(re.findall(r'import\s+(\S+)', content))

            module_name = str(py_file.relative_to(self.resource_path)).replace("/", ".").replace(".py", "")
            import_graph[module_name] = imports

        # Simple heuristic: if two modules import each other
        for module, imports in import_graph.items():
            for imported in imports:
                if imported in import_graph and module in import_graph[imported]:
                    findings.append(
                        Finding(
                            category="architecture",
                            severity=FindingSeverity.MEDIUM,
                            title="Potential circular import",
                            description=f"{module} and {imported} may have circular dependency",
                            suggestion="Refactor to remove circular dependencies",
                            metadata={"modules": [module, imported]},
                        )
                    )
                    break  # Only report once per module

        return findings

    def _detect_patterns(self) -> list[Finding]:
        """Detect common architectural patterns."""
        findings = []

        # Check for API structure
        has_api = any(self._get_files_by_pattern(pattern) for pattern in [
            "**/api/**/*.py",
            "**/routes/**/*.py",
            "**/controllers/**/*.py",
            "**/views/**/*.py",
        ])

        if has_api:
            findings.append(
                Finding(
                    category="architecture",
                    severity=FindingSeverity.INFO,
                    title="API structure detected",
                    description="Project appears to follow API/MVC pattern",
                    metadata={"pattern": "api"},
                )
            )

        # Check for database models
        has_models = any(self._get_files_by_pattern(pattern) for pattern in [
            "**/models/**/*.py",
            "**/models.py",
            "**/entities/**/*.py",
        ])

        if has_models:
            findings.append(
                Finding(
                    category="architecture",
                    severity=FindingSeverity.INFO,
                    title="Data models detected",
                    description="Project has structured data models",
                    metadata={"pattern": "models"},
                )
            )

        # Check for service layer
        has_services = any(self._get_files_by_pattern(pattern) for pattern in [
            "**/services/**/*.py",
            "**/service/**/*.py",
        ])

        if has_services:
            findings.append(
                Finding(
                    category="architecture",
                    severity=FindingSeverity.INFO,
                    title="Service layer detected",
                    description="Project follows service-oriented architecture",
                    metadata={"pattern": "services"},
                )
            )

        return findings
