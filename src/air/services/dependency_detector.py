"""Dependency detection for multi-repo analysis using Strategy pattern."""

import json
import re
from pathlib import Path

from air.services.detectors import (
    APICallDetector,
    DependencyDetectorStrategy,
    DependencyResult,
    DependencyType,
    GoImportDetector,
    GoModDetector,
    JavaScriptImportDetector,
    JavaScriptPackageJsonDetector,
    PythonImportDetector,
    PythonPyprojectDetector,
    PythonRequirementsDetector,
)


class DependencyDetectorContext:
    """Context class that manages dependency detection strategies.

    Uses the Strategy pattern to allow pluggable dependency detectors.
    """

    def __init__(self):
        """Initialize with all default detectors."""
        self._detectors: list[DependencyDetectorStrategy] = [
            # Package detectors (manifest files)
            PythonRequirementsDetector(),
            PythonPyprojectDetector(),
            JavaScriptPackageJsonDetector(),
            GoModDetector(),
            # Import detectors (code-level)
            PythonImportDetector(),
            JavaScriptImportDetector(),
            GoImportDetector(),
            # API detectors (service-to-service) - stub for now
            # APICallDetector(),  # Disabled - not yet implemented
        ]

    def register_detector(self, detector: DependencyDetectorStrategy) -> None:
        """Register a new dependency detector.

        Args:
            detector: Detector strategy to register
        """
        self._detectors.append(detector)

    def detect_all(
        self,
        repo_path: Path,
        dependency_type: DependencyType | None = None,
    ) -> list[DependencyResult]:
        """Run all applicable detectors on a repository.

        Args:
            repo_path: Path to repository
            dependency_type: Filter to specific dependency type (None = all types)

        Returns:
            List of DependencyResult from all detectors that ran
        """
        results = []

        for detector in self._detectors:
            # Filter by dependency type if specified
            if dependency_type and detector.dependency_type != dependency_type:
                continue

            # Check if detector can run
            if detector.can_detect(repo_path):
                result = detector.detect(repo_path)
                results.append(result)

        return results

    def detect_dependencies(
        self,
        repo_path: Path,
        dependency_type: DependencyType | None = None,
    ) -> set[str]:
        """Detect all dependencies in a repository.

        Args:
            repo_path: Path to repository
            dependency_type: Filter to specific dependency type (None = all types)

        Returns:
            Set of all detected package names
        """
        all_deps = set()
        results = self.detect_all(repo_path, dependency_type)

        for result in results:
            all_deps.update(result.dependencies)

        return all_deps


# Global singleton instance
_detector_context = DependencyDetectorContext()


def detect_dependencies(repo_path: Path) -> set[str]:
    """Detect external dependencies from project files.

    Uses registered detectors via Strategy pattern.

    Args:
        repo_path: Path to repository

    Returns:
        Set of package names this repo depends on
    """
    return _detector_context.detect_dependencies(repo_path)


def detect_dependencies_by_type(
    repo_path: Path,
    dependency_type: DependencyType,
) -> set[str]:
    """Detect dependencies of a specific type.

    Args:
        repo_path: Path to repository
        dependency_type: Type of dependencies to detect

    Returns:
        Set of package names for the specified type
    """
    return _detector_context.detect_dependencies(repo_path, dependency_type)


def get_dependency_results(repo_path: Path) -> list[DependencyResult]:
    """Get detailed dependency results from all detectors.

    Args:
        repo_path: Path to repository

    Returns:
        List of DependencyResult with metadata
    """
    return _detector_context.detect_all(repo_path)


def register_detector(detector: DependencyDetectorStrategy) -> None:
    """Register a custom dependency detector.

    Args:
        detector: Detector strategy to register
    """
    _detector_context.register_detector(detector)


