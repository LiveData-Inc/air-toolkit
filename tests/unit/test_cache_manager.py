"""Unit tests for cache manager."""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from air.services.analyzers.base import AnalyzerResult, Finding, FindingSeverity
from air.services.cache_manager import CacheManager, CacheMetadata, CacheStats


@pytest.fixture
def temp_cache_dir():
    """Create temporary cache directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_repo_dir():
    """Create temporary repository directory."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def cache_manager(temp_cache_dir):
    """Create cache manager with temp directory."""
    return CacheManager(cache_dir=temp_cache_dir, air_version="0.6.1")


@pytest.fixture
def sample_file(temp_repo_dir):
    """Create sample file for testing."""
    file_path = temp_repo_dir / "test.py"
    file_path.write_text("def hello():\n    print('world')\n")
    return file_path


@pytest.fixture
def sample_result():
    """Create sample analyzer result."""
    findings = [
        Finding(
            category="security",
            severity=FindingSeverity.HIGH,
            title="Hardcoded secret",
            description="Found hardcoded API key",
            location="test.py",
            line_number=5,
            suggestion="Use environment variables",
            metadata={"pattern": "api_key"},
        ),
        Finding(
            category="security",
            severity=FindingSeverity.MEDIUM,
            title="SQL injection risk",
            description="Possible SQL injection",
            location="test.py",
            line_number=10,
        ),
    ]

    return AnalyzerResult(
        analyzer_name="security",
        findings=findings,
        summary={"total_issues": 2, "high": 1, "medium": 1},
        metadata={"scan_time": "2025-10-05"},
    )


