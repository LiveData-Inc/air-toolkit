"""Analysis worker for subprocess-based parallel execution."""

import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from air.services.analyzers import (
    ArchitectureAnalyzer,
    CodeStructureAnalyzer,
    PerformanceAnalyzer,
    QualityAnalyzer,
    SecurityAnalyzer,
)

# Analyzer type mapping
ANALYZER_MAP = {
    "security": SecurityAnalyzer,
    "performance": PerformanceAnalyzer,
    "architecture": ArchitectureAnalyzer,
    "quality": QualityAnalyzer,
    "code_structure": CodeStructureAnalyzer,
}


def run_analyzer_subprocess(
    analyzer_type: str,
    repo_path: str,
    include_external: bool = False,
) -> dict[str, Any]:
    """Run single analyzer in subprocess, return JSON result.

    This function is the entry point for subprocess-based analysis.
    It runs in a separate process and communicates via JSON.

    Args:
        analyzer_type: Type of analyzer (security, performance, etc.)
        repo_path: Path to repository to analyze
        include_external: Whether to include external/vendor code

    Returns:
        Dict with analysis results, timing, and metadata

    Raises:
        ValueError: If analyzer_type is unknown
        Exception: If analysis fails
    """
    start_time = time.time()

    try:
        # Validate analyzer type
        if analyzer_type not in ANALYZER_MAP:
            raise ValueError(
                f"Unknown analyzer type: {analyzer_type}. "
                f"Valid types: {', '.join(ANALYZER_MAP.keys())}"
            )

        # Get analyzer class and instantiate
        analyzer_class = ANALYZER_MAP[analyzer_type]
        repo_path_obj = Path(repo_path).expanduser().resolve()

        if not repo_path_obj.exists():
            raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

        # Create analyzer instance
        analyzer = analyzer_class(repo_path_obj, include_external=include_external)

        # Run analysis
        result = analyzer.analyze()

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Return success result
        return {
            "success": True,
            "analyzer": analyzer_type,
            "repo_path": str(repo_path_obj),
            "result": result.to_dict(),
            "elapsed_time": elapsed_time,
            "timestamp": time.time(),
            "pid": os.getpid(),
        }

    except Exception as e:
        # Calculate elapsed time even on failure
        elapsed_time = time.time() - start_time

        # Return error result
        return {
            "success": False,
            "analyzer": analyzer_type,
            "repo_path": repo_path,
            "error": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc(),
            "elapsed_time": elapsed_time,
            "timestamp": time.time(),
            "pid": os.getpid(),
        }


def main():
    """CLI entry point for running analyzer as subprocess.

    Reads arguments from command line and outputs JSON to stdout.
    This allows the worker to be invoked as:
        python -m air.services.analysis_worker security /path/to/repo [--include-external]

    Output is JSON on stdout, suitable for parent process to parse.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Run analyzer in subprocess")
    parser.add_argument("analyzer_type", choices=ANALYZER_MAP.keys(), help="Analyzer to run")
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument(
        "--include-external",
        action="store_true",
        help="Include external/vendor code in analysis",
    )

    args = parser.parse_args()

    # Run analyzer and get result
    result = run_analyzer_subprocess(
        analyzer_type=args.analyzer_type,
        repo_path=args.repo_path,
        include_external=args.include_external,
    )

    # Output JSON to stdout
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
