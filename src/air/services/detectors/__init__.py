"""Dependency detection strategies."""

from .api_detectors import APICallDetector
from .base import DependencyDetectorStrategy, DependencyResult, DependencyType
from .import_detectors import (
    GoImportDetector,
    JavaScriptImportDetector,
    PythonImportDetector,
)
from .package_detectors import (
    GoModDetector,
    JavaScriptPackageJsonDetector,
    PythonPyprojectDetector,
    PythonRequirementsDetector,
)

__all__ = [
    # Base classes
    "DependencyDetectorStrategy",
    "DependencyResult",
    "DependencyType",
    # Package detectors
    "PythonRequirementsDetector",
    "PythonPyprojectDetector",
    "JavaScriptPackageJsonDetector",
    "GoModDetector",
    # Import detectors
    "PythonImportDetector",
    "JavaScriptImportDetector",
    "GoImportDetector",
    # API detectors
    "APICallDetector",
]
