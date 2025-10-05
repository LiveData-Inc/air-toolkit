"""Code-level import dependency detectors."""

import re
from pathlib import Path

from .base import DependencyDetectorStrategy, DependencyResult, DependencyType


class PythonImportDetector(DependencyDetectorStrategy):
    """Detect dependencies from Python import statements."""

    @property
    def name(self) -> str:
        return "Python imports"

    @property
    def dependency_type(self) -> DependencyType:
        return DependencyType.IMPORT

    def can_detect(self, repo_path: Path) -> bool:
        # Check if there are any Python files
        return any(repo_path.rglob("*.py"))

    def detect(self, repo_path: Path) -> DependencyResult:
        imports = set()
        import_locations = {}

        # Scan all Python files
        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                file_imports = self._extract_imports(content)

                for imp in file_imports:
                    imports.add(imp)
                    # Track where import was found
                    if imp not in import_locations:
                        import_locations[imp] = []
                    import_locations[imp].append(str(py_file.relative_to(repo_path)))
            except Exception:
                # Skip files that can't be read
                continue

        # Convert locations to comma-separated strings
        metadata = {pkg: ','.join(locs) for pkg, locs in import_locations.items()}

        return DependencyResult(
            dependencies=imports,
            dependency_type=DependencyType.IMPORT,
            source_file="*.py",
            metadata=metadata,
        )

    def _extract_imports(self, content: str) -> set[str]:
        """Extract import statements from Python source code.

        Args:
            content: Python source code

        Returns:
            Set of imported package names (top-level only)
        """
        imports = set()

        # Match: import foo
        for match in re.finditer(r'^\s*import\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE):
            imports.add(match.group(1).lower())

        # Match: from foo import bar
        for match in re.finditer(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)', content, re.MULTILINE):
            imports.add(match.group(1).lower())

        # Match: from foo.bar import baz (extract foo)
        for match in re.finditer(r'^\s*from\s+([a-zA-Z_][a-zA-Z0-9_]*)\.', content, re.MULTILINE):
            imports.add(match.group(1).lower())

        return imports


class JavaScriptImportDetector(DependencyDetectorStrategy):
    """Detect dependencies from JavaScript/TypeScript import statements."""

    @property
    def name(self) -> str:
        return "JavaScript/TypeScript imports"

    @property
    def dependency_type(self) -> DependencyType:
        return DependencyType.IMPORT

    def can_detect(self, repo_path: Path) -> bool:
        # Check if there are any JS/TS files
        return any(repo_path.rglob("*.js")) or any(repo_path.rglob("*.ts")) or any(repo_path.rglob("*.tsx"))

    def detect(self, repo_path: Path) -> DependencyResult:
        imports = set()
        import_locations = {}

        # Scan all JavaScript/TypeScript files
        for pattern in ["*.js", "*.ts", "*.tsx", "*.jsx"]:
            for js_file in repo_path.rglob(pattern):
                try:
                    content = js_file.read_text()
                    file_imports = self._extract_imports(content)

                    for imp in file_imports:
                        imports.add(imp)
                        if imp not in import_locations:
                            import_locations[imp] = []
                        import_locations[imp].append(str(js_file.relative_to(repo_path)))
                except Exception:
                    continue

        metadata = {pkg: ','.join(locs) for pkg, locs in import_locations.items()}

        return DependencyResult(
            dependencies=imports,
            dependency_type=DependencyType.IMPORT,
            source_file="*.{js,ts,tsx}",
            metadata=metadata,
        )

    def _extract_imports(self, content: str) -> set[str]:
        """Extract import statements from JavaScript/TypeScript source.

        Args:
            content: JavaScript/TypeScript source code

        Returns:
            Set of imported package names
        """
        imports = set()

        # Match: import foo from 'package'
        # Match: import { bar } from 'package'
        for match in re.finditer(r'import\s+.*?from\s+["\']([^"\']+)["\']', content):
            pkg = match.group(1)
            # Skip relative imports (./foo, ../bar)
            if not pkg.startswith('.'):
                # Remove @scope/ and extract package name
                pkg_name = pkg.split('/')[1] if pkg.startswith('@') else pkg.split('/')[0]
                imports.add(pkg_name.lower())

        # Match: const foo = require('package')
        for match in re.finditer(r'require\s*\(\s*["\']([^"\']+)["\']\s*\)', content):
            pkg = match.group(1)
            if not pkg.startswith('.'):
                pkg_name = pkg.split('/')[1] if pkg.startswith('@') else pkg.split('/')[0]
                imports.add(pkg_name.lower())

        return imports


class GoImportDetector(DependencyDetectorStrategy):
    """Detect dependencies from Go import statements."""

    @property
    def name(self) -> str:
        return "Go imports"

    @property
    def dependency_type(self) -> DependencyType:
        return DependencyType.IMPORT

    def can_detect(self, repo_path: Path) -> bool:
        # Check if there are any Go files
        return any(repo_path.rglob("*.go"))

    def detect(self, repo_path: Path) -> DependencyResult:
        imports = set()
        import_locations = {}

        # Scan all Go files
        for go_file in repo_path.rglob("*.go"):
            try:
                content = go_file.read_text()
                file_imports = self._extract_imports(content)

                for imp in file_imports:
                    imports.add(imp)
                    if imp not in import_locations:
                        import_locations[imp] = []
                    import_locations[imp].append(str(go_file.relative_to(repo_path)))
            except Exception:
                continue

        metadata = {pkg: ','.join(locs) for pkg, locs in import_locations.items()}

        return DependencyResult(
            dependencies=imports,
            dependency_type=DependencyType.IMPORT,
            source_file="*.go",
            metadata=metadata,
        )

    def _extract_imports(self, content: str) -> set[str]:
        """Extract import statements from Go source code.

        Args:
            content: Go source code

        Returns:
            Set of imported package names (last component of path)
        """
        imports = set()

        # Match: import "package"
        for match in re.finditer(r'import\s+"([^"]+)"', content):
            pkg_path = match.group(1)
            # Extract last component of path
            pkg_name = pkg_path.split('/')[-1]
            imports.add(pkg_name.lower())

        # Match: import ( ... ) blocks
        import_block = re.search(r'import\s+\((.*?)\)', content, re.DOTALL)
        if import_block:
            block_content = import_block.group(1)
            for match in re.finditer(r'"([^"]+)"', block_content):
                pkg_path = match.group(1)
                pkg_name = pkg_path.split('/')[-1]
                imports.add(pkg_name.lower())

        return imports
