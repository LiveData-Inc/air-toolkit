"""Package manifest file dependency detectors."""

import json
import re
from pathlib import Path

from .base import DependencyDetectorStrategy, DependencyResult, DependencyType


class PythonRequirementsDetector(DependencyDetectorStrategy):
    """Detect dependencies from Python requirements.txt."""

    @property
    def name(self) -> str:
        return "Python requirements.txt"

    def can_detect(self, repo_path: Path) -> bool:
        return (repo_path / "requirements.txt").exists()

    def detect(self, repo_path: Path) -> DependencyResult:
        file_path = repo_path / "requirements.txt"
        deps = set()
        versions = {}

        try:
            for line in file_path.read_text().split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-'):
                    # Extract package name and version
                    match = re.match(r'^([^=<>!~\[]+)([=<>!~]+)(.+)$', line)
                    if match:
                        pkg = match.group(1).strip().lower()
                        version = match.group(3).strip()
                        deps.add(pkg)
                        versions[pkg] = version
                    else:
                        # No version specified
                        pkg = re.split(r'[=<>!~\[]', line)[0].strip()
                        if pkg:
                            deps.add(pkg.lower())
        except Exception:
            pass

        return DependencyResult(
            dependencies=deps,
            dependency_type=DependencyType.PACKAGE,
            source_file="requirements.txt",
            metadata=versions,
        )


class PythonPyprojectDetector(DependencyDetectorStrategy):
    """Detect dependencies from Python pyproject.toml."""

    @property
    def name(self) -> str:
        return "Python pyproject.toml"

    def can_detect(self, repo_path: Path) -> bool:
        return (repo_path / "pyproject.toml").exists()

    def detect(self, repo_path: Path) -> DependencyResult:
        file_path = repo_path / "pyproject.toml"
        deps = set()
        versions = {}

        try:
            content = file_path.read_text()
            # Look for dependencies = [...] section
            match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if match:
                deps_str = match.group(1)
                for dep in re.findall(r'["\']([^"\']+)["\']', deps_str):
                    # Parse package name and version
                    dep_match = re.match(r'^([^=<>!~\[]+)([=<>!~]+)(.+)$', dep)
                    if dep_match:
                        pkg = dep_match.group(1).strip().lower()
                        version = dep_match.group(3).strip()
                        deps.add(pkg)
                        versions[pkg] = version
                    else:
                        pkg = re.split(r'[=<>!~\[]', dep)[0].strip()
                        if pkg:
                            deps.add(pkg.lower())
        except Exception:
            pass

        return DependencyResult(
            dependencies=deps,
            dependency_type=DependencyType.PACKAGE,
            source_file="pyproject.toml",
            metadata=versions,
        )


class JavaScriptPackageJsonDetector(DependencyDetectorStrategy):
    """Detect dependencies from JavaScript/TypeScript package.json."""

    @property
    def name(self) -> str:
        return "JavaScript package.json"

    def can_detect(self, repo_path: Path) -> bool:
        return (repo_path / "package.json").exists()

    def detect(self, repo_path: Path) -> DependencyResult:
        file_path = repo_path / "package.json"
        deps = set()
        versions = {}

        try:
            data = json.loads(file_path.read_text())
            # Get dependencies and devDependencies
            for dep_type in ['dependencies', 'devDependencies']:
                for pkg, ver in data.get(dep_type, {}).items():
                    # Remove @scope/ prefix and add
                    pkg_name = pkg.split('/')[-1].lower()
                    deps.add(pkg_name)
                    # Clean version (remove ^~)
                    versions[pkg_name] = ver.lstrip('^~')
        except Exception:
            pass

        return DependencyResult(
            dependencies=deps,
            dependency_type=DependencyType.PACKAGE,
            source_file="package.json",
            metadata=versions,
        )


class GoModDetector(DependencyDetectorStrategy):
    """Detect dependencies from Go go.mod."""

    @property
    def name(self) -> str:
        return "Go go.mod"

    def can_detect(self, repo_path: Path) -> bool:
        return (repo_path / "go.mod").exists()

    def detect(self, repo_path: Path) -> DependencyResult:
        file_path = repo_path / "go.mod"
        deps = set()
        versions = {}

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
                    # Extract module path and version
                    match = re.search(r'([^\s]+)\s+v([\d.]+)', line)
                    if match:
                        module_path = match.group(1)
                        version = match.group(2)
                        # Extract package name from path
                        pkg_name = module_path.split('/')[-1].lower()
                        deps.add(pkg_name)
                        versions[pkg_name] = version
        except Exception:
            pass

        return DependencyResult(
            dependencies=deps,
            dependency_type=DependencyType.PACKAGE,
            source_file="go.mod",
            metadata=versions,
        )
