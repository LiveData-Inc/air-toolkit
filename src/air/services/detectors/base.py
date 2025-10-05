"""Base classes for dependency detection strategies."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class DependencyType(StrEnum):
    """Type of dependency relationship."""

    PACKAGE = "package"  # Manifest file dependencies (requirements.txt, package.json)
    IMPORT = "import"    # Code-level imports (import foo, require('bar'))
    API = "api"          # HTTP/REST API calls between services


@dataclass
class DependencyResult:
    """Result from a dependency detector.

    Attributes:
        dependencies: Set of package/module names detected
        dependency_type: Type of dependency (package, import, api)
        source_file: File where dependencies were detected
        metadata: Additional information (versions, locations, etc.)
    """

    dependencies: set[str] = field(default_factory=set)
    dependency_type: DependencyType = DependencyType.PACKAGE
    source_file: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


class DependencyDetectorStrategy(ABC):
    """Abstract base class for dependency detection strategies.

    Each detector implements a specific strategy for finding dependencies
    in a particular type of file or code pattern.
    """

    @abstractmethod
    def can_detect(self, repo_path: Path) -> bool:
        """Check if this detector can run on the given repository.

        Args:
            repo_path: Path to repository

        Returns:
            True if detector should run (e.g., if required files exist)
        """
        pass

    @abstractmethod
    def detect(self, repo_path: Path) -> DependencyResult:
        """Detect dependencies in the repository.

        Args:
            repo_path: Path to repository

        Returns:
            DependencyResult with detected dependencies
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of this detector."""
        pass

    @property
    def dependency_type(self) -> DependencyType:
        """Type of dependencies this detector finds.

        Default is PACKAGE. Override for import or API detectors.
        """
        return DependencyType.PACKAGE
