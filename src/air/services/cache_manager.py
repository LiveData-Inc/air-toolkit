"""Cache manager for analysis results."""

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from air.services.analyzers.base import AnalyzerResult, Finding, FindingSeverity


class CacheMetadata:
    """Metadata for cached analysis results."""

    def __init__(
        self,
        file_path: str,
        file_hash: str,
        analyzer_name: str,
        timestamp: datetime,
        air_version: str,
    ):
        """Initialize cache metadata.

        Args:
            file_path: Relative path to analyzed file
            file_hash: SHA256 hash of file content
            analyzer_name: Name of analyzer that produced results
            timestamp: When analysis was cached
            air_version: AIR version that produced the cache
        """
        self.file_path = file_path
        self.file_hash = file_hash
        self.analyzer_name = analyzer_name
        self.timestamp = timestamp
        self.air_version = air_version

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "analyzer_name": self.analyzer_name,
            "timestamp": self.timestamp.isoformat(),
            "air_version": self.air_version,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CacheMetadata":
        """Create from dictionary."""
        return cls(
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            analyzer_name=data["analyzer_name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            air_version=data["air_version"],
        )


class CacheStats:
    """Statistics about the cache."""

    def __init__(
        self,
        total_entries: int,
        cache_size_mb: float,
        hit_count: int,
        miss_count: int,
        last_cleared: datetime | None = None,
    ):
        """Initialize cache stats.

        Args:
            total_entries: Total number of cached entries
            cache_size_mb: Total cache size in MB
            hit_count: Number of cache hits
            miss_count: Number of cache misses
            last_cleared: When cache was last cleared
        """
        self.total_entries = total_entries
        self.cache_size_mb = cache_size_mb
        self.hit_count = hit_count
        self.miss_count = miss_count
        self.last_cleared = last_cleared

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate.

        Returns:
            Hit rate as percentage (0-100)
        """
        total = self.hit_count + self.miss_count
        if total == 0:
            return 0.0
        return (self.hit_count / total) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_entries": self.total_entries,
            "cache_size_mb": self.cache_size_mb,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": self.hit_rate,
            "last_cleared": self.last_cleared.isoformat() if self.last_cleared else None,
        }


class CacheManager:
    """Manages analysis result caching."""

    def __init__(self, cache_dir: Path | None = None, air_version: str = "0.6.1"):
        """Initialize cache manager.

        Args:
            cache_dir: Directory for cache storage (default: .air/cache)
            air_version: Current AIR version
        """
        self.cache_dir = cache_dir or Path.cwd() / ".air" / "cache"
        self.air_version = air_version
        self.stats_file = self.cache_dir / "stats.json"

        # Ensure cache directory exists
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def compute_file_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content.

        Args:
            file_path: Path to file

        Returns:
            SHA256 hash as hex string
        """
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(8192), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            # If we can't hash the file, return empty string
            # This will cause cache miss
            return ""

    def _compute_repo_hash(self, repo_path: Path) -> str:
        """Compute hash identifier for repository.

        Args:
            repo_path: Path to repository

        Returns:
            Hash of absolute path
        """
        hasher = hashlib.sha256()
        hasher.update(str(repo_path.resolve()).encode("utf-8"))
        return hasher.hexdigest()[:16]  # Use first 16 chars

    def _get_cache_path(
        self, repo_path: Path, file_path: Path, analyzer_name: str
    ) -> Path:
        """Get cache file path for a specific analysis.

        Args:
            repo_path: Path to repository
            file_path: Path to analyzed file
            analyzer_name: Name of analyzer

        Returns:
            Path to cache file
        """
        repo_hash = self._compute_repo_hash(repo_path)
        file_hash = self.compute_file_hash(file_path)

        # Create cache directory structure: cache/{repo_hash}/
        repo_cache_dir = self.cache_dir / repo_hash
        repo_cache_dir.mkdir(exist_ok=True)

        # Cache filename: {file_hash}-{analyzer_name}.json
        cache_filename = f"{file_hash}-{analyzer_name}.json"
        return repo_cache_dir / cache_filename

    def _get_metadata_path(
        self, repo_path: Path, file_path: Path, analyzer_name: str
    ) -> Path:
        """Get metadata file path.

        Args:
            repo_path: Path to repository
            file_path: Path to analyzed file
            analyzer_name: Name of analyzer

        Returns:
            Path to metadata file
        """
        cache_path = self._get_cache_path(repo_path, file_path, analyzer_name)
        return cache_path.with_suffix(".meta.json")

    def get_cached_analysis(
        self, repo_path: Path, file_path: Path, analyzer_name: str
    ) -> AnalyzerResult | None:
        """Get cached analysis result if available and valid.

        Args:
            repo_path: Path to repository
            file_path: Path to analyzed file
            analyzer_name: Name of analyzer

        Returns:
            Cached AnalyzerResult or None if not cached/invalid
        """
        cache_path = self._get_cache_path(repo_path, file_path, analyzer_name)
        metadata_path = self._get_metadata_path(repo_path, file_path, analyzer_name)

        # Check if cache exists
        if not cache_path.exists() or not metadata_path.exists():
            self._record_miss()
            return None

        try:
            # Load metadata
            metadata = CacheMetadata.from_dict(json.loads(metadata_path.read_text()))

            # Validate cache is still valid
            current_hash = self.compute_file_hash(file_path)
            if current_hash != metadata.file_hash:
                # File changed, cache invalid
                self._record_miss()
                return None

            # Check AIR version matches (invalidate on version change)
            if metadata.air_version != self.air_version:
                self._record_miss()
                return None

            # Load cached result
            cache_data = json.loads(cache_path.read_text())

            # Reconstruct AnalyzerResult
            findings = [
                Finding(
                    category=f["category"],
                    severity=FindingSeverity(f["severity"]),
                    title=f["title"],
                    description=f["description"],
                    location=f.get("location"),
                    line_number=f.get("line_number"),
                    suggestion=f.get("suggestion"),
                    metadata=f.get("metadata", {}),
                )
                for f in cache_data.get("findings", [])
            ]

            result = AnalyzerResult(
                analyzer_name=cache_data["analyzer"],
                findings=findings,
                summary=cache_data.get("summary", {}),
                metadata=cache_data.get("metadata", {}),
            )

            self._record_hit()
            return result

        except Exception:
            # Cache corrupted or unreadable
            self._record_miss()
            return None

    def set_cached_analysis(
        self, repo_path: Path, file_path: Path, result: AnalyzerResult
    ) -> None:
        """Cache analysis result.

        Args:
            repo_path: Path to repository
            file_path: Path to analyzed file
            result: Analysis result to cache
        """
        cache_path = self._get_cache_path(repo_path, file_path, result.analyzer_name)
        metadata_path = self._get_metadata_path(
            repo_path, file_path, result.analyzer_name
        )

        try:
            # Compute file hash
            file_hash = self.compute_file_hash(file_path)

            # Create metadata
            relative_path = file_path.relative_to(repo_path) if file_path.is_relative_to(repo_path) else file_path
            metadata = CacheMetadata(
                file_path=str(relative_path),
                file_hash=file_hash,
                analyzer_name=result.analyzer_name,
                timestamp=datetime.now(),
                air_version=self.air_version,
            )

            # Write cache data
            cache_path.write_text(json.dumps(result.to_dict(), indent=2))

            # Write metadata
            metadata_path.write_text(json.dumps(metadata.to_dict(), indent=2))

        except Exception:
            # Silently fail if we can't cache
            pass

    def invalidate_cache(self, repo_path: Path, file_path: Path | None = None) -> None:
        """Invalidate cached results.

        Args:
            repo_path: Path to repository
            file_path: Specific file to invalidate, or None for entire repo
        """
        repo_hash = self._compute_repo_hash(repo_path)
        repo_cache_dir = self.cache_dir / repo_hash

        if not repo_cache_dir.exists():
            return

        if file_path is None:
            # Invalidate entire repo cache
            shutil.rmtree(repo_cache_dir, ignore_errors=True)
        else:
            # Invalidate specific file across all analyzers
            file_hash = self.compute_file_hash(file_path)
            for cache_file in repo_cache_dir.glob(f"{file_hash}-*.json"):
                cache_file.unlink(missing_ok=True)
                # Also remove metadata
                cache_file.with_suffix(".meta.json").unlink(missing_ok=True)

    def clear_all(self) -> None:
        """Clear all cached data."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir, ignore_errors=True)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Record clear time
        self._record_clear()

    def get_stats(self) -> CacheStats:
        """Get cache statistics.

        Returns:
            CacheStats object
        """
        total_entries = 0
        total_size_bytes = 0

        # Count all cache files (exclude metadata and stats files)
        for cache_file in self.cache_dir.rglob("*.json"):
            if cache_file.name != "stats.json" and not cache_file.name.endswith(".meta.json"):
                total_entries += 1
                total_size_bytes += cache_file.stat().st_size

        # Load hit/miss stats
        hit_count = 0
        miss_count = 0
        last_cleared = None

        if self.stats_file.exists():
            try:
                stats_data = json.loads(self.stats_file.read_text())
                hit_count = stats_data.get("hit_count", 0)
                miss_count = stats_data.get("miss_count", 0)
                if stats_data.get("last_cleared"):
                    last_cleared = datetime.fromisoformat(stats_data["last_cleared"])
            except Exception:
                pass

        return CacheStats(
            total_entries=total_entries,
            cache_size_mb=total_size_bytes / (1024 * 1024),
            hit_count=hit_count,
            miss_count=miss_count,
            last_cleared=last_cleared,
        )

    def _record_hit(self) -> None:
        """Record a cache hit."""
        self._update_stats(hit=True)

    def _record_miss(self) -> None:
        """Record a cache miss."""
        self._update_stats(hit=False)

    def _record_clear(self) -> None:
        """Record cache clear."""
        stats_data = {
            "hit_count": 0,
            "miss_count": 0,
            "last_cleared": datetime.now().isoformat(),
        }
        self.stats_file.write_text(json.dumps(stats_data, indent=2))

    def _update_stats(self, hit: bool) -> None:
        """Update hit/miss statistics.

        Args:
            hit: True for cache hit, False for miss
        """
        stats_data = {"hit_count": 0, "miss_count": 0, "last_cleared": None}

        if self.stats_file.exists():
            try:
                stats_data = json.loads(self.stats_file.read_text())
            except Exception:
                pass

        if hit:
            stats_data["hit_count"] = stats_data.get("hit_count", 0) + 1
        else:
            stats_data["miss_count"] = stats_data.get("miss_count", 0) + 1

        try:
            self.stats_file.write_text(json.dumps(stats_data, indent=2))
        except Exception:
            pass