def detect_package_name(repo_path: Path) -> str | None:
    """Detect the package name this repo provides.

    Args:
        repo_path: Path to repository

    Returns:
        Package name or None
    """
    # Python: pyproject.toml
    if (repo_path / "pyproject.toml").exists():
        try:
            content = (repo_path / "pyproject.toml").read_text()
            # Simple parsing - look for [project] name = "..."
            match = re.search(r'^\[project\].*?^name\s*=\s*["\']([^"\']+)["\']',
                            content, re.MULTILINE | re.DOTALL)
            if match:
                return match.group(1).lower()
        except Exception:
            pass

    # Python: setup.py
    if (repo_path / "setup.py").exists():
        try:
            content = (repo_path / "setup.py").read_text()
            match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1).lower()
        except Exception:
            pass

    # JavaScript: package.json
    if (repo_path / "package.json").exists():
        try:
            data = json.loads((repo_path / "package.json").read_text())
            name = data.get("name")
            if name:
                # Remove @scope/ prefix
                return name.split('/')[-1].lower()
        except Exception:
            pass

    # Go: go.mod
    if (repo_path / "go.mod").exists():
        try:
            content = (repo_path / "go.mod").read_text()
            match = re.search(r'^module\s+(\S+)', content, re.MULTILINE)
            if match:
                # Extract package name from module path
                return match.group(1).split('/')[-1].lower()
        except Exception:
            pass

    return None


def get_dependency_version(repo_path: Path, package_name: str) -> str | None:
    """Get version of a specific dependency used by this repo.

    Args:
        repo_path: Path to repository
        package_name: Package to find version for

    Returns:
        Version string or None
    """
    package_name_lower = package_name.lower()

    # Python: requirements.txt
    if (repo_path / "requirements.txt").exists():
        try:
            for line in (repo_path / "requirements.txt").read_text().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Match package==version or package>=version
                    match = re.match(rf'^{re.escape(package_name_lower)}\s*([=<>!~]+)\s*(.+)$',
                                   line.lower())
                    if match:
                        return match.group(2).strip()
        except Exception:
            pass

    # JavaScript: package.json
    if (repo_path / "package.json").exists():
        try:
            data = json.loads((repo_path / "package.json").read_text())
            deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
            for pkg, ver in deps.items():
                if pkg.split('/')[-1].lower() == package_name_lower:
                    return ver.lstrip('^~')
        except Exception:
            pass

    return None


def _parse_requirements(file_path: Path) -> set[str]:
    """Parse Python requirements.txt.

    Args:
        file_path: Path to requirements.txt

    Returns:
        Set of package names
    """
    deps = set()
    try:
        for line in file_path.read_text().split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('-'):
                # Extract package name (before ==, >=, etc.)
                pkg = re.split(r'[=<>!~\[]', line)[0].strip()
                if pkg:
                    deps.add(pkg.lower())
    except Exception:
        pass
    return deps


def _parse_pyproject_toml(file_path: Path) -> set[str]:
    """Parse Python pyproject.toml.

    Args:
        file_path: Path to pyproject.toml

    Returns:
        Set of package names
    """
    deps = set()
    try:
        content = file_path.read_text()
        # Look for dependencies = [...] section
        match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
        if match:
            deps_str = match.group(1)
            for dep in re.findall(r'["\']([^"\']+)["\']', deps_str):
                pkg = re.split(r'[=<>!~\[]', dep)[0].strip()
                if pkg:
                    deps.add(pkg.lower())
    except Exception:
        pass
    return deps


def _parse_package_json(file_path: Path) -> set[str]:
    """Parse Node package.json.

    Args:
        file_path: Path to package.json

    Returns:
        Set of package names
    """
    deps = set()
    try:
        data = json.loads(file_path.read_text())
        # Get dependencies and devDependencies
        for dep_type in ['dependencies', 'devDependencies']:
            for pkg in data.get(dep_type, {}).keys():
                # Remove @scope/ prefix and add
                deps.add(pkg.split('/')[-1].lower())
    except Exception:
        pass
    return deps


def _parse_go_mod(file_path: Path) -> set[str]:
    """Parse Go go.mod.

    Args:
        file_path: Path to go.mod

    Returns:
        Set of package names
    """
    deps = set()
    try:
        content = file_path.read_text()
        # Find require block
        in_require = False
        for line in content.split('\n'):
            line = line.strip()

            if line.startswith('require ('):
                in_require = True
                continue
            elif line == ')':
                in_require = False
                continue

            if in_require or line.startswith('require '):
                # Extract module path
                match = re.search(r'([^\s]+)\s+v[\d.]+', line)
                if match:
                    module_path = match.group(1)
                    # Extract package name from path
                    pkg_name = module_path.split('/')[-1]
                    deps.add(pkg_name.lower())
    except Exception:
        pass
    return deps
