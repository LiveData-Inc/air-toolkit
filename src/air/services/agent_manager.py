"""Agent lifecycle management for parallel execution."""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import psutil

from air.utils.console import success
from air.utils.paths import safe_filename


def generate_agent_id(command: str) -> str:
    """Generate unique agent ID.

    Args:
        command: Command name (e.g., "analyze")

    Returns:
        Agent ID in format: YYYYMMDD-HHMM-command-NNN
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    safe_cmd = safe_filename(command)
    return f"{timestamp}-{safe_cmd}"


def get_agent_dir(agent_id: str) -> Path:
    """Get agent directory path.

    Args:
        agent_id: Agent identifier

    Returns:
        Path to agent directory
    """
    return Path(".air/agents") / agent_id


def is_process_running(pid: int | None) -> bool:
    """Check if a process is still running (cross-platform).

    Args:
        pid: Process ID

    Returns:
        True if process is running, False otherwise
    """
    if pid is None:
        return False

    try:
        process = psutil.Process(pid)
        return process.is_running()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False


def spawn_background_agent(
    agent_id: str,
    command: str,
    args: dict[str, Any],
    resource_path: str | None = None,
) -> None:
    """Spawn a background agent.

    Args:
        agent_id: Unique agent identifier
        command: Command to run (e.g., "analyze")
        args: Command arguments
        resource_path: Optional resource path for analysis
    """
    # Create agent directory
    agent_dir = get_agent_dir(agent_id)
    agent_dir.mkdir(parents=True, exist_ok=True)

    # Write metadata
    metadata = {
        "id": agent_id,
        "command": command,
        "args": args,
        "resource_path": resource_path,
        "status": "running",
        "started": datetime.now().isoformat(),
        "pid": None,  # Will be updated by subprocess
    }
    (agent_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    # Build command line arguments
    cmd_args = ["air", command]

    if resource_path:
        cmd_args.append(resource_path)

    # Add agent ID so background process can update its status
    cmd_args.extend(["--id", agent_id])

    # Add args as flags
    for key, value in args.items():
        if isinstance(value, bool):
            if value:
                cmd_args.append(f"--{key}")
        elif value is not None:
            cmd_args.extend([f"--{key}", str(value)])

    # Spawn subprocess in background
    process = subprocess.Popen(
        cmd_args,
        stdout=open(agent_dir / "stdout.log", "w"),
        stderr=open(agent_dir / "stderr.log", "w"),
        cwd=Path.cwd(),
        start_new_session=True,  # Detach from parent
    )

    # Update metadata with PID
    metadata["pid"] = process.pid
    (agent_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    success(f"Started background agent: {agent_id} (PID: {process.pid})")


def load_agent_metadata(agent_id: str) -> dict[str, Any]:
    """Load agent metadata.

    Args:
        agent_id: Agent identifier

    Returns:
        Agent metadata dict

    Raises:
        FileNotFoundError: If agent metadata doesn't exist
    """
    metadata_file = get_agent_dir(agent_id) / "metadata.json"
    if not metadata_file.exists():
        raise FileNotFoundError(f"Agent not found: {agent_id}")

    return json.loads(metadata_file.read_text())


def update_agent_status(agent_id: str, status: str, **kwargs: Any) -> None:
    """Update agent status.

    Args:
        agent_id: Agent identifier
        status: New status (running, complete, failed)
        **kwargs: Additional metadata to update
    """
    metadata = load_agent_metadata(agent_id)
    metadata["status"] = status

    if status == "complete":
        metadata["completed"] = datetime.now().isoformat()
    elif status == "failed":
        metadata["failed"] = datetime.now().isoformat()
        if "error" in kwargs:
            metadata["error"] = kwargs["error"]

    # Add any additional metadata
    metadata.update(kwargs)

    metadata_file = get_agent_dir(agent_id) / "metadata.json"
    metadata_file.write_text(json.dumps(metadata, indent=2))


def list_agents() -> list[dict[str, Any]]:
    """List all agents.

    Auto-updates status for agents whose processes have terminated.

    Returns:
        List of agent metadata dicts
    """
    agents_dir = Path(".air/agents")
    if not agents_dir.exists():
        return []

    agents = []
    for agent_dir in agents_dir.glob("*/"):
        metadata_file = agent_dir / "metadata.json"
        if metadata_file.exists():
            try:
                metadata = json.loads(metadata_file.read_text())

                # Check if process is still running
                if metadata.get("status") == "running":
                    pid = metadata.get("pid")
                    if not is_process_running(pid):
                        # Process has terminated - update status based on exit
                        # Check for errors in stderr
                        stderr_file = agent_dir / "stderr.log"
                        has_errors = False
                        if stderr_file.exists():
                            stderr_content = stderr_file.read_text().strip()
                            has_errors = len(stderr_content) > 0

                        # Update status
                        if has_errors:
                            metadata["status"] = "failed"
                            metadata["failed"] = datetime.now().isoformat()
                        else:
                            metadata["status"] = "complete"
                            metadata["completed"] = datetime.now().isoformat()

                        # Save updated metadata
                        metadata_file.write_text(json.dumps(metadata, indent=2))

                agents.append(metadata)
            except json.JSONDecodeError:
                # Skip corrupted metadata
                continue

    # Sort by started time (newest first)
    agents.sort(key=lambda a: a.get("started", ""), reverse=True)
    return agents


def get_agent_progress(agent_id: str) -> str:
    """Get agent progress message.

    Args:
        agent_id: Agent identifier

    Returns:
        Progress message or empty string
    """
    # For MVP, check stdout for progress
    stdout_file = get_agent_dir(agent_id) / "stdout.log"
    if not stdout_file.exists():
        return ""

    try:
        # Get last non-empty line
        lines = stdout_file.read_text().strip().split("\n")
        for line in reversed(lines):
            if line.strip():
                # Truncate long lines
                return line[:60] + "..." if len(line) > 60 else line
    except Exception:
        pass

    return ""


# Parallel analysis orchestration using ProcessPoolExecutor

import os
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed, TimeoutError as FuturesTimeoutError
from typing import Callable

from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn

from air.services.analysis_worker import run_analyzer_subprocess
from air.services.analyzers.base import AnalyzerResult, Finding, FindingSeverity
from air.utils.console import error, info


class AnalysisOrchestrator:
    """Orchestrates parallel analysis across subprocesses.

    Uses ProcessPoolExecutor to run multiple analyzers in parallel,
    collecting results via JSON communication.
    """

    def __init__(self, max_workers: int | None = None, timeout: int = 300):
        """Initialize orchestrator.

        Args:
            max_workers: Maximum number of parallel processes (defaults to CPU count)
            timeout: Timeout per analyzer in seconds (default: 5 minutes)
        """
        self.max_workers = max_workers or os.cpu_count()
        self.timeout = timeout
        self.executor = ProcessPoolExecutor(max_workers=self.max_workers)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup executor."""
        self.executor.shutdown(wait=True)

    def analyze_parallel(
        self,
        repo_paths: list[Path],
        analyzers: list[str],
        include_external: bool = False,
        progress_callback: Callable[[str, str, bool], None] | None = None,
        show_progress: bool = True,
    ) -> dict[str, list[dict]]:
        """Execute analyzers in parallel, return aggregated results.

        Args:
            repo_paths: List of repository paths to analyze
            analyzers: List of analyzer types (security, performance, etc.)
            include_external: Include external/vendor code in analysis
            progress_callback: Optional callback for progress updates (repo, analyzer, success)
            show_progress: Show progress bar (default: True)

        Returns:
            Dict mapping repo_path -> list of analyzer results (as dicts)
        """
        # Submit all tasks
        futures = {}
        task_count = len(repo_paths) * len(analyzers)

        for repo_path in repo_paths:
            for analyzer_type in analyzers:
                future = self.executor.submit(
                    run_analyzer_subprocess,
                    analyzer_type=analyzer_type,
                    repo_path=str(repo_path),
                    include_external=include_external,
                )
                futures[future] = (repo_path, analyzer_type)

        # Collect results with progress bar
        results = defaultdict(list)

        if show_progress:
            import time
            start_time = time.time()

            # Track completion messages
            completed_analyzers = []

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
            ) as progress:
                # Create individual task for each analyzer (these stay visible)
                task_map = {}
                for repo_path in repo_paths:
                    for analyzer_type in analyzers:
                        task_key = (str(repo_path), analyzer_type)
                        task_id = progress.add_task(
                            f"  [dim]{analyzer_type}: {repo_path.name}[/dim]",  # Indent with 2 spaces
                            total=None  # Spinner, no progress bar
                        )
                        task_map[task_key] = task_id

                # Process results as they complete
                for future in as_completed(futures, timeout=self.timeout * task_count):
                    repo_path, analyzer_type = futures[future]
                    task_key = (str(repo_path), analyzer_type)
                    task_id = task_map[task_key]

                    try:
                        result_json = future.result(timeout=self.timeout)
                        results[str(repo_path)].append(result_json)

                        if result_json.get("success"):
                            elapsed = result_json.get("elapsed_time", 0)
                            # Update task with success (remove spinner, keep visible)
                            progress.stop_task(task_id)
                            progress.update(
                                task_id,
                                description=f"  [green]✓ {analyzer_type}: {repo_path.name}"
                            )
                            completed_analyzers.append((analyzer_type, repo_path.name, elapsed, True))
                            if progress_callback:
                                progress_callback(str(repo_path), analyzer_type, True)
                        else:
                            error_msg = result_json.get("error", "Unknown error")
                            # Update task with failure
                            progress.stop_task(task_id)
                            progress.update(
                                task_id,
                                description=f"  [red]✗ {analyzer_type}: {repo_path.name} - {error_msg}"
                            )
                            completed_analyzers.append((analyzer_type, repo_path.name, 0, False))
                            if progress_callback:
                                progress_callback(str(repo_path), analyzer_type, False)

                    except FuturesTimeoutError:
                        progress.stop_task(task_id)
                        progress.update(
                            task_id,
                            description=f"  [red]✗ {analyzer_type}: {repo_path.name} - Timeout"
                        )
                        completed_analyzers.append((analyzer_type, repo_path.name, 0, False))
                        if progress_callback:
                            progress_callback(str(repo_path), analyzer_type, False)

                    except Exception as e:
                        progress.stop_task(task_id)
                        progress.update(
                            task_id,
                            description=f"  [red]✗ {analyzer_type}: {repo_path.name} - {e}"
                        )
                        completed_analyzers.append((analyzer_type, repo_path.name, 0, False))
                        if progress_callback:
                            progress_callback(str(repo_path), analyzer_type, False)

            # After progress display exits, show total elapsed time
            total_elapsed = time.time() - start_time
            info(f"Analysis complete: {len(completed_analyzers)} tasks in {total_elapsed:.2f}s")
        else:
            # No progress bar - use simple output
            info(f"Submitting {task_count} analysis tasks to {self.max_workers} workers...")
            completed = 0

            for future in as_completed(futures, timeout=self.timeout * task_count):
                repo_path, analyzer_type = futures[future]
                completed += 1

                try:
                    result_json = future.result(timeout=self.timeout)
                    results[str(repo_path)].append(result_json)

                    if result_json.get("success"):
                        elapsed = result_json.get("elapsed_time", 0)
                        info(f"✓ [{completed}/{task_count}] {analyzer_type}: {repo_path.name} ({elapsed:.2f}s)")
                        if progress_callback:
                            progress_callback(str(repo_path), analyzer_type, True)
                    else:
                        error_msg = result_json.get("error", "Unknown error")
                        error(f"✗ [{completed}/{task_count}] {analyzer_type}: {repo_path.name} - {error_msg}")
                        if progress_callback:
                            progress_callback(str(repo_path), analyzer_type, False)

                except FuturesTimeoutError:
                    error(f"✗ [{completed}/{task_count}] {analyzer_type}: {repo_path.name} - Timeout after {self.timeout}s")
                    if progress_callback:
                        progress_callback(str(repo_path), analyzer_type, False)

                except Exception as e:
                    error(f"✗ [{completed}/{task_count}] {analyzer_type}: {repo_path.name} - {e}")
                    if progress_callback:
                        progress_callback(str(repo_path), analyzer_type, False)

        return dict(results)


def reconstruct_analyzer_result(result_dict: dict) -> AnalyzerResult | None:
    """Reconstruct AnalyzerResult from JSON dict.

    Args:
        result_dict: JSON result from subprocess

    Returns:
        AnalyzerResult object or None if failed
    """
    if not result_dict.get("success"):
        return None

    result_data = result_dict.get("result", {})

    # Reconstruct Finding objects
    findings = []
    for finding_dict in result_data.get("findings", []):
        finding = Finding(
            category=finding_dict.get("category", "unknown"),
            severity=FindingSeverity(finding_dict.get("severity", "info")),
            title=finding_dict.get("title", ""),
            description=finding_dict.get("description", ""),
            location=finding_dict.get("location"),
            line_number=finding_dict.get("line_number"),
            suggestion=finding_dict.get("suggestion"),
            metadata=finding_dict.get("metadata", {}),
        )
        findings.append(finding)

    # Reconstruct AnalyzerResult
    return AnalyzerResult(
        analyzer_name=result_data.get("analyzer", "unknown"),
        findings=findings,
        summary=result_data.get("summary", {}),
        metadata=result_data.get("metadata", {}),
    )