class TestCacheManager:
    """Test CacheManager class."""

    def test_init_creates_cache_directory(self, temp_cache_dir):
        """Test that initialization creates cache directory."""
        cache_dir = temp_cache_dir / "test_cache"
        manager = CacheManager(cache_dir=cache_dir)

        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_compute_file_hash(self, cache_manager, sample_file):
        """Test file hashing."""
        hash1 = cache_manager.compute_file_hash(sample_file)

        # Should return consistent hash
        hash2 = cache_manager.compute_file_hash(sample_file)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 produces 64 hex chars

        # Modify file, hash should change
        sample_file.write_text("def hello():\n    print('changed')\n")
        hash3 = cache_manager.compute_file_hash(sample_file)
        assert hash3 != hash1

    def test_compute_file_hash_missing_file(self, cache_manager):
        """Test hashing missing file returns empty string."""
        missing_file = Path("/nonexistent/file.py")
        hash_val = cache_manager.compute_file_hash(missing_file)
        assert hash_val == ""

    def test_cache_and_retrieve_result(
        self, cache_manager, temp_repo_dir, sample_file, sample_result
    ):
        """Test caching and retrieving analysis result."""
        # Cache the result
        cache_manager.set_cached_analysis(temp_repo_dir, sample_file, sample_result)

        # Retrieve from cache
        cached_result = cache_manager.get_cached_analysis(
            temp_repo_dir, sample_file, "security"
        )

        assert cached_result is not None
        assert cached_result.analyzer_name == "security"
        assert len(cached_result.findings) == 2
        assert cached_result.findings[0].title == "Hardcoded secret"
        assert cached_result.findings[0].severity == FindingSeverity.HIGH
        assert cached_result.summary["total_issues"] == 2

    def test_cache_miss_when_not_cached(self, cache_manager, temp_repo_dir, sample_file):
        """Test cache miss when result not cached."""
        result = cache_manager.get_cached_analysis(
            temp_repo_dir, sample_file, "security"
        )
        assert result is None

    def test_cache_invalid_when_file_changes(
        self, cache_manager, temp_repo_dir, sample_file, sample_result
    ):
        """Test cache invalidation when file content changes."""
        # Cache the result
        cache_manager.set_cached_analysis(temp_repo_dir, sample_file, sample_result)

        # Verify it's cached
        cached_result = cache_manager.get_cached_analysis(
            temp_repo_dir, sample_file, "security"
        )
        assert cached_result is not None

        # Modify the file
        sample_file.write_text("def hello():\n    print('modified')\n")

        # Cache should be invalid now
        cached_result = cache_manager.get_cached_analysis(
            temp_repo_dir, sample_file, "security"
        )
        assert cached_result is None

    def test_cache_invalid_when_version_changes(
        self, temp_cache_dir, temp_repo_dir, sample_file, sample_result
    ):
        """Test cache invalidation when AIR version changes."""
        # Cache with version 0.6.1
        manager_v1 = CacheManager(cache_dir=temp_cache_dir, air_version="0.6.1")
        manager_v1.set_cached_analysis(temp_repo_dir, sample_file, sample_result)

        # Try to retrieve with version 0.6.2
        manager_v2 = CacheManager(cache_dir=temp_cache_dir, air_version="0.6.2")
        cached_result = manager_v2.get_cached_analysis(
            temp_repo_dir, sample_file, "security"
        )

        # Cache should be invalid
        assert cached_result is None

    def test_invalidate_specific_file(
        self, cache_manager, temp_repo_dir, sample_file, sample_result
    ):
        """Test invalidating cache for specific file."""
        # Cache the result
        cache_manager.set_cached_analysis(temp_repo_dir, sample_file, sample_result)

        # Verify it's cached
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, sample_file, "security")
            is not None
        )

        # Invalidate this specific file
        cache_manager.invalidate_cache(temp_repo_dir, sample_file)

        # Cache should be cleared
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, sample_file, "security")
            is None
        )

    def test_invalidate_entire_repo(
        self, cache_manager, temp_repo_dir, sample_result
    ):
        """Test invalidating cache for entire repository."""
        # Create multiple files and cache results
        file1 = temp_repo_dir / "file1.py"
        file2 = temp_repo_dir / "file2.py"
        file1.write_text("print('file1')")
        file2.write_text("print('file2')")

        cache_manager.set_cached_analysis(temp_repo_dir, file1, sample_result)
        cache_manager.set_cached_analysis(temp_repo_dir, file2, sample_result)

        # Verify both are cached
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, file1, "security")
            is not None
        )
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, file2, "security")
            is not None
        )

        # Invalidate entire repo
        cache_manager.invalidate_cache(temp_repo_dir)

        # Both should be cleared
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, file1, "security") is None
        )
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, file2, "security") is None
        )

    def test_clear_all_cache(self, cache_manager, temp_repo_dir, sample_result):
        """Test clearing all cached data."""
        # Create files and cache results
        file1 = temp_repo_dir / "file1.py"
        file1.write_text("print('file1')")

        cache_manager.set_cached_analysis(temp_repo_dir, file1, sample_result)

        # Verify cached
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, file1, "security")
            is not None
        )

        # Clear all
        cache_manager.clear_all()

        # Should be empty
        assert (
            cache_manager.get_cached_analysis(temp_repo_dir, file1, "security") is None
        )

    def test_cache_stats_tracking(
        self, cache_manager, temp_repo_dir, sample_file, sample_result
    ):
        """Test cache statistics tracking."""
        # Initial stats should be zero
        stats = cache_manager.get_stats()
        assert stats.total_entries == 0
        assert stats.hit_count == 0
        assert stats.miss_count == 0

        # Cache miss
        cache_manager.get_cached_analysis(temp_repo_dir, sample_file, "security")
        stats = cache_manager.get_stats()
        assert stats.miss_count == 1
        assert stats.hit_count == 0

        # Cache result
        cache_manager.set_cached_analysis(temp_repo_dir, sample_file, sample_result)
        stats = cache_manager.get_stats()
        assert stats.total_entries == 1
        assert stats.cache_size_mb > 0

        # Cache hit
        cache_manager.get_cached_analysis(temp_repo_dir, sample_file, "security")
        stats = cache_manager.get_stats()
        assert stats.hit_count == 1
        assert stats.miss_count == 1
        assert stats.hit_rate == 50.0  # 1 hit, 1 miss

    def test_cache_stats_hit_rate_calculation(self, cache_manager):
        """Test hit rate calculation."""
        # No hits or misses
        stats = CacheStats(
            total_entries=0, cache_size_mb=0, hit_count=0, miss_count=0
        )
        assert stats.hit_rate == 0.0

        # All hits
        stats = CacheStats(
            total_entries=10, cache_size_mb=1.5, hit_count=10, miss_count=0
        )
        assert stats.hit_rate == 100.0

        # 80% hit rate
        stats = CacheStats(
            total_entries=10, cache_size_mb=1.5, hit_count=8, miss_count=2
        )
        assert stats.hit_rate == 80.0

    def test_cache_with_multiple_analyzers(
        self, cache_manager, temp_repo_dir, sample_file
    ):
        """Test caching results from multiple analyzers for same file."""
        # Create results for different analyzers
        security_result = AnalyzerResult(
            analyzer_name="security", findings=[], summary={"type": "security"}
        )
        performance_result = AnalyzerResult(
            analyzer_name="performance", findings=[], summary={"type": "performance"}
        )

        # Cache both
        cache_manager.set_cached_analysis(temp_repo_dir, sample_file, security_result)
        cache_manager.set_cached_analysis(
            temp_repo_dir, sample_file, performance_result
        )

        # Retrieve both
        cached_security = cache_manager.get_cached_analysis(
            temp_repo_dir, sample_file, "security"
        )
        cached_performance = cache_manager.get_cached_analysis(
            temp_repo_dir, sample_file, "performance"
        )

        assert cached_security is not None
        assert cached_performance is not None
        assert cached_security.summary["type"] == "security"
        assert cached_performance.summary["type"] == "performance"

    def test_cache_clear_updates_timestamp(self, cache_manager):
        """Test that clearing cache updates last_cleared timestamp."""
        # Clear cache
        cache_manager.clear_all()

        # Check stats
        stats = cache_manager.get_stats()
        assert stats.last_cleared is not None
        assert isinstance(stats.last_cleared, datetime)


