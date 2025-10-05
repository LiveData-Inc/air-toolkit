"""API dependency detectors (HTTP/REST calls between services)."""

from pathlib import Path

from .base import DependencyDetectorStrategy, DependencyResult, DependencyType


class APICallDetector(DependencyDetectorStrategy):
    """Detect API dependencies from HTTP client calls.

    This is a stub implementation. Future versions will detect:
    - Python: requests.get(), httpx, aiohttp
    - JavaScript: fetch(), axios, http.request()
    - Go: http.Client, http.Get()

    And map them to service endpoints.
    """

    @property
    def name(self) -> str:
        return "API calls (stub)"

    @property
    def dependency_type(self) -> DependencyType:
        return DependencyType.API

    def can_detect(self, repo_path: Path) -> bool:
        # TODO: Check for HTTP client library usage
        return False  # Disabled for now

    def detect(self, repo_path: Path) -> DependencyResult:
        """Detect API dependencies (not yet implemented).

        Future implementation will:
        1. Find HTTP client calls (requests.get, fetch, etc.)
        2. Extract endpoint URLs
        3. Map URLs to known services in the project
        4. Return service-to-service dependencies

        Returns:
            Empty result (stub)
        """
        return DependencyResult(
            dependencies=set(),
            dependency_type=DependencyType.API,
            source_file=None,
            metadata={"status": "not_implemented"},
        )