class TestCacheMetadata:
    """Test CacheMetadata class."""

    def test_to_dict(self):
        """Test converting metadata to dictionary."""
        metadata = CacheMetadata(
            file_path="test.py",
            file_hash="abc123",
            analyzer_name="security",
            timestamp=datetime(2025, 10, 5, 10, 30),
            air_version="0.6.1",
        )

        data = metadata.to_dict()
        assert data["file_path"] == "test.py"
        assert data["file_hash"] == "abc123"
        assert data["analyzer_name"] == "security"
        assert data["air_version"] == "0.6.1"
        assert "2025-10-05" in data["timestamp"]

    def test_from_dict(self):
        """Test creating metadata from dictionary."""
        data = {
            "file_path": "test.py",
            "file_hash": "abc123",
            "analyzer_name": "security",
            "timestamp": "2025-10-05T10:30:00",
            "air_version": "0.6.1",
        }

        metadata = CacheMetadata.from_dict(data)
        assert metadata.file_path == "test.py"
        assert metadata.file_hash == "abc123"
        assert metadata.analyzer_name == "security"
        assert metadata.air_version == "0.6.1"
        assert metadata.timestamp.year == 2025


class TestCacheStats:
    """Test CacheStats class."""

    def test_to_dict(self):
        """Test converting stats to dictionary."""
        stats = CacheStats(
            total_entries=10,
            cache_size_mb=1.5,
            hit_count=8,
            miss_count=2,
            last_cleared=datetime(2025, 10, 5),
        )

        data = stats.to_dict()
        assert data["total_entries"] == 10
        assert data["cache_size_mb"] == 1.5
        assert data["hit_count"] == 8
        assert data["miss_count"] == 2
        assert data["hit_rate"] == 80.0
        assert "2025-10-05" in data["last_cleared"]

    def test_to_dict_no_last_cleared(self):
        """Test to_dict with no last_cleared."""
        stats = CacheStats(
            total_entries=5, cache_size_mb=0.5, hit_count=3, miss_count=2
        )

        data = stats.to_dict()
        assert data["last_cleared"] is None
